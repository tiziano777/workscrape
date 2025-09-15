import json
from json_repair import repair_json
from typing import List
from states.ArxivPdfContentState import State

class Summarizer:
    """
    Genera un riassunto per ogni sezione di un articolo.
    """
    def __init__(self, llm, prompt: str):
        """
        Inizializza la classe con il modello LLM e il prompt di sistema per il riassunto.

        :param llm: Il modello LLM da utilizzare per l'interrogazione.
        :param prompt: Il prompt per la generazione del riassunto.
        """
        self.llm = llm
        self.prompt = prompt
        self.end_prompt = '\n\nSummarized text:\n'

    def _summarize_text(self, text: str) -> str:
        """
        Genera un riassunto per un blocco di testo.
        
        :param text: Il testo della sezione da riassumere.
        :return: La stringa del riassunto.
        """
        try:
            llm_response = self.llm.invoke(f"{self.prompt}\n\{text}{self.end_prompt}").content
            return llm_response
        except Exception as e:
            print(f"Errore nella chiamata a LLM per il riassunto: {e}")
            return "Summary generation failed."

    def __call__(self, state: State) -> State:
        """
        Opera sulla pipeline per riassumere le sezioni di ogni articolo.
        
        :param state: L'oggetto di stato della pipeline.
        :return: Lo stato aggiornato con le sezioni riassunte.
        """

        summarized_sections = {}
        for key, value in state.chunks.items():
            # Genera il riassunto per ogni sezione e lo salva
            summarized_sections[key] = self._summarize_text(value)
        

        state.summarized_chunks = summarized_sections
        
        return state
