import json
from json_repair import repair_json
from typing import List
from states.ArxivPdfContentState import State
import traceback
import re

class ArxivKeywordsExtractor:
    """
    Estrae Keywords e References dai chunks di un paper Arxiv usando un LLM.
    """
    def __init__(self, llm, keyword_prompt: str):
        """
        Inizializza la classe con il modello LLM e il prompt di sistema.
        
        :param llm: Il modello LLM da utilizzare per l'interrogazione.
        :param keyword_prompt: Il prompt per la selezione delle sezioni.
        """
        self.llm = llm
        self.keyword_prompt = keyword_prompt


    def _get_keywords(self, chunk: str) -> List[str]:
        """
        Interroga l'LLM per ottenere una lista di keywords di un chunk.
        
        :param section_keys: Lista delle chiavi di sezione originali.
        :return: Lista di chiavi di sezione filtrate.
        """
        try:
            response = self.llm.invoke( f"{self.keyword_prompt}\n{chunk}" ).content
            filtered_keys = self.extract_json(response)

            if not isinstance(filtered_keys, list):
                raise ValueError("LLM did not return a list of keys.")

            return filtered_keys
            
        except Exception as e:
            print(f"Errore nella chiamata a LLM per il filtering: {e}")
            return set()

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
        
    def _chunk_match(self, keywords, chunk_keys):
        """
        Restituisce la prima chiave di chunk_keys che contiene una delle keywords (match case-insensitive, anche solo come sottostringa).
        """
        for k in chunk_keys:
            for kw in keywords:
                if kw.lower() in k.lower():
                    return k
        return None

    def __call__(self, state: State) -> State:
        """
        Opera sulla pipeline per filtrare le sezioni di ogni articolo.
        
        :param state: L'oggetto di stato della pipeline.
        :return: Lo stato aggiornato con le sezioni abstract and references filtrate.
        """

        # recognize abstract or introduction form chunks, to extract keywords
        desired_chunks_trace = ['abstract','introduction']

        state.abstract_key = self._chunk_match(desired_chunks_trace, state.init_keys)
        print("Abstract key matched: ", state.abstract_key)

        try:
            state.abstract_chunk = state.chunks[state.abstract_key]
        except:
            state.error_status.append('[ChunkSelector] no abstract chunk found')
            print(state.chunks.keys())
            traceback.print_exc()
            return state
        

        try:
            keywords_set = set(self._get_keywords(state.abstract_chunk))
            state.keywords = list(keywords_set)
        except:
            state.error_status.append('[ChunkSelector] problem in LLM call for keywords extraction')
            traceback.print_exc()
            return state


        return {"keywords": state.keywords, "abstract_key": state.abstract_key, "abstract_chunk": state.abstract_chunk}

