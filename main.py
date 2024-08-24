from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# Importamos el scheduler para ejecutar tareas en segundo plano
from apscheduler.schedulers.background import BackgroundScheduler
from db import SessionLocal, engine, Base
from schemas.ticket import TicketSchema
from models.ticket import Ticket
from typing import List

from services.email_service import check_emails

from routes.home_route import router as home_router

# TODO: HACER SISTEMA DE USUARIOS CON ROLES (ROLES: ESPECIALISTAS, LIDER, EMPLEADOS)

# TICKET: ID, TITULO, N° MAQUINA, TIPO (SOFTWARE / HARDWARE), ESTADO, CUIT

# Crear la instancia de la aplicación FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# TODO: responder con un email


@app.post("/tickets/")
async def create_ticket(ticket: TicketSchema):
    db = SessionLocal()  # Crear una nueva sesión de la base de datos
    db_ticket = Ticket(
        subject=ticket.subject.capitalize(),
        description=ticket.description.capitalize(),
        sender_email=ticket.sender_email,
        sender_name=ticket.sender_name,
        cuit=ticket.cuit,
        num_machine=ticket.num_machine,
        type_problem=ticket.type_problem,
        area=ticket.area,
        created_at=ticket.created_at
    )  # Crear un nuevo objeto Ticket con los datos proporcionados
    db.add(db_ticket)  # Añadir el ticket a la sesión
    db.commit()  # Guardar los cambios en la base de datos
    # Refrescar el objeto para obtener los datos actualizados (como el ID)
    db.refresh(db_ticket)
    db.close()  # Cerrar la sesión
    return db_ticket  # Devolver el ticket creado como respuesta


@app.get("/tickets", response_model=List[TicketSchema])
async def get_tickets(offset: int = 0, limit: int = 100):
    db = SessionLocal()
    return db.query(Ticket).offset(offset).limit(limit).all()


# Inicializar el scheduler de tareas en segundo plano
scheduler = BackgroundScheduler()
# Agregar una tarea al scheduler para revisar correos electrónicos cada 5 minutos
scheduler.add_job(check_emails, "interval", minutes=1)


async def start_scheduler():
    print("[+] Inicializando tareas en segundo plano")
    scheduler.start()


async def shutdown_scheduler():
    print("[-] Finalizando tareas en segundo plano")
    scheduler.shutdown()


app.add_event_handler("startup", start_scheduler)
app.add_event_handler("shutdown", shutdown_scheduler)

app.include_router(router=home_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
