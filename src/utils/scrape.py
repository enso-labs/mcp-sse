from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False)

def web_scrape(urls: List[str]) -> str:
    """Retrieve content from a list of URLs or Paths"""
    docs = []
    for url in urls:
        document = md.convert(url)
        if document.title:
            formatted_output = f"# {document.title}\n\n{document.markdown}"
        else:
            formatted_output = document.markdown
        docs.append(formatted_output)
    return "\n\n---\n\n".join(docs)
