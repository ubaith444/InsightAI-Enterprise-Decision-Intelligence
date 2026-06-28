# InsightAI Security Architecture

Date: 2026-06-27

## Security Controls

- JWT authentication
- Role-based access control
- Roles: Super Admin, Admin, Analyst, Viewer
- Workspace isolation on backend routes
- Read-only SQL and MongoDB query validation
- Mutating SQL keyword blocking
- Unsafe MongoDB stage blocking
- Connection string encryption for new database connections
- Masked credentials in API and frontend responses
- AI query rate limiting
- Input sanitation for AI prompts
- Audit logs for sensitive actions
- Admin-only monitoring surfaces
- Human-in-the-loop approval records before publishing, external actions, report sending, dataset deletion, and destructive operations

## Workspace Isolation

APIs validate user access to `workspace_id` before returning or mutating workspace resources. This applies to connections, schema, queries, dashboards, reports, semantic metrics, lineage, knowledge, comments, approvals, realtime snapshots, and source health.

## Secrets

Secrets should be injected through environment variables, Docker secrets, Kubernetes secrets, or a cloud secret manager. The frontend only receives masked credential metadata.

## Compliance Hooks

The Security & Compliance Agent records RBAC, workspace isolation, query permission, PII, and credential-protection checks in every workflow trace.

## Remaining Production Work

Recommended staging additions are external secret-manager integration, SSO/SAML, organization-specific data retention policies, PII classifiers per data domain, and immutable audit storage such as WORM object storage or append-only database tables.
