# crawler/strategy_router.py
import inspect
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
    RegexExtractionStrategy,
    LLMExtractionStrategy
)
from utils.url_classifier import classify_url_type

class StrategyRouter:
    def __init__(self, css_schema: dict = None, llm_schema: dict = None):
        self.css_schema = css_schema or {}
        self.llm_schema = llm_schema or {}

    async def run_url(self, url: str):
        print(inspect.signature(CrawlerRunConfig.__init__))
        url_type = classify_url_type(url)
        browser_conf = BrowserConfig(headless=True)
        run_conf = CrawlerRunConfig(
            cache_mode=None,
            extraction_strategy=self._select_strategy(url_type),
            process_media=True,
            apply_chunking=False
        )

        async with AsyncWebCrawler(config=browser_conf) as crawler:
            result = await crawler.arun(url=url, config=run_conf)
        return result

    def _select_strategy(self, url_type: str):
        if url_type in ("youtube_video", "youtube_channel"):
            return RegexExtractionStrategy(pattern=RegexExtractionStrategy.Url)
        elif url_type in ("arxiv_pdf", "pdf_file"):
            return JsonCssExtractionStrategy(self.css_schema)
        elif url_type == "html_page":
            return JsonCssExtractionStrategy(self.css_schema)
        else:
            return LLMExtractionStrategy(
                provider="openai/gpt-4",
                schema=self.llm_schema,
                extraction_type="schema"
            )
