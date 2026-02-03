from langgraph_scrum.llm import get_llm
from langgraph_scrum.state import ScrumState, Ticket
from langchain_core.messages import SystemMessage, HumanMessage
import uuid
from datetime import datetime

async def product_owner_node(state: ScrumState) -> ScrumState:
    """Analyze requirements and create user stories using configured LLM."""
    print("--- Planning: Product Owner analyzing requirements ---")
    
    requirements = state.get("requirements", "")
    agents = state.get("agents", {})
    po_config = agents.get("product_owner", {}).get("config", {})
    
    try:
        llm = get_llm(po_config)
        
        # System prompt from config or default
        system_prompt = po_config.get("role_description", "You are an expert Product Owner. Analyze requirements and break them down.")
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Analyze these requirements: {requirements}")
        ])
        
        content = response.content
        print(f"[Product Owner] Analysis complete (Length: {len(content)})")
    except Exception as e:
        print(f"[Product Owner] LLM Error: {e}. Falling back to mock.")
        content = f"Analyzed requirements (Mock due to error: {e})"
    
    return {"messages": [{"role": "product_owner", "content": content}]}

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
