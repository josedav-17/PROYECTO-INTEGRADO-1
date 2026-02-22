from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

from app.db.session import get_db
from app.schemas.tickets import TicketCreateIn
from app.schemas.tickets import ConsultarTicketIn

router = APIRouter(prefix="/api/tickets", tags=["tickets-public"])

@router.post("/public")
def crear_ticket_public(ticket: TicketCreateIn, request: Request, db: Session = Depends(get_db)):
    # tu SP espera p_label (ticket_label)
    label = f"TCK-{uuid.uuid4().hex[:8].upper()}"

    sql = text("""
        CALL sp_crear_ticket(
          CAST(:label AS VARCHAR),
          CAST(:nom   AS VARCHAR),
          CAST(:em    AS VARCHAR),
          CAST(:tel   AS VARCHAR),
          CAST(:ws    AS BOOLEAN),
          CAST(:cat   AS VARCHAR),
          CAST(:asu   AS VARCHAR),
          CAST(:des   AS TEXT),
          CAST(:prio  AS VARCHAR),
          CAST(:ip    AS INET)
        )
    """)

    params = {
        "label": label,
        "nom": ticket.nombre,
        "em": str(ticket.email),
        "tel": ticket.telefono,
        "ws": ticket.tieneWhatsapp,
        "cat": ticket.categoria,
        "asu": ticket.asunto or "",
        "des": ticket.descripcion,
        "prio": ticket.prioridad or "MEDIA",
        "ip": request.client.host,  # '127.0.0.1' castea a INET ok
    }

    try:
        db.execute(sql, params)
        db.commit()
        return {"message": "Ticket creado exitosamente", "label": label}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/public/consultar")
def consultar_ticket_publico(payload: ConsultarTicketIn, db: Session = Depends(get_db)):
    q = text("SELECT * FROM fn_consultar_ticket_publico(:label, :email)")
    row = db.execute(q, {"label": payload.label.strip().upper(), "email": str(payload.email)}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    return dict(row)