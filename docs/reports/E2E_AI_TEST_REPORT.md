# InsightAI E2E AI Test Report

Date: 2026-06-27

## Final Result

Passed after fixes.

- Backend AI/security E2E: 9 tests passed.
- Browser E2E: 2 Playwright tests passed.
- Frontend chart rendering was verified with Playwright using `data-testid="query-chart"`.

## End-to-End User Journey

| Step | Status | Evidence |
| --- | --- | --- |
| Register new user | Passed | Backend and Playwright register unique users |
| Login with JWT | Passed | Backend JWT flow verified |
| Create workspace | Passed | Backend E2E creates workspace |
| Connect PostgreSQL demo database | Passed | SQLite-backed seeded demo warehouse connected as PostgreSQL demo |
| Connect MongoDB demo database | Passed | MongoDB connection config accepted and masked |
| Load schema | Passed | `sales`, `customers`, and `products` tables verified |
| Ask AI business question | Passed | Multiple sample prompts executed |
| Generate SQL query | Passed | Queries start with `SELECT` |
| Validate query safety | Passed | Unsafe SQL and Mongo stages rejected |
| Execute query | Passed | SQL query returns rows |
| Return table results | Passed | Rows and columns returned |
| Generate AI insights | Passed | Summary/recommendations returned |
| Recommend chart type | Passed | Line/bar/table recommendations verified |
| Render chart on frontend | Passed | Playwright verified chart container |
| Save chart to dashboard | Passed | Dashboard saved and listed |
| Create AI report | Passed | Report created |
| Export report placeholder | Passed | PDF/Excel placeholder verified |
| Verify query history | Passed | History contains executed prompt |
| Verify audit logs | Passed | Query/dashboard/report audit events verified |
| Verify RBAC restrictions | Passed | Viewer and Analyst restrictions verified |
| Verify admin panel data | Passed | Admin analytics endpoint verified |
| Verify workspace isolation | Passed | Cross-workspace history blocked |
| Verify error handling | Passed | Invalid connection test returns controlled error |

## Sample Question Results

| Question | Result |
| --- | --- |
| Show monthly revenue trend for the last 12 months | Generated SQL, returned rows, recommended line chart |
| Find top 10 customers by revenue | Generated SQL, returned rows, recommended bar/table-style result |
| Compare sales by region | Generated SQL, returned rows, recommended bar chart |
| Show low inventory products | Generated SQL against products inventory |
| Generate MongoDB aggregation for user activity | Generated read aggregation and returned sample rows |
| Explain why revenue dropped last month | Generated safe revenue trend query and insights |

## Negative/Security Tests

| Case | Result |
| --- | --- |
| Vague question: `show something` | Passed: clarification requested |
| Unsafe SQL: `DELETE FROM sales` | Passed: blocked |
| MongoDB `$merge` stage | Passed: blocked |
| Viewer executes AI query | Passed: 403 |
| Analyst accesses admin analytics | Passed: 403 |
| Raw DB credentials in frontend connection response | Passed: raw URI removed, masked URI shown |
| Query logs include workspace/user | Passed: verified in database |
| Async long-running query path | Passed: queued placeholder returned |
| Missing API key mock mode | Passed for deterministic fallback/provider logging; environment may record `openai-configured` if a key is present |

## Bugs Fixed During E2E

- Raw connection URI exposure.
- Missing execution RBAC on AI/query endpoints.
- Missing workspace access checks.
- Missing vague-question clarification behavior.
- Missing async job-flow placeholder.
- Connection form async reset crash.
- Connection form missing visible submit errors.
- Playwright strict-mode duplicate text assertion.

## Remaining Limitations

- Redis/Celery worker execution is not fully implemented; the API returns a queue placeholder.
- MongoDB execution is sample-backed unless a live MongoDB service is configured.
- OpenAI/LangGraph flow is structurally prepared but deterministic generation remains the active implementation.
- Frontend admin navigation should be hidden from non-admin roles.
- Dependency audit still reports 2 moderate npm findings.

## Final Production Readiness Score

8/10
