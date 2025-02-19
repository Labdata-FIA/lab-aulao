from fastapi import FastAPI

from .routes import main_router
from .core.responses import ORJSONResponse

app = FastAPI(
    title="Fast Api Fia",
    version="0.1.0",
    description="Minha api",
    default_response_class=ORJSONResponse
)

app.include_router(main_router)
