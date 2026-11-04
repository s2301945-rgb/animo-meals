# Project setup

Start with [RUN-LOCALLY.md](RUN-LOCALLY.md). The current project is a visitor-facing AI food budget recommender with My Meal Boxes CRUD. There is no admin application or login setup.

- Backend: migrate through revision 0003; run `app.shop_catalog` to add selected shops without inventing meals.
- Frontend: install dependencies and set the public backend URL if needed.
- AI: reuse the private Groq configuration; see [AI-SETUP.md](AI-SETUP.md).
- Menus: import the supplied dataset using [docs/MENU-DATA.md](docs/MENU-DATA.md).
- Use descriptive branches, pull requests, and passing checks before deployment.

Only `.env.example` files belong in Git. Real database credentials, Groq keys, browser keys and backup data stay private. Historical Week 1 and Week 2 files describe earlier milestones.
