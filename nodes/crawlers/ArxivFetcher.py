from nodes.schema_generators.GeminiSchemaGenerator import LLMSchemaExtractor
import os
import json
import random
from typing import Optional, Dict
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai import LLMConfig
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


class ArxivFetcher:
    def __init__(self, provider: str = "gemini/gemini-2.0-flash-001", schema_file: str = "data/schemas.jsonl", user_agents_file: str = "config/http_params/user_agent_params.json", additional_headers_path: str = "config/http_params/additional_headers.json" ):
        """
        Inizializza l'estrattore di schema.
        :param schema_file: percorso file JSONL dove salvare/leggere schemi.
        :param user_agents_file: percorso del file JSON con i user agent rotanti.
        :param additional_headers_path: percorso del file JSON con gli header statici.
        """
        self.schema_extractor=LLMSchemaExtractor()

        
    
    async def __call__(self,state):

        url=state
        # --- PASSO 1: Genera lo schema (sincrono) ---
        schema_definition = self.schema_extractor(url)

        print("Schema estratto/caricato da cache:")
        print(schema_definition) # Stampalo per ispezionarlo!


        # --- PASSO 2: Inizializza la strategia di estrazione JSON/CSS con lo schema ---
        extraction_strategy = JsonCssExtractionStrategy(schema=schema_definition)


        # --- PASSO 3: Configura il crawler SENZA il Markdown generator che aplica filtri sul testo raw. troppo aggressivo per scraping links---
        # rimossa completamente la configurazione del markdown_generator O rendila meno aggressiva

        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=extraction_strategy
        )

        ### PASSO 4: ESTRAZIONE DI INFO STRUTTURATE DALL' INPUT URL con crawler
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url, config=config)
        
        # Return a reusult. markdown.raw_markdown correctly
        
        return result.markdown.raw_markdown