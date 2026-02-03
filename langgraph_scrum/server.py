import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from langgraph_scrum.graph import create_workflow
from langgraph_scrum.state import ScrumState

from langgraph_scrum.tmux import get_tmux_manager

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global tmux
    try:
        tmux = get_tmux_manager()
        print("[Server] Tmux Manager initialized")
        # Pre-create standard agent windows
        tmux.load_layout(["product_owner", "architect", "ui_developer", "backend_developer", "git_agent"])
    except Exception as e:
        print(f"[Server] Failed to initialize Tmux: {e}")
    
    yield
    
    # Shutdown
    print("[Server] Shutting down")

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
        # event is dict like keys: node_name -> state_update
        for node, update in event.items():
            # For demo, just broadcast simple update
            await manager.broadcast({
                "type": "state_update", 
                "node": node,
                "data": str(update)[:200] + "..." # Truncate for log
            })

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
