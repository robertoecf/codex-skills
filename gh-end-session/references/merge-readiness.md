# Merge Readiness Rules

Use this reference after collecting the branch and PR snapshot. The goal is to decide what to do next with minimal ambiguity.

## 1. Branch state

### Clean worktree

- Required before final merge work.
- Preferred before rebasing, because rebases with local edits raise avoidable risk.

### Dirty worktree

- If edits are intentional and ready, test and commit them.
- If edits are exploratory or partial, keep the branch out of merge mode.
- Do not open or merge a PR while hiding important local changes from Git history.

### Upstream missing

- Push with upstream before doing PR work.
- A branch without upstream is not ready to communicate through a PR.

### Ahead of upstream

- Push before requesting review or merge.
- A local only commit invalidates the PR as the canonical source of truth.

### Behind upstream or base branch

- Sync before final review or merge.
- Prefer the repository's standard sync strategy. If none is visible, prefer rebase for feature branch sync because it keeps the branch linear.

## 2. PR state

### No PR exists

- Open one if the branch has reviewable work.
- Keep the PR in draft when the code still needs major local iteration.

### PR exists and is draft

- Leave it in draft if the remaining work is structural or likely to invalidate review.
- Mark ready for review when the branch is coherent, tests are relevantly green, and the description explains scope and risk.

### PR exists and is open

- Update it in place.
- Prefer amending the PR description over writing detached summaries elsewhere.

## 3. Review feedback

### Human feedback

Treat the following as blocking until resolved or explicitly rebutted:

- `CHANGES_REQUESTED`
- Unresolved review threads from maintainers or reviewers
- Comments that point to correctness, safety, or repository policy problems

Treat the following as important but not automatically blocking:

- Naming suggestions
- Refactoring preferences without correctness impact
- Broader design discussions that do not block the current deliverable

### Bot feedback

Bot feedback is worth implementing when it identifies one of these:

- Failing required checks
- Clear bug risk
- Security or policy issues
- Mechanical cleanup with low regression risk

Bot feedback is usually not worth implementing when it:

- Adds abstraction without need
- Rephrases style opinions already covered by formatters or lint rules
- Pushes speculative optimization

## 4. Checks

### Failing checks

- Blocking unless the repository marks them optional.
- Read the actual failing job or annotation before changing code.

### Pending checks

- Blocking for merge unless optional.
- Do not merge on assumption.

### Passing checks

- Necessary but not sufficient.
- Passing automation does not clear unresolved human review threads.

## 5. Merge decision

Merge is reasonable when all of these are true:

- Worktree is clean
- Branch is pushed
- PR is open and not in draft
- Required checks are passing
- No unresolved blocking human feedback remains
- Merge state is not blocked by conflicts or branch protection

If one item above is false, do not merge. Fix the blocking condition first.

## 6. Cleanup

After merge:

- Switch to a safe branch, usually the default branch
- Pull the latest default branch
- Delete the local feature branch with `git branch -d`
- Delete the remote branch if it still exists

Do not delete the branch before the merge is confirmed.
