"""AI interprets text; deterministic code selects recorded meals and adds prices."""
from decimal import Decimal
from heapq import nsmallest
from itertools import product
import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import AIError, MealPreferences, extract_preferences
from app.database import get_session
from app.limits import check_limit
from app.models import MenuItem, Stall

router = APIRouter()
Budget = Annotated[Decimal, Field(gt=0, le=10000, decimal_places=2, allow_inf_nan=False)]
NOTICE = ('Suggestions use recorded menu prices, not live stock. Confirm prices and availability '
          'at the shop. Ingredient details may be incomplete; these are not allergy-safe recommendations.')


class RecommendationInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    budget: Budget
    preferences: Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)] = ''


def normalized(text):
    text = re.sub(r'\bkan[\s-]+on\b', 'rice', text.lower())
    words = re.findall(r'[a-z0-9]+', text)
    aliases = {'manok': 'chicken', 'baboy': 'pork', 'kanin': 'rice', 'isda': 'fish',
               'kanon': 'rice', 'itlog': 'egg', 'tubig': 'water', 'maanghang': 'spicy', 'halang': 'spicy',
               'hamburger': 'burger', 'hamborger': 'burger', 'yumburger': 'yumburger burger'}
    return ' '.join(aliases.get(word, word) for word in words)


def candidate_matches(combo, preferences):
    text = normalized(' '.join(f'{item.name} {item.description or ""}' for item, _ in combo))
    if preferences.preferred_food:
        ignored = {'with', 'and', 'a', 'an', 'the', 'meal', 'food', 'dish', 'some', 'or',
                   'at', 'kag', 'ug', 'nga', 'may', 'naay'}
        terms = set(normalized(preferences.preferred_food).split()) - ignored
        if terms and not terms.issubset(set(text.split())):
            return False
    for exclusion in preferences.exclusions:
        term = normalized(exclusion)
        if term and f' {term} ' in f' {text} ':
            return False
    if preferences.avoid_spicy:
        # Missing information is not evidence that a meal is non-spicy.
        for item, _ in combo:
            if item.category not in ('Main dish', 'Snack'):
                continue
            description = normalized(f'{item.name} {item.description or ""}')
            mild = r'\b(non spicy|not spicy|indi spicy|dili spicy|mild|no chili)\b'
            if not re.search(mild, description):
                return False
            if re.search(r'\b(hot|chili|spicy)\b', re.sub(mild, '', description)):
                return False
    return True


def build_suggestions(rows, budget, preferences):
    bases = [row for row in rows if row[0].category in ('Main dish', 'Snack')]
    drinks = [row for row in rows if row[0].category == 'Drink']
    sides = [row for row in rows if row[0].category == 'Side']
    # One base, optionally one side and one drink. No duplicate items or invented portions.
    drink_options = drinks if preferences.include_drink else [None]
    def candidates():
        for base in bases:
            # Restrict each product before generating combinations; do not build a giant result list.
            same_shop = preferences.prefer_same_stall is not False
            allowed_sides = [None] if base[0].category == 'Snack' else [None, *(
                side for side in sides if not same_shop or side[1].id == base[1].id)]
            allowed_drinks = [drink for drink in drink_options if drink is None
                              or not same_shop or drink[1].id == base[1].id]
            for side, drink in product(allowed_sides, allowed_drinks):
                combo = [row for row in (base, side, drink) if row is not None]
                total = sum((item.price for item, _ in combo), Decimal('0.00'))
                if total > budget or not candidate_matches(combo, preferences):
                    continue
                yield {
                    'items': [{'id': item.id, 'name': item.name, 'shop_name': stall.name,
                               'location': stall.location, 'price': str(item.price),
                               'image_url': item.image_url, 'recorded_at': item.updated_at.isoformat()}
                              for item, stall in combo],
                    'total': str(total), 'remaining': str(budget - total),
                    'reason': 'Matches your recorded-menu preferences and stays within your budget.',
                }
    # Lowest price first; stable tie-breaks make results reproducible and testable.
    return nsmallest(6, candidates(), key=lambda result: (
        Decimal(result['total']), tuple(i['id'] for i in result['items'])))


@router.post('/api/recommendations')
def recommend(data: RecommendationInput, request: Request,
              session: Annotated[Session, Depends(get_session)]):
    check_limit(request, 'recommend', 6, 30)
    rows = session.execute(select(MenuItem, Stall).join(Stall).where(
        MenuItem.is_available.is_(True), MenuItem.price > 0,
        MenuItem.price <= data.budget).order_by(MenuItem.id).limit(201)).all()
    if not rows:
        return {'status': 'no_matches', 'suggestions': [], 'preferences': None,
                'message': 'No recorded meals fit this budget yet. Menu data is still being collected.',
                'notice': NOTICE}
    if len(rows) > 200:
        raise HTTPException(422, 'Too many catalog items for one comparison. Try a smaller budget.')
    preferences = MealPreferences(budget_php=float(data.budget), preferred_food=None,
        include_drink=None, avoid_spicy=None, prefer_same_stall=True, exclusions=[])
    if data.preferences:
        try:
            preferences = extract_preferences(data.preferences)
        except AIError as error:
            message = {
                'timeout': 'The AI took too long to respond.',
                'rate_limit': 'The AI service is busy.',
                'invalid_output': 'The AI returned a response we could not use.',
            }.get(error.code, 'The AI service is temporarily unavailable.')
            rate_limited = error.code == 'rate_limit'
            raise HTTPException(
                429 if rate_limited else 503,
                f'{message} Try again later, or clear the preference box to compare recorded prices only.',
                headers={'Retry-After': '60'} if rate_limited else None,
            ) from None
        if preferences.budget_php is not None and Decimal(str(preferences.budget_php)) != data.budget:
            raise HTTPException(422, 'The budget in your description differs from the budget field. Please make them match.')
    preferences.budget_php = float(data.budget)
    suggestions = build_suggestions(rows, data.budget, preferences)
    return {'status': 'ok' if suggestions else 'no_matches', 'suggestions': suggestions,
            'preferences': preferences.model_dump(),
            'message': 'A little planning, more room in your budget.' if suggestions else
                       'No recorded meals match all these preferences. Try another budget or preference. '
                       'Unknown spice details are excluded when you request non-spicy food.',
            'notice': NOTICE}
