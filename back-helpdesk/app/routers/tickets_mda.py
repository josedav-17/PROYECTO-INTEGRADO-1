from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.core.deps import require_roles
from app.schemas.tickets import (
    AsignarIn, TransferirIn, CancelarIn,
    ReclasificarIn, ReabrirIn, PausarIn
)

router = APIRouter(prefix="/api/tickets", tags=["tickets-mda"])

def exec_sp(db: Session, sql: str, params: dict):
    try:
        db.execute(text(sql), params)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{ticket_id}/asignar", dependencies=[Depends(require_roles("ADMIN", "MESA"))])
def asignar(ticket_id: str, datos: AsignarIn, db: Session = Depends(get_db)):
    exec_sp(db, "CALL sp_asignar_ticket(:id, :agente, :com)",
            {"id": ticket_id, "agente": datos.agenteId, "com": datos.motivo})
    return {"message": "Asignado"}

@router.post("/{ticket_id}/transferir", dependencies=[Depends(require_roles("ADMIN", "MESA"))])
def transferir(ticket_id: str, datos: TransferirIn, db: Session = Depends(get_db)):
    exec_sp(db, "CALL sp_transferir_ticket(:id, :area, :agente, :motivo)",
            {"id": ticket_id, "area": datos.nuevaArea, "agente": datos.agenteId, "motivo": datos.motivo})
    return {"message": "Transferido"}

@router.post("/{ticket_id}/reclasificar", dependencies=[Depends(require_roles("ADMIN", "MESA"))])
def reclasificar(ticket_id: str, datos: ReclasificarIn, db: Session = Depends(get_db)):
    exec_sp(db, "CALL sp_reclasificar_ticket(:id, :prio, :cat, :motivo)",
            {"id": ticket_id, "prio": datos.nuevaPrioridad, "cat": datos.nuevaCategoria, "motivo": datos.motivo})
    return {"message": "Reclasificado"}

@router.post("/{ticket_id}/pausar", dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))])
def pausar(ticket_id: str, datos: PausarIn, db: Session = Depends(get_db)):
    exec_sp(db, "CALL sp_pausar_ticket(:id, :motivo)",
            {"id": ticket_id, "motivo": datos.motivo})
    return {"message": "Pausado"}

@router.post("/{ticket_id}/reabrir", dependencies=[Depends(require_roles("ADMIN", "MESA"))])
def reabrir(ticket_id: str, datos: ReabrirIn, db: Session = Depends(get_db)):
    exec_sp(db, "CALL sp_reabrir_ticket(:id, :motivo)",
            {"id": ticket_id, "motivo": datos.motivo})
    return {"message": "Reabierto"}

@router.post("/{ticket_id}/cancelar", dependencies=[Depends(require_roles("ADMIN", "MESA", "AREA"))])
def cancelar(ticket_id: str, datos: CancelarIn, db: Session = Depends(get_db)):
    exec_sp(db, "CALL sp_cancelar_ticket(:id, :motivo, :por)",
            {"id": ticket_id, "motivo": datos.motivo, "por": datos.rol})
    return {"message": "Cancelado"}