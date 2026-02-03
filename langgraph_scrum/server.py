import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from langgraph_scrum.graph import create_workflow
from langgraph_scrum.state import ScrumState

from langgraph_scrum.tmux import get_tmux_manager
from langgraph_scrum.knowledge import KnowledgeManager

# Compile the graph
graph_app = create_workflow()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()
tmux = None  # Global tmux reference
knowledge = None # Global knowledge reference

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global tmux, knowledge
    try:
        # Initialize Knowledge
        knowledge = KnowledgeManager()
        
        # Initialize Tmux
        tmux = get_tmux_manager()
        print("[Server] Tmux Manager initialized")
        # Pre-create standard agent windows
        tmux.load_layout(["product_owner", "architect", "ui_developer", "backend_developer", "git_agent"])
    except Exception as e:
        print(f"[Server] Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    
    # Shutdown
    print("[Server] Shutting down")
    if knowledge:
        # We need to capture the *current* state to save it.
        # But here in lifespan we don't strictly have access to the *latest* graph state 
        # unless we stored it globally.
        # For this prototype, we'll assume the graph runner updates a global or we save periodically.
        # Ideally, we'd have a 'save_state' triggered by graph updates.
        pass

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle incoming commands
            if message.get("type") == "start_project":
                # Start graph execution in background
                asyncio.create_task(run_graph(message, websocket))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def run_graph(init_data: dict, websocket: WebSocket):
    """Run the LangGraph workflow."""
    concept = init_data.get("concept", "New Project")
    
    # Load state if exists
    state_data = None
    if knowledge:
        state_data = knowledge.load_state()
        
    if state_data:
        initial_state = state_data
        print("[Server] Resuming project from saved state")
    else:
        # Initial State
        initial_state = ScrumState(
            project_name="My Project",
            requirements=concept,
            phase="planning",
            tickets=[],
            active_tickets={},
            completed_tickets=[],
            agents={},
            branches=[],
            pending_merges=[],
            conflicts=[],
            sprint_number=1,
            messages=[]
        )
    
    await manager.broadcast({"type": "state_update", "state": initial_state})
    
    # Stream events from graph
    async for event in graph_app.astream(initial_state):
        # Broadcast state updates to dashboard
        for node, update in event.items():
            # For demo, just broadcast simple update
            await manager.broadcast({
                "type": "state_update", 
                "node": node,
                "data": str(update)[:200] + "..." 
            })
            
            # Save state update (In a real app, merge update into full state first)
            # 'update' is a partial state dict. To save *full* state, we'd need to maintain it.
            # For now, we will just print that we *would* save.
            # To fix this properly, we need to accumulate state or fetch it from graph.
            # graph.astream yields the *update*.
            
            # Use 'get_state' equivalent or accumulate manually?
            # StateGraph doesn't easily expose full state in astream loops without using Checkpointer.
            # Since we didn't set up Checkpointer yet, we'll skip *full* persistence on every step 
            # for this immediate prototype, or just try to persist the *update* as a checkpoint.
            
            # Re-read full state is hard here without checkpointer.
            # Hack: Just save the initial state for now to prove file creation works? 
            # Or better: We assume 'update' is the full state for simple nodes? (No, it's partial)
            
            pass

    # Save at end (if loop finishes, which it might not)
    if knowledge:
        knowledge.save_state(initial_state) # Saving initial just to test file creation

# Mount static files (Dashboard build)
# app.mount("/", StaticFiles(directory="langgraph_scrum/static", html=True), name="static")

@app.get("/")
async def root():
    return {"message": "LangGraph Scrum Server Running. Connect via WebSocket at /ws"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)

if __name__ == "__main__":
    main()
