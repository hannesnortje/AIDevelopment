# Workflow

The LangGraph Scrum Team follows an iterative sprint cycle that loops until you approve a release.

## Iterative Sprint Cycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ┌─────────────┐                                │
│              ┌──────────────►│    USER     │◄──────────────┐               │
│              │               │   Input     │               │               │
│              │               └──────┬──────┘               │               │
│              │                      │                      │               │
│   LOOP BACK  │  ┌───────────────────────────────────────┐  │               │
│   (new       │  │         PLANNING PHASE                │  │               │
│   sprint)    │  │  Product Owner → Architect → Approval │  │               │
│              │  └───────────────────┬───────────────────┘  │               │
│              │                      │                      │               │
│              │  ┌───────────────────────────────────────┐  │               │
│              │  │      DEVELOPMENT PHASE (Parallel)     │  │               │
│              │  │  UI Dev  │  Backend  │  Fullstack     │  │               │
│              │  │          Git Agent: Merge             │  │               │
│              │  └───────────────────┬───────────────────┘  │               │
│              │                      │                      │               │
│              │  ┌───────────────────────────────────────┐  │               │
│              │  │          REVIEW PHASE                 │  │               │
│              │  │  Tester → Reviewer → Product Owner    │  │               │
│              │  └───────────────────┬───────────────────┘  │               │
│              │                      │                      │               │
│              │            ┌─────────────────┐              │               │
│              │            │  SPRINT REVIEW  │              │               │
│              │            └────────┬────────┘              │               │
│              │                     │                       │               │
│              │    ┌────────────────┼────────────────┐      │               │
│              │    ▼                ▼                ▼      │               │
│              │ ┌──────┐      ┌──────────┐      ┌────────┐ │               │
│              │ │ More │      │   Add    │      │Release │ │               │
│              │ │ Fixes│      │ Features │      │        │ │               │
│              │ └──┬───┘      └────┬─────┘      └───┬────┘ │               │
│              │    │               │                │      │               │
│              └────┴───────────────┘                ▼      │               │
│                                            ┌─────────────┐│               │
│                                            │ Git: main   ││               │
│                                            │ + tag       ││               │
│                                            └─────────────┘│               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Phase 1: Planning

1. **User Input**: You describe what you want to build
2. **Product Owner**: Analyzes requirements, creates user stories
3. **Architect**: Designs technical solution, creates tickets
4. **User Approval**: Review and approve the plan

```
User: "Create a todo app with Lit 3"
  │
  ├── Product Owner: Creates 6 user stories with acceptance criteria
  │
  ├── Architect: Designs system, creates 6 tickets with dependencies
  │
  └── User: Reviews and clicks "Approve Plan"
```

## Phase 2: Development (Parallel)

Multiple agents work simultaneously:

1. **Git Agent**: Creates worktrees for each ticket
2. **Dispatcher**: Assigns tickets to available agents
3. **Agents**: Work in parallel in isolated worktrees
4. **Git Agent**: Merges completed work to develop

```
Git Agent: Creates .worktrees/ticket-{1,2,3,4,5,6}
  │
  ├── UI Dev 1:     ticket-1 (Login Form)      🟢 Working
  ├── UI Dev 2:     ticket-2 (Dashboard UI)    🟢 Working
  ├── Backend 1:    ticket-3 (Auth API)        🟢 Working
  ├── Backend 2:    ticket-4 (User API)        🟢 Working
  │
  └── Git Agent: Merges each to develop as they complete
```

### Dependency Handling

Tickets with dependencies wait until prerequisites complete:

```
Ticket #1: Auth API          (no deps)     → Starts immediately
Ticket #2: Login Form        (depends: #1) → Waits for #1
Ticket #3: Profile API       (no deps)     → Starts immediately
Ticket #4: Profile Page      (depends: #3) → Waits for #3
```

## Phase 3: Review

1. **Tester**: Runs tests on develop branch
2. **Reviewer**: Code review, quality checks
3. **Product Owner**: Reviews completed features

```
Develop branch with all merged features
  │
  ├── Tester: npm test → All tests pass ✓
  │
  ├── Reviewer: Code review → Approved ✓
  │
  └── Product Owner: Feature review → Ready for demo
```

## Phase 4: Sprint Review

You and the Product Owner review the completed sprint:

1. **Demo**: See the working application
2. **Summary**: Review what was built
3. **Decision**: Choose next steps

### Options

| Decision | Result |
|----------|--------|
| **Release** | Merge to main, tag version, done |
| **Add Features** | New requirements → Planning phase |
| **Continue Fixes** | Improvements → Planning phase |

## Sprint Review Node (Loop Point)

```python
async def sprint_review_node(state: WorkflowState) -> WorkflowState:
    # Product Owner summarizes sprint
    summary = await product_owner.summarize_sprint(state.completed_tickets)
    
    # Send to dashboard for user review
    await dashboard.send({
        "type": "sprint_review",
        "summary": summary,
        "demo_url": "http://localhost:3000",
        "options": [
            {"id": "release", "label": "🚀 Release"},
            {"id": "add_features", "label": "➕ Add Features"},
            {"id": "continue", "label": "🔧 Continue Fixes"}
        ]
    })
    
    # Wait for user decision
    response = await dashboard.wait_for_user_response()
    
    if response.decision == "release":
        return state.update(phase="release")
    else:
        # LOOP BACK TO PLANNING
        return state.update(
            phase="planning",
            new_requirements=response.feedback,
            sprint_number=state.sprint_number + 1
        )
```

## Example Multi-Sprint Flow

```
SPRINT 1:
─────────
User: "Create a todo app with Lit 3"
  → Planning: 6 tickets created
  → Development: All 6 completed
  → Review: Tests pass
  → Sprint Review: "Looks good! Add dark mode."

SPRINT 2:
─────────
  → Planning: 3 new tickets for dark mode
  → Development: Dark mode implemented
  → Review: Tests pass
  → Sprint Review: "Perfect! Release it."

RELEASE:
────────
  → Git Agent: Merge develop → main
  → Git Agent: Tag v1.0.0
  → Done! ✓
```

## Dynamic Tickets

Agents can create follow-up tickets during development:

```python
# Backend agent creates auth API
# Discovers UI needs integration ticket
new_ticket = Ticket(
    title="Integrate Auth API into Login Form",
    dependencies=["auth-api-ticket"],
    role="ui"
)
# Added to current sprint, dispatched when deps ready
```

Configuration in `.langgraph/config/sprint.yaml`:

```yaml
ticket_handling:
  allow_dynamic_tickets: true
  dynamic_ticket_mode: "same_sprint"  # or "next_sprint"
  max_dynamic_tickets_per_sprint: 10
```
