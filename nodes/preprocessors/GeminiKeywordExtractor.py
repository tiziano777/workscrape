import json
from utils.GeminiErrorHandler import GeminiErrorHandler
from states.ArxivState import State
from json_repair import repair_json


class GeminiKeywordExtractor():

    def __init__(self, llm, prompt=None):
        """
        Definisci il modello e impostazioni specifiche.

        :param llm: Modello gemini 
        :param input_context: Dimensione massima user input.
        :param system_prompt: Prompt di sistema da utilizzare per l'annotazione.
        """
        self.llm = llm
        self.system_prompt = prompt
        self.end_prompt = "\nOutput List:\n"
        self.error_handler= GeminiErrorHandler()


    def annotate(self, text):
        """
        Genera un'annotazione per il testo di input utilizzando il modello
        e converte il risultato in un JSON strutturato.

        :param text: abstract che contiene il testo da elaborare.
        :return: Un dizionario Python con l'output JSON.
        """
        
        try:
            call=self.error_handler.gemini_invoke_with_retry(llm=self.llm, prompt=str(self.prompt + text + self.end_prompt))
            keywords=self.extract_json(call.content)


        except Exception as e:
            return e

        return keywords

    def extract_json(self, json_text: str) -> list:
        """
        Ripara e deserializza l'output JSON generato da LLM. Restituisce una lista oppure {} in caso di errore.
        """
        try:
            print("json text: ", json_text)
            repaired_text = repair_json(json_text)
            
            parsed_json = json.loads(repaired_text)

            if not isinstance(parsed_json, list):
                raise ValueError("Parsed JSON is not a list")

            return parsed_json

        except Exception as e:
            return e
     
    def __call__(self, state: State) -> State:
        """
        Estrazione con LLM gemini di Keywords from abstract

        :param state: Il state.abstracts contiene testo da elaborare.
        :return: Un dizionario Python con l'output JSON.
        """
        try:
            for article in state['articles']:
                article['keywords'] = self.annotate(state)
        except:
            state['error_status']="[KeywordExtractor] error in annotate keywords"

        return state
