# Agents

LangGraph Scrum Team uses specialized AI agents, each with a distinct role in the development process.

## Agent Overview

| Agent | Role | Phase | LLM | Capabilities |
|-------|------|-------|-----|--------------|
| Product Owner | Requirements analysis | Planning | Claude | User stories, acceptance criteria |
| Architect | Technical design | Planning | Claude | System design, ticket breakdown |
| UI Developer | Frontend development | Development | GPT-4o | Lit 3 components, browser testing |
| Backend Developer | API development | Development | Claude | Routes, services, database |
| Fullstack Developer | Integration | Development | Claude | Frontend-backend connection |
| Tester | Testing | Testing | Claude | Test writing and execution |
| Reviewer | Code review | Review | Claude | Quality checks, suggestions |
| Git Agent | Version control | All | Claude | Branches, merges, releases |

## Agent Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. GIT AGENT: Creates branch and worktree                                  │
│     └── git worktree add .worktrees/ticket-3 feature/ticket-3              │
│                                                                              │
│  2. DISPATCHER: Spawns agent with Send()                                   │
│     └── Creates tmux pane, assigns ticket                                  │
│                                                                              │
│  3. AGENT: Receives context from knowledge layer                           │
│     └── Decisions, lessons, examples, conventions                          │
│                                                                              │
│  4. AGENT: Works on ticket                                                  │
│     └── Calls LLM, writes files, runs commands                             │
│                                                                              │
│  5. AGENT: Validates and commits                                            │
│     └── Checks conventions, commits to feature branch                      │
│                                                                              │
│  6. GIT AGENT: Merges to develop                                           │
│     └── Cleans up worktree                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Base Agent Structure

All agents inherit from a common base:

```python
class BaseAgent:
    def __init__(self, agent_id: str, knowledge: KnowledgeLayer):
        self.id = agent_id
        self.knowledge = knowledge
        self.tools = ToolExecutor()
    
    async def execute(self, state: AgentState) -> AgentState:
        # 1. Get context from knowledge layer
        context = self.knowledge.get_context_for_task(state.task)
        
        # 2. Build prompt with context
        prompt = self.build_prompt(state.task, context)
        
        # 3. Call LLM
        response = await self.call_llm(prompt)
        
        # 4. Validate against conventions
        validation = self.validate(response, context.conventions)
        
        if not validation.passed:
            return await self.retry_with_feedback(state, validation.errors)
        
        # 5. Execute actions
        result = await self.execute_actions(response.actions)
        
        # 6. Update memory
        self.knowledge.record_lesson(self.extract_lessons(result))
        
        return state.update(result=result)
```

## Agent Configuration

Agents are configured in `.langgraph/config/agents.yaml`:

```yaml
agent_roles:
  product_owner:
    description: "Requirements analysis and user stories"
    phase: planning
    llm: claude-3-5-sonnet
    system_prompt: |
      You are a Product Owner. Analyze requirements and create user stories.
  
  architect:
    description: "System design and technical decisions"  
    phase: planning
    llm: claude-3-5-sonnet
    system_prompt: |
      You are a Software Architect. Design systems and break down into tickets.
  
  ui_developer:
    description: "Frontend development with browser testing"
    phase: development
    llm: gpt-4o
    tools:
      - playwright
    system_prompt: |
      You are a UI Developer. Build Lit 3 web components.
      Test visually using Playwright.
  
  backend_developer:
    description: "API and business logic development"
    phase: development
    llm: claude-3-5-sonnet
    system_prompt: |
      You are a Backend Developer. Build APIs and services.
```

## Spawning Agents

Agents are spawned with their own tmux pane and worktree:

```python
async def spawn_agent(
    ticket_id: str,
    role: str,
    tmux: TmuxManager,
    git_agent: GitAgent
) -> Agent:
    # Git Agent creates the worktree
    worktree_path = await git_agent.create_branch_for_ticket(ticket_id)
    
    # Get role configuration
    role_config = config["agent_roles"][role]
    
    # Create LLM client
    llm = create_llm_client(role_config.get("llm", "claude-3-5-sonnet"))
    
    # Create agent
    agent = Agent(
        agent_id=f"{role}-{ticket_id}",
        role=role,
        llm_client=llm,
        tmux=tmux
    )
    
    # Set up tmux pane
    await agent.setup(worktree_path)
    
    return agent
```

## UI Developer (Special Capabilities)

The UI Developer has browser testing via Playwright:

```python
class UIDeveloperAgent(BaseAgent):
    async def execute(self, state: AgentState) -> AgentState:
        # Generate and write code
        code = await self.generate_code(state.task, context)
        await self.tools.write_file(state.file_path, code)
        
        # Start dev server
        await self.tmux.send_command(self.agent_id, "npm run dev")
        
        # Browser testing
        await self.browser.goto("http://localhost:3000")
        screenshot = await self.browser.screenshot()
        
        # Visual validation with LLM
        validation = await self.validate_screenshot(
            screenshot, 
            state.expected_appearance
        )
        
        if not validation.passed:
            return await self.fix_visual_issues(state, validation.feedback)
        
        return state.update(status="complete")
```

## Git Agent

See [Git Integration](git-integration.md) for details on the Git Agent.

## Adding Custom Agents

To add a custom agent role:

1. Add configuration in `agents.yaml`:
   ```yaml
   my_custom_agent:
     description: "What this agent does"
     phase: development
     llm: claude-3-5-sonnet
     tools: []
     system_prompt: |
       You are a custom agent...
   ```

2. Optionally create a specialized class:
   ```python
   class MyCustomAgent(BaseAgent):
       async def execute(self, state):
           # Custom logic
           pass
   ```

3. Register in the dispatcher configuration
