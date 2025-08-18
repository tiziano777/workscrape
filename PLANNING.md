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
.continue/                       # code asssitant folder, contains rules, mcpServer etc..
docs/
    langgraph-llms.txt           # Markdown con link alla documentazione ufficiale LangGraph
    langgraph-llms-full.text     # Testo completo estratto dalla documentazione
    labngchain-llms.txt          # Extra: link/markdown per strumenti LangChain integrabili
config/                          # File YAML di configurazione (Prompts, LLM, Database, http args, ecc.)
images/                          # Containing jpeg images of agent architectures
crawler_examples/                # Contains examples  of the use of crawl4ai crawling framework
data/                            # Dati in input/output, dataset, cache controllata
log/                             # Log e tracciabilità esecuzioni
nodes/                           # Nodi LangGraph (classi Python: State -> State)
pipelines/                       # Grafi/pipeline: nodi + ponti + policy/strategie
states/                           # Definizione pydantic/typing degli State
utils/                           # Client, LLMClient, interfacce, operazioni dati, helper
main.py                          # Esecuzione/test rapido di una pipeline
requirements.txt                 # Dipendenze da installare
.gitignore                       # Regole git
.env                             # API KEY and secrets
.env.template                    # env file without secrets, usefull when run git clone operation
README.md                        # Istruzioni operative
PLANNING.md                      # Project overview (this file)
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
