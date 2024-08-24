from pydantic import BaseModel
from datetime import datetime


class TicketSchema(BaseModel):
    id: int = 0
    cuit: int
    sender_email: str  # Email del remitente
    sender_name: str
    subject: str  # Asunto del ticket
    type_problem: str
    num_machine: int
    area: str
    description: str  # Descripción del ticket
    created_at: datetime  # Fecha y hora a la que se recibio el ticket
