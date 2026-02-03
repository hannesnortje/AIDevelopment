import os
import git
from git import Repo
import shutil
from typing import List, Optional

class GitTools:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.repo = Repo(self.repo_path)
        self.worktrees_dir = os.path.join(self.repo_path, ".worktrees")
        
        if not os.path.exists(self.worktrees_dir):
            os.makedirs(self.worktrees_dir)
            # Add to gitignore if not present
            gitignore_path = os.path.join(self.repo_path, ".gitignore")
            if os.path.exists(gitignore_path):
                with open(gitignore_path, "r") as f:
                    content = f.read()
                if ".worktrees/" not in content:
                    with open(gitignore_path, "a") as f:
                        f.write("\n.worktrees/\n")

    def create_branch(self, branch_name: str, base: str = "main") -> str:
        """Create a new branch from base."""
        try:
            current = self.repo.active_branch
            # Checkout base first to ensure we branch from updated point
            # Note: In a real agent workflow, we might fetch origin first
            if branch_name in self.repo.heads:
                print(f"[Git] Branch {branch_name} already exists")
                return branch_name
                
            new_branch = self.repo.create_head(branch_name, base)
            print(f"[Git] Created branch {branch_name} from {base}")
            return branch_name
        except Exception as e:
            print(f"[Git] Error creating branch: {e}")
            raise

    def create_worktree(self, branch_name: str) -> str:
        """Create a worktree for the specific branch."""
        worktree_path = os.path.join(self.worktrees_dir, branch_name)
        
        if os.path.exists(worktree_path):
            print(f"[Git] Worktree for {branch_name} already exists at {worktree_path}")
            return worktree_path
            
        try:
            # Ensure branch exists
            if branch_name not in self.repo.heads:
                self.create_branch(branch_name)
                
            self.repo.git.worktree("add", worktree_path, branch_name)
            print(f"[Git] Created worktree at {worktree_path}")
            return worktree_path
        except Exception as e:
            print(f"[Git] Error creating worktree: {e}")
            raise

    def remove_worktree(self, branch_name: str):
        """Remove a worktree."""
        worktree_path = os.path.join(self.worktrees_dir, branch_name)
        if os.path.exists(worktree_path):
            try:
                self.repo.git.worktree("remove", worktree_path)
                # shutil.rmtree(worktree_path) # git worktree remove should handle it, but fallback if needed
                print(f"[Git] Removed worktree at {worktree_path}")
            except Exception as e:
                print(f"[Git] Error removing worktree: {e}")

    def list_branches(self) -> List[str]:
        return [head.name for head in self.repo.heads]

    def merge_branch(self, source_branch: str, target_branch: str = "main") -> bool:
        """Merge source into target."""
        try:
            self.repo.git.checkout(target_branch)
            self.repo.git.merge(source_branch)
            print(f"[Git] Merged {source_branch} into {target_branch}")
            return True
        except Exception as e:
            print(f"[Git] Merge conflict or error: {e}")
            self.repo.git.merge("--abort")
            return False
