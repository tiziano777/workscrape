import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, Any, Optional, List
import os
import json

from states.ArxivState import State

class ChromaDB:
    """
    Client per il database vettoriale che gestisce la connessione,
    il controllo di esistenza del documento e il salvataggio degli embeddings
    con i metadati. Questa classe funge anche da nodo LangGraph.
    """
    
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "arxiv_abstracts"):
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

    def _check_document_exists(self, doc_id: str) -> bool:
        """
        Controlla se un documento con un dato ID esiste già nel DB vettoriale.
        
        Args:
            doc_id (str): L'ID del documento da cercare.
        
        Returns:
            bool: True se il documento esiste, False altrimenti.
        """
        try:
            results = self.collection.get(ids=[doc_id])
            return len(results['ids']) > 0
        except Exception as e:
            print(f"Errore durante il controllo del documento: {e}")
            return False

    def save_document(self, doc: Dict[str, Any], query: str) -> Optional[str]:
        """
        Salva un documento nel database vettoriale se non esiste già.
        
        Args:
            doc (Dict): Il dizionario del documento da salvare, che deve contenere
                        la chiave 'id' e 'abstract'.
                        
        Returns:
            Optional[str]: L'ID del documento salvato, o None se non è stato salvato.
        """

        doc_id = doc.id
        abstract = doc.abstract

        if not doc_id or not abstract:
            print("⚠️ Documento non valido: mancano 'id' o 'abstract'.")
            return None

        if self._check_document_exists(doc_id):
            print(f"✅ Documento con ID '{doc_id}' esiste già. Salvataggio saltato.")
            return None

        try:
            # Prepara il documento per ChromaDB.
            doc_dict = doc.model_dump()
            metadata = {k: v for k, v in doc_dict.items() if k != 'abstract' and k != 'id'}
            metadata['query_string'] = query
            
            # Converte le liste in stringhe JSON per la compatibilità con i metadati di ChromaDB
            for key, value in metadata.items():
                if isinstance(value, list):
                    metadata[key] = json.dumps(value)
            
            self.collection.add(
                documents=[abstract],
                metadatas=[metadata],
                ids=[doc_id]
            )
            print(f"✅ Documento con ID '{doc_id}' salvato con successo.")
            return doc_id
        
        except Exception as e:
            print(f"❌ Errore durante il salvataggio del documento '{doc_id}': {e}")
            return None

    def __call__(self, state: State) -> State:
        """
        Metodo che funge da nodo per LangGraph. 
        Salva gli articoli dallo stato nel database vettoriale.
        """
        query = state.query_string
        articles_to_process = state.articles
        if not articles_to_process:
            print("⚠️ Nessun articolo da salvare nello stato. Operazione saltata.")
            state.error_status.append("Nessun articolo da salvare nello stato.")
            return state

        for doc_model in articles_to_process:
            self.save_document(doc_model,query) 
        
        return state