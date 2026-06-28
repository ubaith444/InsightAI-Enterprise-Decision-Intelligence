# InsightAI API Connectors

Date: 2026-06-27

## Summary

InsightAI now includes an enterprise connector catalog and live REST API integration foundation. The product can catalog common business systems, test REST endpoints, sync JSON payloads into workspace-scoped history, detect response schema, and route API/platform questions through the Enterprise API Integration Agent.

## Connector Catalog

Implemented catalog categories:

- Structured databases: PostgreSQL, MySQL placeholder, SQLite placeholder, SQL Server, Oracle
- NoSQL: MongoDB
- Data warehouses: Snowflake, BigQuery, Redshift
- Business platforms: Salesforce, HubSpot, Stripe, Shopify, Google Analytics 4, Meta Ads, Google Ads, Jira, GitHub, Slack, Notion, Airtable
- Files: CSV, Excel, JSON, Parquet placeholder
- Generic APIs: REST API

## Implemented Backend Routes

- `GET /api/v1/enterprise/connectors/catalog`
- `POST /api/v1/enterprise/api/test`
- `POST /api/v1/enterprise/api/sync`
- `GET /api/v1/enterprise/api/sync-history?workspace_id=...`

## Live REST API Behavior

The REST integration path supports:

- URL validation
- Optional authorization header
- Timeout handling
- JSON schema sampling
- Sync history persistence
- Workspace-scoped sync records
- Error capture for failed upstream calls
- Provider definitions for GitHub, Stripe, and Google Analytics 4
- Provider pagination metadata
- Provider rate-limit metadata

## File Import Behavior

- CSV: real parser
- JSON: real parser
- Excel: real `.xlsx` parser using workbook XML
- Parquet: accepted with warning until a production parquet engine is installed

## Enterprise API Integration Agent

The agent returns integration metadata for API and SaaS questions:

```json
{
  "platforms": ["salesforce"],
  "credential_validation": "required",
  "live_fetch": "available_for_rest_api",
  "pagination": "cursor_and_link_header_ready",
  "retry_policy": "exponential_backoff",
  "incremental_sync": "cursor_metadata_supported",
  "schema_detection": "json_sampling",
  "rate_limit_handling": "backoff_and_warning",
  "oauth_refresh": "provider_hook_ready"
}
```

## Security

- Connector records remain workspace-scoped.
- Credentials are never returned to the frontend.
- Database credentials use encrypted storage for new connections.
- API sync responses persist metadata and schema, not secret headers.

## Remaining Provider Work

OAuth flows, provider-specific SDKs, and warehouse-native drivers should be enabled per customer environment. The platform is ready for those connectors, but live Salesforce, HubSpot, Stripe, Shopify, warehouse, and ad platform syncs require real credentials and provider app registration.
