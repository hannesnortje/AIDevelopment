# Getting Started

This guide walks you through setting up LangGraph Scrum Team and running your first project.

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | LangGraph server and agents |
| Node.js | 18+ | Dashboard and TypeScript projects |
| tmux | Latest | Agent terminal management |
| Git | 2.30+ | Worktree support required |
| LLM API Key | - | Anthropic or OpenAI |

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/hannesnortje/AIDevelopment.git
cd AIDevelopment
```

### 2. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

pip install -e ".[dev]"
```

### 3. Install Dashboard Dependencies

```bash
cd dashboard
npm install
cd ..
```

### 4. Configure API Keys

```bash
# Option 1: Anthropic (recommended)
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: OpenAI
export OPENAI_API_KEY="sk-..."
```

Or add to `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Configuration

Create `.langgraph/config/server.yaml`:

```yaml
server:
  host: localhost
  port: 8765

llm:
  provider: anthropic  # or openai
  model: claude-sonnet-4-20250514
  max_tokens: 4096

agents:
  max_parallel: 5
  default_types:
    - ui_developer
    - backend_developer
    - reviewer

git:
  auto_push: false
  worktrees_dir: .worktrees

tmux:
  session_name: scrum-agents
```

## Running the Server

```bash
# Start the server
python -m langgraph_scrum.server --project /path/to/your/project

# The dashboard opens at http://localhost:3000
```

## Monitoring Agents

Each agent runs in a tmux pane. To watch them work:

```bash
# Attach to the tmux session
tmux attach -t scrum-agents

# Navigation in tmux:
# Ctrl+b, arrow keys - switch between panes
# Ctrl+b, d - detach (agents keep running)
# Ctrl+b, z - zoom current pane
```

## Your First Project

1. **Open the Dashboard** at `http://localhost:3000`

2. **Enter a Project Concept**:
   ```
   Create a todo app with dark mode and user accounts
   ```

3. **Review the Plan**: Product Owner and Architect create requirements and tickets

4. **Approve**: Click "Approve Plan" to start development

5. **Watch**: Agents work in parallel (visible in tmux or dashboard terminal view)

6. **Sprint Review**: When complete, decide to:
   - Release to main
   - Add more features
   - Continue with fixes

## Troubleshooting

### tmux session not found

```bash
# Check if session exists
tmux list-sessions

# Start manually if needed
tmux new-session -s scrum-agents
```

### API key errors

Verify your key is set:

```bash
echo $ANTHROPIC_API_KEY
# Should show your key
```

### Port already in use

```bash
# Find what's using port 8765
lsof -i :8765

# Kill the process or use a different port in config
```

### Git worktree errors

Ensure Git version supports worktrees:

```bash
git --version  # Should be 2.30+

# Clean up stale worktrees
git worktree prune
```

## Next Steps

- [Architecture](architecture.md) - Understand the system design
- [Agents](agents.md) - Learn about agent types and customization
- [Workflow](workflow.md) - Understand the sprint cycle
