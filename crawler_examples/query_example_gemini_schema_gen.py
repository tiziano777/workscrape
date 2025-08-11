import asyncio
import os
from dotenv import load_dotenv

from nodes.gemini_schema_generation import LLMSchemaExtractor

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy



load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")


async def main():


    # Schema LLM powered
    schema_extractor = LLMSchemaExtractor()


    ### INPUT ###
    #url = "https://scholar.google.com/scholar?as_ylo=2025&q=LLM&hl=en&as_sdt=0,5"
    url = "https://arxiv.org/search/?searchtype=all&query=LLM&abstracts=show&size=200&order=-announced_date_first"

    # --- PASSO 1: Genera lo schema (sincrono) ---
    schema_definition = schema_extractor(url)

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

    # Oppure, se vuoi mantenere il markdown_generator ma disabilitare il filtro:
    # config = CrawlerRunConfig(
    #     cache_mode=CacheMode.BYPASS,
    #     markdown_generator=DefaultMarkdownGenerator(content_filter=None), # Disabilita il filtro
    #     extraction_strategy=extraction_strategy
    # )

    ### PASSO 4: ESTRAZIONE DI INFO STRUTTURATE DALL' INPUT URL con crawler
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, config=config)

        print("\n--- Risultati del Crawling ---")
        if result.markdown:
            print("Raw Markdown length:", len(result.markdown.raw_markdown))
            print("Fit Markdown length:", len(result.markdown.fit_markdown))
            if result.markdown.fit_markdown:
                print("\n\n--- Dati FIT MARKDOWN Estratti ---\n\n")
                print("Inizio Fit Markdown:\n", result.markdown.fit_markdown) 
            print("\n\n--- Dati RAW MARKDOWN Estratti ---\n\n")
            print(result.markdown.raw_markdown)

            #SAVE CRAWLED DATA
            file_name = "data/arxiv_crawled_data.md"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(result.markdown.raw_markdown)
            print(f"\n--- Contenuto salvato in '{file_name}' ---")

            exit(0)
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