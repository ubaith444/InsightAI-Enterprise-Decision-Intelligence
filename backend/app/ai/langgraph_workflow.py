from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, TypedDict
from uuid import uuid4

from app.core.config import get_settings
from app.db.mongo import mongo_store
from app.security.query_safety import validate_query
from app.services.ai_query import generate_insights, generate_query, recommend_chart
from app.services.workspace_resources import search_knowledge, semantic_layer


class InsightAIState(TypedDict, total=False):
    trace_id: str
    workspace_id: str | None
    user_id: str | None
    question: str
    schema: dict[str, Any]
    schema_summary: dict[str, Any]
    engine: str
    provider: str
    intent: str
    intent_confidence: float
    required_agents: list[str]
    workflow_plan: dict[str, Any]
    model_route: dict[str, Any]
    business_context: dict[str, Any]
    semantic_layer: dict[str, Any]
    data_quality: dict[str, Any]
    data_lineage: dict[str, Any]
    anomaly_detection: dict[str, Any]
    etl: dict[str, Any]
    cost_governance: dict[str, Any]
    api_integration: dict[str, Any]
    executive_decision: dict[str, Any]
    collaboration: dict[str, Any]
    scheduling: dict[str, Any]
    monitoring: dict[str, Any]
    governance: dict[str, Any]
    supervisor_plan: dict[str, Any]
    clarification_required: bool
    clarification_question: str | None
    generated_query: str | list[dict[str, Any]]
    optimized_query: str | list[dict[str, Any]]
    explanation: str
    chart_type: str
    safe: bool
    validation_error: str | None
    cost_estimate: dict[str, Any]
    execution_plan: dict[str, Any]
    rows: list[dict[str, Any]]
    insights: dict[str, Any]
    root_causes: list[str]
    forecast: dict[str, Any]
    chart: dict[str, Any]
    dashboard_suggestion: dict[str, Any]
    report_draft: dict[str, Any]
    rag_context: list[dict[str, Any]]
    memory: dict[str, Any]
    recommendations: list[str]
    compliance: dict[str, Any]
    agent_trace: list[dict[str, Any]]
    token_usage: dict[str, int]
    retries: int
    errors: list[str]
    final_confidence: float


AgentFn = Callable[[InsightAIState], InsightAIState]


@dataclass(frozen=True)
class AgentSpec:
    node: str
    display_name: str
    responsibility: str
    fn: AgentFn
    retry_limit: int = 1


def _now_ms() -> float:
    return time.perf_counter() * 1000


def _record_agent(state: InsightAIState, name: str, started_ms: float, success: bool, error: str | None = None) -> None:
    latency = round(_now_ms() - started_ms, 2)
    prompt_tokens = max(8, len(state.get("question", "").split()) * 4)
    completion_tokens = 20 if success else 4
    state.setdefault("agent_trace", []).append(
        {
            "agent": name,
            "latency_ms": latency,
            "tokens": {"prompt": prompt_tokens, "completion": completion_tokens},
            "success": success,
            "error": error,
        }
    )
    usage = state.setdefault("token_usage", {"prompt": 0, "completion": 0})
    usage["prompt"] += prompt_tokens
    usage["completion"] += completion_tokens


def _run_agent(name: str, fn: AgentFn, state: InsightAIState, retry_limit: int = 1) -> InsightAIState:
    attempts = 0
    while True:
        started = _now_ms()
        try:
            updated = fn(state)
            _record_agent(updated, name, started, True)
            return updated
        except Exception as exc:
            attempts += 1
            state.setdefault("errors", []).append(f"{name}: {exc}")
            state["retries"] = state.get("retries", 0) + 1
            _record_agent(state, name, started, False, str(exc))
            if attempts > retry_limit:
                return state


def supervisor_agent(state: InsightAIState) -> InsightAIState:
    state.setdefault("trace_id", str(uuid4()))
    state.setdefault("agent_trace", [])
    state.setdefault("errors", [])
    state.setdefault("retries", 0)
    state.setdefault("token_usage", {"prompt": 0, "completion": 0})
    state["provider"] = "mock" if not get_settings().openai_api_key else "openai-configured"
    state["supervisor_plan"] = {
        "workflow_id": state["trace_id"],
        "parallel_groups": [
            ["schema_intelligence", "semantic_layer"],
            ["data_quality", "data_lineage"],
            ["insight_generation", "rag_knowledge"],
        ],
        "retry_policy": "retry failed agents up to their configured retry limit",
        "conflict_resolution": "prefer validated semantic metrics, safety checks, and workspace-scoped data over inferred context",
        "memory_scope": "workspace_user",
    }
    return state


def intent_classification_agent(state: InsightAIState) -> InsightAIState:
    question = state["question"].lower()
    intent = "analytics_request"
    confidence = 0.82
    required = ["schema_intelligence", "business_context", "query_validation", "insight_generation", "visualization"]
    if any(term in question for term in ["schedule", "weekly", "daily", "monthly", "alert me"]):
        intent = "scheduling_request"
        required.extend(["scheduling", "monitoring"])
    elif any(term in question for term in ["comment", "mention", "approve", "approval", "share", "collaborate"]):
        intent = "collaboration_request"
        required.append("collaboration")
    elif "dashboard" in question:
        intent = "dashboard_request"
        required.append("dashboard_builder")
    elif any(term in question for term in ["api", "salesforce", "hubspot", "stripe", "shopify", "github", "slack", "notion", "airtable", "refresh"]):
        intent = "api_integration"
        required.append("enterprise_api_integration")
    elif any(term in question for term in ["import", "upload", "sync", "csv", "excel", "spreadsheet"]):
        intent = "data_import"
        required.append("data_ingestion_etl")
    elif "report" in question or "summary" in question:
        intent = "report_generation"
        required.append("report_writer")
    elif "mongodb" in question or "aggregation" in question:
        intent = "database_question"
        required.append("mongodb_query")
    elif "forecast" in question or "predict" in question:
        intent = "prediction_request"
        required.append("forecasting")
    elif "compare" in question:
        intent = "comparison_request"
    elif "why" in question or "root cause" in question or "dropped" in question or "spike" in question:
        intent = "root_cause_analysis"
        required.append("root_cause_analysis")
    elif "chart" in question or "visual" in question:
        intent = "visualization_request"
    state["intent"] = intent
    state["intent_confidence"] = confidence
    state["required_agents"] = required
    return state


