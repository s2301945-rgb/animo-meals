# REST API · revised visitor scope

All prices are decimal strings in responses. Budget inputs must be positive, no more than PHP 10,000 and have at most two decimal places. Request bodies reject unknown fields.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | /api/health | Database connectivity |
| GET | /api/environment | Environment and deployed commit |
| GET | /api/stalls | Recorded shop names, locations and optional image URLs |
| GET | /api/menu-items?budget=100 | Recorded items, joined shop details, is_listed and recorded timestamp |
| POST | /api/recommendations | Interpret preferences and calculate up to six affordable meal combinations |
| POST | /api/plans | Save an owned meal box |
| GET | /api/plans | List this browser's boxes |
| GET | /api/plans/{id} | Read one owned box |
| PUT | /api/plans/{id} | Rename one owned box |
| DELETE | /api/plans/{id} | Delete one owned box and its snapshot items |

Recommendation body:

```json
{"budget": "100.00", "preferences": "Chicken with rice and a drink, from one shop"}
```

Blank preferences perform recorded-price comparison without the AI. Empty catalogs return `status: no_matches` with no fabricated results and no provider call. AI output is structurally validated; the backend owns all menu selection and money arithmetic. The response includes the extracted preferences for review and a price/availability reminder.

Saved-box creation:

```json
{"title": "Monday lunch", "budget": "100.00", "item_ids": [1, 2]}
```

IDs must come from the actual catalog; illustrative IDs above are not seed data. At save time the API rechecks current catalog inclusion and prices. It stores a snapshot, not a later-changing reference. Rename body: `{"title":"Tipid combo"}`. Update changes the title; save a fresh suggestion to choose a different set of meals.

All `/api/plans` requests require `Authorization: Bearer <64 lowercase hexadecimal characters>`, generated from 32 cryptographically random bytes by the browser. Only a hash is stored. Access is scoped by this hash on every operation. Another key receives 404 for a guessed box ID. Plans are private to possession of the key, not a named human account. Responses are `Cache-Control: no-store`.

Status codes: 401 missing/invalid browser key; 404 missing/not-owned plan; 409 changed catalog prices/items or 20-box limit; 422 malformed request or conflicting budgets; 429 request/provider quota; 503 database or AI service unavailable. Old `/api/admin/*`, photo uploads and catalog writes are not registered.

Provider requests: six per client and thirty globally per minute per process. Plan creation: twenty per client and 120 globally per minute per process. Client identity uses the connection's remote address; shared networks may share limits. Changing browser keys does not bypass the client/global request guard. No raw IPs or preference text are persisted by these guards.
