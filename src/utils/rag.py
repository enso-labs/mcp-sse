import os
from enum import Enum
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_VECTOR_STORE_PATH = "vector_store.json"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class Splitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 0):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)

    def split_docs(self, docs: list[Document]) -> list[Document]:
        return self.splitter.split_documents(docs)

class VectorStore:
    def __init__(self, vector_store: InMemoryVectorStore = None):
        self.vector_store = vector_store if vector_store else get_vector_store()
        
    def load_vector_store(self, path: str = DEFAULT_VECTOR_STORE_PATH):
        try:
            store = self.vector_store.load(path, embedding=get_embedding_model())
            self.vector_store = store
        except Exception as e:
            print(f"Error loading vector store: {e}")
            raise e
        finally:
            return self.vector_store
        
    def add_docs(self, docs: list[Document]):
        try:
            self.load_vector_store()
            updated = self.vector_store.add_documents([Document(**doc) for doc in docs])
            self.vector_store.dump(DEFAULT_VECTOR_STORE_PATH)
            return updated
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return False
        
    async def aadd_docs(self, docs: list[Document]):
        self.load_vector_store()
        await self.vector_store.aadd_documents(docs)
        self.vector_store.dump(DEFAULT_VECTOR_STORE_PATH)
        return True
    
    async def adelete_docs(self, ids: list[str]):
        await self.vector_store.adelete(ids)
        return True
    
    def retrieve(self, 
        query: str, 
        search_type: str = "mmr",  
        search_kwargs: dict = None,
    ):
        self.load_vector_store()
        retriever = self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs,
        )
        results = retriever.invoke(query)
        return results
    
    def list_docs(self):
        self.load_vector_store()
        docs = list(self.vector_store.store.values())
        for doc in docs:
            doc.pop('vector', None)
        return docs
    
    def find_docs_by_ids(self, ids: list[str]):
        self.load_vector_store()
        return self.vector_store.get_by_ids(ids)
    
    
## Retrieval Utils
def get_embedding_model():
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        # With the `text-embedding-3` class
        # of models, you can specify the size
        # of the embeddings you want returned.
        # dimensions=1024
        api_key=OPENAI_API_KEY
    )
    return embeddings

def get_vector_store():
    embedding_model = get_embedding_model()
    return InMemoryVectorStore(embedding_model)