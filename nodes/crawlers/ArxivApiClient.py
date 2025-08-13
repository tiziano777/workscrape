import requests
import xml.etree.ElementTree as ET

from state.arxivState import State

# Definizione dei namespaces per il parsing XML
# L'API di arXiv usa diversi namespace che sono essenziali per trovare i tag corretti
namespaces = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}
class ArxivApiClient:
    '''
    Classe che si occupa di interfacciarsi con API arxiv, restituendo ad ogni query una lista di ricerche correrlate
    '''
    def __init__(self, base_url: str = "http://export.arxiv.org/api/query?", max_results: int = 10, sort_by: str = 'submittedDate', sort_order: str = 'descending'):
        self.base_url = base_url
        self.max_results = max_results
        self.sort_by = sort_by
        self.sort_order = sort_order

    def __call__(self, state: State) -> State:
        """
        Esegue una ricerca sull'API di arXiv e restituisce una lista di articoli.

        Args:
            query (str): La stringa di ricerca.

        Returns:
            list: Una lista di dizionari, ognuno rappresentante un articolo.
        """
        
        # I parametri di ricerca dell'API
        params = {
            'search_query': f"all:{state['query_string']}",  # Ricerca in tutti i campi
            'max_results': self.max_results,
            'sortBy': self.sort_by,
            'sortOrder': self.sort_order
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Solleva un'eccezione in caso di errore HTTP
        except requests.exceptions.RequestException as e:
            print(f"Errore nella richiesta all'API di arXiv: {e}")
            return []

        # Parsing del feed XML
        root = ET.fromstring(response.content)
        
        # I risultati di ricerca sono contenuti nei tag 'entry'
        for entry in root.findall('atom:entry', namespaces):
            # Estrazione dei dati
            article = {
                'id': entry.find('atom:id', namespaces).text,
                'pdf_id': entry.find('atom:id', namespaces).text.replace('abs','pdf'),
                'html_id': entry.find('atom:id', namespaces).text.replace('abs','html'),
                'title': entry.find('atom:title', namespaces).text.strip().replace('\n', ' '),
                'published': entry.find('atom:published', namespaces).text,
                'updated': entry.find('atom:updated', namespaces).text,
                'abstract': entry.find('atom:summary', namespaces).text.strip().replace('\n', ' '),
                'authors': [author.find('atom:name', namespaces).text for author in entry.findall('atom:author', namespaces)]
            }
            state['articles'].append(article)
            
        return state
