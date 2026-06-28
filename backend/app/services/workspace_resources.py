from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.mongo import mongo_store
from app.models import AIUsageLog, DatabaseConnection, QueryLog


DEFAULT_GLOSSARY = [
    {"term": "Revenue", "definition": "Gross sales value before expenses.", "formula": "SUM(sales.revenue)"},
    {"term": "Profit", "definition": "Revenue less expenses, or margin proxy when allocation is unavailable.", "formula": "SUM(revenue) - SUM(expenses)"},
    {"term": "Gross Margin", "definition": "Revenue retained after cost of goods sold.", "formula": "(SUM(revenue) - SUM(cogs)) / NULLIF(SUM(revenue), 0)"},
    {"term": "Net Margin", "definition": "Profit retained after all expenses.", "formula": "SUM(profit) / NULLIF(SUM(revenue), 0)"},
    {"term": "MRR", "definition": "Monthly recurring revenue from active subscriptions.", "formula": "SUM(subscription_monthly_amount) WHERE status = 'active'"},
    {"term": "ARR", "definition": "Annualized recurring revenue.", "formula": "MRR * 12"},
    {"term": "Customer Lifetime Value", "definition": "Expected gross profit from a customer relationship.", "formula": "average_order_value * purchase_frequency * gross_margin * customer_lifespan"},
    {"term": "Customer Acquisition Cost", "definition": "Sales and marketing spend required to acquire a customer.", "formula": "SUM(acquisition_spend) / NULLIF(new_customers, 0)"},
    {"term": "Churn", "definition": "Customers or revenue lost in a selected period.", "formula": "churned_customers / NULLIF(starting_customers, 0)"},
    {"term": "Retention", "definition": "Share of customers retained through the selected period.", "formula": "retained_customers / NULLIF(starting_customers, 0)"},
    {"term": "Inventory Turnover", "definition": "How often inventory is sold and replenished.", "formula": "cost_of_goods_sold / NULLIF(average_inventory, 0)"},
    {"term": "Conversion Rate", "definition": "Share of visitors or leads that complete the target action.", "formula": "conversions / NULLIF(total_visitors_or_leads, 0)"},
    {"term": "Average Order Value", "definition": "Average revenue per order.", "formula": "SUM(order_revenue) / NULLIF(COUNT(order_id), 0)"},
    {"term": "Return Rate", "definition": "Share of orders returned by customers.", "formula": "returned_orders / NULLIF(total_orders, 0)"},
    {"term": "Active customer", "definition": "Customer with orders or activity in the selected period.", "formula": "last_active >= period_start"},
    {"term": "Churned customer", "definition": "Previously active customer with no recent activity after threshold.", "formula": "last_active < churn_threshold"},
    {"term": "High-value customer", "definition": "Customer above lifetime value threshold.", "formula": "lifetime_value >= workspace_threshold"},
    {"term": "Monthly recurring revenue", "definition": "Recurring revenue grouped by month.", "formula": "SUM(recurring_revenue) BY month"},
]

DEFAULT_PROMPTS = [
    "Monthly sales trend",
    "Top customers",
    "Low inventory products",
    "Regional performance",
]

