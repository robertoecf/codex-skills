# Code Fundamentals

Use this file to explain code in durable concepts instead of file-by-file narration.

## Control flow

Focus on:
- Entry point.
- Main branches.
- Exit conditions.
- Error path.

Helpful framing:
- "First it validates, then it decides, then it performs side effects."

## Data flow

Focus on:
- Where data comes from.
- How it is transformed.
- Where it is stored or emitted.
- Which values are authoritative.

Helpful framing:
- "This layer translates external input into an internal model."

## State and ownership

Focus on:
- What state exists.
- Who owns it.
- Who is allowed to mutate it.
- What must stay true after each mutation.

Helpful framing:
- "The hard part here is not the computation, but keeping ownership clear."

## Side effects

Focus on:
- Network calls.
- Disk or database writes.
- Cache updates.
- Logging, events, retries, timers.

Helpful framing:
- "Pure logic is mixed with side effects here," or "The design intentionally separates them here."

## Abstraction and interfaces

Focus on:
- What details are hidden.
- What contract is exposed.
- Whether the abstraction matches a real domain concept.

Helpful framing:
- "This abstraction helps if the team expects multiple implementations," or "This abstraction may be premature if there is only one stable behavior."

## Sync, async, and concurrency

Focus on:
- Whether work must happen in sequence.
- Whether ordering matters.
- Whether shared state can race.
- Whether latency is exposed to callers.

Helpful framing:
- "The complexity here comes from coordination, not from business rules."

## Errors and recovery

Focus on:
- Where errors are detected.
- Whether they are translated or propagated.
- Whether the system can retry safely.
- Whether partial failure leaves inconsistent state.

Helpful framing:
- "This code is reliable only if this step is idempotent," or "This layer is acting as the error boundary."

## How to teach from fundamentals

When the user is learning:
1. Name the concrete behavior in the code.
2. Connect it to one fundamental concept.
3. Show the tradeoff.
4. End with the reusable lesson.

Example pattern:
- "This service exists to keep HTTP concerns out of domain logic. The broader concept is boundary management: when rules live behind a stable boundary, the transport layer can change without rewriting the core behavior."
