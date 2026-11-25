# Git

## Q: Merge vs rebase: when do you use each, and what's the golden rule?
### Solution
- **Merge** keeps the true history and creates a merge commit. It's safe on shared branches.
- **Rebase** replays your commits on top of the target, so the history is linear and clean. Use it to update a feature branch from `main` (`git pull --rebase`) and to tidy commits before a PR (`git rebase -i` to squash/fixup).

**Golden rule:** never rebase commits that others have already pulled (a shared/public branch). It rewrites the hashes and breaks their history. If you must update your own pushed feature branch after a rebase, use `git push --force-with-lease`, never a plain `--force`.

## Q: You committed a secret, or a bad change already on `main`. How do you recover?
### Solution
**A bad change on a shared branch:** `git revert <sha>` creates an inverse commit, so history isn't rewritten. Reverting a merge commit needs `-m 1`.

**A secret:** consider it **compromised the moment it's pushed**. **Rotate it first**, then clean up: remove it from history with `git filter-repo` (or BFG), force-push, and ask collaborators to re-clone. Also expire caches (forks and PR refs may still hold it). Prevent recurrences with pre-commit hooks (gitleaks), GitHub/Bitbucket secret scanning, and `.gitignore` for env files.

Local recovery: `git reflog` finds "lost" commits after a bad reset or rebase; `git reset --soft HEAD~1` undoes the last commit but keeps its changes.
