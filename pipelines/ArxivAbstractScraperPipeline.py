import os
import logging
import traceback
from dotenv import load_dotenv
load_dotenv()

# Langchain and Langgraph Components
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, END, StateGraph

# Nodes,states
from states.ArxivState import State
from nodes.crawlers.ArxivApiClient import ArxivApiClient
from nodes.preprocessors.GeminiKeywordExtractor import GeminiKeywordExtractor
from nodes.preprocessors.ArxivPreprocessor import ArxivPreprocessor
from nodes.storage.AbstractChromaDB import AbstractChromaDB as ChromaDB

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

def create_pipeline(arxivClient: ArxivApiClient, preprocessor1: ArxivPreprocessor, preprocessor2: GeminiKeywordExtractor, writer: ChromaDB):
    """
    Crea e compila la pipeline Langgraph.
    """
    workflow = StateGraph(State)
    workflow.add_node("arxiv_searcher", arxivClient)
    workflow.add_node("writer_node", writer)
    workflow.add_node("preprocessing_node", preprocessor1)
    workflow.add_node("keyword_node", preprocessor2)
    

    # Definizione del flusso di lavoro (edges)
    workflow.add_edge(START, "arxiv_searcher")
    workflow.add_edge("arxiv_searcher", "preprocessing_node")
    workflow.add_edge("preprocessing_node", "keyword_node")
    workflow.add_edge("keyword_node", "writer_node")
    workflow.add_edge("writer_node", END)

    pipeline = workflow.compile()

    try:
        graphImage = pipeline.get_graph().draw_mermaid_png()
        with open("images/gemini_api_llm_abstract_pipeline.png", "wb") as f:
            f.write(graphImage)
        logger.info("Salvata immagine del grafo in graph.png")
    except Exception as e:
        logger.warning(f"Errore durante la generazione del grafo: {e}")
        logger.debug(traceback.format_exc())

    return pipeline

def run_pipeline(query, geminiConfig, dbConfig, prompts):
    """
    Esegue la pipeline Langgraph con la configurazione specificata.
    """

    db_path = dbConfig['db_path']
    collection_name = dbConfig['db_collection']
    keyword_prompt = prompts['keyword_prompt']

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
    arxivClient = ArxivApiClient(max_results=1)
    preprocessor1 = GeminiKeywordExtractor(llm = geminiLLM, prompt=keyword_prompt)
    preprocessor2 = ArxivPreprocessor()
    writer = ChromaDB(db_path,collection_name)
    
    # Crea la pipeline
    graph = create_pipeline(arxivClient, preprocessor1, preprocessor2, writer)

    ### Langfuse ### 
    # `config={"callbacks": [langfuse_handler]}`

    try:
        # Invocazione della pipeline con tracciamento Langfuse
        state = graph.invoke({"query": query}, config={"callbacks": [langfuse_handler]})

        error_status = state.get('error_status',[])
        if error_status == []:
            logger.warning(f"Errore nello stato per query = {query} : {state['error_status']}")
            
        return state
                
    except Exception as e:
        print(traceback.format_exc())
        logger.error(f"Errore durante l'invocazione della pipeline al checkpoint {query}: {e}")
        exit(1)


