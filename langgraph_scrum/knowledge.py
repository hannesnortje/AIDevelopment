import os
import json
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional

class KnowledgeManager:
    def __init__(self, data_dir: str = ".langgraph/data"):
        self.data_dir = os.path.abspath(data_dir)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.state_file = os.path.join(self.data_dir, "state.json")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=os.path.join(self.data_dir, "chroma"))
        self.collection = self.chroma_client.get_or_create_collection(name="scrum_knowledge")

    def add_lesson(self, lesson: str, metadata: Dict[str, Any] = None):
        """Add a lesson learned or documentation snippet."""
        if metadata is None:
            metadata = {}
            
        # simple ID gen
        import uuid
        doc_id = str(uuid.uuid4())
        
        self.collection.add(
            documents=[lesson],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"[Knowledge] Added lesson: {doc_id}")

    def search_lessons(self, query: str, n_results: int = 3) -> List[str]:
        """Search for relevant lessons."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        # Flatten results
        return results['documents'][0] if results['documents'] else []

    def save_state(self, state: Dict[str, Any]):
        """Persist the current state to disk."""
        try:
            # We might need to filter out non-serializable objects if any
            # For TypedDicts composed of primitives/lists/dicts, json dump is fine.
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2, default=str)
            print(f"[Knowledge] State saved to {self.state_file}")
        except Exception as e:
            print(f"[Knowledge] Failed to save state: {e}")

    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load state from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                print(f"[Knowledge] State loaded from {self.state_file}")
                return state
            except Exception as e:
                print(f"[Knowledge] Failed to load state: {e}")
        return None
