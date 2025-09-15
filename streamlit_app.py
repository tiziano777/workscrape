import streamlit as st
import chromadb
from chromadb.utils import embedding_functions

# --- Configurazione e inizializzazione di ChromaDB ---
DB_PATH = "chroma_db"
COLLECTION_NAME = "arxiv_chunks"

@st.cache_resource
def get_chroma_client():
    """Restituisce un client ChromaDB persistente e la collezione."""
    try:
        client = chromadb.PersistentClient(path=DB_PATH)
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-mpnet-base-v2"
        )
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function
        )
        return collection
    except Exception as e:
        st.error(f"❌ Errore di connessione a ChromaDB: {e}")
        st.stop()

# Ottieni la collezione all'avvio dell'app
collection = get_chroma_client()

# --- Funzioni di utilità per le operazioni sul database (CRUD) ---

def add_document(url: str, key: str, text: str):
    """Aggiunge un singolo chunk al database."""
    try:
        # Aggiungi .strip() per pulire gli input
        clean_url = url.strip()
        clean_key = key.strip()
        doc_id = f"{clean_url}-{clean_key}"

        if collection.get(ids=[doc_id])['ids']:
            st.warning(f"⚠️ Chunk con ID '{doc_id}' già esistente.")
            return False
        
        collection.add(
            documents=[text.strip()],
            metadatas=[{"url": clean_url, "key": clean_key}],
            ids=[doc_id]
        )
        st.success("✅ Documento aggiunto con successo!")
        return True
    except Exception as e:
        st.error(f"❌ Errore durante l'aggiunta: {e}")
        return False

def update_document(url: str, key: str, new_text: str):
    """Aggiorna il testo di un chunk esistente."""
    try:
        clean_url = url.strip()
        clean_key = key.strip()
        doc_id = f"{clean_url}-{clean_key}"
        
        if not collection.get(ids=[doc_id])['ids']:
            st.error(f"❌ Chunk con ID '{doc_id}' non trovato.")
            return False
        
        collection.update(
            ids=[doc_id],
            documents=[new_text.strip()]
        )
        st.success("✅ Chunk aggiornato con successo!")
        return True
    except Exception as e:
        st.error(f"❌ Errore durante l'aggiornamento: {e}")
        return False

def delete_document(url: str, key: str):
    """Elimina un chunk dal database."""
    try:
        clean_url = url.strip()
        clean_key = key.strip()
        doc_id = f"{clean_url}-{clean_key}"

        if not collection.get(ids=[doc_id])['ids']:
            st.warning(f"⚠️ Chunk con ID '{doc_id}' non trovato.")
            return False
            
        collection.delete(
            ids=[doc_id]
        )
        st.success("🗑️ Chunk eliminato con successo!")
        return True
    except Exception as e:
        st.error(f"❌ Errore durante l'eliminazione: {e}")
        return False

def count_documents():
    """Conta il numero totale di documenti nella collezione."""
    return collection.count()

def search_by_text(query: str, top_k: int = 5):
    """Esegue una ricerca per similarità di testo."""
    return collection.query(
        query_texts=[query.strip()],
        n_results=top_k,
        include=['metadatas', 'documents', 'distances']
    )

def search_by_url(url: str):
    """Cerca tutti i chunk associati a un URL specifico."""
    return collection.get(
        where={"url": {"$eq": url.strip()}},
        include=['metadatas', 'documents']
    )

# --- Interfaccia utente con Streamlit ---
st.set_page_config(page_title="ChromaDB KB Dashboard", layout="wide")
st.title("👨‍🔬 Dashboard Ricerca e Gestione KB")

# Sidebar per la navigazione
st.sidebar.header("Navigazione")
selected_option = st.sidebar.radio(
    "Scegli un'operazione:",
    ["🔍 Ricerca", "➕ Aggiungi", "🔄 Aggiorna", "🗑️ Elimina"]
)

