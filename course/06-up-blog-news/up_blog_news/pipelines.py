import os
from datetime import datetime

import pandas as pd
import psycopg2
from itemadapter import ItemAdapter
from markdownify import markdownify as md


class UpMarkdownPipeline:
    def process_item(self, item, spider):
        # if is list instance
        if isinstance(item["content"], list):
            content = "".join(item["content"])
        else:
            content = item["content"]

        # convert html to markdown
        item["clean_content"] = md(content)

        return item


class UpExcelExportPipeline:
    def open_spider(self, spider):
        self.data = []

    def close_spider(self, spider):
        exist_file = os.path.exists("exports/up_blog_news.xlsx")

        if exist_file:
            df = pd.read_excel("exports/up_blog_news.xlsx")
            df = pd.concat([df, pd.DataFrame(self.data)], ignore_index=True)
        else:
            df = pd.DataFrame(self.data)

        # remove duplicates
        df = df.drop_duplicates()
        df.to_excel("exports/up_blog_news.xlsx", index=False)

    def process_item(self, item, spider):
        self.data.append(
            {
                "title": item["title"],
                "category": item["category"],
                "date": item["date"],
                "image": item["image"],
                "url": item["url"],
                "scraped_at": item["scraped_at"],
                "content": item["content"],
                "clean_content": item["clean_content"],
            }
        )

        return item


class PostgresPipeline:
    """
    To create table in postgres:

    CREATE TABLE up_blog_posts (
        id SERIAL PRIMARY KEY,
        url VARCHAR(500) UNIQUE NOT NULL,
        title TEXT,
        category VARCHAR(255),
        date DATE,
        content TEXT,
        clean_content TEXT,
        image TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    Create index:

    CREATE UNIQUE INDEX idx_url ON up_blog_posts (url);
    """

    def __init__(self, db_host, db_port, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            db_host=settings.get("POSTGRES_HOST"),
            db_port=settings.get("POSTGRES_PORT"),
            db_user=settings.get("POSTGRES_USER"),
            db_password=settings.get("POSTGRES_PASSWORD"),
            db_name=settings.get("POSTGRES_DB_NAME"),
        )

    def open_spider(self, spider):
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                dbname=self.db_name,
            )
            self.cursor = self.conn.cursor()
            spider.logger.info("🟢 [PostgresPipeline] connection established")
        except psycopg2.Error as e:
            spider.logger.error(f"🔴 [PostgresPipeline] Error on connection: {e}")
            raise

    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)

            insert_query = """
            INSERT INTO up_blog_posts (
                url,
                title,
                category,
                date,
                content,
                clean_content,
                image
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING;
            """

            # insert_query = """
            # INSERT INTO up_blog_posts (
            #     url,
            #     title,
            #     category,
            #     date,
            #     content,
            #     clean_content,
            #     image
            # )
            # VALUES (%s, %s, %s, %s, %s, %s, %s)
            # ON CONFLICT (url) DO
            # UPDATE SET
            #     title = EXCLUDED.title,
            #     category = EXCLUDED.category,
            #     date = EXCLUDED.date,
            #     content = EXCLUDED.content,
            #     clean_content = EXCLUDED.clean_content,
            #     image = EXCLUDED.image,
            #     updated_at = CURRENT_TIMESTAMP;
            # """

            self.cursor.execute(
                insert_query,
                (
                    adapter.get("url"),
                    adapter.get("title"),
                    adapter.get("category"),
                    adapter.get("date"),
                    adapter.get("content"),
                    adapter.get("clean_content"),
                    adapter.get("image"),
                ),
            )

            self.conn.commit()
            spider.logger.info(
                f"✅ [PostgresPipeline] Item inserted/updated: {adapter.get('url')}"
            )

        except psycopg2.Error as e:
            spider.logger.error(f"❌ [PostgresPipeline] Error on insert item: {e}")
            self.conn.rollback()

        return item

    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            spider.logger.info("🔴 [PostgresPipeline] connection closed")
