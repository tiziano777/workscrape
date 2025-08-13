<frameworks>
we use langgprah framework, and also langchain for additional functionalities.
in .continue/docs there are the following documentation txt files:
- langgraph-llms-full.txt: contains examples expalined.
- langgraph-llms.txt: contains markdown links usefull to research info from online langgraph documentation
- langchain-llms.txt: contains markdown links usefull to research info from online langchain documentation

For a quick overview on how setup a API LLM:
https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html

For observability, we use langfuse:
https://langfuse.com/docs/observability/sdk/python/sdk-v3

As vector storage, we us qdrant open source:
https://github.com/qdrant/qdrant-client

</frameworks>

<code-structure>
.continue/                       # code asssitant folder, contains rules, mcpServer etc..
docs/
    langgraph-llms.txt           # Markdown con link alla documentazione ufficiale LangGraph
    langgraph-llms-full.text     # Testo completo estratto dalla documentazione
    labngchain-llms.txt          # Extra: link/markdown per strumenti LangChain integrabili
config/                          # File YAML di configurazione (LLM, DB, HTTP, ecc.)
data/                            # Dati in input/output, dataset, cache controllata
log/                             # Log e tracciabilità esecuzioni
nodes/                           # Nodi LangGraph (classi Python: State -> State)
pipelines/                       # Grafi/pipeline: nodi + ponti + policy/strategie
state/                           # Definizione pydantic/typing degli State
utils/                           # Client, LLMClient, interfacce, operazioni dati, helper
main.py                          # Esecuzione/test rapido di una pipeline
requirements.txt                 # Dipendenze
.gitignore                       # Regole git
.env                             # API KEY and secrets
README.md                        # Istruzioni operative
</code-structure>

<description>
We want to create an agent capable to create a strong KB from arxiv articles.
The input is a search string s.t. "LLM".
Output can be:
a set of papers refs, stored in high level with its abstract,
and another collection that stores chunks of the entire paper.
</description>


<high-level-procedure>
We want to build a langgraph agent capable to:
0. Given a "search_string" in input
1. Perform API cal to axiv API endpoint
2. Store formatted results in a vector storage collection called 'abstracts'

3. For every html_id obtained
    3.1 use a crawler for extract structured markdown from every arxiv html content
    3.2 chunk by section the content
    3.3 summarize the sections
    3.4 lower the content
    3.5 also creates an dddtional metadata fields that is a list of link that appears in the chunk
4. these chunks can be stored into a vector storage collection called "chunks" with relative metadata. 
</high-level-procedure>

