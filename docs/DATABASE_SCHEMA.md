# Database Schema

InsightAI uses PostgreSQL for relational application state and demo business
tables, and MongoDB for flexible workspace documents.

## PostgreSQL application tables

| Table | Purpose | Key fields |
| --- | --- | --- |
| `users` | Authenticated users and global role. | `id`, `email`, `full_name`, `hashed_password`, `role`, `is_active`, `created_at` |
| `workspaces` | Tenant/workspace boundary. | `id`, `name`, `slug`, `owner_id`, `created_at` |
| `workspace_members` | User membership and workspace-level role. | `id`, `workspace_id`, `user_id`, `role` |
| `database_connections` | Workspace data sources with masked credentials. | `id`, `workspace_id`, `name`, `kind`, `uri`, `is_read_only`, `selected_assets`, `created_by` |
| `query_logs` | Generated and executed analytics requests. | `id`, `workspace_id`, `user_id`, `connection_id`, `question`, `generated_query`, `engine`, `status`, `row_count`, `error`, `insights` |
| `ai_usage_logs` | Provider/model usage for cost governance. | `id`, `workspace_id`, `user_id`, `provider`, `model`, `prompt_tokens`, `completion_tokens` |
| `audit_logs` | Immutable user and system audit events. | `id`, `workspace_id`, `actor_id`, `action`, `entity_type`, `entity_id`, `metadata_json`, `created_at` |

## PostgreSQL demo dataset

`data/postgres/business_dataset.sql` seeds business analytics tables used by
the demo workspace. The dataset covers sales, customers, products, orders,
employees, regions, expenses, inventory, and related KPI examples.

## MongoDB collections

MongoDB stores flexible workspace objects:

- `dashboards`
- `reports`
- `workspace_resources`
- `comments`
- `approvals`
- `notifications`
- `scheduled_reports`
- `exports`
- `source_health`
- `knowledge_documents`
- `ai_memory`
- `agent_traces`

Example collection shape is documented in `data/mongo/example_collections.json`.

## Migrations

The backend includes Alembic configuration in `backend/alembic.ini` and the
initial migration in `backend/alembic/versions/0001_initial.py`. The app also
creates metadata during local startup to keep the demo stack simple.
