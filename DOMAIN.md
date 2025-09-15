<frameworks>
1. we use langgprah framework, and also langchain for additional functionalities.
    in .continue/docs there are the following documentation txt files:
    - langgraph-llms-full.txt: contains examples expalined.
    - langgraph-llms.txt: contains markdown links usefull to research info from online langgraph documentation
    - langchain-llms.txt: contains markdown links usefull to research info from online langchain documentation

2. For a quick overview on how setup a API LLM:
    https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html

3. For observability, we use langfuse:
https://langfuse.com/guides/cookbook/integration_langgraph

4. As vector storage, we use open source chromaDB
</frameworks>

<code-structure>
.venv/                           # (ignored) virtualenv, reccomended to create a virtualenv for our agent
chroma_db/                       # (ignored) chromaDB database, used for store vectors
docs/                            # Documentation files (links, full text)
    langgraph-llms.txt           # langgraph docs, markdown: [url description] https://doc.url
    langgraph-llms-full.text     # langgraph docs, full-text
    langchain-llms.txt           # langchain docs, markdown: [url description] https://doc.url
config/                          # YAML configuration for prompts, LLM, storage, API call, http, crawler etc.
images/                          # Architecture diagrams
crawler_examples/                # Crawl4AI examples
data/                            # Input/output data, datasets, cache
log/                             # (ignored) Execution logs
nodes/*                          # Langgraph nodes (Python classes)
pipelines/*                      # Graph definitions (nodes, edges, policies)
states/*                         # Pydantic state definitions
utils/                           # Embed function, Clients, helpers, data operations
main.py                          # Main entry point to run a pipeline
requirements.txt                 # Project dependencies
.gitignore                       # Git ignore rules
.env                             # (ignored) Environment variables (API keys)
.env.template                    # Template for the .env file
README.md                        # Project overview
PLANNING.md                      # This file
</code-structure>

<description>
We want to create two different agents capable to create a strong KB from arxiv articles.

- First-level agent is used to retrive a list or url and abstract by querying Arxiv API.
The input is a search string s.t. "LLM".
Output can be:
a set of papers refs, stored in high level with its abstract.

- Second-level Crawler Agent is used to retrive and store chunks from paper url.
The input is a set of selected arxiv urls.
Output can be a structured dict for each paper, that contains related section chunks. 
</description>