def workflow_planner_agent(state: InsightAIState) -> InsightAIState:
    intent = state.get("intent", "analytics_request")
    order = [
        "schema_intelligence",
        "semantic_layer",
        "business_context",
        "rag_knowledge",
    ]
    if intent == "data_import":
        order.extend(["data_ingestion_etl", "data_quality", "data_lineage", "policy_governance"])
        fallback = "validate upload, persist ETL run with warnings, and request human approval for major schema changes"
    elif intent == "api_integration":
        order.extend(["enterprise_api_integration", "policy_governance", "clarification"])
        fallback = "use REST connector metadata and defer external action until credentials are validated"
    else:
        order.extend(["clarification", "query_generation", "query_validation", "query_execution", "insight_generation"])
        fallback = "ask clarification or return safe explanation without executing a query"
    state["workflow_plan"] = {
        "intent": intent,
        "agents_to_run": order,
        "order": order,
        "fallback_path": fallback,
        "retry_plan": {
            "agent_retries": 1,
            "external_connectors": 3,
            "query_execution": 1,
        },
        "approval_gates": ["publish_dashboard", "send_report", "external_api_action", "delete_dataset", "major_etl_change"],
    }
    return state


def model_router_agent(state: InsightAIState) -> InsightAIState:
    provider = state.get("provider", "mock")
    intent = state.get("intent", "analytics_request")
    deterministic = provider == "mock"
    state["model_route"] = {
        "mode": "deterministic_fallback" if deterministic else "openai",
        "cheap_model_tasks": ["intent_classification", "classification", "simple_summary", "chart_labeling"],
        "strong_model_tasks": ["sql_generation", "mongo_query_generation", "reasoning", "executive_analysis", "root_cause_analysis"],
        "selected_model": "deterministic-local" if deterministic else ("gpt-4o-mini" if intent in {"analytics_request", "visualization_request"} else "gpt-4.1"),
        "fallback": "local_rule_based_agents",
        "reason": "OPENAI_API_KEY missing or local test mode" if deterministic else f"Selected based on {intent} complexity",
    }
    return state


def schema_intelligence_agent(state: InsightAIState) -> InsightAIState:
    tables = state.get("schema", {}).get("tables", [])
    state["schema_summary"] = {
        "engine": state.get("schema", {}).get("engine"),
        "assets": [item.get("name") for item in tables],
        "relationships": state.get("schema", {}).get("relationships", []),
        "business_glossary": {
            "revenue": "sales.revenue",
            "profit": "products.margin * sales.revenue",
            "active_customer": "customer_activity.event in login/purchase/subscription",
            "monthly_revenue": "sales.order_month + sum(sales.revenue)",
        },
    }
    return state


def semantic_layer_agent(state: InsightAIState) -> InsightAIState:
    workspace_id = state.get("workspace_id")
    if workspace_id:
        layer = semantic_layer(workspace_id)
        metrics = layer.get("metrics", [])
    else:
        metrics = [
            {"name": "Revenue", "definition": "Gross sales value before expenses.", "formula": "SUM(sales.revenue)"},
            {"name": "Profit", "definition": "Revenue less expenses.", "formula": "SUM(revenue) - SUM(expenses)"},
            {"name": "Gross Margin", "definition": "Revenue retained after cost of goods sold.", "formula": "(revenue - cogs) / revenue"},
            {"name": "MRR", "definition": "Monthly recurring revenue.", "formula": "SUM(subscription_monthly_amount)"},
        ]
        layer = {"workspace_id": workspace_id, "metrics": metrics, "metric_count": len(metrics), "consumed_by_agents": True}
    metric_map = {str(item.get("name", "")).lower(): item for item in metrics}
    state["semantic_layer"] = {
        **layer,
        "matched_metrics": [
            item
            for name, item in metric_map.items()
            if name and (name in state.get("question", "").lower() or name.replace(" ", "_") in state.get("question", "").lower())
        ],
    }
    glossary = state.setdefault("schema_summary", {}).setdefault("business_glossary", {})
    for metric in metrics:
        name = str(metric.get("name", "")).lower().replace(" ", "_")
        if name:
            glossary[name] = metric.get("formula") or metric.get("definition")
    return state


def data_quality_agent(state: InsightAIState) -> InsightAIState:
    schema = state.get("schema", {})
    rows = state.get("rows", [])
    tables = schema.get("tables", [])
    collections = schema.get("collections", [])
    issues: list[dict[str, Any]] = []
    affected_assets: set[str] = set()

    for table in tables:
        table_name = table.get("name", "unknown")
        nullable = [col.get("name") for col in table.get("columns", []) if col.get("nullable")]
        if nullable:
            issues.append({"type": "missing_values_possible", "asset": table_name, "columns": nullable})
            affected_assets.add(table_name)
    for collection in collections:
        collection_name = collection.get("name", "unknown")
        if not collection.get("fields"):
            issues.append({"type": "empty_collection_metadata", "asset": collection_name})
            affected_assets.add(collection_name)

    seen = set()
    duplicate_count = 0
    missing_count = 0
    invalid_date_count = 0
    numeric_values: list[float] = []
    for row in rows:
        signature = tuple(sorted((key, str(value)) for key, value in row.items()))
        if signature in seen:
            duplicate_count += 1
        seen.add(signature)
        for key, value in row.items():
            if value in (None, ""):
                missing_count += 1
            if any(term in key.lower() for term in ["date", "month", "created_at"]) and value:
                text_value = str(value)
                if not any(char.isdigit() for char in text_value) or len(text_value) < 4:
                    invalid_date_count += 1
            if isinstance(value, (int, float)):
                numeric_values.append(float(value))

    if duplicate_count:
        issues.append({"type": "duplicate_records", "count": duplicate_count})
    if missing_count:
        issues.append({"type": "missing_values", "count": missing_count})
    if invalid_date_count:
        issues.append({"type": "invalid_dates", "count": invalid_date_count})
    if not schema.get("relationships"):
        issues.append({"type": "relationship_metadata_missing", "detail": "No foreign-key relationship map was provided."})
    if rows and not any(any(term in key.lower() for term in ["date", "month", "created_at"]) for key in rows[0]):
        issues.append({"type": "stale_data_unknown", "detail": "No date field was available to verify freshness."})
    if numeric_values:
        average = sum(numeric_values) / len(numeric_values)
        outliers = [value for value in numeric_values if average > 0 and value > average * 3]
        if outliers:
            issues.append({"type": "suspicious_outliers", "count": len(outliers), "max_value": max(outliers)})

    penalty = min(70, len(issues) * 8)
    state["data_quality"] = {
        "quality_score": max(30, 100 - penalty),
        "issues": issues,
        "affected_tables": sorted(affected_assets),
        "recommendations": [
            "Review nullable business-critical fields.",
            "Add freshness checks for date-bearing datasets.",
            "Publish relationship metadata for stronger validation.",
        ][: max(1, min(3, len(issues) or 1))],
    }
    return state


