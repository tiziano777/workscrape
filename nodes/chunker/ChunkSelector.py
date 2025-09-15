import json
from json_repair import repair_json
from typing import List
from states.ArxivPdfContentState import State

class ChunkSelector:
    """
    Filtra le sezioni di un articolo basandosi su un prompt LLM.
    Mantiene solo le sezioni di contenuto descrittivo rilevante.
    """
    def __init__(self, llm, prompt: str):
        """
        Inizializza la classe con il modello LLM e il prompt di sistema.
        
        :param llm: Il modello LLM da utilizzare per l'interrogazione.
        :param prompt: Il prompt per la selezione delle sezioni.
        """
        self.llm = llm
        self.prompt = prompt
        self.end_prompt = '\n\nSection keys:\n'


    def _get_filtered_keys(self, section_keys: List[str]) -> List[str]:
        """
        Interroga l'LLM per ottenere una lista di chiavi di sezione filtrate.
        
        :param section_keys: Lista delle chiavi di sezione originali.
        :return: Lista di chiavi di sezione filtrate.
        """
        try:
            response = self.llm.invoke( f"{self.prompt}\n{section_keys}{self.end_prompt}" ).content
            filtered_keys = self.extract_json(response)
            
            if not isinstance(filtered_keys, list):
                raise ValueError("LLM did not return a list of keys.")
            
            return filtered_keys
            
        except Exception as e:
            print(f"Errore nella chiamata a LLM per il filtering: {e}")
            return []

    def extract_json(self, json_text: str) -> list:
        """
        Ripara e deserializza l'output JSON generato da LLM. Restituisce una lista oppure {} in caso di errore.
        """
        try:
            #print("json text: ", json_text)
            repaired_text = repair_json(json_text)
            parsed_json = json.loads(repaired_text)

            if not isinstance(parsed_json, list):
                raise ValueError("Parsed JSON is not a list")

            return parsed_json

        except Exception as e:
            return e

    def __call__(self, state: State) -> State:
        """
        Opera sulla pipeline per filtrare le sezioni di ogni articolo.
        
        :param state: L'oggetto di stato della pipeline.
        :return: Lo stato aggiornato con le sezioni filtrate.
        """
        try:
            state.filtered_keys = self._get_filtered_keys(state.init_keys)
        except:
            state.error_status.append('[ChunkSelector] problem in LLM call for filtering chunks')
            return state
        
        state.chunks = {key: state.chunks[key] for key in state.filtered_keys}


        return state
