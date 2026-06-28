# RBAC Matrix

InsightAI uses ranked roles in `backend/app/security/rbac.py`.

| Rank | Role | Intended scope |
| --- | --- | --- |
| 4 | Super Admin | Platform-wide administration and diagnostics. |
| 3 | Admin | Workspace administration and operational management. |
| 2 | Analyst | Query, dashboard, report, and analysis workflows. |
| 1 | Viewer | Read-only workspace consumption. |

## Capability matrix

| Capability | Super Admin | Admin | Analyst | Viewer |
| --- | --- | --- | --- | --- |
| View own profile | Yes | Yes | Yes | Yes |
| List users | Yes | Yes | No | No |
| Create workspace | Yes | Yes | Yes | No |
| View workspace content | Yes | Member only | Member only | Member only |
| Create database connection | Yes | Yes | Yes | No |
| Test database connection | Yes | Yes | Yes | No |
| Inspect schema | Yes | Yes | Yes | Read-only where exposed |
| Ask AI analytics questions | Yes | Yes | Yes | Limited/read-only |
| Validate generated query | Yes | Yes | Yes | Yes |
| Execute safe read query | Yes | Yes | Yes | No |
| Create dashboards and reports | Yes | Yes | Yes | No |
| Export reports | Yes | Yes | Yes | Yes |
| Manage approvals/comments | Yes | Yes | Yes | Comment/read only |
| View audit logs | Yes | Yes | No | No |
| View admin analytics and agent traces | Yes | Admin where enabled | No | No |

## Enforcement notes

- Authentication requires a bearer JWT.
- `require_role()` enforces minimum global role rank.
- Workspace access is allowed for Super Admin users or explicit
  `workspace_members` rows.
- Connection access is derived from the owning workspace.
- Query safety is enforced independently from RBAC.
