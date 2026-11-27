# Technology and external-work disclosure

## Implemented components

| Part | Actual implementation and environment |
| --- | --- |
| Frontend | JavaScript ES modules, HTML and custom CSS; React and React DOM 19.3.1, Vite 7.3.7, ESLint 9.39.5. Vercel Hobby production hosting. Node 24 is configured in CI; the hosted Node patch was not independently read. No UI component framework. |
| Backend | Python 3.13.15 configured for Render Free; FastAPI 0.162.0, Uvicorn 0.54.0, Starlette 1.10.0, Pydantic 2.14.1, pydantic-settings 2.16.2 and HTTPX 0.28.1. |
| Database | Supabase PostgreSQL 17 family, SQLAlchemy 2.0.55, Psycopg 3.3.6 and Alembic 1.20.1. The current server patch was not re-read. Isolated local/CI tests use SQLite. Staging is a separate restricted PostgreSQL role/schema in the same project. |
| Authentication | Random browser-held bearer keys, hashed in database records. Supabase Auth was used in an earlier scope and is now retired. No active admin UI or account login. |
| AI | Groq chat-completions endpoint, configured openai/gpt-oss-20b, strict JSON-schema extraction, 30-second timeout, 2,048 maximum completion tokens, temperature zero. No immutable provider snapshot identifier recorded. No embeddings, RAG, vector database, agent framework or tool calling. |
| Quality and delivery | Git/GitHub, GitHub Actions, Pytest 9.2.0, Ruff 0.17.3, ESLint, Vite build; Alembic migration checks and JUnit artifacts. Manual Chrome/Playwright browser scripts supported verification. Runtime logs are in Render/Vercel; health/environment endpoints are in the API. No dedicated APM, analytics, alerting or distributed quota service. |
| Coding assistance | OpenAI Codex/ChatGPT substantially assisted code, tests, UI, debugging, deployment operations and documentation. Session model versions varied and were not fully recorded; no unsupported model/version claim is made. Human responsibility remains with the solo developer. |
| Image creation | Built-in image-generation tool produced the twelve current food-cover illustrations. Its underlying model/version was not exposed in the recorded output. The images are labeled as illustrations and encoded in a shared WebP atlas. The retained logo's provenance/license has not been independently verified. |

Full significant and transitive versions are in [frontend/package-lock.json](../frontend/package-lock.json) and [backend/requirements.txt](../backend/requirements.txt). React and Vite use MIT licenses; FastAPI is MIT, SQLAlchemy MIT, Pydantic MIT, Psycopg LGPL, Alembic MIT and Pytest MIT. See each upstream project's license for redistribution obligations. This is a source disclosure, not an independently generated legal SBOM.

## Providers, plans and limits

The project was configured to use Vercel Hobby, Render Free, Supabase Free and Groq free access. No paid hosting upgrade is requested in the repository. Current invoices, assistant subscription costs and any existing account credits have not been audited. Provider limits may change and account-specific dashboards take precedence.

- [Groq rate limits](https://console.groq.com/docs/rate-limits): the public free-plan table for openai/gpt-oss-20b lists 30 requests/minute, 1,000 requests/day, 8,000 tokens/minute and 200,000 tokens/day. The application additionally limits recommendation requests to six per client and thirty per backend process per minute. These guards are not a billing cap or cross-instance counter.
- [Render Free](https://render.com/docs/free): 750 instance hours per workspace/month; web services idle-sleep after 15 minutes and can cold-start. The filesystem is ephemeral, so persistent application data is in PostgreSQL rather than local SQLite.
- [Supabase Free](https://supabase.com/pricing): 500 MB database per project; service resource quotas apply. This report does not claim a paid backup/PITR entitlement.
- [Vercel Hobby](https://vercel.com/docs/plans/hobby): intended for personal, noncommercial use; included quotas and platform limits apply. No commercial entitlement is claimed.
- GitHub's public-repository Actions runs provide CI/CD. No long-term runner consumption or invoice audit was performed.

Provider references were checked on November 27, 2026. The runtime API uses Groq, not the OpenAI API; no OpenAI platform key is required for this Groq-hosted open model.

## Content, assets and templates

- Campus shop/menu names, local prices and locations came from developer-supplied information. Two shop menus and some locations remain unconfirmed.
- Selected delivery-menu prices came from [Jollibee Bacolod La Salle](https://www.foodpanda.ph/restaurant/r9ql/jollibee-bacolod-la-salle), [McDonald's North Drive La Salle](https://www.foodpanda.ph/restaurant/r8sy/mcdonalds-north-drive-la-salle) and [Potato Corner North Drive](https://www.foodpanda.ph/restaurant/mjnw/potato-corner-north-drive). Delivery references are not independently verified USLS Agora counter prices. No separate redistribution license for these menu data is recorded; brand names do not imply affiliation.
- Interface fonts are [DM Sans](https://github.com/google/fonts/tree/main/ofl/dmsans) and [Manrope](https://github.com/google/fonts/tree/main/ofl/manrope), supplied through Google Fonts under the corresponding SIL Open Font License files.
- [Food-cover artwork and prompt](FOOD-COVERS.md) describe the AI-generated illustrations, their classification and the production asset. Synthetic images do not prove serving size or actual vendor presentation.
- The handoff uses a copy of the [instructor-provided DOCX template](https://docs.google.com/document/d/1nstfqO42Pj1OpvX7_z6y1KifGaqb7rjJ/edit), preserving its three-page section order and compact tables. Body text is raised from the template's 9 pt to the assignment-required 10 pt. Title borders were removed by the Google Docs sanitizer. No purchased UI template is identified in the current source review; a complete historical snippet-provenance audit has not been performed.
