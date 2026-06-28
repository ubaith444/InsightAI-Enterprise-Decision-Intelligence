from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ai.langgraph_workflow import run_insight_graph, run_result_agents
from app.models import AIUsageLog, AuditAction, DatabaseConnection, QueryLog, User
from app.security.query_safety import ensure_mongo_pipeline_is_safe, ensure_sql_is_safe
from app.security.crypto import decrypt_secret
from app.services.audit import audit
from app.services.connectors import read_schema


def execute_sql(query: str, connection: DatabaseConnection | None = None) -> list[dict[str, Any]]:
    settings = get_settings()
    safe_query = ensure_sql_is_safe(query, settings.default_query_limit)
    uri = decrypt_secret(connection.uri) if connection else settings.database_url
    engine = create_engine(uri, connect_args={"check_same_thread": False} if uri.startswith("sqlite") else {})
    with engine.connect() as conn:
        result = conn.execution_options(timeout=settings.query_timeout_seconds).execute(text(safe_query))
        return [dict(row._mapping) for row in result]


def execute_mongo(pipeline: list[dict[str, Any]] | str, connection: DatabaseConnection | None = None) -> list[dict[str, Any]]:
    safe_pipeline = ensure_mongo_pipeline_is_safe(pipeline)
    if connection is not None:
        try:
            from pymongo import MongoClient

            collection_name = connection.selected_assets[0] if connection.selected_assets else "customer_activity"
            uri = decrypt_secret(connection.uri)
            client = MongoClient(uri, serverSelectionTimeoutMS=1200)
            database = client.get_default_database() if "/" in uri.rsplit("@", 1)[-1] else client[get_settings().mongo_database]
            rows = list(database[collection_name].aggregate(safe_pipeline, maxTimeMS=get_settings().query_timeout_seconds * 1000))
            for row in rows:
                row.pop("_id", None)
            return rows
        except Exception:
            if get_settings().app_env not in {"local", "test"}:
                raise
    sample = [
        {"customer": "Nimbus Co", "event": "subscription", "value": 42, "created_at": "2026-06-22"},
        {"customer": "Atlas Retail", "event": "purchase", "value": 28, "created_at": "2026-06-21"},
        {"customer": "Vertex Health", "event": "login", "value": 19, "created_at": "2026-06-20"},
    ]
    return sample[: next((stage["$limit"] for stage in safe_pipeline if "$limit" in stage), 100)]


def ask_ai(
    db: Session,
    user: User,
    workspace_id: str,
    question: str,
    connection: DatabaseConnection | None,
    engine: str,
    execute: bool = True,
) -> dict[str, Any]:
    schema = read_schema(connection)
    state = run_insight_graph(question, schema, engine, workspace_id=workspace_id, user_id=user.id)
    if state.get("clarification_required"):
        insights = {
            "summary": state["explanation"],
            "trends": [],
            "anomalies": [],
            "recommendations": ["Specify a business metric, dimension, and time range."],
        }
        log = QueryLog(
            workspace_id=workspace_id,
            user_id=user.id,
            connection_id=connection.id if connection else None,
            question=question,
            generated_query="",
            engine=state["engine"],
            status="needs_clarification",
            row_count=0,
            insights=insights,
        )
        db.add(log)
        db.add(AIUsageLog(workspace_id=workspace_id, user_id=user.id, provider=state.get("provider", "mock"), prompt_tokens=120, completion_tokens=40))
        db.commit()
        db.refresh(log)
        audit(db, AuditAction.query_generated, "query", user.id, workspace_id, log.id, {"status": "needs_clarification"})
        return {
            "log_id": log.id,
            "question": question,
            "engine": state["engine"],
            "generated_query": "",
            "explanation": state["explanation"],
            "safe": True,
            "rows": [],
            "columns": [],
            "insights": insights,
            "chart": {"type": "table", "columns": []},
            "follow_up_questions": ["Which metric should I analyze?", "Which time period should I use?", "Which table or collection should I query?"],
            "agent_trace": state.get("agent_trace", []),
            "final_confidence": state.get("final_confidence", 0),
            "query_confidence": {
                "confidence_score": state.get("final_confidence", 0),
                "reasoning_summary": state.get("explanation", "Clarification required before query generation."),
                "risk_level": "low",
                "suggested_corrections": ["Specify metric, dimension, and time period."],
            },
        }
    rows: list[dict[str, Any]] = []
    status = "generated"
    error = None
    try:
        if not state.get("safe", False):
            raise ValueError(state.get("validation_error") or "Query did not pass validation")
        if state["engine"] == "mongodb":
            safe_query = ensure_mongo_pipeline_is_safe(state["generated_query"])
            rows = execute_mongo(safe_query, connection) if execute else []
        else:
            safe_query = ensure_sql_is_safe(str(state["generated_query"]))
            rows = execute_sql(safe_query, connection) if execute else []
        status = "executed" if execute else "generated"
    except Exception as exc:
        safe_query = state.get("generated_query", "")
        status = "failed"
        error = str(exc)
    state = run_result_agents(state, rows)
    insights = state["insights"]
    chart = state["chart"]
    log = QueryLog(
        workspace_id=workspace_id,
        user_id=user.id,
        connection_id=connection.id if connection else None,
        question=question,
        generated_query=str(safe_query),
        engine=state["engine"],
        status=status,
        row_count=len(rows),
        error=error,
        insights=insights,
    )
    db.add(log)
    db.add(AIUsageLog(workspace_id=workspace_id, user_id=user.id, provider=state.get("provider", "mock"), prompt_tokens=450, completion_tokens=180))
    db.commit()
    db.refresh(log)
    audit(db, AuditAction.query_generated, "query", user.id, workspace_id, log.id)
    if execute and status == "executed":
        audit(db, AuditAction.query_executed, "query", user.id, workspace_id, log.id, {"row_count": len(rows)})
    return {
        "log_id": log.id,
        "question": question,
        "engine": state["engine"],
        "generated_query": safe_query,
        "explanation": state["explanation"],
        "safe": error is None,
        "rows": rows,
        "columns": list(rows[0].keys()) if rows else [],
        "insights": insights,
        "chart": chart,
        "follow_up_questions": [
            "Which region is driving the change?",
            "How does this compare to the previous period?",
            "Which customers should the team prioritize next?",
        ],
        "agent_trace": state.get("agent_trace", []),
        "final_confidence": state.get("final_confidence", 0),
        "query_confidence": {
            "confidence_score": state.get("final_confidence", 0),
            "reasoning_summary": state.get("explanation", "Generated by the multi-agent workflow."),
            "risk_level": state.get("cost_governance", {}).get("workspace_usage_status", "within_limits"),
            "suggested_corrections": state.get("cost_governance", {}).get("warnings", []) or ["Query is read-only and includes enforced limits."],
        },
    }
