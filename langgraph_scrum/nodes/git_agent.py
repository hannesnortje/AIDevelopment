from langgraph_scrum.state import ScrumState
from langgraph_scrum.tools.git import GitTools

# Global instance for now
git_tools = GitTools()

async def git_agent_node(state: ScrumState) -> dict:
    """Handle Git operations requested by other agents."""
    print("--- Git Agent: Processing requests ---")
    
    # Logic to look for tickets requesting git actions or messy state
    # For now, we sync the branches list to state
    
    branches = git_tools.list_branches()
    
    # Auto-create worktrees for active tickets (PROTOTYPE LOGIC)
    tickets = state.get("tickets", [])
    active_tickets = [t for t in tickets if t["status"] == "in_progress"]
    
    for ticket in active_tickets:
        if not ticket.get("branch"):
            # Assign branch if missing
            branch_name = f"feature/{ticket['id']}"
            git_tools.create_branch(branch_name)
            git_tools.create_worktree(branch_name)
            # Updating ticket in state is complex with reducers in LangGraph 
            # without emitting a full update or using specific reducer logic.
            # Here we just perform side effects and return global updates.
            
    return {"branches": branches}
