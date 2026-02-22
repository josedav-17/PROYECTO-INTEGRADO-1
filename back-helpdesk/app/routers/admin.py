from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.core.deps import require_roles
from app.schemas.tickets import AnonimizarIn

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/tickets/anonimizar", dependencies=[Depends(require_roles("ADMIN"))])
def anonimizar(datos: AnonimizarIn, db: Session = Depends(get_db)):
    try:
        db.execute(text("CALL sp_anonimizar_tickets_antiguos(:m)"), {"m": datos.mesesAntiguedad})
        db.commit()
        return {"message": "Anonimización ejecutada"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))