from states.ArxivState import State
from pipelines.ArxivPaperExtractorPipeline import run_pipeline
import asyncio
import yaml
import os
from dotenv import load_dotenv
load_dotenv()

async def main():

    ### QUERY SEARCH STRING ###
    url = "https://arxiv.org/html/2508.15260"

    # TODO:
    # check if 'url' exist in chromaDB 'arxiv_chunks' collection
    # if exists, return alert, "this paper is already in DB, skipping crawling process"
    # and then returns all chunks from the target PDF!

    MODEL_CONFIG = "./config/gemini2.0-flash.yml"
    PROMPTS_PATH = "./config/prompts.yml"
    DB_CONFIG = "./config/storage_config/chunks_chromadb.yml"

    with open(MODEL_CONFIG, "r", encoding="utf-8") as f:
        llmConfig = yaml.safe_load(f)

    api_key = os.environ.get("GEMINI_API_KEY")
    llmConfig["gemini_api_key"] = api_key

    with open(DB_CONFIG, "r", encoding="utf-8") as f:
        dbConfig = yaml.safe_load(f)

    with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
        prompts = yaml.safe_load(f)

    result = await run_pipeline(url, geminiConfig=llmConfig, dbConfig=dbConfig, prompts=prompts)

    
    

asyncio.run(main())