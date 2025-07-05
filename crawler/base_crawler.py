import os
from crawl4ai import Crawler as Crawl4AICore

class Crawler:
    """
    Classe wrapper per crawl4ai con possibilità di estendere e personalizzare comportamento.
    """
    def __init__(self, urls: list[str] = None, output_dir: str = 'crawl_output'):
        self.urls = urls if urls else []
        self.output_dir = output_dir
        self.config_dict = {
            'depth': 0,
            'maxPages': 1000,
            'html.extract_text': True,
            'html.store_raw': False,
            'fetch.images': False,
            'fetch.pdf': True,
            'fetch.video': True,
            'fetch.javascript': False,
            'save_format': 'json',
            'output_dir': self.output_dir,
        }

    def add_urls(self, new_urls: list[str]):
        """
        Aggiunge nuovi URL evitando duplicati.
        """
        self.urls.extend(u for u in new_urls if u not in self.urls)

    def clear_urls(self):
        """
        Resetta la lista degli URL.
        """
        self.urls = []

    def set_output_dir(self, path: str):
        """
        Cambia il path della directory di output.
        """
        self.output_dir = path
        self.config_dict['output_dir'] = path

    def configure(self, custom_config: dict):
        """
        Aggiorna la configurazione del crawler con override opzionale.
        """
        self.config_dict.update(custom_config)

    def run(self) -> str:
        """
        Esegue il crawling. Restituisce la directory di output.
        """
        if not self.urls:
            raise ValueError("Lista URL vuota. Aggiungere almeno un URL prima di eseguire.")

        os.makedirs(self.output_dir, exist_ok=True)

        crawler = Crawl4AICore()
        crawler.config(self.config_dict)
        crawler.add_urls(self.urls)
        crawler.run()

        return self.output_dir
