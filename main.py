# mcp/main.py
import json
import os
from typing import List, Optional
from src.middleware.api_key import get_headers, middleware
from src.utils.rag import DEFAULT_VECTOR_STORE_PATH
from pydantic import BaseModel
import uvicorn
from mcp_wrap.server import FastMCP
from langchain_core.documents import Document

from src.config import Config
from src.utils.scrape import retrieve_webpage

from src.utils.rag import VectorStore, Splitter
from src.utils.github import GitHubAPI

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
async def index_github_repository(
    owner: str,
    repo: str,
    extensions: List[str],
    path: str = "",
    ref: Optional[str] = None,
    chunk_size: int = 0,
    chunk_overlap: int = 0
) -> str:
    """
    Index a GitHub repository's contents into the knowledge base.
    
    Args:
        owner: GitHub repository owner/organization
        repo: Repository name
        extensions: List of file extensions to index (e.g. [".py", ".md"])
        path: Optional path within repository to start indexing from
        ref: Optional branch, tag, or commit SHA
        chunk_size: Size of text chunks for splitting documents
        chunk_overlap: Overlap between chunks
    
    Returns:
        str: Summary of indexing operation
    """
    ctx = mcp.get_context()
    headers = get_headers(ctx.request_context)
    authorization = headers.get("authorization") or headers.get("x-github-pat")
    if not authorization:
        raise ValueError("Authorization header is required")
    
    # Initialize GitHub client
    github_client = GitHubAPI(pat_token=authorization)
    
    try:
        # Get and index repository contents
        documents = await github_client.get_repository_contents_to_vectorstore(
            owner=owner,
            repo=repo,
            extensions=extensions,
            path=path,
            ref=ref,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        return (
            f"Successfully indexed {len(documents)} documents from {owner}/{repo}\n"
            f"Extensions processed: {', '.join(extensions)}\n"
            f"Path: {path or 'root'}\n"
            f"Reference: {ref or 'default branch'}"
        )
        
    except Exception as e:
        return f"Error indexing repository: {str(e)}"

#####################################################################################
# RAG
#####################################################################################
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