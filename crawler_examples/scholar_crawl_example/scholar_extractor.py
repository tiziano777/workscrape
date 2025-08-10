import asyncio
import random
import os
from urllib.parse import urlencode, urlparse, parse_qs
from dotenv import load_dotenv
import json
import datetime 

from nodes.gemini_schema_generation import LLMSchemaExtractor

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

from crawler_examples.scholar_crawl_example.scholarRelatedSearches import GoogleScholarRelatedSearchExtractor

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")

# Set globale per tenere traccia degli URL già processati (per evitare cicli e ridondanza)
processed_urls = set()

# Set globale per tenere traccia dei url dei risultati estratti (per deduplicare i paper)
all_extracted_result_urls = set()

# Lista globale per accumulare tutti i dati strutturati estratti
all_extracted_data = []

# Limite di finestre asincrone per evitare di sovraccaricare
MAX_CONCURRENT_TASKS = 1

##############################################################################

async def extract_and_process_url(
    crawler: AsyncWebCrawler,
    base_scholar_url_template: str,
    search_string: str,
    depth: int,
    schema_extractor: LLMSchemaExtractor,
    scholar_linker: GoogleScholarRelatedSearchExtractor,
    max_depth: int,
    output_filename: str
    ):
    """
    Esegue il crawling di un URL, estrae i risultati e le ricerche correlate,
    e gestisce i livelli di ramificazione.
    """
    global processed_urls, all_extracted_result_urls, all_extracted_data

    tasks = []
    
    for start_param in [0, 10]:
        parsed_url_template = urlparse(base_scholar_url_template)
        query_params_template = parse_qs(parsed_url_template.query)
        
        query_params_template['q'] = [search_string]
        query_params_template['start'] = [str(start_param)]
        
        new_query_string = urlencode(query_params_template, doseq=True)
        current_url = parsed_url_template._replace(query=new_query_string).geturl()

        if current_url in processed_urls:
            print(f"[Depth {depth}] Skipping already processed search URL: {current_url}")
            continue

        print(f"\n--- Processing URL (Depth {depth}): {current_url} ---")

        delay = random.uniform(1, 5) # Ritardo casuale tra 1 e 5 secondi
        print(f"[{datetime.datetime.now().isoformat()}] Waiting for {delay:.2f} seconds before fetching {current_url}...")
        await asyncio.sleep(delay)

        try:
            print(f"[Depth {depth}] Generating schema for {current_url}...")

            # Chiama l'estrattore di schema
            schema_definition = schema_extractor(current_url)
            
            # Crea la strategia di estrazione e la passa direttamente al config
            extraction_strategy = JsonCssExtractionStrategy(schema=schema_definition)
            
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                stream = False,
                extraction_strategy=extraction_strategy,
            )
            
            # Il crawler ora gestirà l'estrazione automaticamente
            result = await crawler.arun(current_url, config=config)

            processed_urls.add(current_url)

            if result.markdown and result.markdown.raw_markdown:
                print(f"[Depth {depth}] Raw Markdown length: {len(result.markdown.raw_markdown)}")
                print(f"[Depth {depth}] Raw Markdown: {(result.markdown)}")
                
                exit(0)


                # --- Estrarre e processare Related Searches ---
                if depth < max_depth:
                    related_searches_urls = scholar_linker(result.markdown.raw_markdown)
                    print(f"[Depth {depth}] Found {len(related_searches_urls)} potential related searches. Exploring next level (Depth {depth + 1})...")
                    
                    for related_url in related_searches_urls:
                        parsed_related_url = urlparse(related_url)
                        related_query_params = parse_qs(parsed_related_url.query)
                        related_search_string = related_query_params.get('q', [''])[0]

                        if related_search_string:
                            tasks.append(
                                asyncio.create_task(
                                    extract_and_process_url(
                                        crawler,
                                        base_scholar_url_template,
                                        related_search_string,
                                        depth + 1,
                                        schema_extractor,
                                        scholar_linker,
                                        max_depth,
                                        output_filename 
                                    )
                                )
                            )
                
            else:
                print(f"[Depth {depth}] No raw markdown content for {current_url}")

            # --- Gestione ed estrazione dei dati strutturati (i papers) ---
            # Il campo 'extracted_content' dovrebbe ora essere popolato dal crawler
            if hasattr(result, 'extracted_content') and result.extracted_content:
                extracted_count = 0
                items_to_process = []

                if isinstance(result.extracted_content, list):
                    items_to_process = result.extracted_content
                elif isinstance(result.extracted_content, dict):
                    items_to_process = [result.extracted_content]

                for item in items_to_process:
                    if isinstance(item, dict) and 'url' in item:
                        paper_url = item['url']
                        if paper_url not in all_extracted_result_urls:
                            all_extracted_result_urls.add(paper_url)
                            all_extracted_data.append(item)
                            print(f"[Depth {depth}] Extracted NEW paper URL: {paper_url}")
                            extracted_count += 1
                        else:
                            print(f"[Depth {depth}] Skipping already extracted paper URL: {paper_url}")
                    else:
                        all_extracted_data.append(item)
                        extracted_count += 1
                        print(f"[Depth {depth}] Extracted item without URL (deduplication by URL skipped): {item}")

                print(f"[Depth {depth}] Successfully extracted {extracted_count} NEW structured papers from {current_url}")
            else:
                print(f"[Depth {depth}] No structured content (papers) extracted for {current_url}")
                if hasattr(result, 'error') and result.error:
                    print(f"[Depth {depth}] Crawler error: {result.error}")

        except Exception as e:
            print(f"[Depth {depth}] Error processing {current_url}: {e}")

    if tasks:
        await run_tasks_with_concurrency_limit(tasks, MAX_CONCURRENT_TASKS)

