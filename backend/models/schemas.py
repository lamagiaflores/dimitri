from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DeviceType(str, Enum):
    mobile = "mobile"
    desktop = "desktop"


class UserMode(str, Enum):
    personal = "personal"
    business = "business"


class TaskStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    error_internal = "error_internal"  # nunca se muestra al usuario como "fallido"


class VoiceCommand(BaseModel):
    uid: str
    transcript: str = Field(..., min_length=1)
    device: DeviceType = DeviceType.mobile
    mode: UserMode = UserMode.personal
    session_id: Optional[str] = None
    language: str = "es-PE"


class ChatMessage(BaseModel):
    uid: str
    session_id: str
    text: Optional[str] = None
    attachments: List[Dict[str, str]] = Field(default_factory=list)  # name, mime, storagePath
    mode: UserMode = UserMode.personal


class AdaptiveResponse(BaseModel):
    spoken: str
    expression: str = "happy"
    chat_reply: Optional[str] = None
    task_id: Optional[str] = None
    deliverable_created: bool = False
    deliverable_type: Optional[str] = None
    download_url: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class DeliverableOut(BaseModel):
    id: str
    type: str
    title: str
    filename: Optional[str] = None
    download_url: Optional[str] = None
    status: TaskStatus = TaskStatus.ready
    origin: str = "voice"
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)