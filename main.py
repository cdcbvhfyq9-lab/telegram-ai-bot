import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = os.getenv("ADMIN_ID")

client = OpenAI(api_key=OPENAI_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom dostim! 👋 Savolingni yoz, AI javob beradi 🤖")


async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen o‘quv markazi uchun yordamchi botsan. Qisqa va tushunarli javob ber."},
                {"role": "user", "content": user_text}
            ]
        )
        answer = resp.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        print("AI ERROR:", e)
        await update.message.reply_text("Xatolik bo‘ldi. Keyinroq urinib ko‘r.")


async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # admin tekshiruv
    if ADMIN_ID and str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("⛔ Bu buyruq faqat admin uchun.")
        return

    if not CHANNEL_ID:
        await update.message.reply_text("CHANNEL_ID yo‘q (Render env variables).")
        return

    if not context.args:
        await update.message.reply_text("Post matnini yoz.\nMisol: /post Bugun 18:00 da dars bor!")
        return

    text = " ".join(context.args)

    try:
        await context.bot.send_message(chat_id=int(CHANNEL_ID), text=text)
        await update.message.reply_text("✅ Kanalga post joylandi")
    except Exception as e:
        print("POST ERROR:", e)
        await update.message.reply_text("Post yuborilmadi. Bot kanalga admin qilinganini tekshir.")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN yo‘q")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY yo‘q")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

    print("Bot ishlayapti...")
    app.run_polling()


if __name__ == "__main__":
    main()
