from pydantic import BaseModel, Field


class News(BaseModel):
    title: str = Field(..., description="The title of the news")
    link: str = Field(..., description="The link of the news")
    image: str = Field(..., description="The image of the news")
    description: str = Field(..., description="The description of the news")


class NewsResponse(BaseModel):
    total: int = Field(..., description="The total number of news")
    news: list[News] = Field(..., description="The list of news")
