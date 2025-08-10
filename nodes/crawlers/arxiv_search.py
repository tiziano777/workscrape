import requests
import xml.etree.ElementTree as ET

# Definizione dei namespaces per il parsing XML
# L'API di arXiv usa diversi namespace che sono essenziali per trovare i tag corretti
namespaces = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}

def search_arxiv(query: str, max_results: int = 10, sort_by: str = 'submittedDate', sort_order: str = 'descending'):
    """
    Esegue una ricerca sull'API di arXiv e restituisce una lista di articoli.

    Args:
        query (str): La stringa di ricerca.
        max_results (int): Il numero massimo di risultati da restituire.
        sort_by (str): Il campo per l'ordinamento (es. 'submittedDate', 'relevance').
        sort_order (str): L'ordine di ordinamento ('ascending' o 'descending').

    Returns:
        list: Una lista di dizionari, ognuno rappresentante un articolo.
    """
    # L'endpoint dell'API di arXiv
    base_url = "http://export.arxiv.org/api/query?"
    
    # I parametri di ricerca dell'API
    params = {
        'search_query': f"all:{query}",  # Ricerca in tutti i campi
        'max_results': max_results,
        'sortBy': sort_by,
        'sortOrder': sort_order
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Solleva un'eccezione in caso di errore HTTP
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta all'API di arXiv: {e}")
        return []

    # Parsing del feed XML
    root = ET.fromstring(response.content)
    
    articles = []
    # I risultati di ricerca sono contenuti nei tag 'entry'
    for entry in root.findall('atom:entry', namespaces):
        # Estrazione dei dati
        article = {
            'id': entry.find('atom:id', namespaces).text,
            'title': entry.find('atom:title', namespaces).text.strip().replace('\n', ' '),
            'published': entry.find('atom:published', namespaces).text,
            'updated': entry.find('atom:updated', namespaces).text,
            'abstract': entry.find('atom:summary', namespaces).text.strip().replace('\n', ' '),
            'authors': [author.find('atom:name', namespaces).text for author in entry.findall('atom:author', namespaces)]
        }
        articles.append(article)
        
    return articles

# Esempio di utilizzo:
# Replicazione della tua query: 'LLM', 200 risultati, ordinati per data di annuncio (submittedDate)
if __name__ == "__main__":
    query_string = "LLM"
    max_results_to_fetch = 200
    
    print(f"Ricerca di '{query_string}' su arXiv...")
    
    arxiv_articles = search_arxiv(
        query=query_string,
        max_results=max_results_to_fetch,
        sort_by='submittedDate',
        sort_order='descending'
    )
    
    if arxiv_articles:
        print(f"Trovati {len(arxiv_articles)} articoli.")

        file_name = "data/arxiv_crawled_data.md"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(str(arxiv_articles))
        print(f"\n--- Contenuto salvato in '{file_name}' ---")
    else:
        print("Nessun articolo trovato.")