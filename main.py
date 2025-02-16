from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import time
import os

# Thiết lập log để debug dễ hơn
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Token bot Telegram
TOKEN = "7666413078:AAHPEwCP26AWgLf4UeA1Lzn5JQqMVdNtUmw"
GROUP_ID = -2381062851  # Thay bằng ID group của mày

# Số dư giả lập
user_balance = {"user": 1000, "bot": 1000}  # Mỗi bên 1000 USDT
open_orders = []

# Khởi tạo Flask server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Telegram đang chạy!"

@app.route('/health')
def health_check():
    return "OK", 200  # Koyeb cần cái này để biết service còn sống

def run_flask():
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)

# Xử lý lệnh bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot trade đã hoạt động! Dùng /help để xem lệnh.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    📌 Lệnh bot hỗ trợ:
    /balance - Xem số dư
    /trade <MUA/BÁN> <coin> <số lượng> <giá> - Đặt lệnh
    """
    await update.message.reply_text(help_text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.username or "user"
    balance_text = f"💰 Số dư của {user}: {user_balance['user']} USDT\n🤖 Số dư bot: {user_balance['bot']} USDT"
    await update.message.reply_text(balance_text)

async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.username or "user"
    args = context.args

    if len(args) != 4:
        await update.message.reply_text("⚠️ Sai cú pháp! Dùng: /trade <MUA/BÁN> <coin> <số lượng> <giá>")
        return

    action, coin, amount, price = args

    try:
        amount = float(amount)
        price = float(price)
    except ValueError:
        await update.message.reply_text("❌ Số lượng và giá phải là số hợp lệ!")
        return

    total_cost = amount * price

    if action.upper() == "MUA":
        if user_balance["user"] >= total_cost:
            user_balance["user"] -= total_cost
            user_balance["bot"] += total_cost
            open_orders.append((user, action, coin, amount, price))
            await update.message.reply_text(f"✅ {user} đã mua {amount} {coin} giá {price} USDT!")
        else:
            await update.message.reply_text("❌ Không đủ USDT để mua!")

    elif action.upper() == "BÁN":
        if user_balance["bot"] >= total_cost:
            user_balance["user"] += total_cost
            user_balance["bot"] -= total_cost
            open_orders.append((user, action, coin, amount, price))
            await update.message.reply_text(f"✅ {user} đã bán {amount} {coin} giá {price} USDT!")
        else:
            await update.message.reply_text("❌ Bot không đủ USDT để mua!")
    else:
        await update.message.reply_text("❌ Hành động không hợp lệ! Chỉ chấp nhận MUA hoặc BÁN.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("LỆNH"):
        await update.message.reply_text("📜 Bot đã ghi nhận lệnh: " + text)

# Chạy bot Telegram
def run_telegram_bot():
    bot = Application.builder().token(TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("help", help_command))
    bot.add_handler(CommandHandler("balance", balance))
    bot.add_handler(CommandHandler("trade", trade))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("🤖 Bot Telegram đang chạy...")
    bot.run_polling()

if __name__ == "__main__":
    # Chạy Flask server trên một luồng riêng
    Thread(target=run_flask, daemon=True).start()

    # Chạy bot Telegram trên luồng chính
    run_telegram_bot()
