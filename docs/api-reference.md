# API Reference

This document describes the WebSocket API and data types used by LangGraph Scrum Team.

## WebSocket Connection

Connect to the server at `ws://localhost:8765/ws`.

## Commands (Client → Server)

### Project Management

| Command | Parameters | Description |
|---------|------------|-------------|
| `start_project` | `{concept: string, team_config: TeamConfig}` | Start new project |
| `approve_plan` | `{}` | Approve current plan |
| `revise_plan` | `{feedback: string}` | Request plan revision |

### Ticket Management

| Command | Parameters | Description |
|---------|------------|-------------|
| `approve_ticket` | `{ticket_id: string}` | Approve completed ticket |
| `reject_ticket` | `{ticket_id: string, feedback: string}` | Reject ticket with feedback |

### Agent Management

| Command | Parameters | Description |
|---------|------------|-------------|
| `add_agent` | `{role: string, llm: string}` | Add new agent at runtime |
| `remove_agent` | `{agent_id: string}` | Remove idle agent |

### Sprint Control

| Command | Parameters | Description |
|---------|------------|-------------|
| `pause_sprint` | `{}` | Pause all agents |
| `resume_sprint` | `{}` | Resume agents |
| `sprint_decision` | `{decision: string, feedback?: string}` | User decision at review |

### Terminal

| Command | Parameters | Description |
|---------|------------|-------------|
| `subscribe_terminal` | `{agent_id: string}` | Subscribe to agent's terminal output |

### Git

| Command | Parameters | Description |
|---------|------------|-------------|
| `resolve_conflict` | `{branch: string, resolution: string}` | Resolve merge conflict |

## Events (Server → Client)

### State Updates

| Event | Data | Description |
|-------|------|-------------|
| `state_update` | `ScrumState` | Full state update |
| `ticket_update` | `Ticket` | Single ticket changed |
| `agent_status` | `{agent_id: string, status: AgentStatus}` | Agent status changed |

### Approvals

| Event | Data | Description |
|-------|------|-------------|
| `approval_needed` | `{ticket_id: string, preview: string}` | Ticket ready for review |
| `plan_ready` | `{plan: string, tickets: Ticket[]}` | Plan ready for approval |

### Terminal

| Event | Data | Description |
|-------|------|-------------|
| `terminal_output` | `{agent_id: string, data: string}` | Terminal output chunk |

### Git

| Event | Data | Description |
|-------|------|-------------|
| `conflict_detected` | `ConflictInfo` | Merge conflict needs resolution |
| `merge_complete` | `{branch: string}` | Branch merged successfully |

### Lifecycle

| Event | Data | Description |
|-------|------|-------------|
| `sprint_complete` | `SprintSummary` | Sprint finished |
| `sprint_review` | `{summary: string, options: Option[]}` | Sprint review prompt |
| `error` | `{message: string, code: string}` | Error occurred |

## Data Types

### Ticket

```typescript
interface Ticket {
  id: string;
  title: string;
  description: string;
  type: "feature" | "bug" | "chore";
  status: "draft" | "approved" | "in_progress" | "review" | "testing" | "done" | "rejected";
  assigned_to: string | null;
  branch: string | null;
  dependencies: string[];
  files_changed: string[];
  created_at: string;
  updated_at: string;
}
```

### ScrumState

```typescript
interface ScrumState {
  project_name: string;
  project_path: string;
  phase: "planning" | "development" | "review" | "complete";
  
  requirements: string;
  technical_spec: string;
  plan_approved: boolean;
  
  tickets: Ticket[];
  active_tickets: Record<string, Ticket>;
  completed_tickets: Ticket[];
  
  agents: Record<string, AgentStatus>;
  
  branches: string[];
  pending_merges: string[];
  conflicts: ConflictInfo[];
  
  sprint_number: number;
}
```

### AgentStatus

```typescript
interface AgentStatus {
  agent_id: string;
  role: string;
  state: "idle" | "working" | "done" | "error";
  current_ticket: string | null;
  llm: string;
  tmux_pane: string;
}
```

### TeamConfig

```typescript
interface TeamConfig {
  agents: AgentConfig[];
  max_parallel: number;
  sprint_settings: SprintSettings;
}

interface AgentConfig {
  role: string;
  count: number;
  llm: string;
  system_prompt?: string;
  tools?: string[];
}

interface SprintSettings {
  max_tickets: number;
  auto_merge: boolean;
  auto_release: boolean;
}
```

### ConflictInfo

```typescript
interface ConflictInfo {
  branch: string;
  files: string[];
  timestamp: string;
}
```

### SprintSummary

```typescript
interface SprintSummary {
  sprint_number: number;
  completed_tickets: Ticket[];
  code_changes: CodeChange[];
  test_results: TestResult;
  demo_url: string;
}
```

## Example Usage

### Starting a Project

```typescript
const ws = new WebSocket('ws://localhost:8765/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'start_project',
    concept: 'Todo app with dark mode and user accounts',
    team_config: {
      agents: [
        { role: 'Product Owner', count: 1, llm: 'claude-3-5-sonnet' },
        { role: 'Architect', count: 1, llm: 'claude-3-5-sonnet' },
        { role: 'UI Developer', count: 2, llm: 'gpt-4o' },
        { role: 'Backend Developer', count: 2, llm: 'claude-3-5-sonnet' },
      ],
      max_parallel: 5,
      sprint_settings: {
        max_tickets: 10,
        auto_merge: true,
        auto_release: false
      }
    }
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'plan_ready':
      console.log('Plan ready:', message.plan);
      break;
    case 'state_update':
      updateUI(message.state);
      break;
    case 'terminal_output':
      appendTerminal(message.agent_id, message.data);
      break;
  }
};
```

### Sprint Decision

```typescript
// After sprint review
ws.send(JSON.stringify({
  type: 'sprint_decision',
  decision: 'add_features',  // or 'release', 'continue'
  feedback: 'Add user profile page and settings'
}));
```
