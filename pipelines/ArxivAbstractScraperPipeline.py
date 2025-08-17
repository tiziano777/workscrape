import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, Any, Optional, List
import os
import json
import yaml
import logging
import traceback

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, END, StateGraph

from states.ArxivState import State

from nodes.crawlers.ArxivApiClient import ArxivApiClient
from nodes.preprocessors.GeminiKeywordExtractor import GeminiKeywordExtractor
from nodes.storage.ChromaDB import ChromaDB

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

langfuse = Langfuse(
    public_key="pk-lf-faa982dc-270f-4990-93bb-199a94d62e94",
    secret_key="sk-lf-23dbe47b-3611-426d-9d6f-f14d8bad6c3c",
    host="http://localhost:3000"
)
langfuse_handler = CallbackHandler()

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

def create_pipeline(arxixClient: ArxivApiClient, preprocessor: GeminiKeywordExtractor, writer: ChromaDB):

    workflow = StateGraph(State)
    workflow.add_node("arxiv_searcher", arxixClient)
    workflow.add_node("writer_node", writer)
    workflow.add_node("preprocessor_node", preprocessor)

    workflow.add_edge(START, "arxiv_searcher")
    workflow.add_edge("arxiv_searcher", "preprocessor_node")
    workflow.add_edge("preprocessor_node", "writer_node")
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

def run_pipeline(query, geminiConfig, dbConfig, prompts):

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
    #mistralLLM = {}

    # CLASSI NODI
    arxivClient = ArxivApiClient(max_results=20)
    preprocessor = GeminiKeywordExtractor(llm = geminiLLM, prompt=keyword_prompt)
    writer = ChromaDB(db_path,collection_name)
    
    # CREATE PIPELINE CALL
    graph = create_pipeline(arxivClient, preprocessor, writer)

    # PIPELINE INVOCATION 
    # =======================================================
    # Invocazione della pipeline con tracciamento Langfuse
    # =======================================================
 
    try:
        state = graph.invoke({"query_string": query}, config={"callbacks": [langfuse_handler]})

        if state['error_status'] is not None:
            logger.warning(f"Errore nello stato per query = {query} : {state['error_status']}")
                
                
    except Exception as e:
        print(traceback.format_exc())
        logger.error(f"Errore durante l'invocazione della pipeline al checkpoint {query}: {e}")

        return state
