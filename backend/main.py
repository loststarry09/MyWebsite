from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from routers import blog_router


class PingResponse(BaseModel):
    """统一定义 /api/ping 的响应结构，便于后续接口文档与类型约束。"""

    message: str


app = FastAPI(title="MyWebsite Backend API")

# 开发阶段先放开跨域，后续可按域名白名单收敛。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/ping", response_model=PingResponse)
def ping() -> PingResponse:
    """健康检查接口，用于验证 FastAPI 服务已正常启动。"""

    return PingResponse(message="pong")


app.include_router(blog_router)
