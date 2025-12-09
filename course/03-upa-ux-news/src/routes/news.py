from urllib.parse import urljoin

import requests
from fastapi import APIRouter, HTTPException
from lxml import html

from src.models.news import News, NewsResponse

router = APIRouter()

PAGE_URL = "https://www.unipamplona.edu.co"


def scrape_upa_web():
    response = requests.get(PAGE_URL)
    tree = html.fromstring(response.content)

    content_slides = tree.xpath('//ul[@class="uk-slideshow"]/li')

    news = []

    for li_element in content_slides:
        overlay = li_element.xpath(".//div[contains(@class, 'uk-overlay-panel')]")
        if not overlay:
            continue

        overlay = overlay[0]
        title_list = overlay.xpath(".//h3/text()")
        title: str = title_list[0].strip() if title_list else ""

        description_text_list = overlay.xpath(".//p//text()")
        description: str = " ".join(
            t.strip() for t in description_text_list if t.strip()
        )

        link = li_element.xpath(".//a/@href") or []
        image = li_element.xpath(".//img/@src") or []

        if not all([link, image]):
            continue

        full_link = urljoin(PAGE_URL, link[0])
        full_image = urljoin(PAGE_URL, image[0])

        news.append(
            News(
                title=title,
                description=description,
                link=full_link,
                image=full_image,
            )
        )

    return news


@router.get(
    "/news",
    response_model=NewsResponse,
    summary="Get news",
    description="Returns the news.",
    tags=["Scraper"],
)
async def get_news():
    try:
        news = scrape_upa_web()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return NewsResponse(total=len(news), news=news)
