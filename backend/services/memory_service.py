import json
from typing import Dict, List
from sqlalchemy.orm import Session

from models import Memory, Message
from services.ai_service import _get_model


def get_all_memory(db: Session) -> Dict[str, str]:
    records = db.query(Memory).all()
    return {r.memory_key: r.memory_value for r in records}


def save_memory(db: Session, memory_dict: Dict[str, str]) -> None:
    for key, value in memory_dict.items():
        if not key or value is None:
            continue
        record = db.query(Memory).filter(Memory.memory_key == key).first()
        if record:
            record.memory_value = str(value)
        else:
            record = Memory(memory_key=key, memory_value=str(value))
            db.add(record)
    db.commit()


def build_context(db: Session, thread_id: int):
    universal_memory = get_all_memory(db)

    messages = (
        db.query(Message)
        .filter(Message.thread_id == thread_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    thread_messages = [{"role": m.role, "content": m.content} for m in messages]

    return universal_memory, thread_messages


def extract_memory(user_message: str, assistant_message: str, existing_memory: Dict[str, str]) -> Dict[str, str]:
    existing_text = "\n".join(
        f"- {k}: {v}" for k, v in existing_memory.items()
    ) or "None"

    prompt = f"""Extract key persistent facts about the user from this conversation exchange
that would be useful to remember in future conversations (e.g. health issues, symptoms,
preferences, names, ongoing topics).

Existing known facts:
{existing_text}

New exchange:
User: {user_message}
Assistant: {assistant_message}

Return ONLY a valid JSON object of new or updated key-value facts to store.
Use short snake_case keys and concise values. If there is nothing new or worth
remembering, return an empty JSON object {{}}.
Do not include any explanation, markdown formatting, or code fences. Output raw JSON only.
"""

    try:
        model = _get_model()
        response = model.generate_content(prompt)
        text = response.text.strip() if response.text else "{}"

        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        extracted = json.loads(text)
        if isinstance(extracted, dict):
            return {str(k): str(v) for k, v in extracted.items()}
        return {}
    except Exception:
        return {}
