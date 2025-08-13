from fastapi.testclient import TestClient
from src.template_llm_api.main import app

client = TestClient(app)

def test_read_root():
    """
    ルートエンドポイント(/)のテスト。
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
