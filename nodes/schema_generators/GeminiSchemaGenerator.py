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


class LLMSchemaExtractor:
    '''
    Estrae schema di estrazione struttutrata con chiamata LLM, restitutisce uno schema e lo salva in un file jsonl
    La chiaamta viene effettuata alal pagina target per ottenere html,
    i parametri della request sono passati dalla lettura di un file di configurazione json
    '''
    def __init__(self, provider: str = "gemini/gemini-2.0-flash-001", schema_file: str = "data/schemas.jsonl", user_agents_file: str = "params/user_agent_params.json", additional_headers_path: str = "params/additional_headers.json" ):
        """
        Inizializza l'estrattore di schema.
        :param schema_file: percorso file JSONL dove salvare/leggere schemi.
        :param user_agents_file: percorso del file JSON con i user agent rotanti.
        :param additional_headers_path: percorso del file JSON con gli header statici.
        """
        load_dotenv()
        self.api_token = os.getenv("GEMINI_API_KEY")
        self.schema_file = schema_file
        self.provider = provider
    
        self.user_agents_file = user_agents_file
        self.additional_headers_path = additional_headers_path

        # Carica il pool di user agent
        try:
            with open(self.user_agents_file, "r", encoding="utf-8") as f:
                self.user_agents_list = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Errore nella lettura del file degli user-agent: {e}")
            self.user_agents_list = [{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", "sec-ch-ua": "\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"126\"", "sec-ch-ua-platform": "\"Windows\""}]

        # Carica gli header statici
        try:
            with open(self.additional_headers_path, "r", encoding="utf-8") as f:
                self.static_headers = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Errore nella lettura del file degli headers: {e}")
            self.static_headers = {}

    def get_headers(self) -> Dict[str, str]:
        """
        Seleziona un user-agent casuale e lo unisce agli header statici.
        :return: Un dizionario di header completo e allineato.
        """
        user_agent_fields = random.choice(self.user_agents_list)
        
        headers = self.static_headers.copy()
        headers["User-Agent"] = user_agent_fields["User-Agent"]
        
        # Aggiungi gli header sec-ch-ua solo se presenti nel dizionario
        if "sec-ch-ua" in user_agent_fields:
            headers["sec-ch-ua"] = user_agent_fields["sec-ch-ua"]
        if "sec-ch-ua-platform" in user_agent_fields:
            headers["sec-ch-ua-platform"] = user_agent_fields["sec-ch-ua-platform"]
        
        return headers

    def fetch_html(self, url: str) -> str:
        """
        Scarica e ritorna il contenuto HTML della pagina indicata dall'URL.
        Setta un User agent a random da un pool.
        :raises requests.HTTPError se la risposta non è 200 OK.
        """
        headers = self.get_headers()
        print("\n--- Analisi della richiesta GET per schema retriver ---")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print("---------------------------------")
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    
    def _extract_deepest_subdomain(self, url: str) -> Optional[str]:
        """
        Estrae il sottodominio più profondo dal percorso di un URL.
        Ad esempio, 'http://arxiv.org/pdf/1234.5678' -> 'pdf'.
        """
        try:
            parsed_url = urlparse(url)
            # Ottiene il primo segmento del percorso, rimuovendo il '/' iniziale
            subdomain = parsed_url.path.strip('/').split('/')[0]
            if subdomain:
                return subdomain
        except:
            return None
        return None

    def load_schema_from_file(self, url: str) -> Optional[Dict]:
        """
        Cerca nel file JSONL se esiste uno schema salvato per un URL,
        confrontando solo il sottodominio più profondo.
        Restituisce lo schema se trovato, altrimenti None.
        """
        if not os.path.isfile(self.schema_file):
            return None

        input_subdomain = self._extract_deepest_subdomain(url)
        if not input_subdomain:
            return None

        with open(self.schema_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    saved_url = record.get("url")
                    if saved_url:
                        saved_subdomain = self._extract_deepest_subdomain(saved_url)
                        # Confronta solo il sottodominio più profondo
                        if saved_subdomain == input_subdomain:
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
            provider=self.provider, 
            api_token=self.api_token
        )
        schema = JsonCssExtractionStrategy.generate_schema(html, llm_config=llm_config)
        return schema
    
    def __call__(self, url: str) -> dict:
        """
        Se esiste schema in file per url, lo ritorna.
        Altrimenti scarica html, genera schema, salva e ritorna.
        """
        cached_schema = self.load_schema_from_file(url)
        if cached_schema is not None:
            return cached_schema
        
        html = self.fetch_html(url)
        schema = self.generate_schema(html)
        self.save_schema_to_file(url, schema)
        
        return schema