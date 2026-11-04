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

[Historical provider evidence](docs/verification/ai-provider.json) records one successful sample, not overall extraction accuracy. Automated tests mock provider responses and verify extraction validation, exact budget boundaries, empty catalogs, unavailable listings, ownership of saved boxes and provider failures. [Evaluation examples](docs/evaluation-cases.json) provide a small manual acceptance set; no new live evaluation score is claimed.

Provider references: [structured outputs](https://console.groq.com/docs/structured-outputs), [rate limits](https://console.groq.com/docs/rate-limits).
