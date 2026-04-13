from fastapi.testclient import TestClient

from app.main import app


def test_system_and_chat_endpoints_smoke():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 200
        assert client.get("/version").status_code == 200

        response = client.post("/chat/send", json={"message": "hello"})
        assert response.status_code == 200
        body = response.json()
        assert "conversation_id" in body
        assert "reply" in body

        tool_calls = client.get(f"/conversations/{body['conversation_id']}/tool-calls")
        assert tool_calls.status_code == 200
