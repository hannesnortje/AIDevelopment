import pytest
import asyncio
import json
import websockets
from typing import List

SERVER_URL = "ws://localhost:8765/ws"

@pytest.mark.asyncio
async def test_scrum_workflow():
    """
    Integration test for the full Scrum workflow.
    Assumes the server is running.
    """
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            print("[Test] Connected to server")
            
            # 1. Start Project
            start_payload = {
                "type": "start_project", 
                "concept": "Integration Test App"
            }
            await websocket.send(json.dumps(start_payload))
            print("[Test] Sent start_project command")
            
            # 2. Monitor for States
            expected_nodes = ["product_owner", "architect", "user_approval", "dispatch"]
            seen_nodes = set()
            
            # We want to see at least these nodes activate
            # Timeout after 30 seconds
            try:
                async with asyncio.timeout(30):
                    while len(seen_nodes) < len(expected_nodes):
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if data.get("type") == "state_update":
                            node = data.get("node")
                            if node:
                                print(f"[Test] Node update: {node}")
                                seen_nodes.add(node)
                                
                            state = data.get("state")
                            if state and state.get("project_name") == "My Project": # Default mock name
                                print("[Test] Initial state received")

            except asyncio.TimeoutError:
                pytest.fail(f"Timed out waiting for nodes. Seen: {seen_nodes}")
                
            # Verify we saw the expected progression
            for node in expected_nodes:
                assert node in seen_nodes, f"Missing node execution: {node}"
                
            print("[Test] Workflow verification passed!")
            
    except ConnectionRefusedError:
        pytest.fail("Could not connect to server. Is it running?")
