import json
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "data/hotels.json"
CHROMA_PATH = "chroma_db"

def init_db():
    print("Initializing ChromaDB...")
    
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        hotels = json.load(f)

    documents = []
    for hotel in hotels:
        content = (
            f"Hotel: {hotel['name']}\n"
            f"Location: {hotel['location']}\n"
            f"Category: {hotel['category']}\n"
            f"Price per night: ${hotel['price_per_night']}\n"
            f"Rating: {hotel['rating']}\n"
            f"Description: {hotel['description']}\n"
            f"Amenities: {', '.join(hotel['amenities'])}"
        )
        metadata = {
            "id": hotel["id"],
            "name": hotel["name"],
            "location": hotel["location"],
            "price_per_night": hotel["price_per_night"],
            "category": hotel["category"]
        }
        documents.append(Document(page_content=content, metadata=metadata))

    # Initialize HuggingFace Embeddings (runs locally, completely free)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create ChromaDB vector store
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print(f"Successfully embedded and stored {len(documents)} luxury experiences in {CHROMA_PATH}.")
    return vectorstore

class SimpleRetriever:
    def invoke(self, query: str):
        if not os.path.exists(DATA_PATH):
            return []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            hotels = json.load(f)
        documents = []
        for hotel in hotels:
            content = (
                f"Hotel: {hotel['name']}\nLocation: {hotel['location']}\n"
                f"Category: {hotel['category']}\nPrice per night: ${hotel['price_per_night']}\n"
                f"Rating: {hotel['rating']}\nDescription: {hotel['description']}\n"
                f"Amenities: {', '.join(hotel['amenities'])}"
            )
            documents.append(Document(page_content=content))
        return documents

def get_chroma_retriever():
    """Original PyTorch/ChromaDB retriever (Causes OOM on 512MB RAM free tiers)"""
    if not os.path.exists(CHROMA_PATH):
        print("Vector DB not found. Initializing on the fly...")
        init_db()
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 2})

def get_retriever():
    """Custom lightweight JSON retriever (Uses ~30MB RAM)"""
    return SimpleRetriever()

if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY environment variable is not set. Please set it in a .env file.")
    else:
        init_db()
