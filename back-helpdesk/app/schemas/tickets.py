from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class TicketCreateIn(BaseModel):
    nombre: str
    documento: Optional[str] = None
    email: EmailStr
    telefono: Optional[str] = None
    tieneWhatsapp: bool = False
    empresaDepartamento: Optional[str] = None

    categoria: str
    subcategoria: Optional[str] = None
    asunto: Optional[str] = None
    descripcion: str
    prioridad: Optional[str] = "MEDIA"
    areaAsignada: Optional[str] = None  # opcional

class AsignarIn(BaseModel):
    agenteId: str
    motivo: str

class TransferirIn(BaseModel):
    nuevaArea: str
    agenteId: str
    motivo: str

class CancelarIn(BaseModel):
    motivo: str
    rol: Literal["USUARIO", "AGENTE"]

class ReclasificarIn(BaseModel):
    nuevaPrioridad: str
    nuevaCategoria: str
    motivo: str

class ReabrirIn(BaseModel):
    motivo: str

class PausarIn(BaseModel):
    motivo: str

class AnonimizarIn(BaseModel):
    mesesAntiguedad: int

class ConsultarTicketIn(BaseModel):
    label: str
    email: EmailStr