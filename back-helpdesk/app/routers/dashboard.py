from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/tickets", tags=["dashboard"])

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rol = user.get("rol")
    area = user.get("area")

    result = db.execute(
        text("SELECT * FROM fn_dashboard_tickets_filtrado(:rol, :area)"),
        {"rol": rol, "area": area},
    )
    return [dict(row._mapping) for row in result]