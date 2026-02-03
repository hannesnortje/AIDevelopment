from langgraph.graph import StateGraph, END
from langgraph_scrum.state import ScrumState
from langgraph_scrum.nodes import (
    product_owner_node,
    architect_node, 
    user_approval_node,
    dispatch_agents,
    agent_work,
    git_merge_node,
    tester_node,
    reviewer_node,
    sprint_review_node,
    release_node,
    router
)

def create_workflow():
    workflow = StateGraph(ScrumState)
    
    # Planning
    workflow.add_node("product_owner", product_owner_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("user_approval", user_approval_node)
    
    # Development
    workflow.add_node("dispatch", dispatch_agents)
    workflow.add_node("agent_work", agent_work)
    workflow.add_node("git_merge", git_merge_node)
    
    # Review
    workflow.add_node("tester", tester_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("sprint_review", sprint_review_node)
    workflow.add_node("release", release_node)
    
    # Edges
    # Planning Flow
    workflow.set_entry_point("product_owner")
    workflow.add_edge("product_owner", "architect")
    workflow.add_edge("architect", "user_approval")
    workflow.add_edge("user_approval", "dispatch")
    
    # Development Flow
    workflow.add_conditional_edges("dispatch", dispatch_agents) # This node returns Sends
    workflow.add_edge("agent_work", "git_merge")
    workflow.add_edge("git_merge", "tester")
    
    # Review Flow
    workflow.add_edge("tester", "reviewer")
    workflow.add_edge("reviewer", "sprint_review")
    
    # Loop/Finish Logic
    workflow.add_conditional_edges(
        "sprint_review",
        router,
        {
            "release": "release",
            "planning": "product_owner",
            END: END
        }
    )
    
    workflow.add_edge("release", END)
    
    return workflow.compile()
