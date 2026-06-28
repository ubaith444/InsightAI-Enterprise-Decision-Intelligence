from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models import DatabaseConnection
from app.ai.langgraph_workflow import run_insight_graph
from app.security.crypto import decrypt_secret


def _login_admin(client: TestClient) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": "admin@insightai.ai", "password": "InsightAI123"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _demo_workspace_id(client: TestClient, headers: dict[str, str]) -> str:
    workspaces = client.get("/api/v1/workspaces", headers=headers)
    assert workspaces.status_code == 200
    return next(item["id"] for item in workspaces.json() if item["slug"] == "acme-revenue")


def test_demo_schema_includes_all_business_datasets_and_intelligence():
    with TestClient(app) as client:
        headers = _login_admin(client)
        workspace_id = _demo_workspace_id(client, headers)
        connections = client.get(f"/api/v1/connections?workspace_id={workspace_id}", headers=headers)
        assert connections.status_code == 200
        connection_id = next(item["id"] for item in connections.json() if item["name"] == "Acme Analytics Warehouse")

        schema = client.get(f"/api/v1/connections/{connection_id}/schema", headers=headers)
        assert schema.status_code == 200, schema.text
        table_names = {table["name"] for table in schema.json()["tables"]}
        assert {"sales", "customers", "products", "orders", "employees", "regions", "expenses", "inventory"}.issubset(table_names)
        assert schema.json()["business_glossary"]["revenue"]
        assert schema.json()["metric_definitions"]["regional_performance"]


def test_connection_uri_is_encrypted_at_rest_and_masked_in_api():
    with TestClient(app) as client:
        headers = _login_admin(client)
        workspace_id = _demo_workspace_id(client, headers)
        payload = {
            "workspace_id": workspace_id,
            "name": f"Encrypted Warehouse {uuid4().hex[:6]}",
            "kind": "postgresql",
            "uri": "postgresql://user:secret@localhost:5432/demo",
            "is_read_only": True,
            "selected_assets": ["sales"],
        }
        created = client.post("/api/v1/connections", headers=headers, json=payload)
        assert created.status_code == 200, created.text
        assert "secret" not in str(created.json())
        assert created.json()["masked_uri"] == "postgresql://***:***@localhost:5432/demo"

        with SessionLocal() as db:
            item = db.get(DatabaseConnection, created.json()["id"])
            assert item is not None
            assert item.uri.startswith("enc::")
            assert decrypt_secret(item.uri) == payload["uri"]


def test_workspace_resources_exports_health_usage_and_isolation():
    with TestClient(app) as client:
        headers = _login_admin(client)
        workspace_id = _demo_workspace_id(client, headers)

        glossary = client.get(f"/api/v1/resources/business-glossary?workspace_id={workspace_id}", headers=headers)
        assert glossary.status_code == 200
        assert any(item["name"] == "Revenue" for item in glossary.json())

        saved = client.get(f"/api/v1/resources/saved-prompts?workspace_id={workspace_id}", headers=headers)
        assert saved.status_code == 200
        assert any("Monthly" in item["name"] for item in saved.json())

        schedule = client.post(
            "/api/v1/resources/scheduled-reports",
            headers=headers,
            json={"workspace_id": workspace_id, "name": "Weekly executive report", "cadence": "weekly", "delivery_channels": ["email", "slack"]},
        )
        assert schedule.status_code == 200, schedule.text
        assert schedule.json()["status"] == "scheduled"
        assert schedule.json()["delivery_status"]["email"] == "ready"

        export = client.post(
            "/api/v1/resources/exports",
            headers=headers,
            json={"workspace_id": workspace_id, "format": "csv", "source_type": "query", "rows": [{"region": "North", "revenue": 100}]},
        )
        assert export.status_code == 200, export.text
        assert export.json()["status"] == "ready"

        health = client.get(f"/api/v1/resources/source-health/list?workspace_id={workspace_id}", headers=headers)
        assert health.status_code == 200
        assert health.json()[0]["status"] in {"connected", "review_required"}

        usage = client.get(f"/api/v1/resources/usage/analytics?workspace_id={workspace_id}", headers=headers)
        assert usage.status_code == 200
        assert "token_usage" in usage.json()


