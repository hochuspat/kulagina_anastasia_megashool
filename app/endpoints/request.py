from fastapi import APIRouter, Depends

from app.schemas.request import PredictionRequest
from app.service.web_query_service import WebQueryService

api_router = APIRouter()

@api_router.post("/request")
async def request(
                data: PredictionRequest,
                service: WebQueryService = Depends(WebQueryService)
):
    return await service.process_query(data)