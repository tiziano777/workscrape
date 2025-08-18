# workscrape
workscrape is a project that uses Langgraph to build two distinct agents designed to create a comprehensive knowledge base from scientific papers on arXiv. It focuses on smart data retrieval and processing to build a structured, queryable knowledge base.

## 🌟 Project Overview
This project implements two core agents to automate the process of collecting and structuring information from arXiv:

**First-Level Agent** ( ArxivAbstractScraperPipeline ): This agent takes a simple search string (e.g., "LLM") as input. It queries the arXiv API to retrieve a list of relevant papers, including their URLs, abstracts, and high-level metadata. The output is a structured list of paper references.

**Second-Level Agent** ( ArxivPaperExtractorPipeline ): This agent accepts a list of selected arXiv paper URLs as input. It crawls each paper to extract its content, intelligently breaking it down into logical chunks. This process preserves the original formatting, including LaTeX and HTML tags, to ensure no key information from formulas or sections is lost during the ingestion process. The final output is a structured dictionary for each paper, ready for ingestion into a vector store.

## ⚙️ Key Technologies
**Langgraph**: The core framework for building the agentic workflows.

**LangChain**: Used for additional functionalities, such as interacting with language models and other tools.

**Langfuse**: Provides observability and debugging capabilities for the Langgraph pipelines, allowing you to trace every step of the agent's execution.

**ChromaDB**: An open-source vector database used for storing and querying the processed paper chunks.

**Pydantic**: Used for defining robust data schemas, ensuring data consistency across the different states and nodes of the pipeline.

## 📂 Code Structure

```bash
docs/                            # Documentation files (links, full text)
    langgraph-llms.txt
    langgraph-llms-full.text
    langchain-llms.txt
config/                          # YAML configuration for prompts, LLM settings, etc.
images/                          # Architecture diagrams
crawler_examples/                # Crawl4AI examples
data/                            # Input/output data, datasets, cache
log/                             # Execution logs
nodes/                           # Langgraph nodes (Python classes)
pipelines/                       # Graph definitions (nodes, edges, policies)
states/                          # Pydantic state definitions
utils/                           # Clients, helpers, data operations
main.py                          # Main entry point to run a pipeline
requirements.txt                 # Project dependencies
.gitignore                       # Git ignore rules
.env                             # Environment variables (API keys)
.env.template                    # Template for the .env file
README.md                        # This file
PLANNING.md                      # Project planning overview
```

## 🛠️ Setup and Installation
1. Prerequisites

Python 3.10+
Docker & Docker Compose (for Langfuse)

2. Clone the Repository
```bash
git clone https://github.com/your-username/workscrape.git
cd workscrape
```

3. Set up the Environment
Create a new .env file by copying the template. Fill in your API keys and secrets.

```bash
cp .env.template .env
```

4. Install Dependencies
Install the required Python libraries using pip.

```bash
pip install -r requirements.txt
```

5. Run Langfuse
Langfuse is crucial for observability. Use Docker Compose to get it running locally.
In a separate directory (e.g., outside workscrape)

```bash
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker compose up -d
```
Your Langfuse instance will be available at http://localhost:3000. You can then use the provided keys in your .env file.

6. Run the Pipeline
To execute a pipeline, you can run the main.py script. It will load the configuration and start the agents.

```bash
python main.py
```

This will start the pipeline, and you can monitor its execution in the Langfuse UI at http://localhost:3000.
