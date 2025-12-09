from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    status: str = Field(..., description="The status of the API")
