from database import SessionLocal, engine
import models

# Crear tablas
models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    # Verificamos si ya existe para no duplicar
    if not db.query(models.TicketModel).filter_by(id="TCK-ABC123").first():
        ticket = models.TicketModel(
            id="TCK-ABC123",
            nombre="Andrés Felipe Restrepo",
            documento="10203040",
            correo="a.restrepo@universidad.edu.co",
            telefono="+57 300 123 4567",
            tiene_whatsapp=True,
            categoria="Plataforma Académica",
            descripcion="Falla técnica reportada vía web.",
            estado="PENDIENTE",
            prioridad="ALTA",
            area="Sistemas"
        )
        db.add(ticket)
        db.commit()
        print("✅ Base de datos inicializada con ticket TCK-ABC123")
    db.close()

if __name__ == "__main__":
    seed_data()