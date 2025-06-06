
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from farming import claim_all_wallets, add_wallet
from keep_alive import keep_alive
import json, os

USER_DB_FILE = "users.json"

if __name__ == '__main__':
    keep_alive()

def load_users():
    if not os.path.exists(USER_DB_FILE):
        return []
    with open(USER_DB_FILE, "r") as f:
        return json.load(f)

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_chat.id)
    await update.message.reply_text("🤖 Bot aktif!\nGunakan `/addtoken <wallet> <api_token>` untuk menambahkan farming.")

async def addtoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        address = context.args[0]
        token = context.args[1]
        success = add_wallet(address, token)
        save_user(update.effective_chat.id)
        if success:
            await update.message.reply_text("✅ Wallet ditambahkan.")
        else:
            await update.message.reply_text("⚠️ Wallet sudah ada.")
    except:
        await update.message.reply_text("❌ Format salah! Contoh: `/addtoken 0xABC... eyJhbGci...`")

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = claim_all_wallets()
    await update.message.reply_text(f"✅ Farming Manual\n\n{result}", parse_mode="Markdown")

async def auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = claim_all_wallets()
    await update.message.reply_text(f"✅ [AUTO FARMING] Claim berjalan...\n\n{result}", parse_mode="Markdown")

async def auto_farm_job(app):
    while True:
        print("[AUTO FARMING] Claim berjalan...")
        result = claim_all_wallets()
        users = load_users()
        for uid in users:
            try:
                await app.bot.send_message(chat_id=uid, text=f"🤖 Auto Farming\n\n{result}", parse_mode="Markdown")
            except Exception as e:
                print(f"❌ Gagal kirim ke {uid}: {e}")
        await asyncio.sleep(43200)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addtoken", addtoken))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("auto", auto))
    app.job_queue.run_once(lambda c: asyncio.create_task(auto_farm_job(app)), 1)
    app.run_polling()
