from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import BM25ContentFilter, LLMContentFilter
from crawl4ai import LLMConfig

# --- OPZIONE 1: Markdown con regole di ranking su pattern match, ITF-IDF style ---

bm25_filter = BM25ContentFilter(
    user_query="arxiv",   # La tua query di ricerca
    bm25_threshold=0.3             # Soglia BM25 (più alta = meno contenuti)
    )
bm25_markdown_generator = DefaultMarkdownGenerator(content_filter=bm25_filter,options={"ignore_links": False})

# --- OPZIONE 2: Markdown Generator con LLM Filter (intelligente) ---

llm_filter = LLMContentFilter(
        llm_config=LLMConfig(
            provider="openai/gpt-4o",
            api_token="your-api-token"  # Oppure usa la variabile d'ambiente
        ),
        instruction="""
        Estrai solo il contenuto principale ed educativo:
        - Concetti chiave e spiegazioni
        - Esempi di codice importanti
        - Dettagli tecnici essenziali
        
        Escludi:
        - Elementi di navigazione
        - Sidebar e footer
        - Pubblicità e contenuti non rilevanti
        """,
        chunk_token_threshold=4096,     # Dimensione dei chunk per l'elaborazione
        verbose=True
    )

llm_markdown_generator = DefaultMarkdownGenerator(
    content_filter=llm_filter
)
