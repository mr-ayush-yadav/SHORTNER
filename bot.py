from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from app import db, URL, generate_short, app as flask_app

TOKEN = "8256929214:AAEhZsOKWczsXqC1GSWFZXZUS-X-kbwuyOM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Apna link bhejo short karne ke liye.")

async def shorten(update: Update, context: ContextTypes.DEFAULT_TYPE):
    long_url = update.message.text
    
    with flask_app.app_context():
        short = generate_short()
        new_url = URL(original=long_url, short=short, user_id=1)
        db.session.add(new_url)
        db.session.commit()

    short_url = f"http://127.0.0.1:5000/{short}"
    await update.message.reply_text(f"Short URL: {short_url}")

app_bot = ApplicationBuilder().token(TOKEN).build()

app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten))

app_bot.run_polling()