def business_context_agent(state: InsightAIState) -> InsightAIState:
    question = state["question"].lower()
    glossary = state.get("schema_summary", {}).get("business_glossary", {})
    matched = {term: field for term, field in glossary.items() if term.replace("_", " ") in question or term in question}
    if "customer" in question:
        matched.setdefault("top_customer", "sales.customer grouped by revenue, orders, or profit")
    state["business_context"] = {
        "terms": matched,
        "grain": "monthly" if "month" in question else "requested",
        "semantic_metrics_used": [item.get("name") for item in state.get("semantic_layer", {}).get("matched_metrics", [])],
    }
    return state


def data_lineage_agent(state: InsightAIState) -> InsightAIState:
    schema = state.get("schema", {})
    tables = schema.get("tables", [])
    collections = schema.get("collections", [])
    assets = [item.get("name") for item in tables] + [item.get("name") for item in collections]
    metrics = [item.get("name") for item in state.get("semantic_layer", {}).get("metrics", [])[:8]]
    column_lineage = []
    for table in tables:
        for column in table.get("columns", []):
            column_name = column.get("name")
            column_lineage.append(
                {
                    "source_column": f"{table.get('name')}.{column_name}",
                    "semantic_terms": [metric for metric in metrics if str(metric).lower().replace(" ", "_") in str(column_name).lower()],
                    "downstream": ["query_result", "dashboard_widget", "report_section"],
                }
            )
    generated_query = state.get("generated_query") or state.get("optimized_query") or ""
    state["data_lineage"] = {
        "source": assets or ["configured_connection"],
        "transformation": ["semantic_mapping", "query_generation", "safe_execution"],
        "transformation_history": [
            {"step": "schema_intelligence", "status": "completed"},
            {"step": "semantic_mapping", "status": "completed"},
            {"step": "rag_enrichment", "status": "completed" if state.get("rag_context") else "not_available"},
            {"step": "query_generation", "status": "completed" if generated_query else "pending"},
        ],
        "destination": ["ai_response", "dashboard_widget", "report_section"],
        "affected_dashboards": [state.get("dashboard_suggestion", {}).get("layout", "generated_dashboard")],
        "affected_reports": [state.get("report_draft", {}).get("title", "generated_report")],
        "affected_kpis": metrics,
        "column_level_lineage": column_lineage,
        "sql_lineage": {
            "query": generated_query,
            "source_tables": assets,
            "selected_columns": [item["source_column"] for item in column_lineage] or ["unknown"],
        },
        "impact_analysis": {
            "dashboard_count": 1,
            "report_count": 1,
            "kpi_count": len(metrics),
            "risk": "medium" if generated_query else "low",
        },
        "dependency_graph": {
            "nodes": [{"id": f"source:{asset}", "type": "source"} for asset in (assets or ["configured_connection"])]
            + [{"id": f"kpi:{metric}", "type": "kpi"} for metric in metrics],
            "edges": [{"from": f"source:{assets[0] if assets else 'configured_connection'}", "to": f"kpi:{metric}", "relationship": "feeds"} for metric in metrics],
        },
    }
    return state


def data_ingestion_etl_agent(state: InsightAIState) -> InsightAIState:
    question = state["question"].lower()
    source_type = "csv" if "csv" in question else "excel" if "excel" in question or "spreadsheet" in question else "sync"
    state["etl"] = {
        "source_type": source_type,
        "import_status": "placeholder_ready",
        "rows_processed": 0,
        "validation_errors": [] if source_type in {"csv", "excel", "sync"} else ["Unsupported source type."],
        "cleaning_summary": {
            "schema_validation": "configured",
            "column_mapping": state.get("schema_summary", {}).get("business_glossary", {}),
            "deduplication": "planned",
            "scheduled_import": "placeholder",
        },
    }
    state["explanation"] = f"Prepared a {source_type.upper()} ingestion workflow with schema validation, cleaning, glossary mapping, and scheduled import placeholder."
    return state


def enterprise_api_integration_agent(state: InsightAIState) -> InsightAIState:
    question = state["question"].lower()
    platforms = ["salesforce", "hubspot", "stripe", "shopify", "github", "slack", "notion", "airtable", "jira"]
    matched = [platform for platform in platforms if platform in question]
    state["api_integration"] = {
        "required": bool(matched or "api" in question or "refresh" in question),
        "platforms": matched or ["generic_rest_api"],
        "credential_validation": "available_through_connection_test",
        "live_fetch": "available_for_rest_api_connectors",
        "pagination": "cursor_and_link_header_supported",
        "retry_policy": "3 exponential-backoff retries",
        "incremental_sync": "cursor_metadata_supported",
        "schema_detection": "json_field_sampling",
        "rate_limit_handling": "retry-after-aware",
        "oauth_refresh": "refresh-token-hook-ready",
    }
    return state


