import os
import httpx
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 必須環境変数を起動時に解決＆検証
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
if not OLLAMA_API_URL or not LLM_MODEL_NAME:
    raise RuntimeError("環境変数 OLLAMA_API_URL と LLM_MODEL_NAME を設定してください")

# FastAPIのインスタンスを作成
app = FastAPI()

# リクエスト/レスポンスボディの型を定義
class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000, description="LLMへの入力プロンプト")

class GenerateResponse(BaseModel):
    response: str

# ルートエンドポイント（/）に対するGETリクエストのハンドラ
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# /generateエンドポイント（POST）
@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> dict:
    """
    Ollama APIにリクエストを送信し、LLMからの応答を返します。
    """
    payload = {
        "model": LLM_MODEL_NAME,
        "prompt": request.prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_API_URL, json=payload, timeout=60.0)
            response.raise_for_status()  # 2xx以外のステータスコードで例外を発生
    except httpx.TimeoutException as e:
        logger.error("Ollama APIへのリクエストがタイムアウトしました: %s", e)
        raise HTTPException(status_code=504, detail="Upstream API request timed out.") from e
    except httpx.HTTPStatusError as e:
        logger.error("Ollama APIがエラーステータスを返しました: %s", e)
        raise HTTPException(status_code=502, detail=f"Upstream API returned an error: {e.response.status_code}") from e
    except httpx.RequestError as e:
        logger.error("Ollama APIへの接続に失敗しました: %s", e)
        raise HTTPException(status_code=502, detail="Failed to connect to upstream API.") from e

    try:
        ollama_response = response.json()
    except ValueError as e:
        logger.error("Ollama APIからのレスポンスJSONのパースに失敗しました: %s", e)
        raise HTTPException(status_code=502, detail="Upstream API returned invalid JSON.") from e

    text = ollama_response.get("response")

    if not isinstance(text, str):
        logger.error("Ollama APIからのレスポンス形式が不正です。'response'キーが文字列ではありません。")
        raise HTTPException(status_code=502, detail="Upstream API response format is invalid.")

    logger.info("Ollama APIから正常に応答を取得しました。 (文字数: %d)", len(text))

    return {"response": text}
