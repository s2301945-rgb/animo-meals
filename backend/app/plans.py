"""Database CRUD for a visitor's plans using a browser-held random bearer secret."""
import hashlib
import re
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_session
from app.limits import check_limit
from app.models import MenuItem, SavedPlan, SavedPlanItem, Stall
from app.recommendations import Budget

router = APIRouter(prefix='/api/plans', tags=['My meal plans'])
Db = Annotated[Session, Depends(get_session)]
bearer = HTTPBearer(auto_error=False)
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


def owner(response: Response,
          credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    response.headers['Cache-Control'] = 'no-store'
    if not credentials or not re.fullmatch(r'[a-f0-9]{64}', credentials.credentials):
        raise HTTPException(401, 'Open My meal plans in this browser to access your saved plans.')
    return hashlib.sha256(credentials.credentials.encode()).hexdigest()


Owner = Annotated[str, Depends(owner)]


class PlanInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: Title
    budget: Budget
    item_ids: list[Annotated[int, Field(gt=0, strict=True)]] = Field(min_length=1, max_length=3)


class PlanUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: Title


def output(plan):
    total = sum((item.price for item in plan.items), Decimal('0.00'))
    return {'id': plan.id, 'title': plan.title, 'budget': str(plan.budget),
            'total': str(total), 'remaining': str(plan.budget - total),
            'created_at': plan.created_at.isoformat(),
            'items': [{'name': item.name, 'shop_name': item.shop_name,
                       'location': item.location, 'price': str(item.price)} for item in plan.items]}


def find(session, record_id, owner_hash):
    plan = session.scalar(select(SavedPlan).where(SavedPlan.id == record_id,
                                                SavedPlan.owner_hash == owner_hash))
    if plan is None:
        raise HTTPException(404, 'Meal plan not found in this browser.')
    return plan


@router.get('')
def list_plans(session: Db, owner_hash: Owner):
    return [output(plan) for plan in session.scalars(select(SavedPlan).where(
        SavedPlan.owner_hash == owner_hash).order_by(SavedPlan.id.desc()))]


@router.get('/{record_id}')
def get_plan(record_id: int, session: Db, owner_hash: Owner):
    return output(find(session, record_id, owner_hash))


@router.post('', status_code=201)
def create_plan(data: PlanInput, request: Request, session: Db, owner_hash: Owner):
    check_limit(request, 'plan_write', 20, 120)
    count = session.scalar(select(func.count()).select_from(SavedPlan).where(SavedPlan.owner_hash == owner_hash))
    if count >= 20:
        raise HTTPException(409, 'You can save up to 20 plans. Delete an older plan first.')
    if len(set(data.item_ids)) != len(data.item_ids):
        raise HTTPException(422, 'Choose each meal item once.')
    rows = session.execute(select(MenuItem, Stall).join(Stall).where(
        MenuItem.id.in_(data.item_ids), MenuItem.is_available.is_(True), MenuItem.price > 0)).all()
    if len(rows) != len(data.item_ids):
        raise HTTPException(409, 'A selected item is no longer listed. Request fresh suggestions.')
    if sum((item.price for item, _ in rows), Decimal('0.00')) > data.budget:
        raise HTTPException(409, 'Recorded prices exceed this budget. Request fresh suggestions.')
    plan = SavedPlan(owner_hash=owner_hash, title=data.title, budget=data.budget,
        items=[SavedPlanItem(name=item.name, shop_name=stall.name, location=stall.location,
                             price=item.price) for item, stall in rows])
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return output(plan)


@router.put('/{record_id}')
def rename_plan(record_id: int, data: PlanUpdate, session: Db, owner_hash: Owner):
    plan = find(session, record_id, owner_hash)
    plan.title = data.title
    session.commit()
    return output(plan)


@router.delete('/{record_id}', status_code=204)
def delete_plan(record_id: int, session: Db, owner_hash: Owner):
    session.delete(find(session, record_id, owner_hash))
    session.commit()
    return Response(status_code=204, headers={'Cache-Control': 'no-store'})