# Strumento di diagnostica
if st.sidebar.button("Conta Documenti nel DB"):
    num_docs = count_documents()
    st.sidebar.info(f"Il tuo database contiene **{num_docs}** documenti.")

# Sezione Ricerca
if selected_option == "🔍 Ricerca":
    st.header("Ricerca nella Knowledge Base")
    search_type = st.radio("Seleziona il tipo di ricerca:", ["Ricerca testuale", "Ricerca per URL"])

    if search_type == "Ricerca testuale":
        query = st.text_input("Inserisci la stringa di ricerca:", placeholder="e.g., 'intelligenza artificiale generativa'")
        top_k = st.slider("Numero di risultati:", 1, 10, 5)
        if st.button("Cerca"):
            if query:
                with st.spinner("Ricerca in corso..."):
                    results = search_by_text(query, top_k)
                    if results['ids'][0]:
                        for i, doc_id in enumerate(results['ids'][0]):
                            metadata = results['metadatas'][0][i]
                            document = results['documents'][0][i]
                            distance = results['distances'][0][i]
                            st.subheader(f"Risultato {i+1} (Distanza: {distance:.2f})")
                            st.write(f"**URL:** {metadata['url']}")
                            st.write(f"**Chiave (key):** {metadata['key']}")
                            st.markdown(f"**Testo:**\n> {document}")
                            st.markdown("---")
                    else:
                        st.info("Nessun risultato trovato.")
            else:
                st.warning("Inserisci una stringa di ricerca.")
                
    elif search_type == "Ricerca per URL":
        url_query = st.text_input("Inserisci l'URL del documento:", placeholder="e.g., 'https://arxiv.org/abs/2301.12345'")
        if st.button("Cerca per URL"):
            if url_query:
                with st.spinner("Ricerca in corso..."):
                    results = search_by_url(url_query)
                    if results['ids']:
                        for i, doc_id in enumerate(results['ids']):
                            metadata = results['metadatas'][i]
                            document = results['documents'][i]
                            st.subheader(f"Chunk {i+1}:")
                            st.write(f"**URL:** {metadata['url']}")
                            st.write(f"**Chiave (key):** {metadata['key']}")
                            st.markdown(f"**Testo:**\n> {document}")
                            st.markdown("---")
                    else:
                        st.info("Nessun chunk trovato per l'URL specificato.")
            else:
                st.warning("Inserisci un URL.")

# --- Sezioni CRUD ---

elif selected_option == "➕ Aggiungi":
    st.header("Aggiungi un nuovo chunk")
    add_url = st.text_input("URL del documento:", key="add_url")
    add_key = st.text_input("Chiave (key) del chunk:", key="add_key")
    add_text = st.text_area("Testo da salvare:", height=200, key="add_text")
    
    if st.button("Aggiungi Chunk"):
        if add_url and add_key and add_text:
            add_document(add_url, add_key, add_text)
        else:
            st.warning("Per favore, compila tutti i campi.")

elif selected_option == "🔄 Aggiorna":
    st.header("Aggiorna un chunk esistente")
    update_url = st.text_input("URL del documento:", key="update_url")
    update_key = st.text_input("Chiave (key) del chunk:", key="update_key")
    update_text = st.text_area("Nuovo testo per il chunk:", height=200, key="update_text")
    
    if st.button("Aggiorna Chunk"):
        if update_url and update_key and update_text:
            update_document(update_url, update_key, update_text)
        else:
            st.warning("Per favore, compila tutti i campi.")

elif selected_option == "🗑️ Elimina":
    st.header("Elimina un chunk")
    delete_url = st.text_input("URL del documento:", key="delete_url")
    delete_key = st.text_input("Chiave (key) del chunk:", key="delete_key")
    
    if st.button("Elimina Chunk"):
        if delete_url and delete_key:
            delete_document(delete_url, delete_key)
        else:
            st.warning("Per favore, compila tutti i campi.")