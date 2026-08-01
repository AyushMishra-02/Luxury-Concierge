# The Luxury Concierge 

An ultra-premium, AI-powered travel agent that curates bespoke luxury itineraries, estates, private islands, and yachts around the globe. 


## Architecture

This is a full-stack, stateful AI application consisting of two parts:

### 1. The Multi-Agent Backend (`/backend`)
Powered by **LangGraph** and **Groq** (using LLaMA 3.3). The backend features a team of specialized AI agents:
- **Intake Agent:** Analyzes the conversation history to extract travel dates, budgets, and preferences.
- **Researcher Agent:** Uses a custom RAG (Retrieval-Augmented Generation) pipeline via **ChromaDB** and **HuggingFace Embeddings** (`all-MiniLM-L6-v2`) to search a database of hyper-specific luxury properties.
- **Itinerary Agent:** Crafts the final, day-by-day luxury itinerary based on the selected property and user preferences.

It uses **FastAPI** to serve the agentic workflow and `MemorySaver` to maintain persistent conversational state across sessions.

### 2. The Premium Frontend (`/frontend`)
A modern, glassmorphic UI built with **Next.js** and **React**.
- **Aesthetic:** Designed with mesh gradients, `Playfair Display`, and `Outfit` fonts to emulate the feel of a luxury brand.
- **Interactive:** Features a fluid UI that transitions from a beautiful full-screen search into an editorial-style itinerary view.
- **Stateful Chat:** Includes a "Refine Your Journey" feature that allows users to chat back and forth with the AI to tweak their trip.

## How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Groq API Key](https://console.groq.com/keys)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the `backend` folder and add your Groq key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
5. Run the FastAPI server:
   ```bash
   python main.py
   ```
   *(The server will run on `http://0.0.0.0:8000`. On first run, it will automatically download the HuggingFace embeddings model and initialize the Vector Database).*

### Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser to experience the app!


