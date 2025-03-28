from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False)

def retrieve_webpage(url: str) -> str:
    """Retrieve a web page"""
    result = md.convert(url)
    
    # Format the output for better readability
    formatted_output = ""
    
    if result.title:
        formatted_output = f"# {result.title}\n\n{result.markdown}"
    else:
        formatted_output = result.markdown
    
    return formatted_output