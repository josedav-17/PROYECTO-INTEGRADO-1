from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class TicketCreate(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    tieneWhatsapp: bool = Field(False, alias="tiene_whatsapp")
    categoria: str
    asunto: str
    descripcion: str

class TicketResponse(BaseModel):
    uuid: UUID
    ticket_label: str
    solicitante_nombre: str
    solicitante_email: str
    estado_id: int
    prioridad_id: int
    creado_en: datetime

    class Config:
        from_attributes = True