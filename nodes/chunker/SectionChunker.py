import re
from states.ArxivPdfContentState import State
from typing import Dict

class SectionChunker:
    def __init__(self):
        pass
    
    def normalize_title_as_key(self, title: str) -> str:
        """
        Normalizza un titolo di sezione per creare una chiave robusta per un dizionario.
        
        Esempio: "2.1 Strategy" -> "2_1_strategy"
        Esempio: "Schema definition" -> "schema_definition"
        """
        # Sostituisce i punti nei numeri con underscore (es. "2.1" -> "2_1")
        key = re.sub(r'(\d+)\.', r'\1_', title)
        
        # Sostituisce tutti i caratteri non alfanumerici (tranne gli underscore)
        # e gli spazi con un singolo underscore.
        key = re.sub(r'[\W_]+', '_', key.strip()).strip('_')
        
        # Converte il tutto in minuscolo per coerenza.
        return key.lower()
    
    def chunk_by_section(self, document_text: str) -> Dict[str, str]:
        """
        Divide un documento Markdown in un dizionario, basandosi sui marcatori
        '## ' e '### '.

        Args:
            document_text (str): Il testo del documento Markdown.

        Returns:
            Dict[str, str]: Un dizionario dove la chiave è il titolo della
                        sezione e il valore è il contenuto. La chiave viene
                        normalizzata per renderla robusta.
        """
        sections = {}
        
        # Prepara il testo per una corretta suddivisione
        document_text = "\n" + document_text.strip()
        
        # Pattern per trovare titoli e contenuti.
        pattern = r"(\n(##\s.+|###\s.+))([\s\S]*?)(?=\n(##\s|###\s|$))"
        
        matches = re.findall(pattern, document_text)
        
        for match in matches:
            full_title_line = match[1].strip()
            content = match[2].strip()
            
            # 1. Estrae il titolo, rimuovendo '##' o '###'
            title = re.sub(r'^(##\s|###\s)', '', full_title_line).strip()
            
            # 2. Normalizza il titolo per creare una chiave robusta
            key = self.normalize_title_as_key(title)
            
            # Aggiunge la coppia chiave-contenuto al dizionario
            sections[key] = content
            
        return sections

    def __call__(self, state: State) -> State:
        state.chunks = self.chunk_by_section(state.markdown)
        state.init_keys = list(state.chunks.keys())
        return state