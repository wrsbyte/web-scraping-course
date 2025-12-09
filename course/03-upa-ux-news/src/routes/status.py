from fastapi import APIRouter

from src.models.status import StatusResponse

router = APIRouter()


@router.get(
    "/",
    response_model=StatusResponse,
    summary="Get API status",
    description="Returns the current status of the API.",
    tags=["Status"],
)
async def status():
    return StatusResponse(status="ok")
