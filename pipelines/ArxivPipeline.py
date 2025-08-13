'''

TODO: this is only the scheletro preso da un altro prgetto!!

'''
import json
import os
import yaml
import logging
import traceback

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, END, StateGraph

from states.ner_state import State

from nodes.crawlers.ArxivApiClient import ArxivApiClient
from nodes.OCR.MistralOCR import MistralOCR
from nodes.storage.MongoClient import MongoClient

from langfuse import Langfuse
from langfuse.model import CreateTrace

# Carica le chiavi API Langfuse dalle variabili d'ambiente
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    langfuse = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY
    )
    print("✅ Langfuse client inizializzato con successo.")
else:
    print("⚠️ Chiavi API Langfuse non impostate. L'osservabilità Langfuse non sarà attiva.")
    langfuse = None

# === Setup Logging ===
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)
log_filename = os.path.join(log_dir, f"arxiv_pipeline.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_pipeline(arxixClient: ArxivApiClient, ocr: MistralOCR, writer: MongoClient):

    workflow = StateGraph(State)
    workflow.add_node("arxiv_searcher", arxixClient)
    workflow.add_node("OCR_node", ocr)
    workflow.add_node("writer_node", writer)

    workflow.add_edge(START, "arxiv_searcher")
    workflow.add_edge("arxiv_searcher", "OCR_node")
    workflow.add_edge("OCR_node","writer_node")
    workflow.add_edge("writer_node", END)

    pipeline = workflow.compile()

    try:
        graphImage = pipeline.get_graph().draw_mermaid_png()
        with open("images/gemini_api_llm_ner_pipeline.png", "wb") as f:
            f.write(graphImage)
        logger.info("Salvata immagine del grafo in graph.png")
    except Exception as e:
        logger.warning(f"Errore durante la generazione del grafo: {e}")
        logger.debug(traceback.format_exc())

    return pipeline

def run_pipeline(query, mistralConfig, geminiConfig, dbConfig):
    
    db_name=dbConfig['db_name']
    collection_name=dbConfig['db_collection']

    # Inizializza il modello LLM
    geminiLLM = ChatGoogleGenerativeAI(
        model = geminiConfig["model_name"],
        google_api_key = geminiConfig["gemini_api_key"],
        temperature = geminiConfig["temperature"],
        max_output_tokens = geminiConfig["max_output_tokens"],
        top_p = geminiConfig["top_p"],
        top_k = geminiConfig.get("top_k", None),
    )
    mistralLLM = {}

    # CLASSI NODI
    arxivClient = ArxivApiClient(llm = geminiLLM)
    mistralOCR = MistralOCR(llm = mistralLLM)
    writer = MongoClient(db_name = db_name, collection_name = collection_name)
    

    # CREATE PIPELINE CALL
    graph = create_pipeline(arxivClient, mistralOCR, writer)

    # PIPELINE INVOCATION 
    # =======================================================
    # Invocazione della pipeline con tracciamento Langfuse
    # =======================================================
    if langfuse:
        trace_id = f"arxiv_pipeline_trace_{query.replace(' ', '_')}"
        trace = langfuse.trace(CreateTrace(id=trace_id, name="Arxiv Pipeline"))

        try:
            state = graph.invoke(
                {"query_string": query},
                {"langfuse_parent_observation_id": trace.id}
            )

            if state['error_status'] is not None:
                logger.warning(f"Errore nello stato per query = {query} : {state['error_status']}")
                        
        except Exception as e:
            print(traceback.format_exc())
            logger.error(f"Errore durante l'invocazione della pipeline al checkpoint {query}: {e}")
        
        logger.info("Esecuzione completata e tracciata su Langfuse.")

    else:
        # Codice di fallback senza Langfuse
        try:
            state = graph.invoke({"query_string": query})

            if state['error_status'] is not None:
                logger.warning(f"Errore nello stato per query = {query} : {state['error_status']}")
                        
        except Exception as e:
            print(traceback.format_exc())
            logger.error(f"Errore durante l'invocazione della pipeline al checkpoint {query}: {e}")
            
        logger.info("Esecuzione completata (senza tracciamento Langfuse).")