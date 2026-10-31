"""Validated CRUD for the existing stalls -> menu_items relationship."""
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import auth_config, require_admin
from app.database import get_session
from app.models import MenuItem, Stall

router = APIRouter()
protected = APIRouter(dependencies=[Depends(require_admin)])
Db = Annotated[Session, Depends(get_session)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class StallInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: Name
    location: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class StallOut(StallInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class ItemInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    stall_id: Annotated[int, Field(gt=0, strict=True)]
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    description: Annotated[str | None, StringConstraints(strip_whitespace=True, max_length=2000)] = None
    price: Annotated[Decimal, Field(gt=0, le=10000, decimal_places=2, allow_inf_nan=False)]
    category: Literal['Main dish', 'Drink', 'Snack', 'Side']
    is_available: Annotated[bool, Field(strict=True)] = True


class ItemOut(ItemInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    updated_at: datetime


def find(session, model, record_id):
    record = session.get(model, record_id)
    if record is None:
        raise HTTPException(404, 'Record not found.')
    return record


def commit(session):
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, 'This change conflicts with an existing record.') from None


def unique_stall(session, name, current_id=None):
    query = select(Stall.id).where(func.lower(Stall.name) == name.lower())
    if current_id is not None:
        query = query.where(Stall.id != current_id)
    if session.scalar(query) is not None:
        raise HTTPException(409, 'A shop with this name already exists.')


@router.get('/api/admin/auth-config')
def public_auth_config(response: Response):
    url, key = auth_config()
    response.headers['Cache-Control'] = 'no-store'
    # Only the publishable/anon key belongs here. Never configure a service-role key.
    return {'url': url, 'publishable_key': key}


@router.get('/api/stalls', response_model=list[StallOut])
def list_stalls(session: Db):
    return session.scalars(select(Stall).order_by(Stall.name)).all()


@router.get('/api/stalls/{record_id}', response_model=StallOut)
def get_stall(record_id: int, session: Db):
    return find(session, Stall, record_id)


@router.get('/api/menu-items/{record_id}', response_model=ItemOut)
def get_item(record_id: int, session: Db):
    return find(session, MenuItem, record_id)


@protected.get('/api/admin/me')
def admin_identity():
    return {'role': 'admin'}


@protected.post('/api/stalls', response_model=StallOut, status_code=201)
def create_stall(data: StallInput, session: Db):
    unique_stall(session, data.name)
    stall = Stall(**data.model_dump())
    session.add(stall)
    commit(session)
    session.refresh(stall)
    return stall


@protected.put('/api/stalls/{record_id}', response_model=StallOut)
def update_stall(record_id: int, data: StallInput, session: Db):
    stall = find(session, Stall, record_id)
    unique_stall(session, data.name, record_id)
    for key, value in data.model_dump().items():
        setattr(stall, key, value)
    commit(session)
    session.refresh(stall)
    return stall


@protected.delete('/api/stalls/{record_id}', status_code=204)
def delete_stall(record_id: int, session: Db):
    stall = find(session, Stall, record_id)
    if session.scalar(select(MenuItem.id).where(MenuItem.stall_id == record_id).limit(1)):
        raise HTTPException(409, 'Move or delete this shop’s menu items before deleting the shop.')
    session.delete(stall)
    commit(session)
    return Response(status_code=204)


@protected.post('/api/menu-items', response_model=ItemOut, status_code=201)
def create_item(data: ItemInput, session: Db):
    find(session, Stall, data.stall_id)
    item = MenuItem(**data.model_dump())
    session.add(item)
    commit(session)
    session.refresh(item)
    return item


@protected.put('/api/menu-items/{record_id}', response_model=ItemOut)
def update_item(record_id: int, data: ItemInput, session: Db):
    item = find(session, MenuItem, record_id)
    find(session, Stall, data.stall_id)
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    commit(session)
    session.refresh(item)
    return item


@protected.delete('/api/menu-items/{record_id}', status_code=204)
def delete_item(record_id: int, session: Db):
    session.delete(find(session, MenuItem, record_id))
    commit(session)
    return Response(status_code=204)


router.include_router(protected)
