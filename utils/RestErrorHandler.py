import traceback
import time
import requests

class RestErrorHandler:

    def __init__(self):
        pass

    def rest_invoke_with_retry(self, llm, prompt, max_retries=5, retry_count=0):
        """
        Retry per endpoint REST che restituisce { 'response': ..., 'success': true/false }.
        """
        try:
            result = llm.invoke(prompt)

            if isinstance(result, dict) and result.get("success") is True:
                return result["response"]
            elif isinstance(result, dict) and result.get("success") is False:
                print(f"[rest_invoke_with_retry] Tentativo fallito (retry #{retry_count + 1})")
                if retry_count < max_retries:
                    time.sleep(1)  # backoff statico, puoi renderlo esponenziale
                    return self.rest_invoke_with_retry(llm, prompt, max_retries, retry_count + 1)
                raise RuntimeError("Max retries exceeded (REST).")
            else:
                raise RuntimeError(f"Formato risposta non riconosciuto: {result}")

        except requests.exceptions.RequestException as e:
            traceback.print_exc()
            raise RuntimeError(f"Errore HTTP REST: {e}")
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Errore generico REST: {e}")