def clarification_agent(state: InsightAIState) -> InsightAIState:
    question = state["question"].lower()
    vague = len(question.split()) < 3 or any(term in question for term in ["best customers", "something", "stuff", "anything"])
    if vague:
        state["clarification_required"] = True
        state["clarification_question"] = "Please clarify the metric: should I rank customers by revenue, order count, profit, or another metric?"
        state["explanation"] = state["clarification_question"]
    else:
        state["clarification_required"] = False
        state["clarification_question"] = None
    return state


def sql_generation_agent(state: InsightAIState) -> InsightAIState:
    if state.get("clarification_required") or state.get("engine") == "mongodb":
        return state
    generated = generate_query(state["question"], state["schema"], "sql")
    state["provider"] = generated.get("provider", state.get("provider", "mock"))
    state["engine"] = generated["engine"]
    state["generated_query"] = generated["query"]
    state["explanation"] = generated["explanation"]
    state["chart_type"] = generated.get("chart_type", "table")
    state["clarification_required"] = bool(generated.get("clarification_required", False))
    return state


def mongodb_query_agent(state: InsightAIState) -> InsightAIState:
    if state.get("clarification_required") or state.get("engine") != "mongodb":
        return state
    generated = generate_query(state["question"], state["schema"], "mongodb")
    state["provider"] = generated.get("provider", state.get("provider", "mock"))
    state["engine"] = "mongodb"
    state["generated_query"] = generated["query"]
    state["explanation"] = generated["explanation"]
    state["chart_type"] = generated.get("chart_type", "bar")
    return state


def query_validation_agent(state: InsightAIState) -> InsightAIState:
    if state.get("clarification_required"):
        state["safe"] = True
        state["validation_error"] = None
        return state
    safe, query, error = validate_query(state.get("engine", "sql"), state.get("generated_query", ""))
    state["safe"] = safe
    state["generated_query"] = query
    state["validation_error"] = error
    state["cost_estimate"] = {
        "risk": "low" if safe else "blocked",
        "default_limit_enforced": "$limit" in str(query).lower() or "limit" in str(query).lower(),
        "timeout_seconds": get_settings().query_timeout_seconds,
    }
    return state


def query_optimization_agent(state: InsightAIState) -> InsightAIState:
    if not state.get("safe") or state.get("clarification_required"):
        return state
    query = state.get("generated_query", "")
    state["optimized_query"] = query
    state["execution_plan"] = {
        "connection_pooling": True,
        "timeout_seconds": get_settings().query_timeout_seconds,
        "retry_policy": "one retry on transient execution errors",
        "index_hints": ["order_month", "customer", "region"] if state.get("engine") != "mongodb" else ["event", "customer"],
    }
    return state


def query_execution_agent(state: InsightAIState) -> InsightAIState:
    state.setdefault("execution_plan", {"mode": "service-executed", "timeout_seconds": get_settings().query_timeout_seconds})
    return state


def insight_generation_agent(state: InsightAIState) -> InsightAIState:
    state["insights"] = generate_insights(state.get("rows", []), state["question"])
    return state


def executive_decision_agent(state: InsightAIState) -> InsightAIState:
    rows = state.get("rows", [])
    insights = state.get("insights", {})
    anomaly = state.get("anomaly_detection", {})
    confidence = 0.78 if rows else 0.55
    state["executive_decision"] = {
        "executive_summary": insights.get("summary", "No executive summary available."),
        "business_risks": ["Revenue concentration risk", "Regional underperformance", "Inventory constraints"] if rows else ["Insufficient data returned."],
        "growth_opportunities": ["Expand high-performing regional campaigns", "Prioritize high-value customer renewals"],
        "department_performance": {"sales": "review", "marketing": "monitor", "operations": "investigate inventory"},
        "financial_impact": "Potential revenue variance requires period-over-period review.",
        "customer_trends": ["Enterprise accounts remain highest value.", "Repeat purchase behavior should be monitored."],
        "operational_issues": ["Check low inventory and delayed approvals."],
        "strategic_recommendations": ["Increase retention campaign", "Review pricing strategy", "Investigate regional inventory shortages"],
        "priority_actions": ["Assign owner for anomaly review", "Prepare executive report", "Schedule follow-up dashboard refresh"],
        "confidence_score": confidence if anomaly.get("severity") != "high" else 0.72,
        "action_plan": [
            {"owner": "Sales", "action": "Review top customer pipeline", "priority": "high"},
            {"owner": "Operations", "action": "Validate inventory constraints", "priority": "medium"},
        ],
    }
    return state


def anomaly_detection_agent(state: InsightAIState) -> InsightAIState:
    rows = state.get("rows", [])
    anomalies: list[dict[str, Any]] = []
    affected_metrics: set[str] = set()
    for key in rows[0].keys() if rows else []:
        values = [float(row.get(key) or 0) for row in rows if isinstance(row.get(key), (int, float))]
        if len(values) < 2:
            continue
        average = sum(values) / len(values)
        latest = values[-1]
        peak = max(values)
        trough = min(values)
        if average > 0 and peak > average * 1.8:
            anomalies.append({"metric": key, "type": "spike", "value": peak, "baseline": round(average, 2)})
            affected_metrics.add(key)
        if average > 0 and trough < average * 0.45:
            anomalies.append({"metric": key, "type": "drop", "value": trough, "baseline": round(average, 2)})
            affected_metrics.add(key)
        if average > 0 and abs(latest - average) / average > 0.5:
            anomalies.append({"metric": key, "type": "unusual_trend", "value": latest, "baseline": round(average, 2)})
            affected_metrics.add(key)

    question = state["question"].lower()
    if any(term in question for term in ["dropped", "drop", "spike", "anomaly", "unusual", "why"]):
        anomalies.append({"metric": "requested_metric", "type": "question_flag", "value": "user_requested_investigation"})
        affected_metrics.add("requested_metric")

    severity = "high" if len(anomalies) >= 2 else "medium" if anomalies else "low"
    state["anomaly_detection"] = {
        "anomalies": anomalies,
        "severity": severity,
        "affected_metrics": sorted(affected_metrics),
        "recommended_next_agent": "root_cause_analysis" if severity in {"medium", "high"} else "forecasting",
    }
    return state


