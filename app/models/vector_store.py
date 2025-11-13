import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Initiating vector store 
class VectorStore:
    def __init__(self, path):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory=path,
            embedding_function=self.embeddings
        )
    # Inside vector store you are adding the documents so this will create vectors on document that is added 
    def add_documents(self,documents):
        self.vector_store.add_documents(documents)

    def similarity_search(self,query, k =4):
        return self.vector_store.similarity_search(query,k=k)