from urllib.parse import urljoin
from datetime import date
from typing import AsyncGenerator, List

from dateutil.relativedelta import relativedelta
from playwright.async_api import async_playwright, Page


class KanteiClient:
    BASE_URL = "https://www.kantei.go.jp/"

    def __init__(self):
        self.dt = date(2022, 11, 1)

    def _build_url(self, path: str) -> str:
        return urljoin(self.BASE_URL, path)

    def _next_month(self) -> None:
        self.dt += relativedelta(months=1)

    def _get_archive_url(self):
        end_dt = date(2024, 8, 1)
        while self.dt <= end_dt:
            yield self._build_url(f"jp/101_kishida/actions/{self.dt:%Y%m}/index.html")
            self._next_month()

    async def _get_article_content(self, page: Page, url: str) -> str:
        retry_num = 3
        for _ in range(retry_num):
            try:
                await page.goto(url)
                await page.wait_for_timeout(1000.0)
                article = page.locator(".section")
                return await article.inner_text()
            except Exception as e:
                # エラーが起こった場合は5分待機する
                print(f"Error fetching article content from {url}: {e}")
                await page.wait_for_timeout(5 * 60 * 1000.0)
                continue
        return ""

    async def _extract_links(self, page: Page) -> List[str]:
        article_links = await page.query_selector_all("div.news-list-title a")
        links = []
        for link in article_links:
            if href := await link.get_attribute("href"):
                links.append(href)
        return links

    async def _get_article_links(
        self, page: Page, archive_url: str
    ) -> AsyncGenerator[str, None]:
        await page.goto(archive_url, wait_until="networkidle")
        await page.wait_for_timeout(1000.0)
        links = await self._extract_links(page)
        for link in links:
            yield link

    async def get_data(self) -> AsyncGenerator[str, None]:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            try:
                page = await browser.new_page()
                for archive_url in self._get_archive_url():
                    async for article_url in self._get_article_links(page, archive_url):
                        full_url = self._build_url(article_url)
                        print(full_url)
                        article_text = await self._get_article_content(page, full_url)
                        if article_text:
                            yield article_text.replace("もっと見る", "").strip()
            finally:
                await browser.close()
