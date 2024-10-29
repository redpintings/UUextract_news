from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extract import UU  # 假设 UU 类在你的 extract 模块中

app = FastAPI()

# 初始化 UU 类和 RemoveUseless 类
u = UU()


class URLRequest(BaseModel):
    url: str


@app.post("/extract_plain_text/")
async def extract_plain_text(request: URLRequest):
    try:
        # 调用 u.uu 方法提取信息
        result = u.uu(url=request.url)

        if result is None:
            raise HTTPException(status_code=404, detail="Failed to extract content from the URL.")

        # 获取 plain_text
        plain_text = result.get('plain_text')

        if plain_text is None:
            raise HTTPException(status_code=404, detail="Plain text not found in the extracted content.")

        return {"url": request.url, "plain_text": plain_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)