def test_v3_semantic_lineage_and_collaboration_resources():
    with TestClient(app) as client:
        headers = _login_admin(client)
        workspace_id = _demo_workspace_id(client, headers)

        semantic = client.get(f"/api/v1/resources/semantic-layer?workspace_id={workspace_id}", headers=headers)
        assert semantic.status_code == 200, semantic.text
        metric_names = {item["name"] for item in semantic.json()["metrics"]}
        assert {"Revenue", "Gross Margin", "Customer Lifetime Value", "Average Order Value"}.issubset(metric_names)

        created_metric = client.post(
            "/api/v1/resources/semantic-metrics",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "name": "Net Revenue",
                "definition": "Revenue after discounts and credits.",
                "formula": "SUM(revenue) - SUM(discounts)",
                "dimensions": ["month", "region"],
                "tags": ["finance"],
            },
        )
        assert created_metric.status_code == 200, created_metric.text

        lineage = client.get(f"/api/v1/resources/data-lineage?workspace_id={workspace_id}", headers=headers)
        assert lineage.status_code == 200, lineage.text
        assert lineage.json()["nodes"]
        assert lineage.json()["edges"]
        assert "Revenue" in lineage.json()["affected_kpis"]

        comment = client.post(
            "/api/v1/resources/comments",
            headers=headers,
            json={"workspace_id": workspace_id, "target_type": "dashboard", "target_id": "demo", "body": "@finance review this", "mentions": ["finance"]},
        )
        assert comment.status_code == 200, comment.text
        assert comment.json()["mentions"] == ["finance"]

        approval = client.post(
            "/api/v1/resources/approvals",
            headers=headers,
            json={"workspace_id": workspace_id, "target_type": "dashboard", "target_id": "demo", "action": "publish_dashboard", "requested_reason": "executive review"},
        )
        assert approval.status_code == 200, approval.text
        assert approval.json()["status"] == "pending"
        assert approval.json()["human_in_the_loop"] is True

        activity = client.get(f"/api/v1/resources/activity-feed?workspace_id={workspace_id}", headers=headers)
        assert activity.status_code == 200
        assert any(item["action"] == "approval.requested" for item in activity.json())


def test_ai_response_includes_query_confidence():
    with TestClient(app) as client:
        headers = _login_admin(client)
        workspace_id = _demo_workspace_id(client, headers)
        response = client.post(
            "/api/v1/ai/ask",
            headers=headers,
            json={"workspace_id": workspace_id, "question": "Show expenses by region", "engine": "sql", "execute": True},
        )
        assert response.status_code == 200, response.text
        confidence = response.json()["query_confidence"]
        assert confidence["confidence_score"] > 0
        assert confidence["reasoning_summary"]
        assert confidence["risk_level"]
        assert confidence["suggested_corrections"]


def test_rag_knowledge_searches_pdfs_sops_policies_contracts_and_meeting_notes():
    with TestClient(app) as client:
        headers = _login_admin(client)
        workspace_id = _demo_workspace_id(client, headers)

        documents = client.get(f"/api/v1/resources/knowledge-documents?workspace_id={workspace_id}", headers=headers)
        assert documents.status_code == 200
        document_types = {item["document_type"] for item in documents.json()}
        assert {"pdf", "sop", "policy", "contract", "meeting_note"}.issubset(document_types)

        created = client.post(
            "/api/v1/resources/knowledge-documents",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "title": "Renewal Contract Notes",
                "document_type": "contract",
                "content": "Renewal contracts include cancellation windows, service credits, and executive approval for high-value customers.",
                "tags": ["contract", "renewal"],
            },
        )
        assert created.status_code == 200, created.text

        search = client.post(
            "/api/v1/resources/knowledge-search",
            headers=headers,
            json={"workspace_id": workspace_id, "query": "revenue drop meeting notes policy contract", "document_types": ["pdf", "sop", "policy", "contract", "meeting_note"], "limit": 5},
        )
        assert search.status_code == 200, search.text
        result_types = {item["document_type"] for item in search.json()["results"]}
        assert result_types & {"policy", "contract", "meeting_note"}

        state = run_insight_graph(
            "Explain the revenue drop using meeting notes and policies",
            {"engine": "sqlite", "tables": [{"name": "sales"}]},
            "sql",
            rows=[{"order_month": "2026-06", "revenue": 100}],
            workspace_id=workspace_id,
            user_id="rag-user",
        )
        assert state["rag_context"]
        assert any(item.get("document_type") in {"meeting_note", "policy", "contract"} for item in state["rag_context"])
