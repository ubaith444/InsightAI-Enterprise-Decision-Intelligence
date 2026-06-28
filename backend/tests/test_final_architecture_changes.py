import io
import zipfile

from fastapi.testclient import TestClient

from app.ai.langgraph_workflow import list_agent_traces, run_insight_graph
from app.main import app
from app.services.enterprise_integrations import import_dataset, sync_rest_api


def _admin(client: TestClient) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": "admin@insightai.ai", "password": "InsightAI123"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _workspace(client: TestClient, headers: dict[str, str]) -> str:
    response = client.get("/api/v1/workspaces", headers=headers)
    assert response.status_code == 200
    return next(item["id"] for item in response.json() if item["slug"] == "acme-revenue")


def _xlsx_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "")
        archive.writestr("xl/sharedStrings.xml", """<?xml version="1.0" encoding="UTF-8"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <si><t>customer</t></si><si><t>revenue</t></si><si><t>Nimbus</t></si>
</sst>""")
        archive.writestr("xl/worksheets/sheet1.xml", """<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row><c t="s"><v>0</v></c><c t="s"><v>1</v></c></row>
    <row><c t="s"><v>2</v></c><c><v>100</v></c></row>
  </sheetData>
</worksheet>""")
    return buffer.getvalue()


def test_planner_router_governance_and_observability_are_persisted():
    state = run_insight_graph(
        "Show monthly revenue trend using policy context",
        {"engine": "sqlite", "tables": [{"name": "sales", "columns": [{"name": "revenue"}, {"name": "order_month"}]}]},
        "sql",
        rows=[{"order_month": "2026-06", "revenue": 100}],
        workspace_id="final-architecture",
        user_id="user",
    )
    order = [item["agent"] for item in state["agent_trace"]]
    assert order.index("Workflow Planner Agent") < order.index("Schema Intelligence Agent")
    assert order.index("Business Context Agent") < order.index("RAG Knowledge Agent")
    assert order.index("RAG Knowledge Agent") < order.index("SQL Generation Agent")
    assert state["model_route"]["mode"] in {"deterministic_fallback", "openai"}
    assert state["governance"]["approval_requirements"]["sending_reports"] is True
    assert state["monitoring"]["prompt_version"] == "insightai-agent-v3.1"
    assert state["monitoring"]["tool_calls"]
    persisted = next(trace for trace in list_agent_traces("final-architecture") if trace["id"] == state["trace_id"])
    assert persisted["agent_outputs"]["workflow_plan"]["retry_plan"]["external_connectors"] == 3
    assert persisted["agent_outputs"]["model_route"]["fallback"] == "local_rule_based_agents"
    assert persisted["agent_outputs"]["governance"]["retention_policy"] == "workspace_default_365_days"


def test_excel_import_and_priority_provider_sync(monkeypatch):
    excel = import_dataset("workspace", "sales.xlsx", _xlsx_bytes(), "excel")
    assert excel["import_status"] == "completed"
    assert excel["rows_processed"] == 1
    assert excel["preview_rows"][0]["customer"] == "Nimbus"

    class FakeResponse:
        status_code = 200
        headers = {"content-type": "application/json", "x-ratelimit-remaining": "10"}

        def json(self):
            return [{"id": "repo-1", "name": "insightai"}]

    def fake_get(url, headers, timeout):
        assert url == "https://api.github.com/user/repos"
        assert headers["Authorization"] == "Bearer test"
        assert timeout == 8
        return FakeResponse()

    monkeypatch.setattr("httpx.get", fake_get)
    sync = sync_rest_api("workspace", "", "Bearer test", provider="github")
    assert sync["status"] == "success"
    assert sync["provider"] == "github"
    assert sync["provider_config"]["pagination"] == "link_header"


def test_settings_lineage_report_dashboard_and_websocket_flows():
    with TestClient(app) as client:
        headers = _admin(client)
        workspace_id = _workspace(client, headers)

        settings = client.post(
            "/api/v1/resources",
            headers=headers,
            json={"workspace_id": workspace_id, "resource_type": "workspace-settings", "name": "Final settings", "payload": {"theme": "system", "query_safety": "strict"}},
        )
        assert settings.status_code == 200, settings.text
        settings_list = client.get(f"/api/v1/resources/workspace-settings?workspace_id={workspace_id}", headers=headers)
        assert any(item["name"] == "Final settings" for item in settings_list.json())

        dashboard = client.post(
            "/api/v1/dashboards",
            headers=headers,
            json={"workspace_id": workspace_id, "name": "Final dashboard", "widgets": [{"title": "Revenue", "rows": [{"month": "June", "revenue": 100}]}]},
        )
        assert dashboard.status_code == 200, dashboard.text
        assert client.get(f"/api/v1/dashboards/{dashboard.json()['id']}/export?workspace_id={workspace_id}&format=csv", headers=headers).status_code == 200

        report = client.post(
            "/api/v1/reports",
            headers=headers,
            json={"workspace_id": workspace_id, "title": "Final report", "report_type": "executive", "sections": [{"title": "KPIs"}]},
        )
        assert report.status_code == 200, report.text
        download = client.get(f"/api/v1/reports/{report.json()['id']}/download?workspace_id={workspace_id}&format=pdf", headers=headers)
        assert download.status_code == 200
        assert download.content.startswith(b"%PDF")

        lineage = client.get(f"/api/v1/resources/data-lineage?workspace_id={workspace_id}", headers=headers)
        assert lineage.status_code == 200
        assert "column_level_lineage" in lineage.json()
        assert "impact_analysis" in lineage.json()

        snapshot = client.get(f"/api/v1/realtime/snapshot?workspace_id={workspace_id}", headers=headers)
        assert snapshot.status_code == 200
        assert snapshot.json()["refresh_intervals"] == [5, 15, 30, 60]

        with client.websocket_connect(f"/api/v1/realtime/ws/{workspace_id}") as websocket:
            message = websocket.receive_json()
            assert message["event"] == "live_metrics"
            assert message["metrics"]["active"] is True
