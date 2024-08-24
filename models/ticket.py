from db import Base
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from datetime import datetime
import pytz

# Zona horaria de Buenos Aires (GMT-3)
buenos_aires_timezone = pytz.timezone('America/Argentina/Buenos_Aires')


class Ticket(Base):
    __tablename__ = "tickets"  # Nombre de la tabla en la base de datos
    # ID del ticket, clave primaria
    id = Column(Integer, primary_key=True, index=True)
    sender_name = Column(String(255))
    sender_email = Column(String(255))  # Email del remitente
    cuit = Column(Integer, nullable=False)

    subject = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    type_problem = Column(String(255), index=True, nullable=False)
    num_machine = Column(Integer, nullable=False)
    area = Column(String(255), nullable=True)

    # Estado del ticket (por defecto "abierto")
    status = Column(String(255), default="open")
    # Fecha y hora de creación del ticket
    created_at = Column(DateTime, default=datetime.utcnow().replace(
        tzinfo=pytz.utc).astimezone(buenos_aires_timezone))
