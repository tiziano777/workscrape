from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class ArticleMetadata(BaseModel):
    id: str = Field(default=None, description="url principale del paper")
    pdf_id: str = Field(default=None, description="url pdf del paper")
    html_id: str = Field(default=None, description="url html del paper")

    title: Optional[str] = Field(default='', description="titolo del paper")
    abstract: Optional[str] = Field(default='', description="abstract del paper")
    keywords:  Optional[List[str]] = Field(default='', description="keywords dell' abstract")

    published: Optional[str] = Field(default='', description="prima data di pubblicazione del paper")
    updated: Optional[str] = Field(default='', description="data di ultimo update del paper")

    authors: Optional[List[str]] = Field(default=[], description="autori del paper")

class ArticleContent(BaseModel):
    raw_text: Optional[str] = Field(default=None, description="Testo del paper")
    chunks: Optional[List[str]] = Field(default=None, description="Chunks del paper")


class State(BaseModel):
    query_string: Optional[str] = Field(default=None, description="Testo di input")
    articles: Optional[List[ArticleMetadata]] = Field(default=None, description="Lista di articoli arxiv da query string api call")

    selected_articles: Optional[List[ArticleMetadata]] = Field(default=None, description="Lista di articoli arxiv selezionati da query string api call")

    articles_content: Optional[List[ArticleContent]] = Field(default=None, description="Chunks per ogni articolo estratto da query_string api call")

    selected_chunks: Optional[List[str]] = Field(default=None, description="chunks rilevanti tra i vari papers")

    store_research: bool = Field(default=True, description="scegli se salvare la ricerca per analisi future")
    error_status: Optional[str] = Field(default=None, description="Errori riscontrati (if any)")
    
