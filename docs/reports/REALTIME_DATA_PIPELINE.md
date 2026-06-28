# InsightAI Realtime Data Pipeline

Date: 2026-06-27

## Architecture

Frontend realtime dashboard

-> FastAPI API Gateway

-> Realtime snapshot API and WebSocket stream

-> Usage analytics, query logs, source health, agent traces

-> Celery/Redis for long-running refresh jobs

-> Optional Kafka abstraction for production streaming

## Implemented Endpoints

- `GET /api/v1/realtime/snapshot?workspace_id=...`
- `WS /api/v1/realtime/ws/{workspace_id}`

## Refresh Intervals

Supported:

- 5 seconds
- 15 seconds
- 30 seconds
- 60 seconds
- Manual refresh

## Live Dashboard Features

- Live KPI cards
- Recent query activity
- Workspace usage metrics
- WebSocket-ready stream payload
- Automatic frontend refresh through TanStack Query

## Streaming Extension Path

The local implementation does not require Kafka. In production, a Kafka adapter can publish:

- Query execution events
- Data sync events
- Report completion events
- Anomaly alerts
- Agent trace events

The current WebSocket layer can subscribe to that stream without changing the frontend contract.
