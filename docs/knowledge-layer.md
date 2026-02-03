# Knowledge Layer

The Knowledge Layer provides memory, context, and conventions to agents, enabling consistent and informed decision-making.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEMORY ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────┐         ┌────────────────────────────┐         │
│  │      SQLite DB         │  sync   │     ChromaDB (Vector)      │         │
│  │   (Structured Data)    │ ──────► │    (Semantic Search)       │         │
│  ├────────────────────────┤         ├────────────────────────────┤         │
│  │ • decisions            │         │ • decision_embeddings      │         │
│  │ • lessons_learned      │         │ • lesson_embeddings        │         │
│  │ • conversations        │         │ • code_pattern_embeddings  │         │
│  │ • ticket_history       │         │ • codebase_index           │         │
│  └────────────────────────┘         └────────────────────────────┘         │
│            │                                    │                           │
│            ▼                                    ▼                           │
│     Exact Queries                      Semantic Queries                     │
│   "Get decision by ID"              "How do we handle auth?"               │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    FILE SYSTEM (Git-tracked)                           │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │  .langgraph/                                                          │ │
│  │  ├── conventions/     # YAML - human editable rules                  │ │
│  │  ├── examples/        # Code patterns - templates                    │ │
│  │  └── trajectory/      # YAML - roadmap, priorities                   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Storage Selection

| Query Type | Example | Best Storage |
|------------|---------|--------------|
| Exact lookup | "Get decision dec-001" | SQLite |
| Filtered list | "Lessons from last week" | SQLite |
| Semantic search | "How do we handle errors?" | ChromaDB |
| Similar code | "Find patterns like this" | ChromaDB |
| Human editing | Update conventions | File System |
| Version control | Track changes over time | File System (Git) |

## Memory Store

```python
class MemoryStore:
    def __init__(self, project_path: str):
        self.db = sqlite3.connect(project_path / ".langgraph/memory/memory.db")
        self.chroma = chromadb.Client(...)
        self._init_tables()
        self._init_collections()
    
    def store_decision(self, decision: Decision) -> None:
        """Store in both SQLite and Vector DB."""
        # SQLite for structured queries
        self.db.execute("""
            INSERT INTO decisions (id, topic, decision, reason, ...)
            VALUES (?, ?, ?, ?, ...)
        """, (decision.id, decision.topic, ...))
        
        # ChromaDB for semantic search
        self.decision_collection.add(
            ids=[decision.id],
            documents=[f"{decision.topic}: {decision.decision}"],
            metadatas=[{"topic": decision.topic}]
        )
    
    def search_decisions(self, query: str, limit: int = 5) -> list[Decision]:
        """Semantic search for relevant decisions."""
        results = self.decision_collection.query(
            query_texts=[query],
            n_results=limit
        )
        return [self.get_decision(id) for id in results['ids'][0]]
```

## Context Retrieval

When an agent receives a task, context is retrieved and injected into the prompt:

```python
class KnowledgeRetriever:
    def get_context_for_task(self, task: str, file_paths: list[str] = None) -> AgentContext:
        # 1. Search for relevant decisions
        decisions = self.memory.search_decisions(task, limit=3)
        
        # 2. Search for relevant lessons
        lessons = self.memory.search_lessons(task, limit=3)
        
        # 3. Search for similar code patterns
        examples = self.memory.search_code_patterns(task, limit=3)
        
        # 4. Get applicable conventions
        conventions = []
        if file_paths:
            for file_path in file_paths:
                conventions.extend(self.conventions.get_for_file(file_path))
        
        return AgentContext(
            decisions=decisions,
            lessons=lessons,
            code_examples=examples,
            conventions=conventions
        )
```

## Memory Lifecycle

```
1. TASK RECEIVED
   └── Retrieve relevant context from memory
       • "Have we decided on this before?"
       • "What did we learn about this?"
       • "How did we implement similar things?"

2. CONTEXT INJECTED
   └── Add to agent prompt
       "Follow this pattern: [code example]"
       "Use fetch, not axios (decision dec-001)"

3. AGENT EXECUTES
   └── Works with full context

4. RESULT VALIDATED
   └── Check against conventions
   └── If rejected: record as lesson

5. MEMORY UPDATED
   └── Store new decisions made
   └── Store lessons if issues found
   └── Index new code patterns
```

## Conventions Store

File-based, human-editable rules:

```yaml
# .langgraph/conventions/code-style.yaml
typescript:
  strict: true
  noImplicitAny: true

naming:
  components: PascalCase
  functions: camelCase
  constants: SCREAMING_SNAKE_CASE

forbidden:
  - pattern: "console.log"
    message: "Use logger utility instead"
    severity: warning
  - pattern: "any"
    message: "Avoid 'any' type"
    severity: error
```

```yaml
# .langgraph/conventions/architecture.yaml
folder_structure:
  src:
    components:
      description: Reusable UI components
      naming: PascalCase.tsx
    lib:
      description: Utility functions
      naming: camelCase.ts

state_management:
  global: zustand
  forms: lit-element reactive properties

forbidden_patterns:
  - "Redux (use Zustand)"
  - "Inline styles (use Tailwind)"
```

## Examples Store

Code templates for agents to reference:

```
.langgraph/examples/
├── components/
│   ├── Button.tsx          # Standard button pattern
│   ├── Form.tsx            # Form with validation
│   └── Modal.tsx           # Modal dialog pattern
├── api/
│   ├── route-handler.ts    # Standard route pattern
│   └── middleware.ts       # Auth middleware
└── tests/
    └── component.test.tsx  # Component test pattern
```

## Decision Records

```yaml
# .langgraph/memory/decisions/dec-001.yaml
id: dec-001
date: 2026-02-01
topic: HTTP Client Selection
decision: Use native fetch instead of axios
reason: |
  - Reduces bundle size
  - Built-in fetch enhancements
  - No additional dependency
alternatives_rejected:
  - axios: "Adds 13KB to bundle"
related_files:
  - src/lib/api-client.ts
```

## Lesson Records

```yaml
# .langgraph/memory/lessons/les-001.yaml
id: les-001
date: 2026-02-02
type: bug_pattern
description: Form submission without validation caused runtime errors
solution: Always use Zod schema validation before form submission
code_pattern: |
  const schema = z.object({ ... });
  const result = schema.safeParse(formData);
  if (!result.success) {
    return { errors: result.error.flatten() };
  }
affected_tickets:
  - ticket-005
```
