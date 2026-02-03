# Git Integration

LangGraph Scrum Team uses Git worktrees for isolated parallel development, coordinated by a dedicated Git Agent.

## Git Agent Responsibilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BRANCH CREATION                                                            │
│  • Create feature/ticket-{id} branches from develop                        │
│  • Create worktrees for each branch                                        │
│  • Assign worktrees to dev agents                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  MONITORING                                                                 │
│  • Track which agents are working on which branches                        │
│  • Monitor commit activity                                                  │
│  • Detect when agents complete work                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  MERGING                                                                    │
│  • Merge completed feature branches to develop                             │
│  • Handle merge conflicts (auto-resolve or flag for human)                 │
│  • Cleanup worktrees after merge                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  RELEASE                                                                    │
│  • Merge develop to main                                                   │
│  • Create version tags                                                      │
│  • Push to remote                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Git Worktrees

Git worktrees allow multiple working directories from the same repository:

```
/my-project/
├── .git/                    # Shared git database
├── src/                     # Main directory (develop branch)
├── .worktrees/              # Worktrees directory (gitignored)
│   ├── ticket-1/            # Agent 1's workspace (feature/ticket-1)
│   │   └── src/
│   ├── ticket-2/            # Agent 2's workspace (feature/ticket-2)
│   │   └── src/
│   └── ticket-3/            # Agent 3's workspace (feature/ticket-3)
│       └── src/
└── .langgraph/              # Shared knowledge layer
```

## Branch Strategy

```
main (protected)
├── Only release-ready code
├── Protected from direct pushes
└── Merged from develop via release

develop (integration)
├── Integration branch
├── All feature branches merge here
└── CI/CD runs on every merge

feature/ticket-{id} (per-ticket)
├── Created when ticket is claimed
├── Agent works in isolation
├── Merged to develop when approved
└── Deleted after merge
```

## GitAgent Implementation

```python
class GitAgent:
    def __init__(self, repo_path: str, tmux: TmuxManager):
        self.repo = git.Repo(repo_path)
        self.worktrees_dir = Path(repo_path) / ".worktrees"
        self.tmux = tmux
    
    async def create_branch_for_ticket(self, ticket_id: str) -> Path:
        """Create feature branch and worktree."""
        branch_name = f"feature/ticket-{ticket_id}"
        worktree_path = self.worktrees_dir / f"ticket-{ticket_id}"
        
        # Create branch from develop
        if branch_name not in [b.name for b in self.repo.heads]:
            develop = self.repo.heads.develop
            self.repo.create_head(branch_name, develop)
        
        # Create worktree
        if not worktree_path.exists():
            self.repo.git.worktree("add", str(worktree_path), branch_name)
        
        return worktree_path
    
    async def merge_ticket_to_develop(self, ticket_id: str) -> MergeResult:
        """Merge completed ticket's branch to develop."""
        branch_name = f"feature/ticket-{ticket_id}"
        
        self.repo.heads.develop.checkout()
        
        try:
            self.repo.git.merge(
                branch_name, "--no-ff",
                "-m", f"Merge {branch_name}: Ticket #{ticket_id}"
            )
            return MergeResult(success=True)
        except git.GitCommandError as e:
            if "CONFLICT" in str(e):
                self.repo.git.merge("--abort")
                return MergeResult(
                    success=False,
                    conflicts=list(self.repo.index.unmerged_blobs().keys()),
                    needs_human=True
                )
            raise
    
    async def cleanup_ticket(self, ticket_id: str):
        """Remove worktree after merge."""
        worktree_path = self.worktrees_dir / f"ticket-{ticket_id}"
        if worktree_path.exists():
            self.repo.git.worktree("remove", str(worktree_path), "--force")
    
    async def merge_develop_to_main(self, version: str = None) -> MergeResult:
        """Release: merge develop to main."""
        self.repo.heads.main.checkout()
        self.repo.git.merge("develop", "--no-ff", "-m", "Release to main")
        
        if version:
            self.repo.create_tag(version)
        
        return MergeResult(success=True)
```

## Workspace Lifecycle

```
1. TICKET ASSIGNED
   └── Dispatcher: "Agent UI-1, claim ticket #3"

2. WORKTREE CREATED
   └── git worktree add .worktrees/ticket-3 feature/ticket-3

3. AGENT WORKS
   └── All file operations in isolated workspace
   └── npm install, npm run dev - independent

4. WORK COMPLETE
   └── Agent commits final changes
   └── Ticket status → "review"

5. REVIEW & APPROVAL
   └── Reviewer examines changes
   └── Tester runs tests

6. MERGE TO DEVELOP
   └── git merge --no-ff feature/ticket-3

7. CLEANUP
   └── git worktree remove .worktrees/ticket-3
   └── git branch -d feature/ticket-3
```

## Conflict Resolution

When conflicts occur:

1. **Git Agent detects conflict** during merge attempt
2. **Dashboard notified** with conflict details
3. **User decides**:
   - Manual resolution
   - Abort and reassign ticket
4. **After resolution**, merge completes

```python
async def handle_conflict(self, branch: str, conflict: str) -> MergeResult:
    conflicting_files = self.parse_conflicts(conflict)
    
    # Attempt simple auto-resolution
    for file in conflicting_files:
        resolution = await self.attempt_auto_resolve(file)
        if not resolution.success:
            return MergeResult(
                success=False,
                needs_human_review=True,
                conflicts=conflicting_files
            )
    
    return MergeResult(success=True)
```

## Configuration

```yaml
# .langgraph/config/server.yaml
git:
  auto_push: false        # Push after merges
  worktrees_dir: .worktrees
  branch_prefix: feature/
  require_review: true    # Require review before merge
```
