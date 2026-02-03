import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

class Config:
    def __init__(self):
        self._config = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
            "MODEL_PROVIDER": os.getenv("MODEL_PROVIDER", "anthropic"),
            "MODEL_NAME": os.getenv("MODEL_NAME", "claude-3-5-sonnet-20240620"),
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        self._config[key] = value
        # Optional: Write back to .env if desired, but for now runtime only
        # or we could implement a .env updater.
        # For security, runtime memory update is safer than writing to disk immediately
        # unless user explicitly wants persistence.
        
        # If we want to persist to .env:
        # with open(env_path, "a") as f:
        #    f.write(f"\n{key}={value}")
        pass

    def update(self, updates: Dict[str, Any]):
        for k, v in updates.items():
            self.set(k, v)

# Global config instance
config = Config()
