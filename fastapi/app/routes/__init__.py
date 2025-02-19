from app.routes.produto import router as produto_router
from fastapi import APIRouter

main_router = APIRouter()

main_router.include_router(produto_router, prefix="/produtos", tags=["aluno"])

