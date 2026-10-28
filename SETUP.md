# Add these files to your existing AnimoMeals repository

These are configuration templates and a backlog, not a working application.

1. Copy `.gitignore` into your repository root, beside your existing README.md.
2. Copy the `frontend` and `backend` folders into the repository. If they already exist, merge the folders without replacing existing application files.
3. Keep `.env.example` files in Git. When configuring local development, copy each example to `.env` in the same folder. Real `.env` files must stay out of Git.
4. Use `BACKLOG.md` to create GitHub Issues: repository → Issues → New issue. Each numbered section is one issue. Copy its title, description, and acceptance criteria.
5. Optionally create a milestone named `Week 1` and assign issues 1–7 to it.
6. Make these changes on `chore/project-setup`, open a pull request to `main`, and review the file list before merging.

The frontend uses public configuration only. AI credentials and database passwords belong in the backend environment. An environment example does not load variables automatically; application configuration will be added when the backend is implemented.

If a secret was already committed, adding `.gitignore` does not remove it from Git history. Revoke the exposed credential and remove the tracked secret file.

Next implementation step: scaffold React and FastAPI, then create an Alembic migration for `stalls` and `menu_items`.
