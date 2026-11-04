# Administrator feature retired

As of the November 4, 2026 scope revision, AnimoMeals has no administrator dashboard, login, shop/menu mutation endpoints, or visitor photo uploads. Old `#admin` bookmarks open the visitor website.

Visitors use **My Meal Boxes** for create/read/update/delete operations. The developer imports the occasional recorded menu dataset using [docs/MENU-DATA.md](docs/MENU-DATA.md). No Supabase Auth account or publishable-key setup is required. Existing external Auth accounts/storage objects are not automatically deleted by this code change.

See [README.md](README.md) and [docs/REVISED-SCOPE.md](docs/REVISED-SCOPE.md) for the current project.
