import os
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# FastAPIのインスタンスを作成
app = FastAPI()

# リクエストボディの型を定義
class GenerateRequest(BaseModel):
    prompt: str

# ルートエンドポイント（/）に対するGETリクエストのハンドラ
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# /generateエンドポイント（POST）
@app.post("/generate")
async def generate(request: GenerateRequest):
    """
    Ollama APIにリクエストを送信し、LLMからの応答を返します。
    """
    ollama_api_url = os.getenv("OLLAMA_API_URL")
    llm_model_name = os.getenv("LLM_MODEL_NAME")

    payload = {
        "model": llm_model_name,
        "prompt": request.prompt,
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(ollama_api_url, json=payload, timeout=60.0)
        response.raise_for_status()  # エラーがあれば例外を発生させる

    ollama_response = response.json()
    print("Ollama APIからのレスポンス:", ollama_response)  # コンソールに出力

    return {"response": ollama_response.get("response")}
