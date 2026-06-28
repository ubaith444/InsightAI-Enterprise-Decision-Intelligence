# InsightAI Demo Video

Recorded artifact:

- `docs/assets/demos/insightai-demo.webm`

## Walkthrough Coverage

The video demonstrates:

- User login
- Workspace creation
- Database connection
- Live data synchronization
- Natural language analytics
- Multi-agent workflow execution
- AI query generation
- Dashboard creation
- Executive report generation
- Data lineage visualization
- Human approval workflow
- Agent monitoring dashboard
- Audit logs
- Real-time KPI updates
- Report export
- Settings and RBAC

## Re-record Command

```powershell
cd frontend
npm.cmd run build
node_modules\.bin\playwright.cmd test --config demo.playwright.config.ts
```

The recorder saves the final video to `docs/assets/demos/insightai-demo.webm`.
