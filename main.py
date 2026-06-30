from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.db.database import init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(router, prefix=settings.api_prefix)




app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Research Assistant API is running"}
