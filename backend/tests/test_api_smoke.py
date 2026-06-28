from fastapi.testclient import TestClient

from app.main import app


def test_demo_login_and_ai_query_smoke():
    with TestClient(app) as client:
        login = client.post("/api/v1/auth/login", json={"email": "admin@insightai.ai", "password": "InsightAI123"})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        workspaces = client.get("/api/v1/workspaces", headers=headers)
        assert workspaces.status_code == 200
        workspace_id = workspaces.json()[0]["id"]

        answer = client.post(
            "/api/v1/ai/ask",
            headers=headers,
            json={"workspace_id": workspace_id, "question": "Show revenue by month", "engine": "sql", "execute": True},
        )
        assert answer.status_code == 200, answer.text
        payload = answer.json()
        assert payload["safe"] is True
        assert len(payload["rows"]) > 0
        assert payload["chart"]["type"] == "line"
