from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import Base, engine, get_db
import models
import schemas
from services import ai_service, memory_service

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini AI Chat Application")


@app.post("/threads", response_model=schemas.ThreadResponse)
def create_thread(thread: schemas.ThreadCreate, db: Session = Depends(get_db)):
    new_thread = models.ChatThread(title=thread.title)
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    return new_thread


@app.get("/threads", response_model=List[schemas.ThreadResponse])
def list_threads(db: Session = Depends(get_db)):
    return db.query(models.ChatThread).order_by(models.ChatThread.created_at.asc()).all()


@app.get("/threads/{thread_id}", response_model=schemas.ThreadDetailResponse)
def get_thread(thread_id: int, db: Session = Depends(get_db)):
    thread = db.query(models.ChatThread).filter(models.ChatThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@app.post("/chat/{thread_id}", response_model=schemas.ChatResponse)
def chat(thread_id: int, request: schemas.ChatRequest, db: Session = Depends(get_db)):
    thread = db.query(models.ChatThread).filter(models.ChatThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    universal_memory, thread_messages = memory_service.build_context(db, thread_id)

    ai_text = ai_service.generate_response(
        universal_memory=universal_memory,
        thread_messages=thread_messages,
        user_message=request.message,
    )

    user_msg = models.Message(thread_id=thread_id, role="user", content=request.message)
    assistant_msg = models.Message(thread_id=thread_id, role="assistant", content=ai_text)
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    extracted = memory_service.extract_memory(
        user_message=request.message,
        assistant_message=ai_text,
        existing_memory=universal_memory,
    )
    if extracted:
        memory_service.save_memory(db, extracted)

    return schemas.ChatResponse(
        thread_id=thread_id,
        user_message=user_msg,
        assistant_message=assistant_msg,
    )


@app.get("/memory", response_model=schemas.MemoryResponse)
def get_memory(db: Session = Depends(get_db)):
    records = db.query(models.Memory).all()
    return schemas.MemoryResponse(memory=records)