from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    f"http://{host}:{port}"
    for host in ("localhost", "127.0.0.1")
    for port in (3000, 3001, 3002)
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(router, prefix=settings.api_v1_prefix)
