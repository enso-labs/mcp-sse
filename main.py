# mcp/main.py
import json
import os
from src.middleware.api_key import middleware
from src.utils.rag import DEFAULT_VECTOR_STORE_PATH
from pydantic import BaseModel
import uvicorn
from mcp_wrap.server import FastMCP
from langchain_core.documents import Document

from src.config import Config
from src.utils.scrape import retrieve_webpage

from src.utils.rag import VectorStore, Splitter

# Initialize FastMCP server instance
mcp = FastMCP(
    name=Config.APP_NAME.value,
    instructions=Config.MCP_INSTRUCTIONS.value,
    settings={
        'debug': Config.APP_DEBUG.value,          # Enable debug mode
        'port': Config.APP_PORT.value,          # Port to run server on
        'log_level': Config.APP_LOG_LEVEL.value,  # Logging verbosity
    }
)

vector_store = VectorStore()
splitter = Splitter()

##########################
# Tools
##########################
class Split(BaseModel):
    active: bool = True
    chunk_size: int = 1000
    chunk_overlap: int = 0

@mcp.tool()
async def scrape_to_knowledge_base(url: str, title: str, split: Split) -> str:
    """Scrape a web page and add it to the knowledge base"""
    page = retrieve_webpage(url)
    docs = [Document(page_content=page, metadata={"source": url, "title": title})]
    if split.active:
        docs = splitter.split_docs(docs)
        # Add chunk index to metadata for each document
        for i, doc in enumerate(docs):
            doc.metadata["chunk"] = i
    await vector_store.aadd_docs(docs)
    return f"Scraped {url} resulting in {len(docs)} documents"

@mcp.tool()
async def retrieve_documents(query: str, search_type: str = "mmr", search_kwargs: dict = {'k': 10}) -> list[dict]:
    """Rewrite the query to be more specific and retrieve documents from the knowledge base"""
    results = vector_store.retrieve(query, search_type, search_kwargs)
    docs = [doc.model_dump() for doc in results]
    return json.dumps(docs)

@mcp.tool()
async def delete_document(doc_id: str) -> str:
    """Delete a document from the knowledge base"""
    await vector_store.adelete_docs([doc_id])
    return f"Deleted document {doc_id}"

@mcp.tool()
async def wipe_knowledge_base() -> str:
    """Wipe the knowledge base"""
    ctx = mcp.get_context()
    middleware(ctx.request_context)
    
    if os.path.exists(DEFAULT_VECTOR_STORE_PATH):
        os.remove(DEFAULT_VECTOR_STORE_PATH)
    
    # Also clear the in-memory vector store
    vector_store.load_vector_store()
    
    return f"Wiped knowledge base"


##########################
# Main
##########################
if __name__ == "__main__":
    print(f"Starting MCP server... {Config.APP_NAME.value} on port {Config.APP_PORT.value}")
    # Start server with Server-Sent Events transport
    uvicorn.run(
        mcp.sse_app(), 
        host="0.0.0.0", 
        port=Config.APP_PORT.value, 
        log_level=Config.APP_LOG_LEVEL.value.lower(),
    )