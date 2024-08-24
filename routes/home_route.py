from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from db import SessionLocal
from models.ticket import Ticket

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def home(request: Request, offset: int = 0, limit: int = 100):
    db = SessionLocal()
    tickets: list[Ticket] = db.query(Ticket).offset(offset).limit(limit).all()
    return templates.TemplateResponse("index.html", {"request": request, "tickets": tickets})
