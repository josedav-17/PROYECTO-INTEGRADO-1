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

    def dashboard(self, rol: str | None = None, area: str | None = None):
        return self._fetch_all(
            """
            SELECT
                ticket_uuid,
                label,
                categoria,
                correo,
                estado_code,
                prioridad_nom,
                area_asignada,
                actualizado_en,
                sla_horas,
                horas_restantes,
                vencido
            FROM public.fn_dashboard_tickets_full_filtrado(:rol, :area)
            """,
            {
                "rol": (rol or "").strip().upper(),
                "area": (area or "").strip(),
            },
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


    def consultar_publico(self, label: str, email: str):
        row = self._fetch_one(
            """
            SELECT *
            FROM public.fn_consultar_ticket_publico(:label, :email)
            """,
            {
                "label": label,
                "email": email,
            },
        )

        if not row:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")

        return {
            "ticketUuid": str(row["ticket_uuid"]) if row.get("ticket_uuid") else None,
            "ticketLabel": row["ticket_label"],
            "ticketNum": row.get("ticket_num"),
            "solicitanteNombre": row["solicitante_nombre"],
            "solicitanteEmail": row["solicitante_email"],
            "solicitanteTel": row.get("solicitante_tel"),
            "tieneWhatsapp": bool(row.get("tiene_whatsapp", False)),
            "documento": row.get("documento"),
            "empresaDepartamento": row.get("empresa_departamento"),
            "tipoSolicitud": row.get("tipo_solicitud"),
            "categoria": row["categoria"],
            "subcategoria": row.get("subcategoria"),
            "asunto": row.get("asunto"),
            "descripcionProblema": row["descripcion_problema"],
            "respuestaCliente": row.get("respuesta_cliente"),
            "areaAsignada": row.get("area_asignada"),
            "prioridadNombre": row.get("prioridad_nombre"),
            "estadoNombre": row.get("estado_nombre"),
            "creadoEn": row["creado_en"].isoformat() if row.get("creado_en") else None,
            "actualizadoEn": row["actualizado_en"].isoformat() if row.get("actualizado_en") else None,
            "ultimaFechaHistorial": row["ultima_fecha_historial"].isoformat() if row.get("ultima_fecha_historial") else None,
            "ultimaAccion": row.get("ultima_accion"),
            "ultimoMotivo": row.get("ultimo_motivo"),
            "ultimoActorNombre": row.get("ultimo_actor_nombre"),
            "ultimoActorRol": row.get("ultimo_actor_rol"),
            "estadoAntes": row.get("estado_antes"),
            "estadoDespues": row.get("estado_despues"),
            "prioridadAntes": row.get("prioridad_antes"),
            "prioridadDespues": row.get("prioridad_despues"),
            "areaAntes": row.get("area_antes"),
            "areaDespues": row.get("area_despues"),
        }
    

    def archivar(
            self,
            ticket_id: str,
            motivo: str,
            actor_user_id: str | None = None,
            actor_nombre: str | None = None,
            actor_email: str | None = None,
            actor_rol: str | None = None,
        ):
            self._exec_sp(
                """
                CALL public.sp_archivar_ticket(
                    :id,
                    :motivo,
                    :actor_user_id,
                    :actor_nombre,
                    :actor_email,
                    :actor_rol
                )
                """,
                {
                    "id": ticket_id,
                    "motivo": motivo,
                    "actor_user_id": actor_user_id,
                    "actor_nombre": actor_nombre,
                    "actor_email": actor_email,
                    "actor_rol": actor_rol,
                },
            )

    def actualizar_ticket(
        self,
        ticket_id: str,
        estado: str,
        prioridad: str,
        area: str,
        respuesta: str,
        actor_user_id: str | None = None,
        actor_nombre: str | None = None,
        actor_email: str | None = None,
        actor_rol: str | None = None,
    ):
        self._exec_sp(
            """
            CALL public.sp_actualizar_ticket(
                :id,
                :estado,
                :prioridad,
                :area,
                :respuesta,
                :actor_user_id,
                :actor_nombre,
                :actor_email,
                :actor_rol
            )
            """,
            {
                "id": ticket_id,
                "estado": estado,
                "prioridad": prioridad,
                "area": area,
                "respuesta": respuesta,
                "actor_user_id": actor_user_id,
                "actor_nombre": actor_nombre,
                "actor_email": actor_email,
                "actor_rol": actor_rol,
            },
        )


    def dashboard_metricas(self, rol: str | None = None, area: str | None = None):
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
                actualizado_en,
                fecha_limite_sla,
                horas_restantes_sla,
                sla_vencido
            FROM public.fn_dashboard_metricas_filtrado(:rol, :area)
            """,
            {
                "rol": (rol or "").strip().upper(),
                "area": (area or "").strip(),
            },
        )