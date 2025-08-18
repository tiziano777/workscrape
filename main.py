from states.ArxivState import State
from pipelines.ArxivAbstractScraperPipeline import run_pipeline
import asyncio
import yaml
import os
from dotenv import load_dotenv
load_dotenv()

async def main():

    ### QUERY SEARCH STRING ###
    query_string = "LLM"

    MODEL_CONFIG = "./config/gemini2.0-flash.yml"
    PROMPTS_PATH = "./config/prompts.yml"
    DB_CONFIG = "./config/storage_config/abstracts_chromadb.yml"

    with open(MODEL_CONFIG, "r", encoding="utf-8") as f:
        llmConfig = yaml.safe_load(f)

    api_key = os.environ.get("GEMINI_API_KEY")
    llmConfig["gemini_api_key"] = api_key

    with open(DB_CONFIG, "r", encoding="utf-8") as f:
        dbConfig = yaml.safe_load(f)

    with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
        prompts = yaml.safe_load(f)

    result = run_pipeline(query_string, geminiConfig=llmConfig, dbConfig=dbConfig, prompts=prompts)
    print(result)
    
    



    


asyncio.run(main())