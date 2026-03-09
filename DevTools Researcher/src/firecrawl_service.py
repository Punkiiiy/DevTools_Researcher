from firecrawl.client import FirecrawlApp
from firecrawl.v2.types import ScrapeOptions

from dotenv import load_dotenv
import os

load_dotenv()

class FirecrawlService:
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise EnvironmentError("Environment variable FIRECRAWL_API_KEY not found")
        self.app = FirecrawlApp(api_key=api_key)


    def search_companies(self, query: str, limit: int = 5):
        try:
            results = self.app.search(
                query=f"{query} company prices",
                limit=limit,
                scrape_options=ScrapeOptions(
                    formats=["markdown"]
                )
            )
            return results
        except Exception as e:
            print(e)
            return []


    def scrape_page(self, url: str):
        try:
            results = self.app.scrape(
                url=url,
                format=["markdown"]
            )
            return results
        except Exception as e:
            print(e)
            return None