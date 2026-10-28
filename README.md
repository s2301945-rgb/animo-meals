# AnimoMeals: Your AI-Powered Canteen Meal Finder

## Current Week 1 Status

The local foundation includes a React menu page, FastAPI endpoints, two related database tables, a saved Alembic migration, fictional seed records, and automated checks. See [Run locally](RUN-LOCALLY.md) for beginner-friendly commands.

Local development defaults to SQLite when DATABASE_URL is absent. The original laptop is now connected to Supabase PostgreSQL: migration 0001, three fictional stalls, and ten menu items have been verified. Groq structured extraction and a backend smoke-test command are implemented; a real provider call is still pending key configuration. Administrator CRUD, meal-combination recommendations, and live deployment are not implemented yet. See [AI setup](AI-SETUP.md). The features below describe the intended completed project.

## Branch Strategy

`main` holds reviewed changes. Work happens on descriptive feature branches, such as `feature/week-1-app`, and enters `main` through a pull request. The solo developer reviews the diff and validation results before merging. GitHub Actions runs install, lint, build, migration, and backend checks on pull requests.

## Backlog and Consultation

- [All project issues](https://github.com/s2301945-rgb/animo-meals/issues)
- [Week 1 milestone](https://github.com/s2301945-rgb/animo-meals/milestone/1)
- [Local setup and verification](RUN-LOCALLY.md)

Supabase migration and API verification are complete. Week 1 still needs a successful real AI provider call and pipeline-triggered live deployment. The current source includes the Groq verification command; do not mark the real-call requirement complete until evidence exists.

AnimoMeals is an AI-assisted application designed to help La Salle students discover budget-friendly canteen meals tailored to their preferences. Simply input your budget and food desires, such as "I have ₱100 and want a non-spicy chicken meal with a drink," and AnimoMeals will suggest meal combinations from recorded menus. You'll see prices, stall locations, and your remaining budget at a glance.



## Project Goals

*   Empower students to compare affordable canteen meal options.
*   Utilize AI to interpret natural language budgets and food preferences.
*   Calculate optimal meal combinations based on recorded prices.
*   Provide administrators with tools to manage stalls, menu items, and availability.
*   Develop a complete, end-to-end application (frontend, backend, database).

AnimoMeals prioritizes affordability and preference matching. Please note that the application does not assess food quality or nutritional value without supporting data.

## Developer and Responsibilities

This project is an individual endeavor.

**Developer:** LANCE FRANCIS M. GARGARITANO
**Course/Section:** BSCS 4B

| Role                      | Responsibility                                                                 |
| :------------------------ | :----------------------------------------------------------------------------- |
| Project Lead              | Manage project scope, backlog, schedule, and documentation                     |
| Frontend Developer        | Build responsive user interfaces and integrate with the backend                |
| Backend Developer         | Implement REST APIs, data validation, AI integration, and meal logic           |
| Database Developer        | Design database schemas, manage migrations, and populate demonstration data    |
| Tester and Deployment Maintainer | Verify application behavior, configure automated checks, and manage deployment |

## Technology Stack

| Part                | Technology          | Purpose                                                              |
| :------------------ | :------------------ | :------------------------------------------------------------------- |
| Frontend            | React + Vite        | Interactive user interface, development server, and production builds |
| Styling             | CSS                 | Responsive layouts and visual design                                 |
| Backend             | Python + FastAPI    | REST API, validation, AI requests, and recommendation logic          |
| Database            | Supabase PostgreSQL | Persistent relational data storage                                   |
| Database Access     | SQLAlchemy          | ORM for Python database interaction                                  |
| Migrations          | Alembic             | Track and apply database schema changes                              |
| AI Provider         | Groq API   | Extract structured preferences with Groq-hosted GPT-OSS 20B                  |
| Frontend Hosting    | Vercel Hobby        | Host the frontend application                                        |
| Backend Hosting     | Render Free         | Host the backend application                                         |
| Repository & Automation | GitHub + GitHub Actions | Source control, issue tracking, CI/CD, and deployment automation     |

The project aims to utilize free service plans within their usage limits. Availability and limitations are subject to the current terms of each provider.

## Initial Scope

The first version of AnimoMeals will focus on a single campus and a curated selection of canteen stalls.

### Student Features

*   Browse available menu items and stall details.
*   Input budget and food preferences.
*   Utilize natural language for search queries.
*   Compare various meal combinations within their budget.
*   View item prices, total costs, remaining budget, and last update times.
*   Receive clear feedback when no matching combinations are found.

### Administrator Features

*   Create, view, update, and delete stall information.
*   **Note:** Menu prices and availability require manual updates. Listings will display their last update time, and confirmation at the stall is recommended. Free hosting may experience pauses or slow wake-up times; the deployed application will be verified before consultations and defenses.
