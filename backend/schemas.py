from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict


class ThreadCreate(BaseModel):
    title: str


class ThreadResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    thread_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ThreadDetailResponse(ThreadResponse):
    messages: List[MessageResponse] = []


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    thread_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse


class MemoryItem(BaseModel):
    memory_key: str
    memory_value: str
    updated_at: datetime

    class Config:
        from_attributes = True


class MemoryResponse(BaseModel):
    memory: List[MemoryItem]