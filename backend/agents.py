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
# Using Groq's fast LLaMA 3.3 model
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def intake_node(state: GraphState):
    print("--- INTAKE AGENT ---")
    sys_msg = SystemMessage(content="You are a luxury travel concierge intake agent. "
                              "Review the entire conversation and extract the CURRENT destination, budget, dates, and any preferences. "
                              "If the user is updating or refining their previous request, ensure your summary reflects those changes. "
                              "Format the output as a clean summary.")
    
    # We pass the system message + the entire conversation history to the LLM
    prompt_messages = [sys_msg] + state["messages"]
    
    response = llm.invoke(prompt_messages)
    return {"parsed_requirements": response.content}

def researcher_node(state: GraphState):
    print("--- RESEARCHER AGENT ---")
    researcher_llm = llm.bind_tools([search_luxury_hotels])
    messages = [
        SystemMessage(content="You are a luxury travel researcher. Use the search_luxury_hotels tool "
                              "to find the best luxury experiences matching the requirements. "
                              "Return a summary of the best options found."),
        HumanMessage(content=f"Requirements: {state['parsed_requirements']}\n\nPlease search for appropriate luxury experiences.")
    ]
    
    response = researcher_llm.invoke(messages)
    if response.tool_calls:
        # Execute the first tool call for simplicity
        tool_call = response.tool_calls[0]
        tool_output = search_luxury_hotels.invoke(tool_call["args"])
        
        # Add tool output to context and get final answer
        messages.append(response)
        messages.append(HumanMessage(content=f"Tool Output:\n{tool_output}\n\nBased on this, summarize the best options."))
        final_response = llm.invoke(messages)
        return {"hotel_options": final_response.content}
    else:
        return {"hotel_options": response.content}

def itinerary_node(state: GraphState):
    print("--- ITINERARY AGENT ---")
    
    # Get the latest user query from the message history to pass context
    latest_query = state["messages"][-1].content if state["messages"] else ""
    
    messages = [
        SystemMessage(content="You are a luxury travel itinerary planner. "
                              "Create a luxurious, day-by-day itinerary based on the selected hotel options and user requirements. "
                              "The itinerary should include exclusive activities, fine dining, and relaxation. "
                              "Output the final itinerary formatted in Markdown. Do not include pleasantries, just the itinerary."),
        HumanMessage(content=f"Latest User Query: {latest_query}\nRequirements: {state['parsed_requirements']}\nHotel Options: {state['hotel_options']}")
    ]
    response = llm.invoke(messages)
    
    # Return the new itinerary, AND append it to the chat history so the agent remembers it next time!
    return {
        "final_itinerary": response.content,
        "messages": [response]
    }

# Build Graph
workflow = StateGraph(GraphState)

workflow.add_node("intake", intake_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("itinerary", itinerary_node)

workflow.add_edge(START, "intake")
workflow.add_edge("intake", "researcher")
workflow.add_edge("researcher", "itinerary")
workflow.add_edge("itinerary", END)

# Compile with MemorySaver to persist state across follow-up questions
memory = MemorySaver()
travel_agent_app = workflow.compile(checkpointer=memory)
