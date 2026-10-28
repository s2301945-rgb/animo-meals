# Week 1 AI verification with Groq

## Provider choice

Groq is the chosen provider for the backend text extraction task. The user's existing Gemini project reports that its free tier is unavailable. Groq publishes free-plan limits for `openai/gpt-oss-20b`, which supports strict structured output. This is a Groq-hosted model: an OpenAI API key is not used.

References:
- https://console.groq.com/docs/rate-limits
- https://console.groq.com/docs/structured-outputs

Use a free Groq account without upgrading billing. Free quotas are limited; account availability must be verified by a real request. The command makes one request and never retries automatically.

## What is implemented

- A backend-only extraction function returns a validated budget, preferred food, drink requirement, spicy-food exclusion, same-stall preference, and ingredient exclusions.
- Missing preferences remain null rather than guessed.
- Invalid input, missing keys, authentication failures, quota limits, timeouts, malformed responses, and incomplete output have safe error messages.
- Automated tests use mock responses and never consume real API quota.
- There is no public paid-call endpoint or frontend AI button in this Week 1 increment.

## Configure and make one real test call

Create a project key yourself in https://console.groq.com/keys. Give it a recognizable name such as AnimoMeals. An expiration date is recommended; do not paste the key into chat or commit it.

From the repository root in PowerShell:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.ai_smoke_test --configure --output ../../ai-provider-verification.json
```

At the hidden prompt, paste the key and press Enter. The command sends a fictional meal request to Groq. After a successful, validated response, it saves `GROQ_API_KEY` and `GROQ_MODEL` in the ignored `backend/.env` while preserving the database configuration. On failure, the new key is not saved.

The evidence file contains only the sample request, extracted fields, provider, model, timestamp, and validation status. A successful provider connection does not prove accuracy across all possible requests. Inspect the extracted fields and later evaluate a labeled set of student requests.

After configuration, rerun a test without entering the key:

```powershell
.\.venv\Scripts\python.exe -m app.ai_smoke_test --output ../../ai-provider-verification.json
```

Do not run real provider calls in CI. Manual menu browsing continues to work without an AI key.

## Remaining work

The Week 1 AI connection requirement is complete only after a real provider response is verified and its evidence is saved. Full preference-review UI, an authenticated or rate-limited API route, and meal-combination recommendations are later features. Deployment remains a separate Week 1 task.
