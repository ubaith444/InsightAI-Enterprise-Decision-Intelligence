from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models import AIUsageLog, QueryLog, Role, User, WorkspaceMember


def _register(client: TestClient, role: Role | None = None) -> tuple[dict, dict]:
    suffix = uuid4().hex[:8]
    response = client.post(
        "/api/v1/auth/register",
        json={"email": f"qa-{suffix}@example.com", "full_name": f"QA User {suffix}", "password": "InsightAI123"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    if role:
        with SessionLocal() as db:
            user = db.get(User, body["user"]["id"])
            assert user is not None
            user.role = role
            for membership in db.query(WorkspaceMember).filter(WorkspaceMember.user_id == user.id):
                membership.role = role
            db.commit()
        body["user"]["role"] = role.value
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    return body, headers


def _admin_headers(client: TestClient) -> dict:
    response = client.post("/api/v1/auth/login", json={"email": "admin@insightai.ai", "password": "InsightAI123"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_complete_ai_business_intelligence_journey():
    with TestClient(app) as client:
        session, headers = _register(client)

        workspace_response = client.post("/api/v1/workspaces", headers=headers, json={"name": f"QA Revenue {uuid4().hex[:6]}"})
        assert workspace_response.status_code == 200, workspace_response.text
        workspace_id = workspace_response.json()["id"]

        sql_connection = client.post(
            "/api/v1/connections",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "name": "PostgreSQL Demo Warehouse",
                "kind": "postgresql",
                "uri": "sqlite:///./insightai.db",
                "is_read_only": True,
                "selected_assets": ["sales", "customers", "products"],
            },
        )
        assert sql_connection.status_code == 200, sql_connection.text
        sql_body = sql_connection.json()
        assert "uri" not in sql_body
        assert sql_body["masked_uri"] == "sqlite://***"

        mongo_connection = client.post(
            "/api/v1/connections",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "name": "MongoDB Demo Memory",
                "kind": "mongodb",
                "uri": "mongodb://insight:secret@localhost:27017/insightai",
                "is_read_only": True,
                "selected_assets": ["customer_activity", "dashboard_configs"],
            },
        )
        assert mongo_connection.status_code == 200, mongo_connection.text
        assert "secret" not in str(mongo_connection.json())

        schema = client.get(f"/api/v1/connections/{sql_body['id']}/schema", headers=headers)
        assert schema.status_code == 200, schema.text
        assert {"sales", "customers", "products"}.issubset({table["name"] for table in schema.json()["tables"]})

        questions = [
            "Show monthly revenue trend for the last 12 months",
            "Find top 10 customers by revenue",
            "Compare sales by region",
            "Show low inventory products",
            "Explain why revenue dropped last month",
        ]
        answers = []
        for question in questions:
            answer = client.post(
                "/api/v1/ai/ask",
                headers=headers,
                json={"workspace_id": workspace_id, "connection_id": sql_body["id"], "question": question, "engine": "sql", "execute": True},
            )
            assert answer.status_code == 200, answer.text
            payload = answer.json()
            assert payload["safe"] is True
            assert payload["generated_query"].lower().startswith("select")
            assert "limit" in payload["generated_query"].lower()
            assert payload["rows"]
            assert payload["insights"]["summary"]
            assert payload["chart"]["type"] in {"line", "bar", "table", "area", "pie", "donut", "kpi", "map"}
            answers.append(payload)

        mongo_answer = client.post(
            "/api/v1/ai/ask",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "connection_id": mongo_connection.json()["id"],
                "question": "Generate MongoDB aggregation for user activity",
                "engine": "mongodb",
                "execute": True,
            },
        )
        assert mongo_answer.status_code == 200, mongo_answer.text
        assert mongo_answer.json()["engine"] == "mongodb"
        assert mongo_answer.json()["rows"]

        vague = client.post(
            "/api/v1/ai/ask",
            headers=headers,
            json={"workspace_id": workspace_id, "question": "show something", "engine": "sql", "execute": True},
        )
        assert vague.status_code == 200
        assert "clarify" in vague.json()["explanation"].lower()
        assert vague.json()["rows"] == []

        unsafe_sql = client.post("/api/v1/ai/validate", json={"engine": "sql", "query": "DELETE FROM sales"})
        assert unsafe_sql.status_code == 200
        assert unsafe_sql.json()["safe"] is False

        unsafe_mongo = client.post("/api/v1/ai/validate", json={"engine": "mongodb", "query": [{"$match": {}}, {"$merge": "x"}]})
        assert unsafe_mongo.status_code == 200
        assert unsafe_mongo.json()["safe"] is False

        job = client.post(
            "/api/v1/queries/execute",
            headers=headers,
            json={"workspace_id": workspace_id, "engine": "sql", "query": "SELECT * FROM sales", "async_job": True},
        )
        assert job.status_code == 200, job.text
        assert job.json()["job"]["backend"] == "redis-celery"
        job_status = client.get(f"/api/v1/queries/jobs/{job.json()['job']['id']}", headers=headers)
        assert job_status.status_code == 200
        assert job_status.json()["status"] == "success"
        assert job_status.json()["result"]["row_count"] > 0

        dashboard = client.post(
            "/api/v1/dashboards",
            headers=headers,
            json={"workspace_id": workspace_id, "name": "QA Revenue Dashboard", "widgets": [{"title": "Monthly revenue", "chart": answers[0]["chart"]}]},
        )
        assert dashboard.status_code == 200, dashboard.text

        report = client.post(
            "/api/v1/reports",
            headers=headers,
            json={"workspace_id": workspace_id, "title": "QA Weekly AI Report", "report_type": "weekly", "sections": [{"title": "Revenue"}]},
        )
        assert report.status_code == 200, report.text
        assert report.json()["payload"]["export"]["pdf"] == "downloadable"

        history = client.get(f"/api/v1/queries/history?workspace_id={workspace_id}", headers=headers)
        assert history.status_code == 200
        assert len(history.json()) >= len(questions)

        with SessionLocal() as db:
            logs = db.query(QueryLog).filter(QueryLog.workspace_id == workspace_id, QueryLog.user_id == session["user"]["id"]).all()
            assert logs
            assert all(log.workspace_id and log.user_id for log in logs)
            usage_providers = {item.provider for item in db.query(AIUsageLog).filter(AIUsageLog.workspace_id == workspace_id).all()}
            assert usage_providers
            assert usage_providers.issubset({"mock", "openai-configured"})

        admin_headers = _admin_headers(client)
        audit = client.get(f"/api/v1/audit-logs?workspace_id={workspace_id}", headers=admin_headers)
        assert audit.status_code == 200, audit.text
        assert {item["action"] for item in audit.json()} & {"query_executed", "dashboard_created", "report_generated"}

        admin = client.get("/api/v1/admin/analytics", headers=admin_headers)
        assert admin.status_code == 200
        assert admin.json()["query_logs"] >= len(questions)


def test_rbac_workspace_isolation_and_error_handling():
    with TestClient(app) as client:
        analyst_session, analyst_headers = _register(client, Role.analyst)
        viewer_session, viewer_headers = _register(client, Role.viewer)
        outsider_session, outsider_headers = _register(client, Role.analyst)

        workspace_id = client.get("/api/v1/workspaces", headers=analyst_headers).json()[0]["id"]

        viewer_workspace = client.get("/api/v1/workspaces", headers=viewer_headers).json()[0]["id"]
        viewer_execute = client.post(
            "/api/v1/ai/ask",
            headers=viewer_headers,
            json={"workspace_id": viewer_workspace, "question": "Show revenue by month", "engine": "sql", "execute": True},
        )
        assert viewer_execute.status_code == 403

        analyst_admin = client.get("/api/v1/admin/analytics", headers=analyst_headers)
        assert analyst_admin.status_code == 403

        isolated_history = client.get(f"/api/v1/queries/history?workspace_id={workspace_id}", headers=outsider_headers)
        assert isolated_history.status_code == 403

        bad_connection = client.post(
            "/api/v1/connections",
            headers=analyst_headers,
            json={"workspace_id": workspace_id, "name": "Broken", "kind": "postgresql", "uri": "not-a-valid-uri", "is_read_only": True},
        )
        assert bad_connection.status_code == 200
        test_result = client.post(f"/api/v1/connections/{bad_connection.json()['id']}/test", headers=analyst_headers)
        assert test_result.status_code >= 400

        assert analyst_session["user"]["id"] != viewer_session["user"]["id"] != outsider_session["user"]["id"]
