import scrapy
from scrapy.loader import ItemLoader

from up_blog_news.items import UpBlogNewsItem


class UpBlogNewsSpiderSpider(scrapy.Spider):
    name = "up_blog_news_spider"
    allowed_domains = ["up.edu.mx"]

    def __init__(self, *args, **kwargs):
        super(UpBlogNewsSpiderSpider, self).__init__(*args, **kwargs)

    async def start(self):
        urls = [
            "https://www.up.edu.mx/tema/noticias/page/1/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # get all news index
        for post in response.css("h2.wp-block-post-title"):
            link = post.css("a::attr(href)").get()

            self.logger.info(f"✨ News: {link}")

            yield response.follow(link, self._transform_news_post)

        # validate has next page
        next_page = response.css("span.page-numbers.current + a::attr(href)").get()
        if next_page is not None:
            # TODO: remove this when finish. Only for testing
            if "/3/" in next_page:
                self.logger.info(f"🐛 Ignore next page: {next_page}. Return")

                return

            self.logger.info(f"✨ Next page: {next_page}")
            yield response.follow(next_page, self.parse)

    def _transform_news_post(self, response):
        item = ItemLoader(item=UpBlogNewsItem(), response=response)
        item.add_css("title", "h1.wp-block-post-title::text")
        item.add_css("category", "div.taxonomy-category a::text")
        item.add_css("date", "div.wp-block-post-date time::text")
        item.add_css(
            "image",
            "figure.wp-block-post-featured-image img::attr(src)",
        )
        item.add_css(
            "content",
            "div.wp-block-post-content, .entry-content::text",
        )
        # item.add_value("content", "<h1>Test</h1>")
        item.add_value("url", response.url)

        yield item.load_item()
