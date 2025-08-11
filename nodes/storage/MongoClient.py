import os
import json
import pymongo
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

# Carica le variabili d'ambiente dal file .env
load_dotenv()
# Recupera la stringa di connessione da una variabile d'ambiente
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
if not MONGODB_CONNECTION_STRING:
    raise ValueError("MONGODB_CONNECTION_STRING environment variable not set. Please set it in your .env file.")



class MongoClient:
    """
    Gestisce le operazioni di INSERT per un database MongoDB.
    Permette di specificare il database, la collezione e lo schema di validazione
    al momento dell'istanza.
    """

    def __init__(self, db_name: str, collection_name: str, schema_file_path: str):
        """
        Inizializza la connessione al client MongoDB e seleziona il database e la collezione.
        Carica lo schema JSON da un file e crea un indice univoco sul campo 'id'.

        Args:
            db_name (str): Il nome del database.
            collection_name (str): Il nome della collezione.
            schema_file_path (str): Il percorso del file dello schema JSON.
        """
        try:
            self.client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            print(f"✅ Connessione a MongoDB stabilita con successo. Database: '{db_name}', Collezione: '{collection_name}'")

            # Carica lo schema JSON da un file esterno
            with open(schema_file_path, 'r') as f:
                self.schema = json.load(f)

            # Crea un indice univoco sul campo 'id'.
            self.collection.create_index([("id", pymongo.ASCENDING)], unique=True)
            print("✅ Indice univoco sul campo 'id' creato/verificato.")
        except pymongo.errors.ConnectionFailure as e:
            print(f"❌ Errore di connessione a MongoDB: {e}")
            raise
        except FileNotFoundError as e:
            print(f"❌ Errore: file dello schema non trovato al percorso '{schema_file_path}'.")
            raise
        except Exception as e:
            print(f"❌ Si è verificato un errore inatteso durante l'inizializzazione: {e}")
            raise

    def _validate_document(self, doc: dict) -> bool:
        """
        Metodo interno per validare un singolo documento rispetto allo schema JSON caricato.
        
        Args:
            doc (dict): Il documento da validare.
        
        Returns:
            bool: True se il documento è valido, altrimenti False.
        """
        try:
            validate(instance=doc, schema=self.schema)
            return True
        except ValidationError as e:
            print(f"⚠️ Errore di validazione per il documento con ID '{doc.get('id')}': {e.message}")
            return False

    def insert(self, documents: list[dict]):
        """
        Inserisce una lista di documenti nella collezione.
        Ogni documento viene validato prima dell'inserimento.
        Se un documento non supera la validazione o ha un 'id' già esistente, viene saltato.

        Args:
            documents (list[dict]): Una lista di dizionari, dove ogni dizionario
                                    rappresenta un documento da inserire.
        """
        if not documents:
            print("Nessun documento da inserire.")
            return

        inserted_count = 0
        skipped_count = 0
        total_count = len(documents)
        print(f"Tentativo di inserire {total_count} documenti...")

        for doc in documents:
            if not self._validate_document(doc):
                skipped_count += 1
                continue

            try:
                self.collection.insert_one(doc)
                inserted_count += 1
            except DuplicateKeyError:
                skipped_count += 1
                print(f"⚠️ Documento con ID '{doc.get('id')}' già presente, saltato.")
            except Exception as e:
                print(f"❌ Errore durante l'inserimento del documento: {e}")

        print("\n--- Riepilogo Inserimento ---")
        print(f"✅ Documenti inseriti con successo: {inserted_count}")
        print(f"➡️ Documenti saltati (duplicati o non validi): {skipped_count}")
        print(f"📝 Totale documenti processati: {total_count}")
