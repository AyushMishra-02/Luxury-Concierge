from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.tools import tool
import database

# Define the Tool
@tool
def search_luxury_hotels(query: str) -> str:
    """Search for luxury hotels, yachts, and resorts based on a query (e.g., beachfront, under $5000, Paris)."""
    retriever = database.get_retriever()
    docs = retriever.invoke(query)
    if not docs:
        return "No matching luxury experiences found."
    
    results = []
    for doc in docs:
        results.append(doc.page_content)
    return "\n\n---\n\n".join(results)

# Define State
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    parsed_requirements: str
    hotel_options: str
    final_itinerary: str

# Define Nodes
# Upgraded back to the brilliant 70B model for maximum luxury quality.
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)

def intake_node(state: GraphState):
    print("--- INTAKE AGENT ---")
    sys_msg = SystemMessage(content="You are a luxury travel concierge. Extract the destination and preferences from the user's request. Keep it extremely brief, just 1-2 sentences.")
    prompt_messages = [sys_msg] + state["messages"]
    response = llm.invoke(prompt_messages)
    return {"parsed_requirements": response.content}

def researcher_node(state: GraphState):
    print("--- RESEARCHER AGENT ---")
    sys_msg = SystemMessage(content=(
        "You are an elite luxury travel researcher. Based on the user's requirements, "
        "recommend 2-3 TRUE, real-world ultra-luxury hotels or resorts specifically in their requested destination. "
        "Provide real details like the hotel name, neighborhood/location, and exclusive amenities. "
        "If they ask for a specific city like Udaipur, only recommend real 5-star hotels in Udaipur (e.g., Taj Lake Palace). "
        "Do not hallucinate hotels or recommend hotels from the wrong country."
    ))
    messages = [sys_msg, HumanMessage(content=state["parsed_requirements"])]
    response = llm.invoke(messages)
    return {"hotel_options": response.content}

def itinerary_node(state: GraphState):
    print("--- ITINERARY AGENT ---")
    latest_query = state["messages"][-1].content if state["messages"] else ""
    
    sys_msg = SystemMessage(content=(
        "You are an elite, world-class luxury travel concierge for ultra-high-net-worth individuals. "
        "Create a breathtaking, ultra-luxurious, day-by-day itinerary based on the user's request and the provided hotel options. "
        "Make the response incredibly detailed and premium. Include things like private helicopter transfers, Michelin-starred dining reservations, "
        "VIP exclusive access, and private yacht charters. Use beautiful Markdown formatting with headers and bullet points. "
        "Do not include basic pleasantries, just deliver the masterpiece itinerary."
    ))
    
    messages = [
        sys_msg,
        HumanMessage(content=f"User Request: {latest_query}\n\nSelected Hotel/Resort Options:\n{state['hotel_options']}")
    ]
    response = llm.invoke(messages)
    
    return {
        "final_itinerary": response.content,
        "messages": [response]
    }

# Build Graph
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("parse_requirements", intake_node)
workflow.add_node("retrieve_hotels", researcher_node)
workflow.add_node("draft_itinerary", itinerary_node)

# Define edges
workflow.add_edge(START, "parse_requirements")
workflow.add_edge("parse_requirements", "retrieve_hotels")
workflow.add_edge("retrieve_hotels", "draft_itinerary")
workflow.add_edge("draft_itinerary", END)

# Compile graph
memory = MemorySaver()
travel_agent_app = workflow.compile(checkpointer=memory)
