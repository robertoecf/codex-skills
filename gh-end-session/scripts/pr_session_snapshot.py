#!/usr/bin/env python3
"""
Collect a concise branch and PR snapshot for end of session workflows.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


GRAPHQL_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      number
      title
      url
      state
      isDraft
      reviewDecision
      mergeable
      mergeStateStatus
      changedFiles
      additions
      deletions
      comments(last: 50) {
        nodes {
          author {
            __typename
            login
          }
          bodyText
          createdAt
          url
        }
      }
      reviews(last: 50) {
        nodes {
          author {
            __typename
            login
          }
          state
          bodyText
          submittedAt
          url
        }
      }
      reviewThreads(first: 50) {
        totalCount
        nodes {
          isResolved
          isOutdated
          comments(last: 20) {
            nodes {
              author {
                __typename
                login
              }
              bodyText
              createdAt
              url
            }
          }
        }
      }
      commits(last: 1) {
        nodes {
          commit {
            statusCheckRollup {
              contexts(first: 100) {
                nodes {
                  __typename
                  ... on CheckRun {
                    name
                    conclusion
                    status
                    detailsUrl
                    workflowName
                  }
                  ... on StatusContext {
                    context
                    state
                    targetUrl
                    description
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


class CommandError(RuntimeError):
    pass


def run(cmd: list[str], cwd: Path, check: bool = True) -> str:
    process = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    if check and process.returncode != 0:
        raise CommandError(process.stderr.strip() or process.stdout.strip() or "command failed")
    return process.stdout.strip()


def run_json(cmd: list[str], cwd: Path) -> Any:
    output = run(cmd, cwd)
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise CommandError(f"invalid JSON from {' '.join(cmd)}: {exc}") from exc


def short_text(text: str | None, limit: int = 120) -> str:
    if not text:
        return ""
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def classify_author(author: dict[str, Any] | None) -> dict[str, str]:
    if not author:
        return {"login": "unknown", "kind": "unknown"}
    login = author.get("login") or "unknown"
    typename = (author.get("__typename") or "").lower()
    is_bot = typename == "bot" or login.endswith("[bot]") or "bot" in login.lower()
    return {"login": login, "kind": "bot" if is_bot else "human"}


def current_branch_info(repo: Path) -> dict[str, Any]:
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo)
    status_lines = run(["git", "status", "--short"], repo).splitlines()
    dirty = bool(status_lines)

    upstream = None
    ahead = 0
    behind = 0
    try:
        upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], repo)
        counts = run(["git", "rev-list", "--left-right", "--count", f"HEAD...{upstream}"], repo)
        ahead_text, behind_text = counts.split()
        ahead = int(ahead_text)
        behind = int(behind_text)
    except CommandError:
        upstream = None

    return {
        "name": branch,
        "upstream": upstream,
        "ahead": ahead,
        "behind": behind,
        "dirty": dirty,
        "changed_files": status_lines,
    }


def repo_info(repo: Path) -> dict[str, Any]:
    data = run_json(
        ["gh", "repo", "view", "--json", "name,nameWithOwner,url,defaultBranchRef"],
        repo,
    )
    owner, name = data["nameWithOwner"].split("/", 1)
    return {
        "owner": owner,
        "name": name,
        "name_with_owner": data["nameWithOwner"],
        "url": data["url"],
        "default_branch": data["defaultBranchRef"]["name"],
    }


def pr_basic_info(repo: Path) -> dict[str, Any] | None:
    try:
        return run_json(
            [
                "gh",
                "pr",
                "view",
                "--json",
                "number,title,url,state,isDraft,reviewDecision,mergeable,mergeStateStatus,headRefName,baseRefName",
            ],
            repo,
        )
    except CommandError as exc:
        message = str(exc).lower()
        if "no pull requests found" in message or "could not find any pull requests" in message:
            return None
        raise


def pr_basic_info_for_target(repo: Path, pr_target: str) -> dict[str, Any] | None:
    target = [] if pr_target == "auto" else [pr_target]
    try:
        return run_json(
            ["gh", "pr", "view", *target, "--json",
             "number,title,url,state,isDraft,reviewDecision,mergeable,mergeStateStatus,headRefName,baseRefName"],
            repo,
        )
    except CommandError as exc:
        message = str(exc).lower()
        if "no pull requests found" in message or "could not find any pull requests" in message:
            if pr_target == "auto":
                return None
        raise


def pr_deep_info(repo: Path, owner: str, name: str, number: int) -> dict[str, Any]:
    return run_json(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={GRAPHQL_QUERY}",
            "-F",
            f"owner={owner}",
            "-F",
            f"repo={name}",
            "-F",
            f"number={number}",
        ],
        repo,
    )["data"]["repository"]["pullRequest"]


def extract_checks(pr_data: dict[str, Any]) -> list[dict[str, Any]]:
    commits = pr_data.get("commits", {}).get("nodes", [])
    if not commits:
        return []
    rollup = commits[0].get("commit", {}).get("statusCheckRollup")
    if not rollup:
        return []
    nodes = rollup.get("contexts", {}).get("nodes", [])
    checks: list[dict[str, Any]] = []
    for node in nodes:
        if not node:
            continue
        typename = node.get("__typename")
        if typename == "CheckRun":
            state = node.get("conclusion") or node.get("status") or "UNKNOWN"
            checks.append(
                {
                    "name": node.get("name"),
                    "workflow": node.get("workflowName"),
                    "state": state,
                    "url": node.get("detailsUrl"),
                    "description": "",
                }
            )
        elif typename == "StatusContext":
            checks.append(
                {
                    "name": node.get("context"),
                    "workflow": None,
                    "state": node.get("state") or "UNKNOWN",
                    "url": node.get("targetUrl"),
                    "description": node.get("description") or "",
                }
            )
    return checks


def summarize_threads(pr_data: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    threads = pr_data.get("reviewThreads", {}).get("nodes", [])
    for thread in threads:
        if thread.get("isResolved") or thread.get("isOutdated"):
            continue
        comments = thread.get("comments", {}).get("nodes", [])
        if not comments:
            continue
        latest = comments[-1]
        author = classify_author(latest.get("author"))
        result.append(
            {
                "author": author["login"],
                "author_kind": author["kind"],
                "url": latest.get("url"),
                "preview": short_text(latest.get("bodyText")),
                "comment_count": len(comments),
            }
        )
    return result


def summarize_reviews(pr_data: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    reviews = pr_data.get("reviews", {}).get("nodes", [])
    for review in reviews:
        author = classify_author(review.get("author"))
        result.append(
            {
                "author": author["login"],
                "author_kind": author["kind"],
                "state": review.get("state"),
                "submitted_at": review.get("submittedAt"),
                "url": review.get("url"),
                "preview": short_text(review.get("bodyText")),
            }
        )
    return result


def summarize_issue_comments(pr_data: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    comments = pr_data.get("comments", {}).get("nodes", [])
    for comment in comments:
        author = classify_author(comment.get("author"))
        result.append(
            {
                "author": author["login"],
                "author_kind": author["kind"],
                "created_at": comment.get("createdAt"),
                "url": comment.get("url"),
                "preview": short_text(comment.get("bodyText")),
            }
        )
    return result


def count_states(checks: list[dict[str, Any]]) -> dict[str, int]:
    passing_states = {"SUCCESS", "SUCCESSFUL", "NEUTRAL", "SKIPPED"}
    failing_states = {"FAILURE", "FAILED", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED"}
    pending_states = {"PENDING", "IN_PROGRESS", "QUEUED", "EXPECTED", "WAITING", "REQUESTED"}

    passing = 0
    failing = 0
    pending = 0
    other = 0

    for check in checks:
        state = (check.get("state") or "").upper()
        if state in passing_states:
            passing += 1
        elif state in failing_states:
            failing += 1
        elif state in pending_states or not state:
            pending += 1
        else:
            other += 1

    return {"passing": passing, "failing": failing, "pending": pending, "other": other}


def compute_actions(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    branch = snapshot["branch"]
    repo_meta = snapshot["repository"]
    pr = snapshot.get("pull_request")
    check_counts = snapshot.get("checks", {}).get("counts", {})
    feedback = snapshot.get("feedback", {})
    on_default_without_pr = not pr and branch["name"] == repo_meta["default_branch"]

    if on_default_without_pr:
        actions.append(
            {
                "code": "create_feature_branch",
                "severity": "blocker",
                "message": "Create a feature branch from the default branch before opening a PR for this work.",
            }
        )

    if branch["dirty"]:
        actions.append(
            {
                "code": "commit_or_stash_changes",
                "severity": "blocker",
                "message": "Commit or stash local changes before syncing, reviewing, or merging.",
            }
        )
    if not branch["upstream"]:
        actions.append(
            {
                "code": "push_with_upstream",
                "severity": "blocker",
                "message": "Push the branch with upstream before relying on the PR as the source of truth.",
            }
        )
    elif branch["ahead"] > 0:
        actions.append(
            {
                "code": "push_local_commits",
                "severity": "blocker",
                "message": "Push local commits so the remote branch and PR match local reality.",
            }
        )
    if branch["behind"] > 0:
        actions.append(
            {
                "code": "sync_branch",
                "severity": "blocker",
                "message": "Sync the branch with its upstream before final review or merge.",
            }
        )

    if not pr:
        actions.append(
            {
                "code": "open_pr",
                "severity": "blocker",
                "message": "Open a PR for the current work branch and use it as the main communication surface.",
            }
        )
        return actions

    if pr["is_draft"]:
        actions.append(
            {
                "code": "decide_draft_state",
                "severity": "warn",
                "message": "Decide whether the PR should stay draft or move to ready for review.",
            }
        )
    if check_counts.get("failing", 0) > 0:
        actions.append(
            {
                "code": "fix_failing_checks",
                "severity": "blocker",
                "message": "Fix failing checks before attempting merge.",
            }
        )
    elif check_counts.get("pending", 0) > 0:
        actions.append(
            {
                "code": "wait_for_checks",
                "severity": "warn",
                "message": "Wait for or re run pending checks before merge.",
            }
        )

    if feedback.get("changes_requested", 0) > 0:
        actions.append(
            {
                "code": "handle_changes_requested",
                "severity": "blocker",
                "message": "Address or explicitly rebut requested changes from human reviewers.",
            }
        )
    if feedback.get("unresolved_human_threads", 0) > 0:
        actions.append(
            {
                "code": "resolve_human_threads",
                "severity": "blocker",
                "message": "Resolve unresolved human review threads before merge.",
            }
        )
    if feedback.get("unresolved_bot_threads", 0) > 0:
        actions.append(
            {
                "code": "evaluate_bot_feedback",
                "severity": "warn",
                "message": "Evaluate unresolved bot feedback and implement only the worthwhile changes.",
            }
        )

    ready = (
        not branch["dirty"]
        and branch["ahead"] == 0
        and branch["behind"] == 0
        and not pr["is_draft"]
        and check_counts.get("failing", 0) == 0
        and check_counts.get("pending", 0) == 0
        and feedback.get("changes_requested", 0) == 0
        and feedback.get("unresolved_human_threads", 0) == 0
        and pr.get("state") == "OPEN"
        and pr.get("mergeable") == "MERGEABLE"
    )
    if ready:
        actions.append(
            {
                "code": "ready_to_merge",
                "severity": "ready",
                "message": "PR appears ready to merge and clean up.",
            }
        )

    return actions


def compute_status(snapshot: dict[str, Any], actions: list[dict[str, str]]) -> str:
    pr = snapshot.get("pull_request")
    if not pr:
        if any(action["code"] == "create_feature_branch" for action in actions):
            return "needs_branch"
        return "no_pr"
    if pr.get("state") in {"MERGED", "CLOSED"}:
        return "closed"
    if any(action["code"] == "ready_to_merge" for action in actions):
        return "ready_to_merge"
    if any(action["severity"] == "blocker" for action in actions):
        return "blocked"
    if any(action["severity"] == "warn" for action in actions):
        return "needs_attention"
    return "reviewable"


def build_snapshot(repo: Path, pr_target: str) -> dict[str, Any]:
    repo_meta = repo_info(repo)
    branch = current_branch_info(repo)
    pr_basic = pr_basic_info_for_target(repo, pr_target)

    snapshot: dict[str, Any] = {
        "repository": repo_meta,
        "branch": branch,
        "pull_request": None,
        "status": "no_pr",
        "checks": {"counts": {"passing": 0, "failing": 0, "pending": 0, "other": 0}, "items": []},
        "feedback": {
            "changes_requested": 0,
            "unresolved_human_threads": 0,
            "unresolved_bot_threads": 0,
            "latest_reviews": [],
            "latest_issue_comments": [],
            "unresolved_threads": [],
        },
        "actions": [],
    }

    if not pr_basic:
        actions = compute_actions(snapshot)
        snapshot["actions"] = actions
        snapshot["status"] = compute_status(snapshot, actions)
        snapshot["next_actions"] = [action["message"] for action in actions]
        return snapshot

    pr_data = pr_deep_info(repo, repo_meta["owner"], repo_meta["name"], int(pr_basic["number"]))
    checks = extract_checks(pr_data)
    check_counts = count_states(checks)
    unresolved_threads = summarize_threads(pr_data)
    reviews = summarize_reviews(pr_data)
    issue_comments = summarize_issue_comments(pr_data)
    changes_requested = sum(
        1
        for review in reviews
        if review["state"] == "CHANGES_REQUESTED" and review["author_kind"] == "human"
    )

    snapshot["pull_request"] = {
        "number": pr_basic["number"],
        "title": pr_basic["title"],
        "url": pr_basic["url"],
        "state": pr_basic["state"],
        "is_draft": pr_basic["isDraft"],
        "review_decision": pr_basic.get("reviewDecision"),
        "merge_state_status": pr_basic.get("mergeStateStatus"),
        "mergeable": pr_basic.get("mergeable"),
        "head_ref": pr_basic.get("headRefName"),
        "base_ref": pr_basic.get("baseRefName"),
        "changed_files": pr_data.get("changedFiles"),
        "additions": pr_data.get("additions"),
        "deletions": pr_data.get("deletions"),
    }
    snapshot["checks"] = {"counts": check_counts, "items": checks}
    snapshot["feedback"] = {
        "changes_requested": changes_requested,
        "unresolved_human_threads": sum(1 for thread in unresolved_threads if thread["author_kind"] == "human"),
        "unresolved_bot_threads": sum(1 for thread in unresolved_threads if thread["author_kind"] == "bot"),
        "latest_reviews": reviews[-10:],
        "latest_issue_comments": issue_comments[-10:],
        "unresolved_threads": unresolved_threads[:20],
    }
    actions = compute_actions(snapshot)
    snapshot["actions"] = actions
    snapshot["status"] = compute_status(snapshot, actions)
    snapshot["next_actions"] = [action["message"] for action in actions]
    return snapshot


def print_text(snapshot: dict[str, Any]) -> None:
    repo_meta = snapshot["repository"]
    branch = snapshot["branch"]
    pr = snapshot["pull_request"]
    checks = snapshot["checks"]
    feedback = snapshot["feedback"]

    print(f"Repository: {repo_meta['name_with_owner']} ({repo_meta['url']})")
    print(f"Default branch: {repo_meta['default_branch']}")
    print(f"Status: {snapshot['status']}")
    print()
    print(f"Branch: {branch['name']}")
    print(f"Upstream: {branch['upstream'] or 'none'}")
    print(f"Ahead/behind: {branch['ahead']}/{branch['behind']}")
    print(f"Worktree: {'dirty' if branch['dirty'] else 'clean'}")
    if branch["dirty"]:
        for changed in branch["changed_files"][:10]:
            print(f"  {changed}")
        if len(branch["changed_files"]) > 10:
            print(f"  ... {len(branch['changed_files']) - 10} more")

    print()
    if not pr:
        print("Pull request: none")
    else:
        print(f"Pull request: #{pr['number']} {pr['title']}")
        print(f"URL: {pr['url']}")
        print(f"State: {pr['state']} | draft: {pr['is_draft']}")
        print(f"Review decision: {pr['review_decision'] or 'none'}")
        print(f"Mergeable: {pr['mergeable'] or 'unknown'} | merge state: {pr['merge_state_status'] or 'unknown'}")
        print(
            "Diff: "
            f"{pr['changed_files']} files, +{pr['additions']} -{pr['deletions']}"
        )

    print()
    print(
        "Checks: "
        f"{checks['counts']['passing']} passing, "
        f"{checks['counts']['pending']} pending, "
        f"{checks['counts']['failing']} failing, "
        f"{checks['counts']['other']} other"
    )
    for item in checks["items"][:10]:
        label = item["name"]
        if item.get("workflow"):
            label = f"{item['workflow']} / {label}"
        state = item["state"]
        extra = f" [{item['description']}]" if item.get("description") else ""
        print(f"  {state}: {label}{extra}")
    if len(checks["items"]) > 10:
        print(f"  ... {len(checks['items']) - 10} more")

    print()
    print(
        "Feedback: "
        f"{feedback['changes_requested']} human changes requested, "
        f"{feedback['unresolved_human_threads']} unresolved human threads, "
        f"{feedback['unresolved_bot_threads']} unresolved bot threads"
    )
    for thread in feedback["unresolved_threads"][:10]:
        print(
            f"  {thread['author_kind']}: {thread['author']} | "
            f"{thread['preview']} | {thread['url']}"
        )
    if len(feedback["unresolved_threads"]) > 10:
        print(f"  ... {len(feedback['unresolved_threads']) - 10} more")

    if feedback["latest_reviews"]:
        print()
        print("Latest reviews:")
        for review in feedback["latest_reviews"][-5:]:
            preview = f" | {review['preview']}" if review["preview"] else ""
            print(f"  {review['state']}: {review['author']}{preview}")

    if feedback["latest_issue_comments"]:
        print()
        print("Latest issue comments:")
        for comment in feedback["latest_issue_comments"][-5:]:
            preview = f" | {comment['preview']}" if comment["preview"] else ""
            print(f"  {comment['author_kind']}: {comment['author']}{preview}")

    print()
    print("Actions:")
    if snapshot["actions"]:
        for action in snapshot["actions"]:
            print(f"  {action['severity']}: {action['code']} | {action['message']}")
    else:
        print("  ready: No immediate actions inferred.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect a branch and PR end of session snapshot.")
    parser.add_argument("--repo", default=".", help="Path to the repository root or a child directory.")
    parser.add_argument(
        "--pr",
        default="auto",
        help="PR target. Use 'auto', a PR number, or a PR URL.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()

    try:
        snapshot = build_snapshot(repo, args.pr)
    except CommandError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(snapshot, indent=2))
    else:
        print_text(snapshot)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
