import chromadb
from chromadb.utils import embedding_functions

from states.ArxivPdfContentState import State



class ChunkChromaDB:
    """
    Client per il database vettoriale che gestisce la connessione,
    il controllo di esistenza del documento e il salvataggio degli embeddings
    con i metadati. Questa classe funge anche da nodo LangGraph.
    """
    
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "arxiv_chunks"):
        """
        Inizializza il client ChromaDB.
        
        Args:
            db_path (str): Il percorso della directory dove verranno salvati i dati del DB.
            collection_name (str): Il nome della collezione da usare.
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Inizializza il client ChromaDB in modalità persistente
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Sceglie un embedding function multilingue
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-mpnet-base-v2"
        )
        
        # Ottiene o crea la collezione
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        print(f"✅ Connesso a ChromaDB e alla collezione '{self.collection_name}'.")

    def _check_document_exists(self, url: str, key: str) -> bool:
        """
        Controlla se un documento (chunk) con una data coppia (url, key) esiste già.
        
        Args:
            url (str): L'URL del documento.
            key (str): La chiave (titolo della sezione) del chunk.
        
        Returns:
            bool: True se il chunk esiste, False altrimenti.
        """
        try:
            # Esegue una query sul DB per cercare metadati corrispondenti
            results = self.collection.get(
                where={
                    "$and": [
                        {"url": {"$eq": url}},
                        {"key": {"$eq": key}}
                    ]
                }
            )
            # Se vengono trovati dei risultati, il documento esiste
            return len(results['ids']) > 0
        except Exception as e:
            print(f"❌ Errore durante il controllo di esistenza per (url='{url}', key='{key}'): {e}")
            return False

    def save_document(self, state: State) -> State:
        """
        Salva i chunk riassunti nel database vettoriale, se non esistono già.
        
        Args:
            state (State): Lo stato LangGraph contenente 'url' e 'summarized_chunks'.
            
        Returns:
            State: Lo stato aggiornato con eventuali messaggi di errore.
        """
        if not state.url or not state.summarized_chunks:
            error_msg = "Il campo 'url' o 'summarized_chunks' è vuoto. Salvataggio saltato."
            print(f"⚠️  {error_msg}")
            state.error_status.append(error_msg)
            return state

        for key, summarized_text in state.summarized_chunks.items():
            try:
                if self._check_document_exists(state.url, key):
                    print(f"✅ Chunk (url='{state.url}', key='{key}') esiste già. Salvataggio saltato.")
                    continue
                
                # Prepara i dati per l'upsert
                documents = [summarized_text]
                metadatas = [{"url": state.url, "key": key}]
                ids = [f"{state.url}-{key}"] # Crea un ID univoco
                
                # Aggiunge (o aggiorna) il chunk nel database
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"✔️ Salvato il chunk (url='{state.url}', key='{key}').")
                
            except Exception as e:
                error_msg = f"❌ Errore durante il salvataggio del chunk (url='{state.url}', key='{key}'): {e}"
                print(error_msg)
                state.error_status.append(error_msg)
        
        return state

    def __call__(self, state: State) -> State:
        """
        Nodo LangGraph che esegue il salvataggio dei chunk.
        """
        return self.save_document(state)