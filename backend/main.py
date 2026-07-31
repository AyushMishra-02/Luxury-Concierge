from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from agents import travel_agent_app

app = FastAPI(title="The Luxury Concierge API")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    query: str

class TripResponse(BaseModel):
    parsed_requirements: str
    hotel_options: str
    final_itinerary: str

@app.post("/api/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest):
    try:
        # Initialize state
        initial_state = {
            "user_query": request.query,
            "parsed_requirements": "",
            "hotel_options": "",
            "final_itinerary": ""
        }
        
        # Invoke LangGraph workflow
        result = travel_agent_app.invoke(initial_state)
        
        return TripResponse(
            parsed_requirements=result.get("parsed_requirements", ""),
            hotel_options=result.get("hotel_options", ""),
            final_itinerary=result.get("final_itinerary", "")
        )
    except Exception as e:
        print(f"Error in plan_trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
