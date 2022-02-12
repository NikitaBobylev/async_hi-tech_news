import aiohttp
import asyncio
import bs4
import datetime
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import lxml
import json
import time
import random
import os

class Parser:
    def __init__(self) -> None:
        self.main_url = "https://hi-tech.news/"
        self.main_url_format = "https://hi-tech.news{}"
        self.format_url = "https://hi-tech.news/page/{}/"
        self.headers = {"accept": "*/*", "user-agent": UserAgent().random}
        self.all_data = []

    async def parse_article(self, sesion, url):
        async with await sesion.get(url=url, headers=self.headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                date = soup.find("div", class_="post").find(
                    "div", class_="tile-views").text.strip()
                picture = soup.find("div", class_="post").find_all(
                    'img')[-1].get("src")
                name = soup.find("h1", class_="title").text.strip()
                text = soup.find("div", class_="the-excerpt").text.strip()
                self.all_data.append(
                    {
                        "name": name,
                        "link": url,
                        "date": date,
                        "picture_link": picture,
                        "text": text

                    }
                )
                print(f"Обработана страница {url}")

    async def parser_links(self, url, session):
        async with await session.get(url=url, headers=self.headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                block = soup.find(
                    "div", class_="blog-posts").find_all(class_="post-body")
                for i in block:
                    personal_link = i.find(class_="title").find(
                        "a").get("href").strip()
                    await self.parse_article(sesion=session, url=personal_link)
                    await asyncio.sleep(0.5)

    async def gather_tasks(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            response = await session.get(url=self.main_url, headers=self.headers)
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            last_page = int(
                soup.find("span", class_="navigations").find_all("a")[-1].text.strip())
            for page in range(1, last_page + 1):
                url = self.format_url.format(page)
                task = asyncio.create_task(self.parser_links(
                    url=url,
                    session=session))
                tasks.append(task)
            await asyncio.gather(*tasks)

    def recording_json(self):
        if not os.path.exists("data/"):
            os.mkdir('data')
        now = datetime.datetime.now().strftime("%d_%m_%Y_%H:%M")
        with open(f"data/{now}.json", "w", encoding="utf-8") as file:
            json.dump(self.all_data, file, indent=4, ensure_ascii=False)

    def main(self):
        asyncio.run(self.gather_tasks())
        self.recording_json()
        print(f"Обработано {len(self.all_data)}")


if __name__ == "__main__":
    Parser().main()
