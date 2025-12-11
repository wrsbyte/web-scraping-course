from datetime import datetime

import scrapy
from itemloaders.processors import Join, TakeFirst


def format_post_date(date_str):
    """
    Format post date to ISO format

    Example:
        >>> format_post_date("diciembre 4, 2025")
        '2025-12-10T00:00:00'
        >>> format_post_date("enero 10, 2025")
        '2025-01-10T00:00:00'
    """

    if not date_str:
        return None

    if isinstance(date_str, list):
        date_str = " ".join(date_str)

    date = date_str.lower()
    date = date.replace(",", "")

    months = {
        "enero": "01",
        "febrero": "02",
        "marzo": "03",
        "abril": "04",
        "mayo": "05",
        "junio": "06",
        "julio": "07",
        "agosto": "08",
        "septiembre": "09",
        "octubre": "10",
        "noviembre": "11",
        "diciembre": "12",
    }

    month = months.get(date.split(" ")[0])
    day = date.split(" ")[1]
    year = date.split(" ")[2]

    return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").isoformat()


class UpBlogNewsItem(scrapy.Item):
    url = scrapy.Field(
        output_processor=Join(),
    )
    title = scrapy.Field(
        output_processor=Join(),
    )
    category = scrapy.Field(
        output_processor=Join(),
    )
    date = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=format_post_date,
    )
    image = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=Join(),
    )
    content = scrapy.Field(
        output_processor=Join(),
    )
    clean_content = scrapy.Field(
        output_processor=Join(),
    )
    scraped_at = scrapy.Field(
        output_processor=Join(),
    )
