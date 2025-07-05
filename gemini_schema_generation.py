import os
import json
from typing import Optional, Dict
import requests
from dotenv import load_dotenv
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai import LLMConfig

class SchemaExtractor:
    def __init__(self, schema_file: str = "schemas.jsonl"):
        """
        Inizializza l'estrattore di schema.
        :param schema_file: percorso file JSONL dove salvare/leggere schemi.
        """
        load_dotenv()
        self.api_token = os.getenv("OPENAI_API_TOKEN")
        self.schema_file = schema_file
        self.headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/114.0.0.0 Safari/537.36")
        }
        
    def fetch_html(self, url: str) -> str:
        """
        Scarica e ritorna il contenuto HTML della pagina indicata dall'URL.
        :raises requests.HTTPError se la risposta non è 200 OK.
        """
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text
    
    def load_schema_from_file(self, url: str) -> Optional[Dict]:
        """
        Cerca nel file JSONL se esiste uno schema salvato per l'URL.
        Restituisce lo schema se trovato, altrimenti None.
        """
        if not os.path.isfile(self.schema_file):
            return None
        with open(self.schema_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if record.get("url") == url:
                        return record.get("schema")
                except json.JSONDecodeError:
                    continue
        return None

    def save_schema_to_file(self, url: str, schema: dict) -> None:
        """
        Salva lo schema associato a un URL nel file JSONL, appending.
        """
        record = {"url": url, "schema": schema}
        with open(self.schema_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    def generate_schema(self, html: str) -> dict:
        """
        Usa JsonCssExtractionStrategy.generate_schema per generare lo schema da HTML.
        """
        llm_config = LLMConfig(
            provider="gemini/gemini-2.0-flash-001",
            api_token=self.api_token
        )
        schema = JsonCssExtractionStrategy.generate_schema(html, llm_config=llm_config)
        return schema
    
    def __call__(self, url: str) -> dict:
        """
        Se esiste schema in file per url, lo ritorna.
        Altrimenti scarica html, genera schema, salva e ritorna.
        """
        # Prova a caricare da file
        cached_schema = self.load_schema_from_file(url)
        if cached_schema is not None:
            return cached_schema
        
        # Scarica HTML
        html = self.fetch_html(url)
        
        # Genera schema via LLM
        schema = self.generate_schema(html)
        
        # Salva schema su file
        self.save_schema_to_file(url, schema)
        
        return schema
