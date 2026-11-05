# AI setup and behavior

The existing backend Groq integration is reused. The configured model is `openai/gpt-oss-20b`; change `GROQ_MODEL` privately if needed. `GROQ_API_KEY` belongs only in backend `.env` or the host's private environment settings. No OpenAI API key is needed for this Groq-hosted model.

The visitor sends a budget and an optional preference description to `POST /api/recommendations`. Groq extracts structured budget, preferred food, drink requirement, non-spicy preference, same-shop preference and exclusions. Pydantic validates the response. If a description states a budget different from the budget field, the visitor must correct it. The entered budget is never silently increased.

The backend matches words against recorded menu names/descriptions, selects combinations and calculates exact decimal totals. Matching is deliberately conservative; aliases include manok/chicken, kanin/rice, baboy/pork and isda/fish. This is not semantic knowledge of every recipe. Exclusions filter recorded mentions only; incomplete ingredient information prevents any allergy-safety guarantee. Non-spicy requests require explicit non-spicy or mild information in the listing.

No AI call is made for empty menus, no affordable recorded items, or blank preferences. Blank preferences use recorded-price comparison. No fabricated recommendations appear if there is no match.

Provider timeouts, unavailable quota, malformed responses and authentication failures show safe messages. Visitors can retry or clear preferences for price-only comparison. The endpoint is limited to six requests per client and thirty total requests per minute per backend process; there are no automatic provider retries. This is a small single-process guard, not a distributed quota service. A shared network may share limits.

## Manual provider smoke test

The original Week 1 verification command remains available from `backend`:

```powershell
.venv/Scripts/python.exe -m app.ai_smoke_test --output ../../ai-provider-verification.json
```

`--configure` prompts privately for a replacement key. Never paste credentials into chat or Git. Do not run real provider calls in CI.

## Week 3 consultation

The recommender sends a structured request to Groq, validates its reply, and matches the extracted preferences against recorded menu items. The backend adds the listed prices and checks the budget before returning suggestions to the browser.

The live evaluation used an isolated test menu with chicken at PHP 60.50, rice at PHP 15.00, and water at PHP 10.00. Three checks passed. The English prompt matched the PHP 85.50 budget exactly, the Tagalog prompt left PHP 14.50 from a PHP 100 budget, and a request with conflicting budgets returned HTTP 422. A local browser also showed the PHP 85.50 suggestion and saved it as a Meal Box. The initial evaluation caught a dropped rice preference and a Tagalog conjunction treated as a food term. The fixes passed the same scenarios on rerun. [Live evaluation results](docs/verification/week-3-live-evaluation.json)

CI runs the recommendation endpoint with mocked Groq HTTP responses. The tests exercise the real response parser and backend matching, including timeouts, provider errors, malformed output, rate limits, and the price-only fallback guidance. [Evaluation examples](docs/evaluation-cases.json)

Provider references: [structured outputs](https://console.groq.com/docs/structured-outputs), [rate limits](https://console.groq.com/docs/rate-limits).