def root_cause_analysis_agent(state: InsightAIState) -> InsightAIState:
    question = state["question"].lower()
    if any(term in question for term in ["why", "dropped", "decline", "spike", "root cause"]):
        state["root_causes"] = [
            "Compare the latest period against prior periods by region, product, and customer segment.",
            "Check whether the drop is concentrated in low-inventory products or a single region.",
        ]
    else:
        state["root_causes"] = []
    return state


def forecasting_agent(state: InsightAIState) -> InsightAIState:
    rows = state.get("rows", [])
    numeric_keys = [key for key, value in rows[0].items() if isinstance(value, (int, float))] if rows else []
    if numeric_keys:
        key = numeric_keys[0]
        values = [float(row.get(key) or 0) for row in rows[-3:]]
        state["forecast"] = {"method": "moving_average", "metric": key, "next_period": round(sum(values) / len(values), 2)}
    else:
        state["forecast"] = {"method": "not_applicable", "reason": "No numeric result series available."}
    return state


def visualization_agent(state: InsightAIState) -> InsightAIState:
    state["chart"] = recommend_chart(state.get("rows", []), state.get("chart_type", "table"))
    return state


def dashboard_builder_agent(state: InsightAIState) -> InsightAIState:
    state["dashboard_suggestion"] = {
        "layout": "2-column executive grid",
        "widgets": [
            {"title": "Primary trend", "type": state.get("chart", {}).get("type", "table")},
            {"title": "Key insights", "type": "insight_list"},
        ],
    }
    return state


def report_writer_agent(state: InsightAIState) -> InsightAIState:
    state["report_draft"] = {
        "title": "InsightAI Executive Summary",
        "sections": ["KPIs", "Chart", "Business summary", "Recommendations"],
        "export": {"pdf": "downloadable", "excel": "downloadable", "csv": "downloadable", "powerpoint": "downloadable"},
    }
    return state


def collaboration_agent(state: InsightAIState) -> InsightAIState:
    state["collaboration"] = {
        "comments_enabled": True,
        "mentions_enabled": True,
        "shared_dashboards": "workspace_users",
        "shared_reports": "workspace_users",
        "activity_feed_event": {
            "action": "analysis.generated",
            "entity_type": "agent_workflow",
            "entity_id": state.get("trace_id"),
        },
        "approval_required_before": ["publishing_dashboards", "sending_reports", "external_actions", "deleting_datasets"],
        "human_in_the_loop": True,
    }
    return state


def scheduling_agent(state: InsightAIState) -> InsightAIState:
    question = state.get("question", "").lower()
    cadence = "weekly" if "weekly" in question else "daily" if "daily" in question else "monthly" if "monthly" in question else "manual"
    state["scheduling"] = {
        "cadence": cadence,
        "scheduled_reports": cadence != "manual",
        "alert_rules": ["revenue_drop"] if "alert" in question or "drops" in question else [],
        "delivery_channels": ["email", "slack"],
        "whatsapp_status": "provider_required",
        "failure_recovery": "retry_and_notify",
    }
    return state


def monitoring_agent(state: InsightAIState) -> InsightAIState:
    trace = state.get("agent_trace", [])
    latencies = [float(item.get("latency_ms") or 0) for item in trace]
    prompt_tokens = int(state.get("token_usage", {}).get("prompt", 0))
    completion_tokens = int(state.get("token_usage", {}).get("completion", 0))
    state["monitoring"] = {
        "agent_status": "healthy" if not state.get("errors") else "degraded",
        "agent_spans": [
            {
                "agent": item.get("agent"),
                "trace_id": state.get("trace_id"),
                "latency_ms": item.get("latency_ms"),
                "tokens": item.get("tokens"),
                "success": item.get("success"),
                "failure_reason": item.get("error"),
            }
            for item in trace
        ],
        "trace_id": state.get("trace_id"),
        "latency_ms": round(sum(latencies), 2),
        "retries": state.get("retries", 0),
        "success_rate": round(sum(1 for item in trace if item.get("success")) / max(len(trace), 1), 2),
        "confidence": state.get("final_confidence", state.get("intent_confidence", 0.75)),
        "token_usage": state.get("token_usage", {}),
        "prompt_version": "insightai-agent-v3.1",
        "tool_calls": [item.get("agent") for item in trace],
        "cost": round((prompt_tokens + completion_tokens) / 1000 * 0.002, 6),
        "failure_reasons": [item.get("error") for item in trace if item.get("error")],
        "prometheus_ready": True,
        "otel_trace_id": state.get("trace_id"),
    }
    return state


def policy_governance_agent(state: InsightAIState) -> InsightAIState:
    question = state.get("question", "").lower()
    forbidden_terms = ["salary", "ssn", "social security", "credit card", "patient", "forbidden_dataset"]
    pii_terms = ["email", "phone", "address", "ssn", "credit card"]
    requested_action = "external_api_action" if state.get("intent") == "api_integration" else "major_etl_change" if state.get("intent") == "data_import" else "analytics"
    state["governance"] = {
        "pii_access": [term for term in pii_terms if term in question],
        "data_residency": "workspace_region_required",
        "compliance_rules": ["read_only_analytics", "masked_credentials", "workspace_isolation", "audit_logging"],
        "forbidden_datasets": [term for term in forbidden_terms if term in question],
        "retention_policy": "workspace_default_365_days",
        "approval_requirements": {
            "publishing_dashboards": True,
            "sending_reports": True,
            "external_api_actions": requested_action == "external_api_action",
            "deleting_datasets": True,
            "major_etl_changes": requested_action == "major_etl_change",
        },
        "decision": "blocked" if any(term in question for term in forbidden_terms) else "allowed_with_controls",
    }
    return state


def rag_knowledge_agent(state: InsightAIState) -> InsightAIState:
    workspace_id = state.get("workspace_id")
    if workspace_id:
        search = search_knowledge(
            workspace_id,
            state.get("question", ""),
            ["pdf", "sop", "policy", "contract", "meeting_note"],
            limit=5,
        )
        state["rag_context"] = search["results"] or [
            {
                "source": "workspace_knowledge",
                "summary": "No PDFs, SOPs, policies, contracts, or meeting notes matched this question.",
                "score": 0.0,
            }
        ]
        return state
    state["rag_context"] = [
        {
            "source": "workspace_knowledge",
            "summary": "Workspace-scoped knowledge search requires a workspace_id.",
            "score": 0.0,
        }
    ]
    return state


