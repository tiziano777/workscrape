from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class State(BaseModel):
    url: Optional[str] = Field(default=None, description="Testo di input")
    markdown: Optional[str] = Field(default=None, description="Markdown dell' url")

    chunks: Optional[Dict[str,str]] = Field(default={}, description="Dizionario dove ogni k:v rappresenta una sezione del paper")
    summarized_chunks: Optional[Dict[str,str]] = Field(default={}, description="Summary dei chunks")

    init_keys: Optional[List[str]] = Field(default=[], description="Chunks per ogni articolo estratto da query_string api call")
    filtered_keys: Optional[List[str]] = Field(default=[], description="chunks rilevanti tra i vari papers")

    error_status: Optional[List[str]] = Field(default=[], description="Errori riscontrati (if any)")
    
