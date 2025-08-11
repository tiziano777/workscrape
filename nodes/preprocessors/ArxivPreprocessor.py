import re
import unicodedata
from typing import List, Dict

class ArxivPreprocessor:
    """
    Classe per la pre-elaborazione del testo degli articoli di Arxiv.
    Esegue la pulizia e la normalizzazione del testo per ottimizzarlo.
    """

    def __init__(self):
        """
        Inizializza il pre-processore. Non sono più necessari parametri di chunking.
        """
        pass

    def _clean_text(self, text: str) -> str:
        """
        Pulisce il testo rimuovendo caratteri non necessari, spazi extra,
        e normalizzando il testo (es. 'à' -> 'a', tutto in minuscolo).

        Args:
            text (str): Il testo originale.

        Returns:
            str: Il testo pulito e normalizzato.
        """
        # Normalizza i caratteri con accenti con NFD (Forma di Normalizzazione di Decomposizione)
        text = unicodedata.normalize('NFD', text)
        # Rimuove tutti i caratteri diacritici (gli accenti)
        text = text.encode('ascii', 'ignore').decode('utf-8')
        
        # Converte il testo in minuscolo
        text = text.lower()
    
        # Rimuove spazi extra, tabulazioni e newline
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def __cal__(self, articles: List) -> List:
        """
        Esegue il pre-processing completo di un singolo articolo.

        Args:
            article (lis): I documenti da processare.

        Returns:
            List: I documenti puliti.
        """
        for article in articles:
            if 'content' not in article or not article['content']:
                print(f"⚠️ Articolo '{article.get('id')}' saltato: manca il contenuto.")
                return None

            # Copia il documento per evitare di modificarlo direttamente
            preprocessed_article = article.copy()
            
            # Pulisci il testo principale
            cleaned_text = self._clean_text(preprocessed_article['content'])
            preprocessed_article['content_cleaned'] = cleaned_text

            # Rimuove il campo 'content' originale per salvare solo il testo pulito
            del preprocessed_article['content']

        return preprocessed_article