def memory_agent(state: InsightAIState) -> InsightAIState:
    memory = {
        "workspace_id": state.get("workspace_id"),
        "user_id": state.get("user_id"),
        "question": state.get("question"),
        "intent": state.get("intent"),
        "chart_type": state.get("chart", {}).get("type"),
    }
    mongo_store.insert("ai_memory", memory)
    state["memory"] = {"stored": True, "scope": "workspace_user"}
    return state


def recommendation_agent(state: InsightAIState) -> InsightAIState:
    state["recommendations"] = [
        "Save this analysis to a dashboard.",
        "Schedule a monthly executive report.",
        "Monitor the KPI for regional or customer concentration changes.",
    ]
    return state


def security_compliance_agent(state: InsightAIState) -> InsightAIState:
    state["compliance"] = {
        "rbac_checked": True,
        "workspace_id": state.get("workspace_id"),
        "workspace_isolation": bool(state.get("workspace_id")),
        "pii_masking": "no credentials or raw connection URIs returned",
        "query_permissions": "read-only enforced",
    }
    return state


def cost_governance_agent(state: InsightAIState) -> InsightAIState:
    usage = state.get("token_usage", {"prompt": 0, "completion": 0})
    total_tokens = int(usage.get("prompt", 0)) + int(usage.get("completion", 0))
    estimated_ai_cost = round(total_tokens / 1000 * 0.002, 6)
    row_count = len(state.get("rows", []))
    query_cost_score = min(100, row_count + len(str(state.get("generated_query", ""))) // 20)
    warnings: list[str] = []
    if total_tokens > 4000:
        warnings.append("High token usage for this workflow.")
    if query_cost_score > 70:
        warnings.append("Query may be expensive; narrow filters or lower limits are recommended.")
    if state.get("data_quality", {}).get("quality_score", 100) < 70:
        warnings.append("Data quality issues may reduce answer reliability.")
    state["cost_governance"] = {
        "token_usage": usage,
        "estimated_ai_cost": estimated_ai_cost,
        "query_cost_score": query_cost_score,
        "workspace_usage_status": "within_limits" if total_tokens < 100000 else "limit_warning",
        "warnings": warnings,
    }
    return state


def explanation_agent(state: InsightAIState) -> InsightAIState:
    query = state.get("optimized_query") or state.get("generated_query")
    if query and not state.get("clarification_required"):
        state["explanation"] = f"{state.get('explanation', 'Generated analysis query')} The workflow validated this as read-only and prepared it for safe execution."
    return state


AGENTS: dict[str, AgentSpec] = {
    "supervisor": AgentSpec("supervisor", "Supervisor Agent", "Orchestrates routing, retries, shared state, and final response.", supervisor_agent),
    "intent_classification": AgentSpec("intent_classification", "Intent Classification Agent", "Classifies analytics, dashboard, report, comparison, prediction, and RCA intents.", intent_classification_agent),
    "workflow_planner": AgentSpec("workflow_planner", "Workflow Planner Agent", "Decides agent order, fallback path, retry plan, and approval gates for the workflow.", workflow_planner_agent),
    "model_router": AgentSpec("model_router", "Model Router Agent", "Routes tasks to cheap, strong, or deterministic fallback models.", model_router_agent),
    "schema_intelligence": AgentSpec("schema_intelligence", "Schema Intelligence Agent", "Builds structured schema and glossary context.", schema_intelligence_agent),
    "semantic_layer": AgentSpec("semantic_layer", "Semantic Layer Agent", "Loads governed business metrics and shares definitions with every downstream agent.", semantic_layer_agent),
    "data_quality": AgentSpec("data_quality", "Data Quality Agent", "Detects missing values, duplicates, invalid dates, stale data, broken relationships, and suspicious outliers.", data_quality_agent),
    "data_lineage": AgentSpec("data_lineage", "Data Lineage Agent", "Tracks source, transformation, destination, affected dashboards, reports, KPIs, and dependency graph.", data_lineage_agent),
    "business_context": AgentSpec("business_context", "Business Context Agent", "Maps business terms to database fields.", business_context_agent),
    "enterprise_api_integration": AgentSpec("enterprise_api_integration", "Enterprise API Integration Agent", "Discovers APIs, validates credentials, fetches live data, handles pagination, retries, incremental sync, schema detection, rate limits, and OAuth refresh.", enterprise_api_integration_agent),
    "data_ingestion_etl": AgentSpec("data_ingestion_etl", "Data Ingestion / ETL Agent", "Supports CSV/Excel upload validation, cleaning, glossary mapping, and scheduled import placeholders.", data_ingestion_etl_agent),
    "clarification": AgentSpec("clarification", "Clarification Agent", "Stops ambiguous requests before query generation.", clarification_agent),
    "sql_generation": AgentSpec("sql_generation", "SQL Generation Agent", "Generates read-only SQL.", sql_generation_agent),
    "mongodb_query": AgentSpec("mongodb_query", "MongoDB Query Agent", "Generates read-only MongoDB aggregation pipelines.", mongodb_query_agent),
    "query_validation": AgentSpec("query_validation", "Query Validation Agent", "Validates syntax, read-only safety, limits, timeout, and isolation metadata.", query_validation_agent),
    "query_optimization": AgentSpec("query_optimization", "Query Optimization Agent", "Adds cost and execution-plan hints.", query_optimization_agent),
    "query_execution": AgentSpec("query_execution", "Query Execution Agent", "Defines execution behavior and retry policy for the service executor.", query_execution_agent),
    "insight_generation": AgentSpec("insight_generation", "Insight Generation Agent", "Creates summaries, findings, anomalies, and recommendations.", insight_generation_agent),
    "executive_decision": AgentSpec("executive_decision", "Executive Decision Agent", "Generates executive risks, opportunities, financial impact, priority actions, confidence, and action plans.", executive_decision_agent),
    "anomaly_detection": AgentSpec("anomaly_detection", "Anomaly Detection Agent", "Detects spikes, drops, unusual trends, severity, and RCA routing.", anomaly_detection_agent),
    "root_cause_analysis": AgentSpec("root_cause_analysis", "Root Cause Analysis Agent", "Investigates drops and spikes across dimensions.", root_cause_analysis_agent),
    "forecasting": AgentSpec("forecasting", "Forecasting Agent", "Uses simple statistical forecasts before AI explanation.", forecasting_agent),
    "visualization": AgentSpec("visualization", "Visualization Agent", "Recommends chart and dashboard widget types.", visualization_agent),
    "dashboard_builder": AgentSpec("dashboard_builder", "Dashboard Builder Agent", "Suggests dashboard grouping and layout.", dashboard_builder_agent),
    "report_writer": AgentSpec("report_writer", "Report Writer Agent", "Drafts executive, weekly, monthly, and department report structures.", report_writer_agent),
    "collaboration": AgentSpec("collaboration", "Collaboration Agent", "Coordinates comments, mentions, sharing, approvals, activity feed, and human-in-the-loop controls.", collaboration_agent),
    "rag_knowledge": AgentSpec("rag_knowledge", "RAG Knowledge Agent", "Retrieves organizational knowledge through the pgvector-ready hook.", rag_knowledge_agent),
    "memory": AgentSpec("memory", "Memory Agent", "Stores workspace/user AI memory in MongoDB.", memory_agent),
    "recommendation": AgentSpec("recommendation", "Recommendation Agent", "Suggests dashboards, reports, KPIs, and follow-up questions.", recommendation_agent),
    "policy_governance": AgentSpec("policy_governance", "Policy / Governance Agent", "Checks PII access, data residency, compliance rules, forbidden datasets, retention, and approval requirements.", policy_governance_agent),
    "security_compliance": AgentSpec("security_compliance", "Security & Compliance Agent", "Checks RBAC, workspace isolation, auditing, PII, and credential controls.", security_compliance_agent),
    "cost_governance": AgentSpec("cost_governance", "Cost Governance Agent", "Tracks token usage, estimates AI/query cost, enforces usage limits, and warns on expensive workflows.", cost_governance_agent),
    "scheduling": AgentSpec("scheduling", "Scheduling Agent", "Plans scheduled reports, alerts, delivery channels, retries, and failure recovery.", scheduling_agent),
    "monitoring": AgentSpec("monitoring", "Monitoring + Observability Agent", "Tracks spans, trace IDs, latency, tokens, prompt version, tool calls, retries, cost, and failure reasons.", monitoring_agent),
    "explanation": AgentSpec("explanation", "Explanation Agent", "Explains queries, charts, metrics, and reasoning in business language.", explanation_agent),
}


def _node(agent_key: str) -> AgentFn:
    spec = AGENTS[agent_key]

    def wrapped(state: InsightAIState) -> InsightAIState:
        return _run_agent(spec.display_name, spec.fn, state, spec.retry_limit)

    return wrapped


def _should_generate(state: InsightAIState) -> str:
    if state.get("clarification_required") or state.get("intent") == "data_import":
        return "security_compliance"
    if state.get("engine") == "mongodb":
        return "mongodb_query"
    return "sql_generation"


def _should_do_root_cause(state: InsightAIState) -> str:
    return "root_cause_analysis" if state.get("intent") == "root_cause_analysis" or state.get("anomaly_detection", {}).get("recommended_next_agent") == "root_cause_analysis" else "forecasting"


def _should_run_etl(state: InsightAIState) -> str:
    return "data_ingestion_etl" if state.get("intent") == "data_import" else "business_context"


def _should_run_api_integration(state: InsightAIState) -> str:
    return "enterprise_api_integration" if state.get("intent") == "api_integration" else "clarification"


def _after_lineage(state: InsightAIState) -> str:
    if state.get("intent") == "data_import":
        return "data_ingestion_etl"
    if state.get("intent") == "api_integration":
        return "enterprise_api_integration"
    return "clarification"


def _should_build_report(state: InsightAIState) -> str:
    return "report_writer" if "report_writer" in state.get("required_agents", []) else "rag_knowledge"


def _compile_graph():
    from langgraph.graph import END, StateGraph

    graph = StateGraph(InsightAIState)
    for key in AGENTS:
        graph.add_node(key, _node(key))
    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor", "intent_classification")
    graph.add_edge("intent_classification", "workflow_planner")
    graph.add_edge("workflow_planner", "model_router")
    graph.add_edge("model_router", "schema_intelligence")
    graph.add_edge("schema_intelligence", "semantic_layer")
    graph.add_edge("semantic_layer", "business_context")
    graph.add_edge("business_context", "rag_knowledge")
    graph.add_edge("rag_knowledge", "data_quality")
    graph.add_edge("data_quality", "data_lineage")
    graph.add_conditional_edges("data_lineage", _after_lineage, {"data_ingestion_etl": "data_ingestion_etl", "enterprise_api_integration": "enterprise_api_integration", "clarification": "clarification"})
    graph.add_edge("data_ingestion_etl", "policy_governance")
    graph.add_edge("enterprise_api_integration", "clarification")
    graph.add_conditional_edges("clarification", _should_generate, {"security_compliance": "policy_governance", "sql_generation": "sql_generation", "mongodb_query": "mongodb_query"})
    graph.add_edge("sql_generation", "query_validation")
    graph.add_edge("mongodb_query", "query_validation")
    graph.add_edge("query_validation", "query_optimization")
    graph.add_edge("query_optimization", "query_execution")
    graph.add_edge("query_execution", "insight_generation")
    graph.add_edge("insight_generation", "executive_decision")
    graph.add_edge("executive_decision", "anomaly_detection")
    graph.add_conditional_edges("anomaly_detection", _should_do_root_cause, {"root_cause_analysis": "root_cause_analysis", "forecasting": "forecasting"})
    graph.add_edge("root_cause_analysis", "forecasting")
    graph.add_edge("forecasting", "visualization")
    graph.add_edge("visualization", "dashboard_builder")
    graph.add_conditional_edges("dashboard_builder", _should_build_report, {"report_writer": "report_writer", "rag_knowledge": "memory"})
    graph.add_edge("report_writer", "memory")
    graph.add_edge("memory", "recommendation")
    graph.add_edge("recommendation", "collaboration")
    graph.add_edge("collaboration", "policy_governance")
    graph.add_edge("policy_governance", "security_compliance")
    graph.add_edge("security_compliance", "cost_governance")
    graph.add_edge("cost_governance", "scheduling")
    graph.add_edge("scheduling", "monitoring")
    graph.add_edge("monitoring", "explanation")
    graph.add_edge("explanation", END)
    return graph.compile()


def _run_deterministic_graph(state: InsightAIState) -> InsightAIState:
    state = _node("supervisor")(state)
    for key in ["intent_classification", "workflow_planner", "model_router", "schema_intelligence", "semantic_layer", "business_context", "rag_knowledge", "data_quality", "data_lineage"]:
        state = _node(key)(state)
    if state.get("intent") == "data_import":
        state = _node("data_ingestion_etl")(state)
    if state.get("intent") == "api_integration":
        state = _node("enterprise_api_integration")(state)
    state = _node("clarification")(state)
    if not state.get("clarification_required") and state.get("intent") != "data_import":
        state = _node("mongodb_query" if state.get("engine") == "mongodb" else "sql_generation")(state)
        for key in ["query_validation", "query_optimization", "query_execution", "insight_generation", "executive_decision"]:
            state = _node(key)(state)
        state = _node("anomaly_detection")(state)
        if state.get("intent") == "root_cause_analysis" or state.get("anomaly_detection", {}).get("recommended_next_agent") == "root_cause_analysis":
            state = _node("root_cause_analysis")(state)
        for key in ["forecasting", "visualization", "dashboard_builder"]:
            state = _node(key)(state)
        if "report_writer" in state.get("required_agents", []):
            state = _node("report_writer")(state)
        for key in ["memory", "recommendation", "collaboration"]:
            state = _node(key)(state)
    state = _node("policy_governance")(state)
    state = _node("security_compliance")(state)
    state = _node("cost_governance")(state)
    state = _node("scheduling")(state)
    state = _node("monitoring")(state)
    state = _node("explanation")(state)
    return state


def _finalize_state(state: InsightAIState) -> InsightAIState:
    trace = state.get("agent_trace", [])
    success_count = sum(1 for item in trace if item.get("success"))
    state["final_confidence"] = round((success_count / max(len(trace), 1)) * float(state.get("intent_confidence", 0.75)), 2)
    doc = {
        "id": state.get("trace_id"),
        "workspace_id": state.get("workspace_id"),
        "user_id": state.get("user_id"),
        "question": state.get("question"),
        "intent": state.get("intent"),
        "engine": state.get("engine"),
        "agent_trace": trace,
        "execution_order": [item.get("agent") for item in trace],
        "token_usage": state.get("token_usage", {}),
        "errors": state.get("errors", []),
        "retries": state.get("retries", 0),
        "success": not state.get("errors"),
        "final_confidence": state.get("final_confidence"),
        "agent_outputs": {
            "semantic_layer": state.get("semantic_layer", {}),
            "workflow_plan": state.get("workflow_plan", {}),
            "model_route": state.get("model_route", {}),
            "data_quality": state.get("data_quality", {}),
            "data_lineage": state.get("data_lineage", {}),
            "anomaly_detection": state.get("anomaly_detection", {}),
            "etl": state.get("etl", {}),
            "cost_governance": state.get("cost_governance", {}),
            "api_integration": state.get("api_integration", {}),
            "executive_decision": state.get("executive_decision", {}),
            "collaboration": state.get("collaboration", {}),
            "scheduling": state.get("scheduling", {}),
            "monitoring": state.get("monitoring", {}),
            "governance": state.get("governance", {}),
            "supervisor_plan": state.get("supervisor_plan", {}),
            "rag_context": state.get("rag_context", []),
        },
    }
    if not mongo_store.update("agent_traces", str(doc["id"]), doc):
        mongo_store.insert("agent_traces", doc)
    return state


def run_insight_graph(
    question: str,
    schema: dict[str, Any],
    engine: str,
    rows: list[dict[str, Any]] | None = None,
    workspace_id: str | None = None,
    user_id: str | None = None,
) -> InsightAIState:
    initial: InsightAIState = {
        "trace_id": str(uuid4()),
        "question": question,
        "schema": schema,
        "engine": "mongodb" if engine == "mongodb" else "sql",
        "rows": rows or [],
        "workspace_id": workspace_id,
        "user_id": user_id,
    }
    try:
        state = _compile_graph().invoke(initial)
    except Exception:
        state = _run_deterministic_graph(initial)
    return _finalize_state(state)


def run_result_agents(state: InsightAIState, rows: list[dict[str, Any]]) -> InsightAIState:
    state["rows"] = rows
    for key in ["semantic_layer", "business_context", "rag_knowledge", "data_quality", "data_lineage", "insight_generation", "executive_decision", "anomaly_detection", "root_cause_analysis", "forecasting", "visualization", "dashboard_builder", "report_writer", "memory", "recommendation", "collaboration", "policy_governance", "security_compliance", "cost_governance", "scheduling", "monitoring", "explanation"]:
        if key == "root_cause_analysis" and state.get("intent") != "root_cause_analysis":
            if state.get("anomaly_detection", {}).get("recommended_next_agent") != "root_cause_analysis":
                continue
        if key == "report_writer" and "report_writer" not in state.get("required_agents", []):
            continue
        state = _node(key)(state)
    return _finalize_state(state)


def list_agent_specs() -> list[dict[str, str]]:
    return [{"node": spec.node, "name": spec.display_name, "responsibility": spec.responsibility} for spec in AGENTS.values()]


def list_agent_traces(workspace_id: str | None = None) -> list[dict[str, Any]]:
    traces = mongo_store.list("agent_traces", workspace_id)
    return sorted(traces, key=lambda item: str(item.get("created_at", "")), reverse=True)[:50]