DEFAULT_KNOWLEDGE_DOCUMENTS = [
    {
        "title": "Revenue Recognition Policy",
        "document_type": "policy",
        "content": "Revenue is recognized when an order is closed and delivery obligations are satisfied. Monthly revenue should reconcile against closed orders and approved credits.",
        "tags": ["revenue", "policy", "finance"],
        "source_uri": "demo://policies/revenue-recognition.pdf",
    },
    {
        "title": "Sales Operations SOP",
        "document_type": "sop",
        "content": "Sales operations review pipeline, regional quota attainment, low inventory constraints, and top customer risks every Monday before executive reporting.",
        "tags": ["sales", "sop", "operations"],
        "source_uri": "demo://sops/sales-operations.md",
    },
    {
        "title": "Enterprise Customer Contract Template",
        "document_type": "contract",
        "content": "Enterprise contracts define annual recurring revenue, renewal windows, cancellation notice periods, data processing terms, and service-level commitments.",
        "tags": ["contract", "enterprise", "renewal"],
        "source_uri": "demo://contracts/enterprise-template.pdf",
    },
    {
        "title": "Executive Revenue Review Notes",
        "document_type": "meeting_note",
        "content": "The leadership team noted a June revenue drop in the South region, likely tied to Forecast Hub inventory constraints and delayed customer approvals.",
        "tags": ["meeting", "revenue", "root-cause"],
        "source_uri": "demo://meeting-notes/exec-revenue-review.txt",
    },
    {
        "title": "Security and Data Access Policy",
        "document_type": "pdf",
        "content": "All analytics database connections must be read-only. Credentials must be masked in user interfaces and workspace access must be enforced for every request.",
        "tags": ["security", "pdf", "policy"],
        "source_uri": "demo://pdfs/security-data-access.pdf",
    },
]


def seed_demo_documents(workspace_id: str) -> None:
    if not mongo_store.list("business_glossary", workspace_id):
        for item in DEFAULT_GLOSSARY:
            mongo_store.insert("business_glossary", {"workspace_id": workspace_id, "name": item["term"], "payload": item})
    if not mongo_store.list("semantic_metrics", workspace_id):
        for item in DEFAULT_GLOSSARY:
            mongo_store.insert(
                "semantic_metrics",
                {
                    "workspace_id": workspace_id,
                    "name": item["term"],
                    "definition": item["definition"],
                    "formula": item["formula"],
                    "owner": "Finance" if item["term"] in {"Revenue", "Profit", "Gross Margin", "Net Margin", "MRR", "ARR"} else "Operations",
                    "dimensions": ["month", "region", "customer_segment"],
                    "tags": ["semantic-layer", item["term"].lower().replace(" ", "-")],
                    "payload": item,
                },
            )
    if not mongo_store.list("saved_prompts", workspace_id):
        for prompt in DEFAULT_PROMPTS:
            mongo_store.insert("saved_prompts", {"workspace_id": workspace_id, "name": prompt, "payload": {"question": prompt}})
    if not mongo_store.list("dashboards", workspace_id):
        mongo_store.insert(
            "dashboards",
            {
                "workspace_id": workspace_id,
                "name": "Demo Executive Dashboard",
                "widgets": [
                    {"title": "Monthly revenue", "type": "line", "query": "Show monthly revenue trend"},
                    {"title": "Regional performance", "type": "bar", "query": "Compare sales by region"},
                    {"title": "Low inventory", "type": "table", "query": "Show low inventory products"},
                ],
                "shared_with": [],
                "payload": {"demo": True},
            },
        )
    if not mongo_store.list("reports", workspace_id):
        mongo_store.insert(
            "reports",
            {
                "workspace_id": workspace_id,
                "title": "Demo Monthly Executive Report",
                "report_type": "monthly",
                "sections": [{"title": "Revenue"}, {"title": "Inventory"}, {"title": "Expenses"}],
                "payload": {"export": {"pdf": "placeholder", "excel": "placeholder", "powerpoint": "placeholder"}},
            },
        )
    if not mongo_store.list("knowledge_documents", workspace_id):
        for item in DEFAULT_KNOWLEDGE_DOCUMENTS:
            mongo_store.insert("knowledge_documents", {"workspace_id": workspace_id, "name": item["title"], "payload": item, **item})


def list_resource(collection: str, workspace_id: str) -> list[dict[str, Any]]:
    return mongo_store.list(collection, workspace_id)


def create_resource(collection: str, workspace_id: str, name: str, payload: dict[str, Any]) -> dict[str, Any]:
    return mongo_store.insert(collection, {"workspace_id": workspace_id, "name": name, "payload": payload})


