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
    ConsultarTicketIn,
    ConsultarTicketOut,
    ArchivarIn,
    ActualizarTicketIn,
)
from app.services.tickets_service import TicketsService

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def get_tickets_service(db: Session = Depends(get_db)) -> TicketsService:
    return TicketsService(db)


def _normalize(value: str | None) -> str:
    return (value or "").strip().upper()


def _ticket_area_name(ticket: dict) -> str:
    return _normalize(
        ticket.get("areaAsignada")
        or ticket.get("area_asignada")
        or ticket.get("area")
    )


def _user_area_name(user: dict) -> str:
    return _normalize(
        user.get("area")
        or user.get("area_nombre")
        or user.get("areaNombre")
    )


def _validate_ticket_access(ticket: dict, user: dict) -> None:
    rol = _normalize(user.get("rol"))

    if rol in ("ADMIN", "MESA"):
        return

    if rol == "AREA":
        ticket_area = _ticket_area_name(ticket)
        user_area = _user_area_name(user)

        if not user_area:
            raise HTTPException(
                status_code=403,
                detail="El usuario no tiene un área asignada"
            )

        if ticket_area != user_area:
            raise HTTPException(
                status_code=403,
                detail="No autorizado para acceder a este ticket"
            )
        return

    raise HTTPException(status_code=403, detail="No autorizado")


def _get_ticket_or_404(svc: TicketsService, ticket_id: str) -> dict:
    data = svc.get_bundle(ticket_id)

    if not data or not data.get("ticket"):
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    return data


@router.post("/crear", response_model=TicketCreateOut)
def crear_ticket(
    datos: TicketCreateIn,
    request: Request,
    svc: TicketsService = Depends(get_tickets_service),
):
    ip_cliente = request.client.host if request.client else None
    return svc.crear(datos.model_dump(), ip_cliente)


# ---------------- DASHBOARD LISTADO ----------------
@router.get("/dashboard")
def dashboard(
    user: dict = Depends(get_current_user),
    svc: TicketsService = Depends(get_tickets_service),
):
    return svc.dashboard(
        rol=user.get("rol"),
        area=user.get("area"),
    )


# ---------------- DASHBOARD METRICAS ----------------
@router.get("/dashboard-metricas")
def dashboard_metricas(
    user: dict = Depends(get_current_user),
    svc: TicketsService = Depends(get_tickets_service),
):
    return svc.dashboard_metricas(
        rol=user.get("rol"),
        area=user.get("area"),
    )


# ---------------- CONSULTA PUBLICA ----------------
@router.post("/consultar", response_model=ConsultarTicketOut)
def consultar_ticket(
    datos: ConsultarTicketIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    return svc.consultar_publico(datos.label, datos.email)


# ---------------- DETALLE ----------------
@router.get(
    "/{ticket_id}",
    dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))]
)
def get_ticket(
    ticket_id: str,
    svc: TicketsService = Depends(get_tickets_service),
    user: dict = Depends(get_current_user),
):
    data = _get_ticket_or_404(svc, ticket_id)
    _validate_ticket_access(data["ticket"], user)
    return data


# ---------------- ACTUALIZAR ----------------
@router.post(
    "/{ticket_id}/actualizar",
    dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))]
)
def actualizar_ticket(
    ticket_id: str,
    datos: ActualizarTicketIn,
    svc: TicketsService = Depends(get_tickets_service),
    user: dict = Depends(get_current_user),
):
    data = _get_ticket_or_404(svc, ticket_id)
    _validate_ticket_access(data["ticket"], user)

    svc.actualizar_ticket(
        ticket_id=ticket_id,
        estado=datos.estado,
        prioridad=datos.prioridad,
        area=datos.area,
        respuesta=datos.respuesta,
        actor_user_id=user.get("id"),
        actor_nombre=user.get("nombre"),
        actor_email=user.get("email"),
        actor_rol=user.get("rol"),
    )
    return {"message": "Ticket actualizado correctamente"}


# ---------------- ASIGNAR ----------------
@router.post(
    "/{ticket_id}/asignar",
    dependencies=[Depends(require_roles("ADMIN", "MESA"))]
)
def asignar(
    ticket_id: str,
    datos: AsignarIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    _get_ticket_or_404(svc, ticket_id)
    svc.asignar(ticket_id, datos.agenteId, datos.motivo)
    return {"message": "Asignado"}


# ---------------- TRANSFERIR ----------------
@router.post(
    "/{ticket_id}/transferir",
    dependencies=[Depends(require_roles("ADMIN", "MESA"))]
)
def transferir(
    ticket_id: str,
    datos: TransferirIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    _get_ticket_or_404(svc, ticket_id)
    svc.transferir(ticket_id, datos.nuevaArea, datos.agenteId, datos.motivo)
    return {"message": "Transferido"}


# ---------------- RECLASIFICAR ----------------
@router.post(
    "/{ticket_id}/reclasificar",
    dependencies=[Depends(require_roles("ADMIN", "MESA"))]
)
def reclasificar(
    ticket_id: str,
    datos: ReclasificarIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    _get_ticket_or_404(svc, ticket_id)
    svc.reclasificar(ticket_id, datos.nuevaPrioridad, datos.nuevaCategoria, datos.motivo)
    return {"message": "Reclasificado"}


# ---------------- PAUSAR ----------------
@router.post(
    "/{ticket_id}/pausar",
    dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))]
)
def pausar(
    ticket_id: str,
    datos: PausarIn,
    svc: TicketsService = Depends(get_tickets_service),
    user: dict = Depends(get_current_user),
):
    data = _get_ticket_or_404(svc, ticket_id)
    _validate_ticket_access(data["ticket"], user)

    svc.pausar(ticket_id, datos.motivo)
    return {"message": "Pausado"}


# ---------------- REABRIR ----------------
@router.post(
    "/{ticket_id}/reabrir",
    dependencies=[Depends(require_roles("ADMIN", "MESA"))]
)
def reabrir(
    ticket_id: str,
    datos: ReabrirIn,
    svc: TicketsService = Depends(get_tickets_service),
):
    _get_ticket_or_404(svc, ticket_id)
    svc.reabrir(ticket_id, datos.motivo)
    return {"message": "Reabierto"}


# ---------------- CANCELAR ----------------
@router.post(
    "/{ticket_id}/cancelar",
    dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))]
)
def cancelar(
    ticket_id: str,
    datos: CancelarIn,
    svc: TicketsService = Depends(get_tickets_service),
    user: dict = Depends(get_current_user),
):
    data = _get_ticket_or_404(svc, ticket_id)
    _validate_ticket_access(data["ticket"], user)

    svc.cancelar(ticket_id, datos.motivo, datos.rol)
    return {"message": "Cancelado"}


# ---------------- ARCHIVAR ----------------
@router.post(
    "/{ticket_id}/archivar",
    dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))]
)
def archivar(
    ticket_id: str,
    datos: ArchivarIn,
    svc: TicketsService = Depends(get_tickets_service),
    user: dict = Depends(get_current_user),
):
    data = _get_ticket_or_404(svc, ticket_id)
    _validate_ticket_access(data["ticket"], user)

    svc.archivar(
        ticket_id,
        datos.motivo,
        actor_user_id=user.get("id"),
        actor_nombre=user.get("nombre"),
        actor_email=user.get("email"),
        actor_rol=user.get("rol"),
    )
    return {"message": "Archivado"}