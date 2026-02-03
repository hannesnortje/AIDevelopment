# Architecture

This document details the system architecture of LangGraph Scrum Team.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐              ┌──────────────────────┐             │
│  │   Web Dashboard      │              │   TMUX SESSION       │             │
│  │   localhost:3000     │              │   scrum-agents       │             │
│  └──────────┬───────────┘              └──────────────────────┘             │
│             │ WebSocket                           ▲ Spawns panes            │
└─────────────┼─────────────────────────────────────┼─────────────────────────┘
              │                                     │
┌─────────────┼─────────────────────────────────────┼─────────────────────────┐
│             ▼                                     │                         │
│  ┌────────────────────────────────────────────────┴───────────────────────┐ │
│  │                     LANGGRAPH SERVER                                   │ │
│  ├────────────────────────────────────────────────────────────────────────┤ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │ │
│  │  │   State     │  │   Ticket    │  │  Knowledge  │  │    Tmux     │   │ │
│  │  │  Manager    │  │ Dispatcher  │  │    Layer    │  │   Manager   │   │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │ │
│  ├────────────────────────────────────────────────────────────────────────┤ │
│  │                PARALLEL AGENTS (via Send() API)                        │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │ │
│  │  │Product  │ │Architect│ │UI Dev   │ │Backend  │ │Reviewer │         │ │
│  │  │Owner    │ │         │ │Agent    │ │Agent    │ │Agent    │         │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘         │ │
│  │  ┌─────────┐                                     ┌─────────┐         │ │
│  │  │ Tester  │                                     │Git Agent│         │ │
│  │  └─────────┘                                     └─────────┘         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                           ORCHESTRATION LAYER                                │
└──────────────────────────────────────────────────────────────────────────────┘
              │
┌─────────────┼────────────────────────────────────────────────────────────────┐
│             ▼                                                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  LLM API    │  │  File       │  │  Git        │  │  Playwright │        │
│  │ Claude/GPT  │  │  System     │  │  Repository │  │  (Browser)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                           EXTERNAL SERVICES                                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Component Communication

| From | To | Protocol | Purpose |
|------|-----|----------|---------|
| Dashboard | LangGraph Server | WebSocket | Commands, status updates |
| LangGraph | LLM API | HTTP/REST | Agent reasoning |
| LangGraph | tmux | Subprocess | Agent terminal panes |
| LangGraph | File System | Direct | Code generation |
| LangGraph | Git | Subprocess | Version control |

## State Manager

Manages the global state of the Scrum project:

```python
class ScrumState(TypedDict):
    project_name: str
    project_path: str
    phase: Literal["planning", "development", "review", "complete"]
    
    # Planning artifacts
    requirements: str
    technical_spec: str
    plan_approved: bool
    
    # Ticket management
    tickets: list[Ticket]
    active_tickets: dict[str, Ticket]  # agent_id -> ticket
    completed_tickets: list[Ticket]
    
    # Agent status
    agents: dict[str, AgentStatus]
    
    # Git state
    branches: list[str]
    pending_merges: list[str]
    conflicts: list[ConflictInfo]
    
    # Memory references
    memory_context: list[str]
    applied_conventions: list[str]
```

## Ticket Dispatcher

Dispatches tickets to agents in parallel using LangGraph's `Send()` API:

```python
from langgraph.constants import Send

def dispatch_tickets(state: ScrumState) -> list[Send]:
    """Dispatch tickets to available agents in parallel."""
    sends = []
    available_agents = get_available_agents(state)
    pending_tickets = get_pending_tickets(state)
    
    for agent, ticket in zip(available_agents, pending_tickets):
        sends.append(Send(
            node=agent.node_name,
            state={"ticket": ticket, "context": get_context(ticket)}
        ))
    
    return sends
```

## LangGraph Workflow

```python
from langgraph.graph import StateGraph

workflow = StateGraph(WorkflowState)

# Planning nodes (sequential)
workflow.add_node("product_owner", product_owner_node)
workflow.add_node("architect", architect_node)
workflow.add_node("user_approval", user_approval_node)

# Development nodes (parallel via Send)
workflow.add_node("dispatch", dispatch_agents)
workflow.add_node("agent_work", agent_work)
workflow.add_node("git_merge", git_merge_node)

# Review nodes
workflow.add_node("tester", tester_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("sprint_review", sprint_review_node)

# Release node
workflow.add_node("release", release_node)

# Edges define the flow
workflow.add_edge("product_owner", "architect")
workflow.add_edge("architect", "user_approval")
workflow.add_conditional_edges("user_approval", router)
workflow.add_edge("agent_work", "git_merge")
workflow.add_edge("git_merge", "tester")
workflow.add_edge("tester", "reviewer")
workflow.add_edge("reviewer", "sprint_review")
workflow.add_conditional_edges("sprint_review", router)  # Loop point!
workflow.add_edge("release", END)

app = workflow.compile()
```

## Parallel Execution

```
┌──────────────┐
│  DISPATCHER  │
└──────┬───────┘
       │ Uses Send() API
  ┌────┴─────┬───────────┬───────────┐
  │          │           │           │
  ▼          ▼           ▼           ▼
┌──────┐  ┌──────┐   ┌──────┐    ┌──────┐
│Send()│  │Send()│   │Send()│    │Send()│
│UI Dev│  │Bckend│   │Fullst│    │ ...  │
└──────┘  └──────┘   └──────┘    └──────┘
    │         │          │           │
    └─────────┴──────────┴───────────┘
                   │
                   ▼ All complete
            ┌─────────────┐
            │  GIT AGENT  │
            │  Merge all  │
            └─────────────┘
```

## Memory Architecture

See [Knowledge Layer](knowledge-layer.md) for detailed memory system documentation.

```
┌───────────────────────┐     ┌────────────────────────┐
│      SQLite DB        │     │   ChromaDB (Vector)    │
│   (Structured Data)   │     │   (Semantic Search)    │
├───────────────────────┤     ├────────────────────────┤
│ • decisions           │     │ • decision_embeddings  │
│ • lessons_learned     │     │ • lesson_embeddings    │
│ • ticket_history      │     │ • code_patterns        │
└───────────────────────┘     └────────────────────────┘
          │                              │
          ▼                              ▼
   Exact Queries              Semantic Queries
   "Get decision X"           "How do we handle auth?"
```
