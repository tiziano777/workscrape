import re


import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import datetime

class GoogleScholarRelatedSearchExtractor:
    """
    Estrae gli URL delle "Related searches" da un raw markdown di Google Scholar
    e aggiunge un filtro "since current year" a ciascun URL.
    """

    def _add_current_year_filter(self, url: str) -> str:
        """
        Aggiunge o aggiorna il parametro 'as_ylo' (anno di inizio) nell'URL.

        Args:
            url: L'URL originale a cui applicare il filtro.
            year: L'anno da impostare come filtro 'since year'.

        Returns:
            L'URL modificato con il filtro dell'anno.
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        current_year = datetime.datetime.now().year

        # Aggiungi o sovrascrivi il parametro as_ylo con l'anno specificato
        query_params['as_ylo'] = [str(current_year)]
        
        # Ricostruisci la stringa della query
        new_query_string = urlencode(query_params, doseq=True)
        
        # Ricostruisci l'URL completo
        return urlunparse(parsed_url._replace(query=new_query_string))

    def __call__(self, raw_markdown: str) -> list[str]:
        """
        Estrae e restituisce una lista di URL delle ricerche correlate,
        modificati per includere il filtro "since current year".

        Args:
            raw_markdown: Il testo raw markdown della pagina di Google Scholar.

        Returns:
            Una lista di stringhe, dove ogni stringa è un URL di una ricerca correlata
            con il filtro "since current year" applicato.
            Ritorna una lista vuota se non vengono trovate ricerche correlate.
        """
        related_searches_with_filter = []

        # L'espressione regolare cerca il blocco "## Related searches"
        # e poi cattura gli URL che seguono nel formato markdown di un link.
        block_pattern = re.compile(r'## Related searches\n((?:\s*\* \[.*?\]\((https:\/\/scholar\.google\.com\/scholar\?hl=en&as_sdt=0,5&qsp=\d+&q=[^&]+&qst=ib)\)\n)+)')
        
        match = block_pattern.search(raw_markdown)
        if match:
            # Estrai tutti i singoli URL all'interno del blocco
            url_line_pattern = re.compile(r'\s*\* \[.*?\]\((https:\/\/scholar\.google\.com\/scholar\?hl=en&as_sdt=0,5&qsp=\d+&q=[^&]+&qst=ib)\)')
            
            for line in match.group(1).split('\n'):
                url_match = url_line_pattern.search(line)
                if url_match:
                    original_url = url_match.group(1)
                    
                    # Applica il filtro dell'anno corrente usando la funzione ausiliaria
                    filtered_url = self._add_current_year_filter(original_url)
                    
                    related_searches_with_filter.append(filtered_url)
        
        return related_searches_with_filter
