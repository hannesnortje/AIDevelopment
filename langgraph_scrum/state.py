from typing import TypedDict, List, Dict, Optional, Literal, Any, Annotated
from datetime import datetime
import operator

# Reducer for lists to allow append behavior
def add_tickets(old: List[Any], new: List[Any]) -> List[Any]:
    return old + new

class Ticket(TypedDict):
    id: str
    title: str
    description: str
    type: Literal["feature", "bug", "chore"]
    status: Literal["draft", "approved", "in_progress", "review", "testing", "done", "rejected"]
    assigned_to: Optional[str]
    branch: Optional[str]
    dependencies: List[str]
    files_changed: List[str]
    created_at: str
    updated_at: str

class AgentStatus(TypedDict):
    agent_id: str
    role: str
    state: Literal["idle", "working", "done", "error"]
    current_ticket: Optional[str]
    llm: str
    tmux_pane: str

class ConflictInfo(TypedDict):
    branch: str
    files: List[str]
    timestamp: str

class ScrumState(TypedDict):
    project_name: str
    project_path: str
    phase: Literal["planning", "development", "review", "release", "complete"]
    
    # Planning
    requirements: str
    technical_spec: str
    plan_approved: bool
    
    # Execution
    # Using reducers for lists that might be updated in parallel or incrementally
    tickets: Annotated[List[Ticket], add_tickets] 
    active_tickets: Dict[str, Ticket]
    completed_tickets: Annotated[List[Ticket], add_tickets]
    
    # Team
    agents: Dict[str, AgentStatus]
    
    # Git
    branches: List[str]
    pending_merges: List[str]
    conflicts: List[ConflictInfo]
    
    # Sprint
    sprint_number: int
    
    # Internal messaging
    messages: List[Dict[str, Any]]