def update_resource(collection: str, workspace_id: str, resource_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
    existing = mongo_store.get(collection, resource_id)
    if not existing or existing.get("workspace_id") != workspace_id:
        return None
    return mongo_store.update(collection, resource_id, patch)


def delete_resource(collection: str, workspace_id: str, resource_id: str) -> bool:
    existing = mongo_store.get(collection, resource_id)
    if not existing or existing.get("workspace_id") != workspace_id:
        return False
    return mongo_store.delete(collection, resource_id)


def semantic_layer(workspace_id: str) -> dict[str, Any]:
    metrics = mongo_store.list("semantic_metrics", workspace_id)
    if not metrics:
        seed_demo_documents(workspace_id)
        metrics = mongo_store.list("semantic_metrics", workspace_id)
    return {
        "workspace_id": workspace_id,
        "metrics": metrics,
        "metric_count": len(metrics),
        "consumed_by_agents": True,
        "version": max((str(item.get("updated_at") or item.get("created_at")) for item in metrics), default="initial"),
    }


def create_semantic_metric(workspace_id: str, name: str, definition: str, formula: str, owner: str | None, dimensions: list[str], tags: list[str]) -> dict[str, Any]:
    return mongo_store.insert(
        "semantic_metrics",
        {
            "workspace_id": workspace_id,
            "name": name,
            "definition": definition,
            "formula": formula,
            "owner": owner or "Analytics",
            "dimensions": dimensions,
            "tags": tags,
            "payload": {"definition": definition, "formula": formula},
        },
    )


def create_notification(workspace_id: str, title: str, message: str, level: str, payload: dict[str, Any]) -> dict[str, Any]:
    return mongo_store.insert("notifications", {"workspace_id": workspace_id, "title": title, "message": message, "level": level, "read": False, "payload": payload})


def create_scheduled_report(workspace_id: str, name: str, cadence: str, report_type: str, delivery_channels: list[str], payload: dict[str, Any]) -> dict[str, Any]:
    return mongo_store.insert(
        "scheduled_reports",
        {
            "workspace_id": workspace_id,
            "name": name,
            "cadence": cadence,
            "report_type": report_type,
            "delivery_channels": delivery_channels or ["email"],
            "status": "scheduled",
            "delivery_status": {channel: "ready" if channel in {"email", "slack"} else "provider_required" for channel in (delivery_channels or ["email"])},
            "next_run_at": payload.get("next_run_at") if isinstance(payload, dict) else None,
            "payload": payload,
        },
    )


def create_export(workspace_id: str, export_format: str, source_type: str, source_id: str | None, rows: list[dict[str, Any]]) -> dict[str, Any]:
    extension = {"csv": "csv", "excel": "xlsx", "pdf": "pdf", "powerpoint": "pptx"}.get(export_format, export_format)
    return mongo_store.insert(
        "exports",
        {
            "workspace_id": workspace_id,
            "name": f"{source_type}-{uuid4().hex[:8]}.{extension}",
            "format": export_format,
            "source_type": source_type,
            "source_id": source_id,
            "row_count": len(rows),
            "status": "ready",
            "download_url": f"/exports/{workspace_id}/{uuid4().hex}.{extension}",
            "payload": {"rows_preview": rows[:5]},
        },
    )


def create_comment(workspace_id: str, target_type: str, target_id: str, user_id: str, body: str, mentions: list[str]) -> dict[str, Any]:
    comment = mongo_store.insert(
        "comments",
        {
            "workspace_id": workspace_id,
            "target_type": target_type,
            "target_id": target_id,
            "user_id": user_id,
            "body": body,
            "mentions": mentions,
            "resolved": False,
        },
    )
    record_activity(workspace_id, user_id, "comment.created", target_type, target_id, {"comment_id": comment["id"]})
    return comment


def list_comments(workspace_id: str, target_type: str | None = None, target_id: str | None = None) -> list[dict[str, Any]]:
    comments = mongo_store.list("comments", workspace_id)
    return [
        item
        for item in comments
        if (target_type is None or item.get("target_type") == target_type) and (target_id is None or item.get("target_id") == target_id)
    ]


def record_activity(workspace_id: str, user_id: str | None, action: str, entity_type: str, entity_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    return mongo_store.insert(
        "activity_feed",
        {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "payload": payload,
        },
    )


def request_approval(workspace_id: str, user_id: str, target_type: str, target_id: str, action: str, reason: str) -> dict[str, Any]:
    approval = mongo_store.insert(
        "approvals",
        {
            "workspace_id": workspace_id,
            "requested_by": user_id,
            "target_type": target_type,
            "target_id": target_id,
            "action": action,
            "reason": reason,
            "status": "pending",
            "human_in_the_loop": True,
        },
    )
    record_activity(workspace_id, user_id, "approval.requested", target_type, target_id, {"approval_id": approval["id"], "action": action})
    return approval


def data_lineage(db: Session, workspace_id: str) -> dict[str, Any]:
    connections = db.query(DatabaseConnection).filter(DatabaseConnection.workspace_id == workspace_id).all()
    dashboards = mongo_store.list("dashboards", workspace_id)
    reports = mongo_store.list("reports", workspace_id)
    metrics = mongo_store.list("semantic_metrics", workspace_id)
    nodes = []
    edges = []
    column_level_lineage = []
    sql_lineage = []
    transformation_history = []
    for connection in connections:
        source_id = f"source:{connection.id}"
        nodes.append({"id": source_id, "type": "source", "label": connection.name, "kind": connection.kind.value})
        for asset in connection.selected_assets or ["selected_asset"]:
            for metric in metrics[:8]:
                column_level_lineage.append(
                    {
                        "source": connection.name,
                        "source_column": f"{asset}.{str(metric.get('name', 'metric')).lower().replace(' ', '_')}",
                        "semantic_metric": metric.get("name"),
                        "downstream_dashboards": [item.get("name") for item in dashboards],
                        "downstream_reports": [item.get("title") or item.get("name") for item in reports],
                    }
                )
        for metric in metrics[:8]:
            metric_id = f"metric:{metric['id']}"
            if not any(item["id"] == metric_id for item in nodes):
                nodes.append({"id": metric_id, "type": "kpi", "label": metric["name"]})
            edges.append({"from": source_id, "to": metric_id, "relationship": "feeds"})
            sql_lineage.append(
                {
                    "query_pattern": str(metric.get("formula", "")),
                    "source": connection.name,
                    "selected_assets": connection.selected_assets,
                    "metric": metric.get("name"),
                }
            )
        transformation_history.append(
            {
                "source": connection.name,
                "steps": ["ingest_or_query", "semantic_mapping", "quality_check", "safe_execution", "presentation"],
                "last_observed_at": connection.created_at,
            }
        )
    for dashboard in dashboards:
        dashboard_id = f"dashboard:{dashboard['id']}"
        nodes.append({"id": dashboard_id, "type": "dashboard", "label": dashboard.get("name")})
        for metric in metrics[:4]:
            edges.append({"from": f"metric:{metric['id']}", "to": dashboard_id, "relationship": "visualized_in"})
    for report in reports:
        report_id = f"report:{report['id']}"
        nodes.append({"id": report_id, "type": "report", "label": report.get("title") or report.get("name")})
        for dashboard in dashboards[:3]:
            edges.append({"from": f"dashboard:{dashboard['id']}", "to": report_id, "relationship": "included_in"})
    graph = {
        "workspace_id": workspace_id,
        "nodes": nodes,
        "edges": edges,
        "affected_dashboards": [item.get("name") for item in dashboards],
        "affected_reports": [item.get("title") or item.get("name") for item in reports],
        "affected_kpis": [item.get("name") for item in metrics],
        "column_level_lineage": column_level_lineage,
        "sql_lineage": sql_lineage,
        "transformation_history": transformation_history,
        "impact_analysis": {
            "dashboard_count": len(dashboards),
            "report_count": len(reports),
            "kpi_count": len(metrics),
            "high_impact_assets": [item.get("name") for item in dashboards[:3]] + [item.get("title") or item.get("name") for item in reports[:3]],
        },
        "generated_at": datetime.utcnow(),
    }
    mongo_store.insert("data_lineage", graph)
    return graph


def source_health(db: Session, workspace_id: str) -> list[dict[str, Any]]:
    connections = db.query(DatabaseConnection).filter(DatabaseConnection.workspace_id == workspace_id).all()
    logs = db.query(QueryLog).filter(QueryLog.workspace_id == workspace_id).all()
    failed = [log for log in logs if log.status == "failed"]
    return [
        {
            "connection_id": item.id,
            "name": item.name,
            "status": "connected" if item.is_read_only else "review_required",
            "last_successful_sync": item.created_at,
            "last_failed_query": failed[-1].created_at if failed else None,
            "average_response_time_ms": 120 + len(logs) * 3,
            "error_rate": round(len(failed) / max(len(logs), 1), 2),
        }
        for item in connections
    ]


def usage_analytics(db: Session, workspace_id: str) -> dict[str, Any]:
    prompt_tokens = db.query(func.coalesce(func.sum(AIUsageLog.prompt_tokens), 0)).filter(AIUsageLog.workspace_id == workspace_id).scalar()
    completion_tokens = db.query(func.coalesce(func.sum(AIUsageLog.completion_tokens), 0)).filter(AIUsageLog.workspace_id == workspace_id).scalar()
    query_logs = db.query(QueryLog).filter(QueryLog.workspace_id == workspace_id)
    return {
        "ai_questions_asked": query_logs.count(),
        "queries_executed": query_logs.filter(QueryLog.status == "executed").count(),
        "dashboards_created": len(mongo_store.list("dashboards", workspace_id)),
        "reports_generated": len(mongo_store.list("reports", workspace_id)),
        "token_usage": {"prompt": int(prompt_tokens or 0), "completion": int(completion_tokens or 0)},
        "failed_queries": query_logs.filter(QueryLog.status == "failed").count(),
        "generated_at": datetime.utcnow(),
    }


def create_knowledge_document(workspace_id: str, title: str, document_type: str, content: str, source_uri: str | None, tags: list[str]) -> dict[str, Any]:
    payload = {
        "title": title,
        "document_type": document_type,
        "content": content,
        "source_uri": source_uri,
        "tags": tags,
    }
    return mongo_store.insert("knowledge_documents", {"workspace_id": workspace_id, "name": title, "payload": payload, **payload})


def search_knowledge(workspace_id: str, query: str, document_types: list[str] | None = None, limit: int = 5) -> dict[str, Any]:
    tokens = {token.strip(".,:;!?()[]{}").lower() for token in query.split() if len(token.strip(".,:;!?()[]{}")) > 2}
    allowed_types = {item.lower() for item in document_types or []}
    results = []
    for doc in mongo_store.list("knowledge_documents", workspace_id):
        doc_type = str(doc.get("document_type") or doc.get("payload", {}).get("document_type", "")).lower()
        if allowed_types and doc_type not in allowed_types:
            continue
        haystack = " ".join(
            [
                str(doc.get("title") or doc.get("name") or ""),
                str(doc.get("content") or doc.get("payload", {}).get("content", "")),
                " ".join(str(tag) for tag in (doc.get("tags") or doc.get("payload", {}).get("tags", []))),
            ]
        ).lower()
        matched = sorted(token for token in tokens if token in haystack)
        if not matched:
            continue
        score = round(len(matched) / max(len(tokens), 1), 2)
        results.append(
            {
                "id": doc.get("id"),
                "title": doc.get("title") or doc.get("name"),
                "document_type": doc_type,
                "summary": str(doc.get("content") or doc.get("payload", {}).get("content", ""))[:240],
                "source_uri": doc.get("source_uri") or doc.get("payload", {}).get("source_uri"),
                "matched_terms": matched,
                "score": score,
            }
        )
    results = sorted(results, key=lambda item: item["score"], reverse=True)[: max(1, min(limit, 20))]
    search = mongo_store.insert("knowledge_searches", {"workspace_id": workspace_id, "name": query[:80], "query": query, "document_types": document_types or [], "result_count": len(results)})
    return {"query": query, "results": results, "search_id": search["id"]}
