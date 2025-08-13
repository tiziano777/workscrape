from nodes.crawlers.ArxivApiClient import ArxivApiClient
from nodes.crawlers.ArxivFetcher import ArxivFetcher
from nodes.chunker.SectionChunker import SectionChunker
from state.arxivState import State
import asyncio
import json

async def main():
    query_string = "LLM"
    arxiv = ArxivApiClient()
    state= arxiv({"query_string": query_string, 'articles':[]})
    first_article=state['articles'][0]['html_id']
    print(first_article)
    fetcher= ArxivFetcher()
    first_article_text = await fetcher(first_article)

    chunker= SectionChunker()
    paper_dict_chunks= chunker(first_article_text)

    print(paper_dict_chunks)

    with open("chunks.json",mode="w") as f:
        f.write(json.dumps(paper_dict_chunks))





asyncio.run(main())