# REST API · revised visitor scope

All prices are decimal strings in responses. Budget inputs must be positive, no more than PHP 10,000 and have at most two decimal places. Preference descriptions allow up to 1,000 characters. JSON write requests have a 16 KiB body limit and reject unknown fields.

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
| PUT | /api/plans/{id} | Edit one owned box (name, budget, meals, quantities) |
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

IDs must come from the actual catalog; illustrative IDs above are not seed data. At save time the API rechecks current catalog inclusion and prices. It stores a snapshot, not a later-changing reference. Update only the fields you want to change. For example:

```json
{"title":"Shared lunch","budget":"200.00","expected_version":1,"items":[{"saved_item_id":10,"quantity":2},{"menu_item_id":3,"quantity":1}]}
```

Use an owned `saved_item_id` to retain a snapshot, or a listed `menu_item_id` to add a meal at its current recorded price. Each entry must contain exactly one reference. Supplying `items` replaces the box contents; omitted items are removed. A box holds 1–20 distinct meals, with integer quantities of 1–20 each. Duplicate references are rejected. Existing snapshots remain usable after catalog changes. Responses include `version`, item `id`, `menu_item_id` (nullable for historical snapshots), `quantity`, unit `price` and `line_total`. Totals use decimal arithmetic. Over-budget edits return 409 without changing the saved box.

Send the returned `version` as `expected_version` to detect stale edits; a conflict returns 409 and requires reloading. Legacy title-only updates remain supported. Creation can use either the legacy `item_ids` array (one portion each) or `items` with catalog references and quantities.

All `/api/plans` requests require `Authorization: Bearer <64 lowercase hexadecimal characters>`, generated from 32 cryptographically random bytes by the browser. Only a hash is stored. Access is scoped by this hash on every operation. Another key receives 404 for a guessed box ID. Plans are private to possession of the key, not a named human account. Responses are `Cache-Control: no-store`.

Errors include a readable `detail` string. The API returns 401 for an invalid browser key, 404 for a missing or inaccessible plan, 409 for catalog changes, over-budget boxes, stale edits or the 20-box limit, 413 for an oversized request, 422 for invalid input, 429 for rate limits, and 503 for database or AI failures. Validation messages omit submitted values. An AI failure also explains how to switch to price-only comparison.

Provider requests: six per client and thirty globally per minute per process. Plan creation: twenty per client and 120 globally per minute per process. Plan edits: thirty per client and 180 globally per minute per process. Client identity uses the connection's remote address; shared networks may share limits. Changing browser keys does not bypass the client/global request guard. No raw IPs or preference text are persisted by these guards.
