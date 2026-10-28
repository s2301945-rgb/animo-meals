import logging
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_session
from app.models import MenuItem, Stall

app = FastAPI(title='AnimoMeals API', version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=['GET'],
    allow_headers=['Accept', 'Content-Type'],
)
Db = Annotated[Session, Depends(get_session)]


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc: SQLAlchemyError):
    # Log the exception type only: driver errors can contain connection credentials.
    logging.getLogger(__name__).error('Database operation failed: %s', type(exc).__name__)
    return JSONResponse(status_code=503, content={'detail': 'Menu service is temporarily unavailable. Please try again.'})


class MenuItemOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    category: str
    is_available: bool
    updated_at: datetime
    stall_name: str
    location: str


@app.get('/api/health')
def health(session: Db):
    session.execute(text('SELECT 1'))
    return {'status': 'ok', 'database': 'connected'}


@app.get('/api/menu-items', response_model=list[MenuItemOut])
def menu_items(
    session: Db,
    budget: Annotated[Decimal | None, Query(gt=0, le=10000, decimal_places=2)] = None,
):
    query = select(MenuItem, Stall).join(Stall).order_by(Stall.name, MenuItem.name)
    if budget is not None:
        query = query.where(MenuItem.price <= budget)
    return [MenuItemOut(
        id=item.id, name=item.name, description=item.description, price=item.price,
        category=item.category, is_available=item.is_available, updated_at=item.updated_at,
        stall_name=stall.name, location=stall.location,
    ) for item, stall in session.execute(query)]
