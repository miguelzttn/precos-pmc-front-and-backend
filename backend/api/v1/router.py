from fastapi import APIRouter

from api.v1.endpoints import frontend
from api.v1.endpoints import busca
from api.v1.endpoints import produtos

api_router = APIRouter(prefix="/v1")

frontend.router.include_router(produtos.router, prefix="/produtos")
frontend.router.include_router(busca.router, prefix="/busca")
api_router.include_router(frontend.router)

