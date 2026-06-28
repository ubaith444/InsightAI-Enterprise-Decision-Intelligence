# InsightAI ETL Architecture

Date: 2026-06-27

## Summary

InsightAI includes a production ETL foundation for workspace-scoped dataset imports and sync history. CSV and JSON imports are implemented with validation, cleaning, deduplication, column normalization, and persisted ETL run metadata. Excel and Parquet are represented as scheduled-processing placeholders until file parser dependencies and storage are attached in a production environment.

## Implemented Routes

- `POST /api/v1/enterprise/etl/import`
- `GET /api/v1/enterprise/etl/runs?workspace_id=...`

## Import Flow

1. User selects workspace and uploads a file.
2. Backend validates file type and source type.
3. CSV or JSON content is parsed.
4. Column names are normalized.
5. Duplicate rows are removed.
6. Validation warnings are collected.
7. ETL run metadata is stored in MongoDB-backed storage.
8. The frontend displays recent ETL runs in `/integrations`.

## ETL Agent Responsibilities

The Data Ingestion / ETL Agent coordinates:

- CSV upload
- JSON upload
- Excel and Parquet placeholder routing
- Uploaded schema validation
- Data cleaning summary
- Duplicate detection
- Business glossary mapping metadata
- Scheduled import placeholder metadata

## Returned ETL Shape

```json
{
  "source_type": "csv",
  "import_status": "completed",
  "rows_processed": 1250,
  "validation_errors": [],
  "cleaning_summary": {
    "duplicates_removed": 18,
    "columns_normalized": true
  }
}
```

## Async Job Readiness

The existing Celery and Redis job foundation is used for long-running query execution and is ready for large dataset imports. Local tests use deterministic eager execution where appropriate; production Docker Compose starts a Redis-backed Celery worker.

## Production Extension Points

- Object storage for uploaded source files
- Excel and Parquet parser dependencies
- Batch chunking for very large files
- Incremental sync and CDC adapters
- Scheduled imports through Celery beat or an external scheduler
- Row-level validation rules per business glossary entry
