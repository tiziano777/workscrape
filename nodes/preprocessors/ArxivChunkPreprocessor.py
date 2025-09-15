import re
import unicodedata
from typing import List, Dict
from states.ArxivPdfContentState import State

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
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
        
        # Converte il testo in minuscolo
        text = text.lower()
    
        # Rimuove spazi extra, tabulazioni e newline
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def __call__(self, state: State) -> State:
        """
        Esegue il pre-processing completo di un singolo articolo.

        Args:
            state (State): I documenti da processare.

        Returns:
            state: I documenti puliti per ogni chunk
        """
        for key, value in state.summarized_chunks.items():
            state.summarized_chunks[key]= self._clean_text(value)
             

        return state
