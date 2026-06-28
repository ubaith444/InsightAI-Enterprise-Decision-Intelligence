from app.ai.langgraph_workflow import list_agent_specs, list_agent_traces, run_insight_graph
from app.models import ConnectionKind, DatabaseConnection
from app.services.query_execution import execute_mongo


def test_langgraph_workflow_runs_named_agents_and_validates_query():
    state = run_insight_graph(
        "Show monthly revenue trend for the last 12 months",
        {"engine": "sqlite", "tables": [{"name": "sales"}]},
        "sql",
        rows=[{"order_month": "2026-06", "revenue": 100}],
    )
    assert state["safe"] is True
    assert state["generated_query"].lower().startswith("select")
    assert state["insights"]["summary"]
    assert state["chart"]["type"] in {"line", "bar", "table", "area", "pie", "donut", "kpi", "map"}
    assert state["schema_summary"]["assets"] == ["sales"]
    assert len(list_agent_specs()) == 35
    assert state["agent_trace"]
    assert state["final_confidence"] > 0
    assert any(item["agent"] == "Supervisor Agent" for item in state["agent_trace"])
    assert any(trace["id"] == state["trace_id"] for trace in list_agent_traces())
    assert state["data_quality"]["quality_score"] > 0
    assert state["workflow_plan"]["fallback_path"]
    assert state["model_route"]["selected_model"]
    assert state["semantic_layer"]["metric_count"] >= 4
    assert state["data_lineage"]["dependency_graph"]["nodes"]
    assert state["governance"]["decision"] == "allowed_with_controls"
    assert state["collaboration"]["human_in_the_loop"] is True
    assert state["scheduling"]["failure_recovery"] == "retry_and_notify"
    assert state["monitoring"]["prometheus_ready"] is True
    assert state["monitoring"]["agent_spans"]
    execution_order = [item["agent"] for item in state["agent_trace"]]
    assert execution_order.index("RAG Knowledge Agent") < execution_order.index("SQL Generation Agent")
    assert state["cost_governance"]["workspace_usage_status"] == "within_limits"


def test_supervisor_routes_ambiguous_prompt_to_clarification_without_query():
    state = run_insight_graph(
        "Show best customers",
        {"engine": "sqlite", "tables": [{"name": "sales"}]},
        "sql",
        workspace_id="workspace",
        user_id="user",
    )
    assert state["clarification_required"] is True
    assert "rank customers" in state["clarification_question"]
    assert state.get("generated_query") in (None, "")
    assert any(item["agent"] == "Clarification Agent" for item in state["agent_trace"])


def test_data_quality_agent_detects_missing_duplicates_dates_and_outliers():
    rows = [
        {"order_date": "2026-06-01", "customer_id": "A", "revenue": 10},
        {"order_date": "not-a-date", "customer_id": "A", "revenue": 10},
        {"order_date": "", "customer_id": None, "revenue": 500},
        {"order_date": "not-a-date", "customer_id": "A", "revenue": 10},
    ]
    state = run_insight_graph(
        "Show revenue anomaly by customer",
        {
            "engine": "sqlite",
            "tables": [{"name": "sales", "columns": [{"name": "customer_id", "nullable": True}, {"name": "order_date", "nullable": False}]}],
        },
        "sql",
        rows=rows,
        workspace_id="workspace",
        user_id="user",
    )
    issue_types = {issue["type"] for issue in state["data_quality"]["issues"]}
    assert {"missing_values", "duplicate_records", "invalid_dates", "suspicious_outliers"}.issubset(issue_types)
    assert state["data_quality"]["quality_score"] < 100


def test_anomaly_detection_agent_routes_to_root_cause_when_severity_requires_it():
    state = run_insight_graph(
        "Explain why revenue spiked last month",
        {"engine": "sqlite", "tables": [{"name": "sales"}]},
        "sql",
        rows=[{"month": "2026-04", "revenue": 100}, {"month": "2026-05", "revenue": 120}, {"month": "2026-06", "revenue": 700}],
    )
    assert state["anomaly_detection"]["severity"] in {"medium", "high"}
    assert state["anomaly_detection"]["recommended_next_agent"] == "root_cause_analysis"
    assert state["root_causes"]
    assert any(item["agent"] == "Anomaly Detection Agent" for item in state["agent_trace"])


def test_etl_agent_runs_only_for_import_upload_sync_intents():
    import_state = run_insight_graph(
        "Upload a CSV of new sales and map columns",
        {"engine": "sqlite", "tables": [{"name": "sales"}]},
        "sql",
        workspace_id="workspace",
        user_id="user",
    )
    analytics_state = run_insight_graph(
        "Show monthly revenue trend",
        {"engine": "sqlite", "tables": [{"name": "sales"}]},
        "sql",
    )
    assert import_state["intent"] == "data_import"
    assert import_state["etl"]["source_type"] == "csv"
    assert import_state.get("generated_query") in (None, "")
    assert any(item["agent"] == "Data Ingestion / ETL Agent" for item in import_state["agent_trace"])
    assert "etl" not in analytics_state or analytics_state["etl"] == {}


def test_cost_governance_output_is_persisted_in_agent_trace():
    state = run_insight_graph(
        "Find top 10 customers by revenue",
        {"engine": "sqlite", "tables": [{"name": "sales"}]},
        "sql",
        rows=[{"customer": "Nimbus", "revenue": 100}],
        workspace_id="governance-workspace",
        user_id="governance-user",
    )
    assert state["cost_governance"]["estimated_ai_cost"] >= 0
    assert state["cost_governance"]["query_cost_score"] >= 0
    persisted = next(trace for trace in list_agent_traces("governance-workspace") if trace["id"] == state["trace_id"])
    assert persisted["agent_outputs"]["cost_governance"]["workspace_usage_status"] == "within_limits"
    assert "data_quality" in persisted["agent_outputs"]


def test_configured_mongodb_connection_executes_real_aggregation(monkeypatch):
    class FakeCollection:
        def aggregate(self, pipeline, maxTimeMS):
            assert pipeline[-1] == {"$limit": 100}
            assert maxTimeMS > 0
            return [{"_id": "internal", "customer": "Nimbus Co", "activity": 42}]

    class FakeDatabase:
        def __getitem__(self, name):
            assert name == "customer_activity"
            return FakeCollection()

    class FakeClient:
        def __init__(self, uri, serverSelectionTimeoutMS):
            assert uri == "mongodb://user:pass@localhost:27017/insightai"
            assert serverSelectionTimeoutMS > 0

        def get_default_database(self):
            return FakeDatabase()

    monkeypatch.setattr("pymongo.MongoClient", FakeClient)
    connection = DatabaseConnection(
        workspace_id="workspace",
        name="Mongo",
        kind=ConnectionKind.mongodb,
        uri="mongodb://user:pass@localhost:27017/insightai",
        selected_assets=["customer_activity"],
        created_by="user",
    )
    rows = execute_mongo([{"$match": {"event": "login"}}], connection)
    assert rows == [{"customer": "Nimbus Co", "activity": 42}]
