from urllib.parse import urlparse
from typing import Literal

URLType = Literal[
    "youtube_video", "youtube_channel",
    "arxiv_pdf", "arxiv_page",
    "pdf_file", "html_page", "unknown"
]

def classify_url_type(url: str) -> URLType:
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.lower()

    if "youtube.com" in netloc or "youtu.be" in netloc:
        if "/channel/" in path or "/c/" in path or "/@" in path:
            return "youtube_channel"
        return "youtube_video"

    if "arxiv.org" in netloc:
        if path.endswith(".pdf") or "/pdf/" in path:
            return "arxiv_pdf"
        return "arxiv_page"

    if path.endswith(".pdf"):
        return "pdf_file"

    if path.endswith("/") or path.endswith(".html") or "." not in path.split("/")[-1]:
        return "html_page"

    return "unknown"
