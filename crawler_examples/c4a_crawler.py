"""
Google Scholar LLM Search Script
Utilizza Crawl4AI per cercare un valore testuale su Google Scholar costruendo un URL di ricerca diretto.
"""

import asyncio
from urllib.parse import quote_plus
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def search_google_scholar(search_query: str):
    """
    Naviga su Google Scholar, cerca un valore testuale e visualizza i risultati.
    
    Args:
        search_query (str): La query di ricerca da inserire.
    """
    
    # Configurazione browser - visibile per vedere cosa succede
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=False,  # False per vedere la navigazione in azione
        viewport_width=1280,
        viewport_height=720,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        java_script_enabled=True,
        ignore_https_errors=True
    )
    
    # Costruisci l'URL di ricerca diretto con la query codificata correttamente
    encoded_query = quote_plus(search_query)
    search_url = f"https://scholar.google.com/scholar?q={encoded_query}&hl=en&as_sdt=0,5"

    # Script C4A semplificato, ora naviga direttamente all'URL dei risultati
    c4a_script = f"""
        // Naviga direttamente all'URL dei risultati di ricerca
        GO {search_url}

        // Aspetta che i risultati siano caricati
        WAIT `#gs_res_ccl` 20
        
        // Aggiungi un ritardo per vedere i risultati prima che lo script finisca
        WAIT 5
    """
    
    # Configurazione del crawler
    run_config = CrawlerRunConfig(
        # L'URL iniziale del metodo arun viene sovrascritto dal comando GO
        # nel C4A script, ma lo passiamo comunque per chiarezza.
        url=search_url, 
        page_timeout=45000,
        screenshot=True,
        verbose=True,
        cache_mode="BYPASS",
        wait_until="networkidle",
        word_count_threshold=5,
        delay_before_return_html=3.0
    )
    
    try:
        print(f"🚀 Avvio del crawler per Google Scholar con query: '{search_query}'...")
        
        async with AsyncWebCrawler(config=browser_config, c4a_script=c4a_script) as crawler:
            result = await crawler.arun(
                url=run_config.url,
                config=run_config
            )
            
            if result.success:
                print("✅ Ricerca completata con successo!")
                print(f"🔗 URL finale: {result.url}")
                
                # Visualizza parte del contenuto Markdown
                print("\n" + "="*60)
                print("📝 CONTENUTO ESTRATTO (primi 1500 caratteri):")
                print("="*60)
                if result.markdown:
                    content_to_show = result.markdown[:1500]
                    print(content_to_show)
                    if len(result.markdown) > 1500:
                        print(f"\n... (e altri {len(result.markdown) - 1500} caratteri)")
                else:
                    print("Nessun contenuto markdown disponibile.")

            else:
                print("❌ Errore durante la ricerca:")
                print(f"🔴 Messaggio errore: {result.error_message}")
                print(f"📊 Status Code: {result.status_code}")
                
    except Exception as e:
        print(f"💥 Errore critico durante l'esecuzione: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Funzione principale per eseguire la ricerca con una query predefinita.
    """
    print("🎓 Google Scholar LLM Search con Crawl4AI")
    print("=" * 50)
    
    search_query = "Large Language Models in clinical medicine"  # Inserisci qui la tua query
    
    asyncio.run(search_google_scholar(search_query))
    
    print("\n" + "=" * 50)
    print("✅ Script completato!")

if __name__ == "__main__":
    main()
