def show_result(result):

    if not result.success:
        print(f"Crawl failed: {result.error_message}")
        print(f"Status code: {result.status_code}")
    else:
        print(result.html)         # Raw HTML
        print(result.cleaned_html) # Cleaned HTML
        print(result.markdown.raw_markdown) # Raw markdown from cleaned html
        print(result.markdown.fit_markdown) # Most relevant content in markdown

        # Check success status
        print(result.success)      # True if crawl succeeded
        print(result.status_code)  # HTTP status code (e.g., 200, 404)

        # Access extracted media and links
        print(result.media)        # Dictionary of found media (images, videos, audio)
        print(result.links)        # Dictionary of internal and external links