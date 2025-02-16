from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = "7666413078:AAHPEwCP26AWgLf4UeA1Lzn5JQqMVdNtUmw"
GROUP_ID = -2381062851  # Thay bằng ID group của mày

# Lưu trạng thái trade
user_balance = {"user": 1000, "bot": 1000}  # Mỗi đứa 1000 USDT
open_orders = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot trade đã hoạt động! Dùng /help để xem lệnh.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Lệnh bot hỗ trợ:
    /balance - Xem số dư
    /trade <MUA/BÁN> <coin> <số lượng> <giá> - Đặt lệnh
    """
    await update.message.reply_text(help_text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.username or "user"
    balance_text = f"Số dư của {user}: {user_balance['user']} USDT\nSố dư bot: {user_balance['bot']} USDT"
    await update.message.reply_text(balance_text)

async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.username or "user"
    args = context.args
    
    if len(args) != 4:
        await update.message.reply_text("Sai cú pháp! Dùng: /trade <MUA/BÁN> <coin> <số lượng> <giá>")
        return
    
    action, coin, amount, price = args
    
    try:
        amount = float(amount)
        price = float(price)
    except ValueError:
        await update.message.reply_text("Số lượng và giá phải là số hợp lệ!")
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

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("trade", trade))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot đang chạy...")
    app.run_polling()
