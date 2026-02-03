from langgraph_scrum.state import ScrumState
from langgraph.graph import END

async def tester_node(state: ScrumState) -> ScrumState:
    """Run tests on the codebase."""
    print("--- Review: Running tests ---")
    return {}

async def reviewer_node(state: ScrumState) -> ScrumState:
    """Review code changes."""
    print("--- Review: Code review ---")
    return {}

async def sprint_review_node(state: ScrumState) -> ScrumState:
    """Present sprint results and decide next steps."""
    print("--- Review: Sprint Review ---")
    return {"phase": "review"}

async def release_node(state: ScrumState) -> ScrumState:
    """Release to main."""
    print("--- Release: Deploying ---")
    return {"phase": "complete"}

def router(state: ScrumState):
    """Decide where to go after sprint review."""
    phase = state.get("phase")
    if phase == "release":
        return "release"
    elif phase == "planning":
        return "planning" # Loop back
    else:
        return END
