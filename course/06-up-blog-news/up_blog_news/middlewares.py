import random
from datetime import datetime

from itemadapter import ItemAdapter


class UpBlogNewsSpiderMiddleware:
    def process_spider_output(self, response, result, spider):
        for r in result:
            if isinstance(r, dict) or hasattr(r, "fields"):
                item = ItemAdapter(r)
                item["scraped_at"] = datetime.utcnow().isoformat()
            yield r


class RotateUserAgentMiddleware:
    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        agents = crawler.settings.get("USER_AGENTS_LIST", [])
        return cls(agents)

    def process_request(self, request, spider):
        if self.agents:
            request.headers["User-Agent"] = random.choice(self.agents)
            spider.logger.info(
                f"✨ [RotateUserAgentMiddleware] User-Agent: {request.headers['User-Agent']}"
            )
