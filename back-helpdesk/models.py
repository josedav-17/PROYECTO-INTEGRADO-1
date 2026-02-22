from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from database import Base
import datetime

class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(String(50), primary_key=True)
    nombre_completo = Column(String(150))
    documento_id = Column(String(20))
    correo_electronico = Column(String(100))
    telefono_contacto = Column(String(30))
    tiene_whatsapp = Column(Boolean, default=False)
    empresa_departamento = Column(String(100))
    
    categoria = Column(String(100))
    subcategoria = Column(String(100))
    asunto = Column(String(200))
    descripcion_problema = Column(Text)
    prioridad = Column(String(20))
    estado = Column(String(30))
    
    sistema_operativo = Column(String(50))
    navegador_version = Column(String(100))
    ip_origen = Column(String(45))
    es_vip = Column(Boolean, default=False)
    
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=datetime.datetime.utcnow)
    fecha_vencimiento = Column(DateTime(timezone=True))
    fecha_resolucion = Column(DateTime(timezone=True))
    
    area_asignada = Column(String(100))
    agente_asignado_id = Column(String(50))
    comentarios_tecnicos = Column(Text)
    solucion_final = Column(Text)
    satisfaccion_cliente = Column(Integer)
    adjunto_url = Column(Text)