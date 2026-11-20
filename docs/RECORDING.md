# Final consultation recording

Keep the recording under 15 minutes. Use the production application at https://animo-meals.vercel.app. Waiting periods can be shortened while preserving the PR number, commit, workflow run, and final deployment evidence.

## Before recording

- Merge the recording-preparation PR after frontend/backend checks pass.
- Explain that the instructor confirmed solo developers can merge their own PRs once required checks pass.
- Open the website, Supabase Table Editor, Render, Vercel, GitHub Actions, branch settings, and the test/evaluation evidence.
- Keep environment values, database URLs, AI credentials, and browser ownership keys masked.
- Use a separate browser profile for demonstration boxes so the recording's data is easy to identify.

## Presentation order

| Time | Demonstration |
| --- | --- |
| 0:00–0:45 | Introduce AnimoMeals, its current working features, completion estimate, and remaining catalog verification. |
| 0:45–4:00 | Set a PHP 100 budget and request chicken with rice. Save a suggestion, open My Meal Boxes, view meals, rename the box, refresh, and delete it. Show a loading state and invalid-budget message. |
| 4:00–6:00 | Create a clearly named demo box and show its saved_plans and saved_plan_items records in Supabase. Explain stalls → menu_items and saved_plans → saved_plan_items. Show Render status/runtime logs and Vercel production/build logs. |
| 6:00–7:15 | Demonstrate Groq preference extraction, backend validation, database matching, and exact budget totals. Show the AI error mapping in backend/app/recommendations.py. |
| 7:15–8:30 | Show passing API tests, mocked provider tests, the real-provider language results, and the GitHub Actions test artifact. |
| 8:30–13:45 | Complete the fresh change-to-deployment demonstration below. Show protection rules, workflow configuration, test/build stages, merge, deployment logs, and the working production site. |
| 13:45–14:30 | Summarize the verified features and remaining catalog details. |

## Fresh change-to-deployment demonstration

Perform these steps during the recording. Choose an unused branch name.

1. Start from an up-to-date main branch and create demo/video-workflow.
2. Add backend/tests/test_video_budget.py containing the harmless test below.
3. Run the test, commit it, and push the branch.
4. Open a PR into main and show the Application checks workflow starting automatically.
5. Show required frontend/backend checks and the blocked merge state while checks are pending or failing. Explain the instructor-approved solo exception for reviews.
6. Merge after the required checks pass.
7. Follow the resulting main-branch workflow. Its deploy-frontend job invokes the configured Vercel hook. Render deploys after successful checks.
8. Show the Vercel and Render deployment logs and final status. Verify the backend revision at https://animo-meals-api.onrender.com/api/environment against the merge commit.
9. Open production, request a meal, and verify that the application still works.

```python
from decimal import Decimal

from app.recommendations import RecommendationInput


def test_video_budget_example_preserves_exact_pesos():
    request = RecommendationInput(budget="50.00", preferences="")
    assert request.budget == Decimal("50.00")
```

The workflow triggers on pull requests to main and pushes to main. Deployment occurs after a successful main push. Show the actual run IDs throughout the recording.

## Evidence to open

- Current production catalog and limitations in verification/catalog-snapshot.json.
- Real-provider examples and acceptance checks in verification/recording-live-audit.json.
- Current Git history scan and local rollback rehearsal in verification/recording-audit.json.
- Staging migration and CRUD results in verification/recording-staging.json.
- Historical pipeline measurements in verification/recording-ci-timings.json.
- Enforced GitHub rules in verification/recording-repository-rules.json and the actual repository settings.
- Current test report under the GitHub Actions api-test-results artifact.

The pipeline measurements show npm installation decreasing from 4 to 2 seconds, frontend job duration decreasing from 15 to 14 seconds, and the overall parallel-job span increasing from 24 to 26 seconds. These are two historical runs, with different test/reporting work, and demonstrate mixed timing results.

## Remaining catalog information

The pending shop needs its name and location. Maria Rosa needs a confirmed location and menu. Pritong Manok needs a menu. Potato Corner USLS Agora counter prices and offerings need confirmation because the recorded references came from the North Drive delivery menu. Describe these data limits when stating completion.

## Submit

Upload the final screen recording to Google Drive, set viewing permissions for the assessor, and test the shared link from a separate signed-out browser before submitting it. Keep clear narration and readable dashboard text.
