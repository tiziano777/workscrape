import os
import logging
import traceback
from dotenv import load_dotenv
load_dotenv()

# Langchain and Langgraph Components
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, END, StateGraph

# Nodes,states
from states.ArxivPdfContentState import State

# Retrive
from nodes.crawlers.ArxivFetcher import ArxivFetcher
# Chunk by sections
from nodes.chunker.SectionChunker import SectionChunker
# parallel tasks, keyqwords and references extractions
from nodes.preprocessors.ArxivReferencesExtractor import ArxivReferencesExtractor
from nodes.preprocessors.ArxivKeywordsExtractor import ArxivKeywordsExtractor
# text preprocessing
from nodes.preprocessors.ArxivPreprocessor import ArxivPreprocessor
# Vector storage
from nodes.storage.ChunkChromaDB import ChunkChromaDB as ChromaDB

# Langfuse classes
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

# Configura l'SDK di Langfuse
# Sostituisci le chiavi con le tue credenziali
langfuse = Langfuse( 
    public_key= os.environ.get('LANGFUSE_PUBLIC_KEY'),
    secret_key= os.environ.get('LANGFUSE_PRIVATE_KEY'), 
    host= os.environ.get('LANGFUSE_STRING_CONNECTION')
)
langfuse_handler = CallbackHandler()

# === Setup Logging ===
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)
log_filename = os.path.join(log_dir, f"arxiv_pipeline.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_pipeline(fetcher: ArxivFetcher, chunker: SectionChunker, keyword: ArxivKeywordsExtractor, references: ArxivReferencesExtractor, preprocessor: ArxivPreprocessor, writer: ChromaDB):
    """
    Crea e compila la pipeline Langgraph.
    """
    workflow = StateGraph(State)
    workflow.add_node("arxiv_fetcher_node", fetcher)
    workflow.add_node("section_chunker_node", chunker)
    workflow.add_node("keyword_extraction_node", keyword)
    workflow.add_node("references_extraction_node", references)
    workflow.add_node("preprocessing_node", preprocessor)
    workflow.add_node("writer_node", writer)
    
    

    # Definizione del flusso di lavoro (edges)
    workflow.add_edge(START, "arxiv_fetcher_node")
    workflow.add_edge("arxiv_fetcher_node", "section_chunker_node")

    # try to parallelize keywords and references extraction
    workflow.add_edge("section_chunker_node", "keyword_extraction_node")
    workflow.add_edge("keyword_extraction_node", "references_extraction_node")


    workflow.add_edge("references_extraction_node", "preprocessing_node")

    workflow.add_edge("preprocessing_node", "writer_node")
    workflow.add_edge("writer_node", END)

    pipeline = workflow.compile()

    try:
        graphImage = pipeline.get_graph().draw_mermaid_png()
        with open("images/gemini_api_llm_chunk_pipeline.png", "wb") as f:
            f.write(graphImage)
        logger.info("Salvata immagine del grafo in graph.png")
    except Exception as e:
        logger.warning(f"Errore durante la generazione del grafo: {e}")
        logger.debug(traceback.format_exc())

    return pipeline

async def run_pipeline(url, geminiConfig, dbConfig, prompts):
    """
    Esegue la pipeline Langgraph con la configurazione specificata.
    """

    db_path = dbConfig['db_path']
    collection_name = dbConfig['db_collection']
    keyword_prompt = prompts['keyword_prompt']
    reference_prompt = prompts['reference_prompt']

    # Inizializza il modello LLM
    geminiLLM = ChatGoogleGenerativeAI(
        model = geminiConfig["model_name"],
        google_api_key = geminiConfig["gemini_api_key"],
        temperature = geminiConfig["temperature"],
        max_output_tokens = geminiConfig["max_output_tokens"],
        top_p = geminiConfig["top_p"],
        top_k = geminiConfig.get("top_k", None),
    )

    # Inizializzazione delle classi dei nodi
    fetcher = ArxivFetcher()
    chunker = SectionChunker()
    keyword = ArxivKeywordsExtractor(llm=geminiLLM, keyword_prompt=keyword_prompt)
    references = ArxivReferencesExtractor(llm=geminiLLM, reference_prompt=reference_prompt)
    preprocessor = ArxivPreprocessor()
    writer = ChromaDB(db_path,collection_name)
    
    # Crea la pipeline
    graph = create_pipeline(fetcher, chunker, keyword, references, preprocessor, writer)

    ### Langfuse ### 
    # `config={"callbacks": [langfuse_handler]}`

    try:
        # Invocazione della pipeline con tracciamento Langfuse
        state = await graph.ainvoke({"url": url}, config={"callbacks": [langfuse_handler]})

        error_status = state.get('error_status',[])
        if error_status == []:
            logger.warning(f"Errore nello stato per query = {url} : {state['error_status']}")
            
        return state
                
    except Exception as e:
        print(traceback.format_exc())
        logger.error(f"Errore durante l'invocazione della pipeline al checkpoint {url}: {e}")
        exit(1)

