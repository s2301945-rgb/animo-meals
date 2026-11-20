# Scope revision · November 4, 2026

## Why the project changed

A solo admin cannot reliably ask every vendor about changing menus and stock. The revised AnimoMeals is an **AI Food Budget Recommender** for visitors, based on a small recorded catalog of regular meals. There is no administrator role. The developer imports menu data occasionally; visitors confirm price and actual availability at the shop.

The original five campus shops remain alongside Jollibee, McDonald's, Potato Corner, and a shop whose name is pending. The production snapshot contains 9 shops and 28 recorded menu items. Maria Rosa and Pritong Manok await menus. Existing records are preserved by migrations. The checked-in datasets mirror published records, including delivery-price and campus-price limitations.

## Requirement mapping

| Course requirement | Revised implementation |
| --- | --- |
| Real database CRUD | Visitors save, read, rename and delete My Meal Boxes through REST and UI |
| Non-trivial AI feature | Structured preference extraction followed by validated database matching and exact combination totals |
| Separate backend API | FastAPI owns provider requests, database access, validation and recommendation logic |
| Real frontend | React calls the API for shops, menus, suggestions and saved boxes |
| Related tables | stalls → menu_items; saved_plans → saved_plan_items |
| Secrets management | Backend-only database/provider settings; hashed browser ownership keys; ignored .env files |
| Error handling | Invalid budgets, provider failures, empty catalogs, changed prices, storage-disabled browsers and request limits |

## Deliberate limits

- No admin dashboard, Supabase login, vendor accounts or public catalog mutations.
- No live-stock promise. `is_listed` describes recorded-catalog inclusion.
- No unsupported nutrition, quality, allergy-safety or distance claims.
- Menu matching uses recorded names/descriptions, not inferred recipes.
- Saved boxes are tied to browser storage; there is no recovery or cross-device identity.
- The price snapshot in an old box is not a current-price guarantee.
- Rate guards are in-process and reset on restart; they are not distributed billing controls.

The existing former admin account, private hosting variables and Storage objects are not deleted by a code refactor. The new application does not use admin identity or upload routes. Historical milestone evidence remains in Git for traceability.
