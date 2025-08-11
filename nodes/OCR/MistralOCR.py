import os
import requests
import base64
import fitz  # PyMuPDF
from typing import Dict


class MistralOCR:
    def __init__(self, api_key: str = None, model: str = "pixtral-12b-2409"):
        """
        Inizializza il client Mistral OCR
        
        Args:
            api_key: API key Mistral (se None, usa MISTRAL_API_KEY env var)
            model: Modello Mistral da usare
        """
        self.api_key = api_key or os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            raise ValueError("API key richiesta: imposta MISTRAL_API_KEY o passa api_key")
        
        self.model = model
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        
    def __call__(self, data: Dict) -> str:
        """
        Estrae tutto il testo dal PDF usando OCR
        
        Args:
            data: Dizionario con campo 'pdf_id' (URL del PDF)
            
        Returns:
            str: Tutto il testo estratto dal PDF
        """
        if 'pdf_id' not in data:
            raise ValueError("Campo 'pdf_id' richiesto")
        
        pdf_url = data['pdf_id']
        
        # Scarica PDF
        pdf_content = self._download_pdf(pdf_url)
        
        # Estrai tutto il testo
        full_text = self._extract_all_pages(pdf_content)
        
        return full_text
    
    def _download_pdf(self, url: str) -> bytes:
        """
        Scarica PDF dall'URL
        """
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    
    def _extract_all_pages(self, pdf_content: bytes) -> str:
        """Estrae testo da tutte le pagine del PDF"""

        # Apri PDF
        doc = fitz.open(stream=pdf_content, filetype="pdf")

        all_text = []
        
        # PAGE ITERATION
        for page_num in range(len(doc)):
            print(f"Pagina {page_num + 1}/{len(doc)}")
            
            page = doc[page_num]
            
            # Converte pagina in immagine PNG
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # Alta risoluzione
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode()
            
            # Chiama Mistral OCR
            page_text = self._ocr_page(img_base64)
            all_text.append(page_text)
        
        doc.close()
        
        # Unisce tutto il testo
        return "\n\n".join(all_text)
    
    def _ocr_page(self, img_base64: str) -> str:
        """Estrae testo da una singola pagina usando Mistral"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Extract all text from this image. Return only the text content, no descriptions or comments."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                        }
                    ]
                }
            ],
            "temperature": 0,
            "max_tokens": 4096
        }
        
        response = requests.post(self.base_url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()