---
name: "learning"
description: "Explain how code works, why it is structured that way, and whether the architectural tradeoffs are sound. Use when Codex needs to help a user understand a code path, unpack the logic behind a module or subsystem, evaluate an architectural decision, compare alternatives, connect local implementation details to broader software engineering fundamentals, or review whether a design is appropriate for the current constraints."
---

# Learning

Help the user understand code and architecture from first principles instead of giving taste-based opinions. Stay grounded in the repository, separate evidence from inference, and explain tradeoffs in a way that matches the user's level.

## Quick start

If you need a reusable session bootstrap, run `scripts/session-bootstrap.sh` and use its output as the default lens for the first pass.

1. Identify the scope:
- The specific file, module, request path, subsystem, or decision the user cares about.
- The user's intent: understand, evaluate, compare, or improve.

2. Build a factual model before judging it:
- Entry points.
- Inputs and outputs.
- State ownership.
- Key dependencies.
- Error paths and invariants.

3. Only then explain:
- What the code is doing.
- Why this shape may have been chosen.
- What it optimizes for.
- What it gives up.

4. Keep the answer split mentally into:
- Fact: what is directly supported by the code or docs.
- Inference: what is likely true from context or structure.
- Recommendation: what should change, if anything.

## Workflow

### 1. Reconstruct the local model

Start from the user's focal point and trace outward just enough to explain it well.

- Identify the responsibility of the unit being examined.
- Trace control flow: who calls it, what branches it takes, where it exits.
- Trace data flow: what enters, what is transformed, what leaves, what is persisted.
- Identify side effects: I/O, database writes, network calls, cache mutation, logging, retries.
- Identify invariants: assumptions that must remain true for the code to be correct.

If the system is large, prefer one request path, one job path, or one domain slice at a time.

### 2. Explain the logic in plain language

Translate implementation into a simple mental model before discussing quality.

- Describe the happy path first.
- Call out important branches, guards, and failure modes.
- Point out where policy lives versus where mechanism lives.
- Map unfamiliar abstractions to fundamentals such as state, boundary, orchestration, transformation, and validation.

When helpful, summarize the code as:
- "This module owns..."
- "This layer decides..."
- "This dependency abstracts..."
- "This invariant protects..."

### 3. Infer the architectural decision carefully

Treat architecture as a response to constraints, not as decoration.

Infer what the design is likely optimizing for:
- Speed of delivery.
- Ease of change.
- Runtime performance.
- Reliability and failure isolation.
- Team ownership boundaries.
- Testability.
- Operational simplicity.

Common evidence includes:
- Layering choices.
- Dependency direction.
- Duplication versus shared abstractions.
- Sync versus async boundaries.
- Centralized versus distributed state.
- Explicit interfaces versus direct coupling.

Never present preference as fact. If multiple interpretations are plausible, say so.

### 4. Evaluate the tradeoffs

Use `references/architecture-lenses.md` when the user wants a judgment, comparison, or recommendation.

Evaluate only the lenses that matter for the current context:
- Cohesion and coupling.
- Boundary clarity.
- Changeability.
- Correctness and invariants.
- Performance and scaling shape.
- Reliability and failure handling.
- Operability and observability.
- Cognitive load for the team.

Prefer statements like:
- "This is a good fit if..."
- "This becomes risky when..."
- "The current design is optimizing X over Y."

### 5. Connect the code to fundamentals

Use `references/code-fundamentals.md` when the user is learning or seems stuck on the logic itself.

Explain the code through durable concepts:
- Control flow.
- Data flow.
- State and ownership.
- Side effects.
- Interfaces and abstraction boundaries.
- Synchronization, latency, or concurrency.
- Error propagation and recovery.

When teaching, move from concrete to general:
1. Show what this code does here.
2. Name the underlying concept.
3. Explain why that concept matters elsewhere.

### 6. Produce the right kind of answer

For understanding requests:
- Start with the simplest faithful explanation.
- Use short examples or mini-traces instead of abstract theory.

For evaluation requests:
- Lead with the main tradeoff.
- Distinguish "reasonable for now" from "likely to break later."

For comparison requests:
- Compare against one or two realistic alternatives, not every possible pattern.

For improvement requests:
- Recommend the smallest change that improves the most important weakness.
- Mention likely migration cost or regression risk.

## Evidence discipline

- Anchor claims to files, call chains, interfaces, configuration, tests, or runtime behavior when available.
- If context is missing, state what is unknown instead of filling gaps with confident guesses.
- Distinguish a local code smell from a system-level architectural flaw.
- Do not criticize duplication if it is preserving boundary clarity.
- Do not praise abstraction if it hides important behavior or raises cognitive load.
- Prefer boring, explicit designs when they better match the problem and team.

## Output patterns

Adapt depth to the user's level, but keep the structure crisp.

### Pattern A: "Help me understand this"

Use:
1. What this code is responsible for.
2. How the main path works.
3. Why it is structured this way.
4. The key concept the user should learn from it.

### Pattern B: "Is this architecture good?"

Use:
1. What problem this design appears to solve.
2. The main strengths.
3. The main risks or limits.
4. Whether it fits the apparent constraints.
5. The smallest worthwhile improvement.

### Pattern C: "Why did they do it this way instead of X?"

Use:
1. What this design optimizes for.
2. What alternative X would improve.
3. What alternative X would worsen.
4. The context that should decide between them.

## References

- Run `scripts/session-bootstrap.sh` when you want a compact architecture-and-logic checklist at the start of a technical session.
- Read `references/architecture-lenses.md` for reusable evaluation criteria and tradeoff questions.
- Read `references/code-fundamentals.md` for durable concepts to explain logic, flow, and abstraction.

Load only the reference file that matches the user's need. Keep explanations concrete, evidence-based, and easy to learn from.
