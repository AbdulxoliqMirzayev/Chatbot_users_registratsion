import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from translit import (
    is_latin,
    is_cyrillic,
    latin_to_cyr,
    cyr_to_latin,
)


load_dotenv()
# .env dep nomlangan   feyil ochib kerakli kalitlarni  qo'yasiz gemini va bot apilari bo'lishi lozim. 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY .env faylida yo‘q")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN .env faylida yo‘q")

# gewmini konfiguratsiyasi
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


with open("/home/abdulxoliq_m/chatbot_Gemini/data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

CONTEXT = "\n".join(
    [
        f"{i+1}. SAVOL: {x['question']} | JAVOB: {x['answer']}"
        for i, x in enumerate(DATA)
    ]
)


def find_answer(user_question: str) -> str:
    prompt = f"""
Sen professional AI assistantsan.

VAZIFA:
- Foydalanuvchi savolining MAZMUNINI tahlil qil
- Quyidagi savol-javoblardan ENG MOSINI tanla
- FAQAT o‘sha savolning JAVOBINI qaytar
- Agar mos savol topilmasa: "Savol aniqlanmadi" deb yoz

Foydalanuvchi savoli:
{user_question}

SAVOL-JAVOBLAR:
{CONTEXT}

Faqat JAVOBNI yoz. Izoh yo‘q.
"""
    response = model.generate_content(prompt)
    return response.text.strip()


# Telegram bot handlerlari

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "🤖 Men aholini ro‘yxatga olish bo‘yicha savollarga javob beruvchi chatbotman.\n\n"
        "✍️ Savolingizni yozing."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_q = update.message.text.strip()

    if not user_q:
        await update.message.reply_text("Savolingizni yozing.")
        return

    try:
        answer = find_answer(user_q)

        # Alifbo moslash
        if is_latin(user_q):
            answer = cyr_to_latin(answer)
        elif is_cyrillic(user_q):
            answer = latin_to_cyr(answer)

        await update.message.reply_text(answer)

    except Exception:
        await update.message.reply_text("❌ Xatolik yuz berdi.")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram chatbot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
