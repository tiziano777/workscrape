from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Annotated, Set
import  operator

class State(BaseModel):
    url: Optional[str] = Field(default=None, description="Testo di input")
    markdown: Optional[str] = Field(default=None, description="Markdown dell' url")

    chunks: Optional[Dict[str,str]] = Field(default={}, description="Dizionario dove ogni k:v rappresenta una sezione del paper")
    init_keys: Optional[List[str]] = Field(default=[], description="Chunks per ogni articolo estratto da query_string api call")
   
    references_key: Optional[str] = Field(default=None, description="Chiave della sezione 'References' se presente")
    abstract_key: Optional[str] = Field(default=None, description="Chiave della sezione 'Abstract' se presente")
    
    references_chunk: Optional[str] = Field(default=None, description="Chunk della sezione 'References' se presente")
    abstract_chunk: Optional[str] = Field(default=None, description="Chunk della sezione 'Abstract' se presente")

    keywords: Annotated[List[str], operator.add] = Field(default=[], description="Keywords estratte dal paper")
    references: Annotated[List[str], operator.add] = Field(default=[], description="References estratte dal paper")

    error_status: Optional[List[str]] = Field(default=[], description="Errori riscontrati (if any)")
    
