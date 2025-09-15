import time
import chromadb
from chromadb.utils import embedding_functions

time.sleep(2) # Per dare tempo al DB di sincronizzare
client = chromadb.PersistentClient(path="../chroma_db")

# Aggiungi questa linea
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-mpnet-base-v2")

# Sostituisci la linea problematica con get_or_create_collection
collection = client.get_or_create_collection(
    name="arxiv_abstracts", 
    embedding_function=embedding_function
)

count = collection.count()
print(f"✅ CONTEGGIO DI TEST NELLA PIPELINE: {count} documenti trovati.")