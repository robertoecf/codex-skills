---
name: gh-end-session
description: "Close a coding session through a disciplined GitHub branch and PR workflow. Use when Codex needs to wrap up work on the current branch, sync local and remote state, run or update a pull request, use the PR as the primary communication surface, inspect human and bot feedback, evaluate whether follow up changes are worthwhile, merge when ready, and delete local and remote branches to keep the repository clean."
---

# GitHub End Session

Close work through the branch that is already in progress and treat the PR as the canonical communication artifact. Prefer updating the existing branch and PR over creating side channels or parallel status summaries.

## Objective

Finish the current work branch until one of these terminal outcomes is reached:

- The branch is synchronized, the PR is updated or opened, and the remaining blocking work is clearly identified.
- The PR is fully reviewable, checks are green, blocking feedback is resolved, and the PR is ready to merge.
- The PR is merged and both remote and local feature branches are deleted.
- A blocker requires user help, such as missing auth, ambiguous product intent, merge conflicts with unclear resolution, or unrelated dirty changes.

## Inputs

Accept any of the following:

- No explicit PR target. Infer the PR from the current branch.
- A PR number.
- A PR URL.
- A repository path via `--repo`.

## Prerequisites

- Verify `gh` authentication first with `gh auth status`.
- If authentication is missing, ask the user to run `gh auth login` before continuing.
- Work from the repository root unless the user explicitly scopes the task differently.
- Assume the current branch is the work branch unless the user names another branch or PR.

## Quick start

1. Run the bundled snapshot script first and inspect the `actions` list before doing anything else.

```bash
python3 "<path-to-skill>/scripts/pr_session_snapshot.py" --repo "." --pr auto
```

2. If machine readable output is useful, add `--json`.

```bash
python3 "<path-to-skill>/scripts/pr_session_snapshot.py" --repo "." --pr auto --json
```

3. Read [references/merge-readiness.md](references/merge-readiness.md) when you need the full decision rules for sync, review handling, merge readiness, or cleanup.

## Core workflow

### 1. Build the factual snapshot

- Capture the current branch, upstream, ahead or behind counts, and worktree status.
- Detect whether a PR already exists for the branch or load the explicit PR target.
- Inspect PR state, checks, review decision, unresolved review threads, reviews, and issue comments.
- Read `status` and `actions` first. Use the details only to validate the next move.

### 2. Make the branch publishable

- If the current branch is the default branch and the work is not already merged, create a feature branch before PR work.
- If the worktree is dirty, run the relevant tests, stage intentional changes, and create a commit with a precise message.
- If the branch has no upstream, push with `git push -u origin <branch>`.
- If the branch is behind its upstream or base branch, sync it according to repository convention. Prefer `git pull --rebase` unless the repository clearly uses merge commits for branch sync.
- If sync changes behavior, rerun the relevant tests and push again.

### 3. Use the PR as the communication hub

- If no PR exists, open one from the current branch with a title and body that explain scope, constraints, tests, and unresolved risks.
- If a PR exists, update that PR instead of creating a second communication channel.
- Put substantive status in the PR description or PR comments. Keep chat as a thin progress channel unless the user explicitly asks for both.
- If the work is still exploratory, keep the PR in draft. If the branch is reviewable, mark it ready for review.

### 4. Triage feedback in the right order

- Inspect unresolved human threads first.
- Treat `CHANGES_REQUESTED`, maintainer comments, and correctness or safety issues as blocking until resolved or explicitly rebutted.
- Inspect bot feedback second. Apply bot suggestions only when they improve correctness, repository policy compliance, maintainability, or required checks.
- If several comments are independent, batch them into a short implementation plan and handle them in one follow up pass.

### 5. Implement the accepted follow ups

- Make the smallest change that resolves the accepted feedback.
- Re run the most relevant tests first, then broader checks only when shared behavior changed.
- Push follow up commits to the same branch so the PR remains the single source of truth.
- Respond in the PR or review thread with the concrete change when that closes the loop.

### 6. Judge merge readiness

- Merge only when the worktree is clean, the branch is pushed, required checks are green, and blocking feedback is resolved.
- Approval without green checks is not merge readiness.
- Prefer the repository's default merge strategy. If none is clear, prefer squash merge for cleanup of feature branches.
- If the snapshot shows `ready_to_merge`, merge through `gh pr merge`.

### 7. Clean up both sides

- After merge, delete the remote branch with the matching `gh pr merge` flag or `git push origin --delete <branch>`.
- Switch back to a safe branch before deleting the local feature branch.
- Pull the default branch after cleanup so the local repository reflects the merged result.

## Stop conditions

Stop and ask the user only when one of these is true:

- `gh` authentication is missing or insufficient.
- There are unrelated local changes and it is unsafe to continue.
- A merge conflict or reviewer request requires product or architectural judgment that is not obvious from repository context.
- Required CI failures look external or ambiguous after a first diagnosis pass.

Do not stop only because:

- There is no PR yet.
- The branch has not been pushed.
- Bot feedback exists but still needs evaluation.
- A small, clearly actionable review fix remains.

## Decision rules

- Prefer one branch per work item.
- Prefer one PR per branch.
- Prefer not to do feature work directly on the default branch.
- Prefer updating the current PR over opening a new one for incremental follow ups on the same work.
- Prefer precise PR descriptions over separate prose summaries.
- Prefer rejecting feedback that adds indirection without improving the system.
- Prefer deleting merged branches immediately to keep the repository clean.
- Prefer action codes from the snapshot over ad hoc interpretation when the next step is obvious.

## Commands

### Snapshot

```bash
python3 "<path-to-skill>/scripts/pr_session_snapshot.py" --repo "." --pr auto
```

### Push branch

```bash
git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
```

### Create or view PR

```bash
gh pr view --web || gh pr create --fill --web
```

### Merge and delete remote branch

```bash
gh pr merge --squash --delete-branch
```

### Delete local branch after merge

```bash
git checkout "$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')" && git pull --ff-only && git branch -d "<branch>"
```

## Output expectations

- Start with the current `status` and highest priority `actions`.
- Keep progress updates short and tied to the workflow phase.
- When work is complete, report:
  - Final branch state
  - PR URL
  - Checks summary
  - Feedback handled
  - Merge result or remaining blocker
  - Cleanup status

## Bundled resources

### scripts/pr_session_snapshot.py

Build a consolidated snapshot of:

- Current branch and upstream state
- Worktree cleanliness
- PR metadata and merge readiness signals
- Checks grouped into passing, pending, and failing
- Human and bot feedback grouped by unresolved threads, reviews, and issue comments
- `status`, `actions`, and suggested next actions derived from the facts

Use text output for interactive work and `--json` when other tooling needs structured data. The script accepts `--pr auto`, a PR number, or a PR URL.

### references/merge-readiness.md

Read this reference when you need the detailed heuristics for:

- Choosing whether to sync, push, or open a PR
- Deciding whether bot feedback should be implemented
- Determining whether a PR is actually ready to merge
- Cleaning up local and remote branches safely
