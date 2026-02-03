# Documentation

Welcome to the LangGraph Scrum Team documentation.

## Quick Links

| Document | Description |
|----------|-------------|
| [Getting Started](getting-started.md) | Installation, setup, first project |
| [Architecture](architecture.md) | System design and component overview |
| [Agents](agents.md) | Agent types and lifecycle |
| [Git Integration](git-integration.md) | Worktrees and branch management |
| [Knowledge Layer](knowledge-layer.md) | Memory and context system |
| [Dashboard](dashboard.md) | Web UI documentation |
| [API Reference](api-reference.md) | WebSocket API |
| [Workflow](workflow.md) | Sprint cycle documentation |

## Overview

LangGraph Scrum Team is an AI-powered development system that:

1. Takes a project concept from you
2. Plans the work with Product Owner and Architect agents
3. Executes development in parallel with specialized agents
4. Reviews and tests the code
5. Merges to main when you approve

Each agent runs in its own tmux pane with an isolated Git worktree, coordinated by LangGraph's parallel execution capabilities.
