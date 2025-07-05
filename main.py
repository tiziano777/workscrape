import asyncio
import os
from dotenv import load_dotenv

from gemini_schema_generation import SchemaExtractor
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter # Puoi lasciarlo ma non usarlo
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")

async def main():

    schema_extractor = SchemaExtractor()

    url = "https://scholar.google.com/scholar?as_ylo=2025&q=LLM&hl=en&as_sdt=0,5"

    # --- PASSO 1: Genera lo schema (sincrono) ---
    schema_definition = schema_extractor(url)
    print("Schema estratto/caricato da cache:")
    print(schema_definition) # Stampalo per ispezionarlo!

    # --- PASSO 2: Inizializza la strategia di estrazione JSON/CSS con lo schema ---
    # Se il tuo schema_extractor restituisce una stringa JSON, potresti dover fare json.loads(schema_definition)
    # se JsonCssExtractionStrategy si aspetta un dict Python.
    extraction_strategy = JsonCssExtractionStrategy(schema=schema_definition)


    # --- PASSO 3: Configura il crawler SENZA il PruningContentFilter troppo aggressivo ---
    # Rimuovi completamente la configurazione del markdown_generator O rendila meno aggressiva
    # Per test, la togliamo del tutto.
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        # Rimosso il markdown_generator (e quindi il PruningContentFilter) per testare l'estrazione
        extraction_strategy=extraction_strategy
    )

    # Oppure, se vuoi mantenere il markdown_generator ma disabilitare il filtro:
    # config = CrawlerRunConfig(
    #     cache_mode=CacheMode.BYPASS,
    #     markdown_generator=DefaultMarkdownGenerator(content_filter=None), # Disabilita il filtro
    #     extraction_strategy=extraction_strategy
    # )


    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, config=config)

        print("\n--- Risultati del Crawling ---")
        if result.markdown:
            print("Raw Markdown length:", len(result.markdown.raw_markdown))
            print("Fit Markdown length:", len(result.markdown.fit_markdown))
            if result.markdown.fit_markdown:
                print("Inizio Fit Markdown:\n", result.markdown.fit_markdown[:500]) # Stampa solo l'inizio

        # Usa hasattr per controllare prima di accedere
        if hasattr(result, 'extracted_content') and result.extracted_content:
            print("\n--- Dati Strutturati Estratti ---")
            print(result.extracted_content)
            # --- QUI CHIAMERAI LA TUA FUNZIONE PER SALVARE I DATI NEL DB ---
            # Esempio: insert_article_data(result.extracted_content)
        else:
            print("\nNessun dato strutturato estratto o attributo 'extracted_content' mancante.")
            if hasattr(result, 'error') and result.error:
                print(f"Errore dal crawler: {result.error}")
            print("Verifica lo schema e la logica di estrazione.")
            print("Controlla anche il 'Fit Markdown' per assicurarti che ci sia contenuto valido.")


if __name__ == "__main__":
    asyncio.run(main())