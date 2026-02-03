# Web Dashboard

The web dashboard provides a browser-based interface for managing the Scrum process, built with Lit 3 and Vite.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🌐 http://localhost:3000                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │ Kanban  │ │ Agents  │ │ Config  │ │   Git   │ │Terminal │              │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘              │
│                                                                              │
│  ┌────────────────────────────┐  ┌────────────────────────────────────────┐│
│  │  📋 KANBAN BOARD           │  │  🖥️ TERMINAL (xterm.js)                ││
│  │  ┌────┐ ┌────┐ ┌────┐     │  │  [product-owner] [ui-dev] [backend]   ││
│  │  │Back│ │ In │ │Done│     │  │  $ npm run dev                         ││
│  │  │log │ │Prog│ │    │     │  │  Server running on port 3000           ││
│  │  └────┘ └────┘ └────┘     │  │                                        ││
│  └────────────────────────────┘  └────────────────────────────────────────┘│
│                                                                              │
│  ┌────────────────────────────┐  ┌────────────────────────────────────────┐│
│  │  🤖 AGENTS                  │  │  🔀 GIT STATUS                         ││
│  │  product-owner  🟢 Active  │  │  main ──────────●                      ││
│  │  ui-dev-1       🟢 Working │  │  develop ───●───┴── merging            ││
│  │  backend-1      🟡 Idle    │  │  feature/1 ─┘                          ││
│  └────────────────────────────┘  └────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

```
dashboard/
├── package.json              # lit, vite, xterm
├── vite.config.ts
├── index.html
├── src/
│   ├── main.ts               # Entry point
│   ├── dashboard-app.ts      # Main component
│   ├── components/
│   │   ├── kanban-board.ts   # Drag-and-drop Kanban
│   │   ├── agent-panel.ts    # Agent status cards
│   │   ├── team-config.ts    # Team configuration
│   │   ├── terminal-view.ts  # xterm.js terminal
│   │   ├── git-status.ts     # Branch visualization
│   │   └── sprint-review.ts  # Sprint review dialog
│   └── services/
│       └── websocket.ts      # WebSocket client
```

## Main Dashboard Component

```typescript
@customElement('dashboard-app')
export class DashboardApp extends LitElement {
  @state() private connected = false;
  @state() private projectState: ProjectState | null = null;
  @state() private activeTab = 'kanban';
  
  private ws: WebSocket | null = null;
  
  connectedCallback() {
    super.connectedCallback();
    this.connectWebSocket();
  }
  
  private connectWebSocket() {
    this.ws = new WebSocket('ws://localhost:8765');
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleServerMessage(message);
    };
  }
  
  render() {
    return html`
      <div class="dashboard">
        <header>
          <h1>🤖 LangGraph Scrum Dashboard</h1>
        </header>
        <nav>
          <button @click=${() => this.activeTab = 'kanban'}>📋 Kanban</button>
          <button @click=${() => this.activeTab = 'agents'}>🤖 Agents</button>
          <button @click=${() => this.activeTab = 'terminal'}>🖥️ Terminal</button>
        </nav>
        <main>${this.renderActiveTab()}</main>
      </div>
    `;
  }
}
```

## Components

### Kanban Board

Displays tickets by status with drag-and-drop:

```typescript
@customElement('kanban-board')
export class KanbanBoard extends LitElement {
  @property({ type: Array }) tickets: Ticket[] = [];
  
  private columns = ['backlog', 'in_progress', 'review', 'testing', 'done'];
  
  render() {
    return html`
      <div class="kanban">
        ${this.columns.map(col => html`
          <div class="column">
            <h3>${col.replace('_', ' ').toUpperCase()}</h3>
            ${this.getTicketsForColumn(col).map(ticket => html`
              <ticket-card .ticket=${ticket}></ticket-card>
            `)}
          </div>
        `)}
      </div>
    `;
  }
}
```

### Terminal View

Live terminal output using xterm.js:

```typescript
@customElement('terminal-view')
export class TerminalView extends LitElement {
  @property({ type: Array }) agents: string[] = [];
  private terminals: Map<string, Terminal> = new Map();
  
  private createTerminal(agentId: string) {
    const term = new Terminal({
      theme: { background: '#1e1e1e' },
      fontSize: 12
    });
    term.open(container);
    this.terminals.set(agentId, term);
  }
  
  public appendOutput(agentId: string, data: string) {
    this.terminals.get(agentId)?.write(data);
  }
}
```

### Agent Panel

Shows agent status and allows adding/removing agents:

```typescript
@customElement('agent-panel')
export class AgentPanel extends LitElement {
  @property({ type: Object }) agents: Record<string, AgentStatus> = {};
  
  render() {
    return html`
      ${Object.entries(this.agents).map(([id, status]) => html`
        <div class="agent-card ${status.state}">
          <div class="name">${id}</div>
          <div class="status">${this.statusIcon(status.state)}</div>
          <div class="task">${status.current_ticket || 'Idle'}</div>
        </div>
      `)}
      <button @click=${() => this.addAgent('ui_developer')}>+ UI Dev</button>
    `;
  }
}
```

### Team Configuration

Initial project setup before starting:

```typescript
@customElement('team-config')
export class TeamConfig extends LitElement {
  @state() private agents: AgentConfig[] = this.getDefaultTeam();
  @state() private concept = '';
  
  private handleStart() {
    this.dispatchEvent(new CustomEvent('start', {
      detail: {
        concept: this.concept,
        config: { agents: this.agents }
      }
    }));
  }
  
  render() {
    return html`
      <h2>📋 Project Planning</h2>
      <textarea placeholder="Describe your project..."></textarea>
      
      <h3>🤖 Team Composition</h3>
      <table>
        <tr><th>Role</th><th>Count</th><th>LLM</th></tr>
        ${this.agents.map(agent => html`
          <tr>
            <td>${agent.role}</td>
            <td><input type="number" value=${agent.count}></td>
            <td><select>${this.llmOptions()}</select></td>
          </tr>
        `)}
      </table>
      
      <button @click=${this.handleStart}>🚀 Start Project</button>
    `;
  }
}
```

## WebSocket Communication

The dashboard communicates with the server via WebSocket:

```typescript
// Client -> Server
ws.send(JSON.stringify({
  type: 'start_project',
  concept: 'Todo app with dark mode',
  team_config: {...}
}));

// Server -> Client
{
  type: 'state_update',
  state: {
    phase: 'development',
    tickets: [...],
    agents: {...}
  }
}
```

See [API Reference](api-reference.md) for complete WebSocket API.

## Server (FastAPI)

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        data = await websocket.receive_json()
        await handle_message(websocket, data)

async def stream_terminal(ws: WebSocket, agent_id: str):
    """Stream tmux output to browser."""
    while True:
        output = await tmux_manager.read_pane_output(agent_id)
        if output:
            await ws.send_json({
                "type": "terminal_output",
                "agent_id": agent_id,
                "data": output
            })
        await asyncio.sleep(0.1)
```

## Running the Dashboard

The dashboard is served by the FastAPI server:

```bash
# Build for production
cd dashboard && npm run build

# Start server (serves dashboard at /)
python -m langgraph_scrum.server

# Open browser
open http://localhost:3000
```

For development with hot reload:

```bash
# Terminal 1: Vite dev server
cd dashboard && npm run dev

# Terminal 2: FastAPI server
python -m langgraph_scrum.server
```
