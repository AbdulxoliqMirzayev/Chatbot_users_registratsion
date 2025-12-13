import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

from translit import (
    is_cyrillic,
    is_latin,
    cyr_to_latin,
    latin_to_cyr,
)


load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY .env faylida topilmadi")

# LLM gemini modelini versiyasini tanlaymiz 2.5 modelini tanlaymiz bu bizga aniq ishlashga yordam beradi 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# datasetni json fayldan yuklaymiz
with open("/home/abdulxoliq_m/chatbot_Gemini/data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

CONTEXT = "\n".join(
    [
        f"{i+1}. SAVOL: {item['question']} | JAVOB: {item['answer']}"
        for i, item in enumerate(DATA)
    ]
)


app = FastAPI(
    title="Gemini Q&A Chatbot API",
    description="Lotin va Kirill alifbosida savollarga javob beruvchi AI chatbot",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


# Prompt yozamiz chatbot vazifasini tushuntirish uchun
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


@app.get("/")
def root():
    return {
        "status": "OK",
        "message": "Gemini Chatbot API ishlayapti",
        "docs": "/docs",
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    user_question = req.question.strip()

    if not user_question:
        return {"answer": "Savol bo‘sh bo‘lishi mumkin emas"}

    answer = find_answer(user_question)

    if "aniqlanmadi" in answer.lower():
        return {"answer": "Savol aniqlanmadi"}
    # user yozgan alifboga moslash 
    if is_latin(user_question):
        answer = cyr_to_latin(answer)
    elif is_cyrillic(user_question):
        answer = latin_to_cyr(answer)

    return {"answer": answer}
