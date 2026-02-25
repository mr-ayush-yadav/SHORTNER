from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests

TOKEN = "8256929214:AAEATXLNEayFnysqLT8RCu4HqrkhQ7DKwoo"

RENDER_URL = "https://shortner-qmsc.onrender.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a long link to shorten.")

async def shorten(update: Update, context: ContextTypes.DEFAULT_TYPE):
    long_url = update.message.text

    try:
        response = requests.post(
            f"{RENDER_URL}/api/shorten",
            json={"url": long_url}
        )

        if response.status_code == 200:
            short_url = response.json()["short_url"]
            await update.message.reply_text(f"Short URL: {short_url}")
        else:
            await update.message.reply_text("Error generating short link.")
    except Exception as e:
        await update.message.reply_text("Server error.")

app_bot = ApplicationBuilder().token(TOKEN).build()

app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten))

app_bot.run_polling()