async def run_tasks_with_concurrency_limit(tasks, limit):
    semaphore = asyncio.Semaphore(limit)

    async def semaphored_task(task):
        async with semaphore:
            return await task

    if tasks:
        await asyncio.gather(*[semaphored_task(task) for task in tasks])

def save_to_jsonl(data: list, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"\nDati estratti salvati in '{filename}' ({len(data)} righe).")

async def main():
    initial_search_strings = ['LLM']
    base_scholar_url_template = "https://scholar.google.com/scholar?hl=en&as_sdt=0,5"

    schema_extractor = LLMSchemaExtractor()
    scholar_linker = GoogleScholarRelatedSearchExtractor()
    output_papers_filename = "/home/tiziano/progetti/workscrape/data/extracted_scholar_papers.jsonl"

    # === Modifica cruciale per usare il browser ===
    # Definisci la configurazione del browser. `headless=True` per non mostrare l'interfaccia grafica.
    browser_config = BrowserConfig(headless=True, java_script_enabled=True)

    # Passa la configurazione del browser all'AsyncWebCrawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        initial_tasks = []
        for search_str in initial_search_strings:
            initial_tasks.append(
                asyncio.create_task(
                    extract_and_process_url(
                        crawler,
                        base_scholar_url_template,
                        search_str,
                        depth=1,
                        schema_extractor=schema_extractor,
                        scholar_linker=scholar_linker,
                        max_depth=2,
                        output_filename=output_papers_filename
                    )
                )
            )
        await run_tasks_with_concurrency_limit(initial_tasks, MAX_CONCURRENT_TASKS)

    print("\n--- Processo di crawling completato ---")
    print(f"Numero totale di URL di ricerca unici processati: {len(processed_urls)}")
    print(f"Numero totale di URL di paper unici estratti: {len(all_extracted_result_urls)}")
    print(f"Numero totale di articoli strutturati (dopo deduplicazione): {len(all_extracted_data)}")

    save_to_jsonl(all_extracted_data, output_papers_filename)

    print("\nEsempio di URL di paper estratti (primi 10):")
    for i, url in enumerate(list(all_extracted_result_urls)[:10]):
        print(f"- {url}")

    print(f"\nEsempio di dati estratti (primi 2 articoli da '{output_papers_filename}'):")
    for i, item in enumerate(all_extracted_data[:2]):
        print(json.dumps(item, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())