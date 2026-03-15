from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


TipoSolicitud = Literal[
    "PETICION",
    "QUEJA",
    "RECLAMO",
    "SUGERENCIA",
    "INCIDENTE",
    "SOLICITUD",
    "CONSULTA",
]


class TicketCreateIn(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150)
    documento: Optional[str] = Field(None, max_length=50)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=30)
    tieneWhatsapp: bool = False
    empresaDepartamento: Optional[str] = Field(None, max_length=150)

    tipo: TipoSolicitud
    categoria: str = Field(..., min_length=2, max_length=100)
    subcategoria: Optional[str] = Field(None, max_length=100)
    asunto: Optional[str] = Field(None, max_length=200)
    descripcion: str = Field(..., min_length=10)
    prioridad: str = Field(..., max_length=20)
    areaAsignada: Optional[str] = Field("MESA", max_length=100)


class TicketCreateOut(BaseModel):
    ticketUuid: str
    ticketLabel: str
    estado: str
    tipo: str
    prioridad: str
    slaHoras: int
    fechaCreacion: str
    fechaLimiteSla: str
    mensaje: str


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


class ConsultarTicketIn(BaseModel):
    label: str
    email: EmailStr