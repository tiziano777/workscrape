from bs4 import BeautifulSoup

def extract_urls_from_bookmarks(html_path: str) -> list[str]:
    """
    Estrae tutti gli href da un file bookmark in formato Netscape.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]
