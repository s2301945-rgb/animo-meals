"""Database CRUD for a visitor's plans using a browser-held random bearer secret."""
import hashlib
import re
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
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


RecordId = Annotated[int, Field(gt=0, strict=True)]
Quantity = Annotated[int, Field(ge=1, le=20, strict=True)]


class PlanItemInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    saved_item_id: RecordId | None = None
    menu_item_id: RecordId | None = None
    quantity: Quantity = 1

    @model_validator(mode='after')
    def one_reference(self):
        if (self.saved_item_id is None) == (self.menu_item_id is None):
            raise ValueError('Choose either a saved item or a catalog item.')
        return self


class PlanInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: Title
    budget: Budget
    item_ids: list[RecordId] | None = Field(default=None, min_length=1, max_length=20)
    items: list[PlanItemInput] | None = Field(default=None, min_length=1, max_length=20)

    @model_validator(mode='after')
    def one_item_list(self):
        if (self.item_ids is None) == (self.items is None):
            raise ValueError('Supply one meal item list.')
        return self


class PlanUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: Title | None = None
    budget: Budget | None = None
    items: list[PlanItemInput] | None = Field(default=None, min_length=1, max_length=20)
    expected_version: RecordId | None = None

    @model_validator(mode='after')
    def valid_update(self):
        fields = self.model_fields_set - {'expected_version'}
        if not fields or any(getattr(self, name) is None for name in fields):
            raise ValueError('Provide a name, budget, or nonempty meal list.')
        return self


def resolve_items(session, entries, plan=None):
    """Resolve client references using trusted catalog prices or owned snapshots."""
    retained = {item.id: item for item in plan.items} if plan else {}
    menu_ids = [entry.menu_item_id for entry in entries if entry.menu_item_id is not None]
    catalog = {item.id: (item, stall) for item, stall in session.execute(
        select(MenuItem, Stall).join(Stall).where(
            MenuItem.id.in_(menu_ids), MenuItem.is_available.is_(True), MenuItem.price > 0))}
    resolved = []
    references = set()
    for entry in entries:
        if entry.saved_item_id is not None:
            item = retained.get(entry.saved_item_id)
            if item is None:
                raise HTTPException(404, 'A saved meal item was not found in this box.')
            reference = ('menu', item.menu_item_id) if item.menu_item_id else ('saved', item.id)
        else:
            row = catalog.get(entry.menu_item_id)
            if row is None:
                raise HTTPException(409, 'A selected meal is no longer listed. Reload the menu and choose another meal.')
            menu, stall = row
            reference = ('menu', menu.id)
            item = SavedPlanItem(menu_item_id=menu.id, name=menu.name, shop_name=stall.name,
                                 location=stall.location, price=menu.price)
        if reference in references:
            raise HTTPException(422, 'Choose each meal once and use its quantity for extra portions.')
        references.add(reference)
        resolved.append((item, entry.quantity))
    return resolved


def validate_total(items, budget):
    total = sum((item.price * quantity for item, quantity in items), Decimal('0.00'))
    if total > budget:
        raise HTTPException(409, f'Meals exceed your budget by PHP {total - budget:.2f}. Increase the budget or remove meals.')


def output(plan):
    total = sum((item.price * item.quantity for item in plan.items), Decimal('0.00'))
    return {'id': plan.id, 'title': plan.title, 'budget': str(plan.budget),
            'total': str(total), 'remaining': str(plan.budget - total),
            'created_at': plan.created_at.isoformat(), 'version': plan.version,
            'items': [{'id': item.id, 'menu_item_id': item.menu_item_id,
                       'quantity': item.quantity, 'line_total': str(item.price * item.quantity),
                       'name': item.name, 'shop_name': item.shop_name,
                       'location': item.location, 'price': str(item.price)} for item in plan.items]}


def find(session, record_id, owner_hash, lock=False):
    query = select(SavedPlan).where(SavedPlan.id == record_id, SavedPlan.owner_hash == owner_hash)
    if lock:
        query = query.with_for_update()
    plan = session.scalar(query)
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
    entries = data.items if data.items is not None else [
        PlanItemInput(menu_item_id=item_id) for item_id in data.item_ids]
    resolved = resolve_items(session, entries)
    validate_total(resolved, data.budget)
    for item, quantity in resolved:
        item.quantity = quantity
    plan = SavedPlan(owner_hash=owner_hash, title=data.title, budget=data.budget,
                     items=[item for item, _ in resolved])
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return output(plan)


@router.put('/{record_id}')
def update_plan(record_id: int, data: PlanUpdate, request: Request, session: Db, owner_hash: Owner):
    check_limit(request, 'plan_edit', 30, 180)
    plan = find(session, record_id, owner_hash, lock=True)
    if data.expected_version is not None and data.expected_version != plan.version:
        raise HTTPException(409, 'This meal box changed in another tab. Reload the saved box before editing again.')
    budget = data.budget if data.budget is not None else plan.budget
    resolved = resolve_items(session, data.items, plan) if data.items is not None else [
        (item, item.quantity) for item in plan.items]
    validate_total(resolved, budget)
    if data.title is not None:
        plan.title = data.title
    plan.budget = budget
    for item, quantity in resolved:
        item.quantity = quantity
    plan.items = [item for item, _ in resolved]
    plan.version += 1
    session.commit()
    session.refresh(plan)
    return output(plan)


@router.delete('/{record_id}', status_code=204)
def delete_plan(record_id: int, session: Db, owner_hash: Owner):
    session.delete(find(session, record_id, owner_hash, lock=True))
    session.commit()
    return Response(status_code=204, headers={'Cache-Control': 'no-store'})
