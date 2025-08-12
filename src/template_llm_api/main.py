from fastapi import FastAPI
from typing import Optional

# FastAPIのインスタンスを作成
app = FastAPI()

# ルートエンドポイント（/）に対するGETリクエストのハンドラ
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
