from langgraph_scrum.state import ScrumState
from langgraph.constants import Send

async def dispatch_agents(state: ScrumState):
    """Dispatch tickets to agents using Send API."""
    print("--- Development: Dispatching agents ---")
    
    tickets = state.get("tickets", [])
    pending_tickets = [t for t in tickets if t["status"] == "draft"]  # Simplified logic
    
    sends = []
    for ticket in pending_tickets:
        # In a real app, logic to assign to specific agent types
        # For now, just dispatch to 'agent_work' node
        sends.append(Send("agent_work", {"ticket": ticket}))
        
    return sends 

async def agent_work(state: dict): # Receives sub-state from Send
    """Simulate agent working on a ticket."""
    ticket = state["ticket"]
    print(f"--- Agent working on ticket: {ticket['title']} ---")
    
    # Simulate work
    ticket["status"] = "review"
    
    return {"completed_tickets": [ticket]} # Return to global state via reducer (conceptually)


async def git_merge_node(state: ScrumState) -> ScrumState:
    """Merge completed branches."""
    print("--- Git: Merging work ---")
    
    # Logic to merge branches
    
    return {"pending_merges": []}
