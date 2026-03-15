from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.schemas.tickets import (
    TicketCreateIn,
    TicketCreateOut,
    AsignarIn,
    TransferirIn,
    CancelarIn,
    ReclasificarIn,
    ReabrirIn,
    PausarIn,
)
from app.services.tickets_service import TicketsService

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def get_tickets_service(db: Session = Depends(get_db)) -> TicketsService:
    return TicketsService(db)


@router.post("/crear", response_model=TicketCreateOut)
def crear_ticket(
    datos: TicketCreateIn,
    request: Request,
    svc: TicketsService = Depends(get_tickets_service),
):
    ip_cliente = request.client.host if request.client else None
    return svc.crear(datos.model_dump(), ip_cliente)


@router.get("/dashboard")
def dashboard(
    user: dict = Depends(get_current_user),
    svc: TicketsService = Depends(get_tickets_service),
):
    return svc.dashboard()


@router.get(
    "/{ticket_id}",
    dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))]
)
def get_ticket(
    ticket_id: str,
    svc: TicketsService = Depends(get_tickets_service),
    user: dict = Depends(get_current_user),
):
    data = svc.get_bundle(ticket_id)

    if not data or not data.get("ticket"):
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    return data


@router.post(
    "/{ticket_id}/asignar",
    dependencies=[Depends(require_roles("ADMIN", "MESA"))]
)
def asignar(
    ticket_id: str,
    datos: AsignarIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    svc.asignar(ticket_id, datos.agenteId, datos.motivo)
    return {"message": "Asignado"}


@router.post(
    "/{ticket_id}/transferir",
    dependencies=[Depends(require_roles("ADMIN", "MESA"))]
)
def transferir(
    ticket_id: str,
    datos: TransferirIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    svc.transferir(ticket_id, datos.nuevaArea, datos.agenteId, datos.motivo)
    return {"message": "Transferido"}


@router.post(
    "/{ticket_id}/reclasificar",
    dependencies=[Depends(require_roles("ADMIN", "MESA"))]
)
def reclasificar(
    ticket_id: str,
    datos: ReclasificarIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    svc.reclasificar(ticket_id, datos.nuevaPrioridad, datos.nuevaCategoria, datos.motivo)
    return {"message": "Reclasificado"}


@router.post(
    "/{ticket_id}/pausar",
    dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))]
)
def pausar(
    ticket_id: str,
    datos: PausarIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    svc.pausar(ticket_id, datos.motivo)
    return {"message": "Pausado"}


@router.post(
    "/{ticket_id}/reabrir",
    dependencies=[Depends(require_roles("ADMIN", "MESA"))]
)
def reabrir(
    ticket_id: str,
    datos: ReabrirIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    svc.reabrir(ticket_id, datos.motivo)
    return {"message": "Reabierto"}


@router.post(
    "/{ticket_id}/cancelar",
    dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))]
)
def cancelar(
    ticket_id: str,
    datos: CancelarIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    svc.cancelar(ticket_id, datos.motivo, datos.rol)
    return {"message": "Cancelado"}