import streamlit as st
import tempfile
from crawler.base_crawler import Crawler
from utils.bookmark_parser import extract_urls_from_bookmarks

st.set_page_config(page_title="Streamlit Web Crawler", layout="centered")
st.title("📡 Minimal Web Crawler with crawl4ai")

if 'url_list' not in st.session_state:
    st.session_state.url_list = []

# Inserimento manuale
url_input = st.text_input("Aggiungi un URL manualmente", placeholder="https://example.com")

if st.button("➕ Aggiungi URL"):
    if url_input and url_input not in st.session_state.url_list:
        st.session_state.url_list.append(url_input)

# Caricamento bookmarks
uploaded_file = st.file_uploader("📁 Carica file bookmarks.html", type=["html"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    try:
        extracted = extract_urls_from_bookmarks(tmp_path)
        st.session_state.url_list.extend([u for u in extracted if u not in st.session_state.url_list])
        st.success(f"{len(extracted)} URL estratti e aggiunti.")
    except Exception as e:
        st.error(f"Errore parsing: {e}")

# Mostra lista
if st.session_state.url_list:
    st.subheader("🌐 URL nella coda")
    for url in st.session_state.url_list:
        st.markdown(f"- {url}")

    if st.button("🚀 Avvia Crawling"):
        with st.spinner("Crawling..."):
            crawler = Crawler(urls=st.session_state.url_list)
            out_dir = crawler.run()
        st.success(f"Crawling completato. Output in: `{out_dir}`")
