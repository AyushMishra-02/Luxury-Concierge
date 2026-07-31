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

def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    # Return a retriever that fetches top 2 most relevant results
    return vectorstore.as_retriever(search_kwargs={"k": 2})

if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY environment variable is not set. Please set it in a .env file.")
    else:
        init_db()
