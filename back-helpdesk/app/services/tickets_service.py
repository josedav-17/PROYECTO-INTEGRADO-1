from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session


class TicketsService:
    def __init__(self, db: Session):
        self.db = db

    def _raise_db_error(self, e: Exception):
        self.db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    def _fetch_one(self, sql: str, params: dict):
        try:
            result = self.db.execute(text(sql), params)
            row = result.mappings().first()
            self.db.commit()
            return dict(row) if row else None
        except Exception as e:
            self._raise_db_error(e)

    def _fetch_all(self, sql: str, params: dict | None = None):
        try:
            result = self.db.execute(text(sql), params or {})
            rows = result.mappings().all()
            return [dict(r) for r in rows]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def _exec_sp(self, sql: str, params: dict):
        try:
            self.db.execute(text(sql), params)
            self.db.commit()
        except Exception as e:
            self._raise_db_error(e)

    def crear(self, data: dict, ip_cliente: str | None = None):
        row = self._fetch_one(
            """
            SELECT
                ticket_uuid,
                ticket_label,
                estado,
                tipo,
                prioridad,
                sla_horas,
                fecha_creacion,
                fecha_limite_sla
            FROM public.fn_crear_ticket(
                :nombre,
                :doc,
                :email,
                :tel,
                :ws,
                :empresa,
                :tipo,
                :cat,
                :subcat,
                :asunto,
                :descripcion,
                :prioridad,
                :area,
                CAST(:ip AS INET)
            )
            """,
            {
                "nombre": data["nombre"],
                "doc": data.get("documento"),
                "email": data["email"],
                "tel": data.get("telefono"),
                "ws": data.get("tieneWhatsapp", False),
                "empresa": data.get("empresaDepartamento"),
                "tipo": data["tipo"],
                "cat": data["categoria"],
                "subcat": data.get("subcategoria"),
                "asunto": data.get("asunto"),
                "descripcion": data["descripcion"],
                "prioridad": data["prioridad"],
                "area": data.get("areaAsignada", "MESA"),
                "ip": ip_cliente,
            },
        )

        if not row:
            raise HTTPException(status_code=400, detail="No se pudo crear el ticket")

        fecha_creacion = row["fecha_creacion"].isoformat() if row.get("fecha_creacion") else None
        fecha_limite_sla = row["fecha_limite_sla"].isoformat() if row.get("fecha_limite_sla") else None

        return {
            "ticketUuid": str(row["ticket_uuid"]),
            "ticketLabel": row["ticket_label"],
            "estado": row["estado"],
            "tipo": row["tipo"],
            "prioridad": row["prioridad"],
            "slaHoras": int(row["sla_horas"]),
            "fechaCreacion": fecha_creacion,
            "fechaLimiteSla": fecha_limite_sla,
            "mensaje": "Ticket creado correctamente",
        }

    def dashboard(self):
        return self._fetch_all(
            """
            SELECT
                uuid,
                ticket_label,
                solicitante_nombre,
                solicitante_email,
                tipo_solicitud,
                categoria,
                subcategoria,
                asunto,
                area_asignada,
                prioridad,
                sla_horas,
                estado,
                creado_en,
                fecha_limite_sla,
                horas_restantes_sla,
                sla_vencido
            FROM public.fn_obtener_dashboard_tickets()
            """
        )

    def get_bundle(self, ticket_id: str):
        row = self._fetch_one(
            """
            SELECT public.fn_ticket_detalle_bundle(:id) AS data
            """,
            {"id": ticket_id},
        )
        return row["data"] if row else None

    def asignar(self, ticket_id: str, agente_id: str, motivo: str):
        self._exec_sp(
            "CALL public.sp_asignar_ticket(:id, :agente, :motivo)",
            {"id": ticket_id, "agente": agente_id, "motivo": motivo},
        )

    def transferir(self, ticket_id: str, nueva_area: str, agente_id: str, motivo: str):
        self._exec_sp(
            "CALL public.sp_transferir_ticket(:id, :area, :agente, :motivo)",
            {
                "id": ticket_id,
                "area": nueva_area,
                "agente": agente_id,
                "motivo": motivo,
            },
        )

    def reclasificar(self, ticket_id: str, nueva_prio: str, nueva_cat: str, motivo: str):
        self._exec_sp(
            "CALL public.sp_reclasificar_ticket(:id, :prio, :cat, :motivo)",
            {
                "id": ticket_id,
                "prio": nueva_prio,
                "cat": nueva_cat,
                "motivo": motivo,
            },
        )

    def pausar(self, ticket_id: str, motivo: str):
        self._exec_sp(
            "CALL public.sp_pausar_ticket(:id, :motivo)",
            {"id": ticket_id, "motivo": motivo},
        )

    def reabrir(self, ticket_id: str, motivo: str):
        self._exec_sp(
            "CALL public.sp_reabrir_ticket(:id, :motivo)",
            {"id": ticket_id, "motivo": motivo},
        )

    def cancelar(self, ticket_id: str, motivo: str, por: str):
        self._exec_sp(
            "CALL public.sp_cancelar_ticket(:id, :motivo, :por)",
            {"id": ticket_id, "motivo": motivo, "por": por},
        )