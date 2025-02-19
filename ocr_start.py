from fastapi import FastAPI
from config import args
from routes import app_routers

# 启动服务
app = FastAPI(
    title="OCR API",
    description="OCR",
    version="1.1.0",
    license_info={
        "name": "Apache 2.0",
        "url": "http://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# 允许跨域请求
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名访问，或者指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(app_routers)

if __name__ == '__main__':
    print("=====================================================\nLoading Seg model and FastAPI starting server...\nPlease wait until server has fully started\n=====================================================")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)
