from langgraph_scrum.state import ScrumState, Ticket
import uuid
from datetime import datetime

async def product_owner_node(state: ScrumState) -> ScrumState:
    """Analyze requirements and create user stories."""
    print("--- Planning: Product Owner analyzing requirements ---")
    
    # Mocking LLM requirement analysis for initial setup
    requirements = state.get("requirements", "")
    
    # In real implementation: Call LLM with requirements
    
    return {"messages": [{"role": "product_owner", "content": "Analyzed requirements"}]}

async def architect_node(state: ScrumState) -> ScrumState:
    """Design authentication system and create tickets."""
    print("--- Planning: Architect designing system ---")
    
    # Mocking ticket creation
    tickets = [
        Ticket(
            id=str(uuid.uuid4())[:8],
            title="Setup Project Structure",
            description="Initialize repository and basic structure",
            type="chore",
            status="draft",
            assigned_to=None,
            branch=None,
            dependencies=[],
            files_changed=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        ),
         Ticket(
            id=str(uuid.uuid4())[:8],
            title="Implement Core API",
            description="Create basic FastAPI endpoints",
            type="feature",
            status="draft",
            assigned_to=None,
            branch=None,
            dependencies=[],
             files_changed=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    ]
    
    return {
        "tickets": tickets, 
        "technical_spec": "Microservices architecture...",
        "plan_approved": False 
    }

async def user_approval_node(state: ScrumState) -> ScrumState:
    """Wait for user approval of the plan."""
    print("--- Planning: Waiting for user approval ---")
    
    # This node would typically pause or check an external signal
    # For now, we assume auto-approval for the basic loop or check a flag
    
    # In a real WebSocket server, this might be where we pause the graph
    # until a "approve_plan" message is received and injected into state.
    
    return {"plan_approved": True} # Auto-approve for testing flow
