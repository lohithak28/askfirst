import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"


def _get_model():
    return genai.GenerativeModel(MODEL_NAME)


def generate_response(universal_memory: Dict[str, str], thread_messages: List[Dict[str, str]], user_message: str) -> str:
    memory_text = "\n".join(
        f"- {k}: {v}" for k, v in universal_memory.items()
    ) or "None"

    history_text = "\n".join(
        f"{m['role'].capitalize()}: {m['content']}" for m in thread_messages
    ) or "None"

    prompt = f"""You are a helpful AI assistant with persistent memory across conversations.

Universal Memory (facts known about the user from all conversations):
{memory_text}

Current Thread History:
{history_text}

User Message:
{user_message}

Instructions:
Answer naturally using all known context above. If the user message refers to something
discussed earlier (in this thread or via Universal Memory), resolve the reference and
answer specifically. Do not ask the user to repeat information that is already known.
"""

    try:
        model = _get_model()
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "I'm sorry, I couldn't generate a response."
    except Exception as e:
        return f"Error generating response: {str(e)}"