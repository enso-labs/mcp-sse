from typing import Optional, Dict, Any, List
import httpx
from urllib.parse import urljoin
import base64
from pathlib import Path
from langchain_core.documents import Document

from src.utils.rag import VectorStore

class GitHubAPI:
    """A class to interact with the GitHub API using a Personal Access Token."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, pat_token: str):
        """
        Initialize the GitHub API client.
        
        Args:
            pat_token (str): GitHub Personal Access Token
        """
        self.pat_token = pat_token
        self.headers = {
            "Authorization": f"token {pat_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHubAPI-Client"
        }
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the GitHub API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parameters
            json_data (Optional[Dict[str, Any]]): JSON data for POST/PUT requests
            
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If the response is not valid JSON
        """
        url = urljoin(self.BASE_URL, endpoint)
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=json_data
            )
            response.raise_for_status()
            return response.json()
    
    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository information.
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            
        Returns:
            Dict[str, Any]: Repository information
        """
        return await self._make_request("GET", f"/repos/{owner}/{repo}")
    
    async def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30
    ) -> Dict[str, Any]:
        """
        Get repository issues.
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            state (str): Issue state (open, closed, all)
            page (int): Page number
            per_page (int): Number of items per page
            
        Returns:
            Dict[str, Any]: Issues information
        """
        params = {
            "state": state,
            "page": page,
            "per_page": per_page
        }
        return await self._make_request("GET", f"/repos/{owner}/{repo}/issues", params=params)
    
    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue.
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            title (str): Issue title
            body (str): Issue body
            labels (Optional[List[str]]): List of labels
            assignees (Optional[List[str]]): List of assignees
            
        Returns:
            Dict[str, Any]: Created issue information
        """
        data = {
            "title": title,
            "body": body,
            "labels": labels or [],
            "assignees": assignees or []
        }
        return await self._make_request("POST", f"/repos/{owner}/{repo}/issues", json_data=data)

    async def get_file_contents(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get contents of a file from a repository.
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            path (str): Path to the file in the repository
            ref (Optional[str]): The name of the commit/branch/tag. Defaults to the default branch
            
        Returns:
            Dict[str, Any]: File content information including decoded content
        """
        params = {"ref": ref} if ref else None
        response = await self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/contents/{path}",
            params=params
        )
        
        if isinstance(response, dict) and "content" in response:
            # Decode base64 content
            content = base64.b64decode(response["content"]).decode("utf-8")
            response["decoded_content"] = content
            
        return response

    async def list_repository_files(
        self,
        owner: str,
        repo: str,
        path: str = "",
        ref: Optional[str] = None,
        extensions: Optional[List[str]] = None,
        recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List files in a repository directory, optionally filtered by extension.
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            path (str): Path in the repository to list
            ref (Optional[str]): The name of the commit/branch/tag
            extensions (Optional[List[str]]): List of file extensions to filter by (e.g. ['.py', '.js'])
            recursive (bool): Whether to recursively list files in subdirectories
            
        Returns:
            List[Dict[str, Any]]: List of file information
        """
        params = {"ref": ref} if ref else None
        response = await self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/contents/{path}",
            params=params
        )
        
        files = []
        
        for item in response:
            if item["type"] == "file":
                if extensions:
                    file_ext = Path(item["name"]).suffix.lower()
                    if file_ext in extensions:
                        files.append(item)
                else:
                    files.append(item)
            elif item["type"] == "dir" and recursive:
                # Recursively get files from subdirectories
                subdir_files = await self.list_repository_files(
                    owner=owner,
                    repo=repo,
                    path=item["path"],
                    ref=ref,
                    extensions=extensions,
                    recursive=True
                )
                files.extend(subdir_files)
        
        return files

    async def search_code(
        self,
        owner: str,
        repo: str,
        query: str,
        extensions: Optional[List[str]] = None,
        path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for code in a repository with optional filters.
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            query (str): Search query
            extensions (Optional[List[str]]): List of file extensions to filter by
            path (Optional[str]): Path to search within
            
        Returns:
            Dict[str, Any]: Search results
        """
        # Build the search query
        search_query = f"{query} repo:{owner}/{repo}"
        
        if extensions:
            ext_filters = " ".join(f"extension:{ext.lstrip('.')}" for ext in extensions)
            search_query = f"{search_query} {ext_filters}"
            
        if path:
            search_query = f"{search_query} path:{path}"
            
        params = {
            "q": search_query,
            "per_page": 100
        }
        
        return await self._make_request("GET", "/search/code", params=params)

    async def get_repository_contents_to_vectorstore(
        self,
        owner: str,
        repo: str,
        extensions: List[str],
        path: str = "",
        ref: Optional[str] = None,
        include_file_info: bool = True,
        chunk_size: int = 0,
        chunk_overlap: int = 0
    ) -> List[Document]:
        """
        Recursively get contents of files with specified extensions and add them to the vector store.
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            extensions (List[str]): List of file extensions to include (e.g. ['.py', '.js'])
            path (str): Path in the repository to start from
            ref (Optional[str]): The name of the commit/branch/tag
            include_file_info (bool): Whether to include file metadata in the document
            chunk_size (int): Size of text chunks for splitting documents
            chunk_overlap (int): Overlap between chunks
            
        Returns:
            List[Document]: List of processed documents
        """
        from src.utils.rag import Splitter
        
        # Get all files recursively
        files = await self.list_repository_files(
            owner=owner,
            repo=repo,
            path=path,
            ref=ref,
            extensions=extensions,
            recursive=True
        )
        
        documents = []
        splitter = Splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # Process each file
        for file in files:
            try:
                # Get file contents
                content = await self.get_file_contents(
                    owner=owner,
                    repo=repo,
                    path=file["path"],
                    ref=ref
                )
                
                if "decoded_content" not in content:
                    continue
                    
                # Create metadata
                metadata = {
                    "source": file["html_url"],
                    "path": file["path"],
                    "sha": file["sha"],
                    "size": file["size"],
                    "type": "github_file"
                } if include_file_info else {"type": "github_file"}
                
                # Create document
                doc = Document(
                    page_content=content["decoded_content"],
                    metadata=metadata
                )
                
                # Split document if needed
                docs = splitter.split_docs([doc])
                
                # Add chunk index to metadata
                for i, split_doc in enumerate(docs):
                    split_doc.metadata["chunk"] = i
                
                documents.extend(docs)
                
            except Exception as e:
                print(f"Error processing file {file['path']}: {e}")
                continue
        
        # Add documents to vector store
        if documents:
            # Process documents in batches of 20
            batch_size = 20
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                await VectorStore().aadd_docs(batch)
        
        return documents
