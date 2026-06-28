import io

from fastapi.testclient import TestClient

from app.ai.langgraph_workflow import list_agent_specs, run_insight_graph
from app.main import app


def _admin(client: TestClient) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": "admin@insightai.ai", "password": "InsightAI123"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _workspace(client: TestClient, headers: dict[str, str]) -> str:
    return next(item["id"] for item in client.get("/api/v1/workspaces", headers=headers).json() if item["slug"] == "acme-revenue")


def test_enterprise_agents_registered_and_orchestrated():
    assert any(item["node"] == "enterprise_api_integration" for item in list_agent_specs())
    assert any(item["node"] == "executive_decision" for item in list_agent_specs())
    state = run_insight_graph(
        "Refresh Salesforce API and explain revenue risk",
        {"engine": "sqlite", "tables": [{"name": "sales"}]},
        "sql",
        rows=[{"region": "South", "revenue": 100}, {"region": "North", "revenue": 180}],
        workspace_id="enterprise-workspace",
        user_id="enterprise-user",
    )
    assert state["api_integration"]["required"] is True
    assert "salesforce" in state["api_integration"]["platforms"]
    assert state["executive_decision"]["priority_actions"]
    assert any(item["agent"] == "Enterprise API Integration Agent" for item in state["agent_trace"])
    assert any(item["agent"] == "Executive Decision Agent" for item in state["agent_trace"])


def test_enterprise_catalog_etl_and_observability_routes():
    with TestClient(app) as client:
        headers = _admin(client)
        workspace_id = _workspace(client, headers)
        catalog = client.get("/api/v1/enterprise/connectors/catalog", headers=headers)
        assert catalog.status_code == 200
        assert "salesforce" in catalog.json()["business_platform"]
        assert "snowflake" in catalog.json()["warehouse"]

        upload = client.post(
            "/api/v1/enterprise/etl/import",
            headers=headers,
            data={"workspace_id": workspace_id, "source_type": "csv"},
            files={"file": ("orders.csv", io.BytesIO(b"customer,revenue\nNimbus,100\nNimbus,100\nAtlas,80\n"), "text/csv")},
        )
        assert upload.status_code == 200, upload.text
        assert upload.json()["rows_processed"] == 2
        assert upload.json()["cleaning_summary"]["deduplicated_rows"] == 1

        runs = client.get(f"/api/v1/enterprise/etl/runs?workspace_id={workspace_id}", headers=headers)
        assert runs.status_code == 200
        assert runs.json()

        snapshot = client.get(f"/api/v1/realtime/snapshot?workspace_id={workspace_id}", headers=headers)
        assert snapshot.status_code == 200
        assert snapshot.json()["refresh_intervals"] == [5, 15, 30, 60]

        metrics = client.get("/api/v1/observability/metrics", headers=headers)
        assert metrics.status_code == 200
        assert "requests_total" in metrics.json()


def test_dashboard_crud_and_report_downloads():
    with TestClient(app) as client:
        headers = _admin(client)
        workspace_id = _workspace(client, headers)
        dashboard = client.post(
            "/api/v1/dashboards",
            headers=headers,
            json={"workspace_id": workspace_id, "name": "Enterprise Dashboard", "widgets": [{"title": "KPI", "rows": [{"metric": "Revenue", "value": 100}]}]},
        )
        assert dashboard.status_code == 200, dashboard.text
        dashboard_id = dashboard.json()["id"]

        updated = client.put(
            f"/api/v1/dashboards/{dashboard_id}",
            headers=headers,
            json={"workspace_id": workspace_id, "name": "Enterprise Dashboard Updated", "widgets": []},
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "Enterprise Dashboard Updated"

        duplicate = client.post(f"/api/v1/dashboards/{dashboard_id}/duplicate?workspace_id={workspace_id}", headers=headers)
        assert duplicate.status_code == 200
        assert "Copy" in duplicate.json()["name"]

        export = client.get(f"/api/v1/dashboards/{dashboard_id}/export?workspace_id={workspace_id}&format=csv", headers=headers)
        assert export.status_code == 200
        assert "text/csv" in export.headers["content-type"]

        report = client.post(
            "/api/v1/reports",
            headers=headers,
            json={"workspace_id": workspace_id, "title": "Enterprise Report", "report_type": "weekly", "sections": []},
        )
        assert report.status_code == 200
        report_id = report.json()["id"]
        for fmt, content_type in [("pdf", "application/pdf"), ("excel", "application/vnd.ms-excel"), ("csv", "text/csv"), ("powerpoint", "presentation")]:
            download = client.get(f"/api/v1/reports/{report_id}/download?workspace_id={workspace_id}&format={fmt}", headers=headers)
            assert download.status_code == 200
            assert content_type in download.headers["content-type"]
            assert download.content
