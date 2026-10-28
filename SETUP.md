# Project setup

Initial setup was merged through PR #1. GitHub Issues #2–#12 track the project, with #2–#8 assigned to the Week 1 milestone.

Follow [RUN-LOCALLY.md](RUN-LOCALLY.md) to run the React frontend and FastAPI backend, apply the local database migration, and seed fictional menu records.

Only `.env.example` files belong in Git. Real `.env` files are ignored. Database credentials and AI keys belong exclusively in backend configuration.

Use feature branches and pull requests for changes. Local SQLite allows development without cloud accounts. Supabase PostgreSQL verification, a real Gemini request, and pipeline-triggered live deployment remain Week 1 tasks.
