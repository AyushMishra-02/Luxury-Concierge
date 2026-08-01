import json
import os
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "data/hotels.json"

class SimpleRetriever:
    def invoke(self, query: str):
        if not os.path.exists(DATA_PATH):
            return []
        
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
            documents.append(Document(page_content=content))
        
        return documents

def get_retriever():
    return SimpleRetriever()

if __name__ == "__main__":
    print("Database is ready! Using lightweight JSON retriever.")
