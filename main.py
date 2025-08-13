from nodes.crawlers.ArxivApiClient import ArxivApiClient
from state.arxivState import State

query_string = "LLM" 
arxiv = ArxivApiClient()

print(arxiv({"query_string": query_string, 'articles':[]}))

'''{
'id': 'http://arxiv.org/abs/2508.09129v1',
'pdf_id': 'http://arxiv.org/pdf/2508.09129v1',
'html_id': "https://arxiv.org/html/2508.09129v1"
'title': 'BrowseMaster: Towards Scalable Web Browsing via Tool-Augmented   Programmatic Agent Pair',
'published': '2025-08-12T17:56:25Z',
'updated': '2025-08-12T17:56:25Z',
'abstract': 'Effective information seeking in the vast and ever-growing digital landscape requires balancing expansive search with strategic reasoning. Current large language model (LLM)-based agents struggle to achieve this balance due to limitations in search breadth and reasoning depth, where slow, serial querying restricts coverage of relevant sources and noisy raw inputs disrupt the continuity of multi-step reasoning. To address these challenges, we propose BrowseMaster, a scalable framework built around a programmatically augmented planner-executor agent pair. The planner formulates and adapts search strategies based on task constraints, while the executor conducts efficient, targeted retrieval to supply the planner with concise, relevant evidence. This division of labor preserves coherent, long-horizon reasoning while sustaining broad and systematic exploration, overcoming the trade-off that limits existing agents. Extensive experiments on challenging English and Chinese benchmarks show that BrowseMaster consistently outperforms open-source and proprietary baselines, achieving scores of 30.0 on BrowseComp-en and 46.5 on BrowseComp-zh, which demonstrates its strong capability in complex, reasoning-heavy information-seeking tasks at scale.',
'authors': ['Xianghe Pang', 'Shuo Tang', 'Rui Ye', 'Yuwen Du', 'Yaxin Du', 'Siheng Chen']}'''