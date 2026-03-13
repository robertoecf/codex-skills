# Architecture Lenses

Use these lenses selectively. Do not force a full checklist when the user's question is narrow.

## Cohesion and coupling

Ask:
- Does this module have one clear reason to change?
- Do dependencies point in a sensible direction?
- Are unrelated concerns mixed together?

Signals:
- High cohesion: related decisions live together.
- Harmful coupling: small changes require edits across many layers or modules.

## Boundary clarity

Ask:
- Is it obvious where validation, orchestration, domain rules, and I/O belong?
- Are interfaces explicit enough to protect callers from internal changes?

Signals:
- Healthy boundaries make ownership and testing easier.
- Weak boundaries leak persistence, transport, or framework details everywhere.

## Changeability

Ask:
- What is easy to change here?
- What kinds of changes would cause cascading edits?
- Is duplication protecting flexibility or creating drift?

Signals:
- Good changeability means common future changes are cheap.
- Premature reuse often hurts changeability more than duplication does.

## Correctness and invariants

Ask:
- Where are the core business rules enforced?
- Are important invariants checked once in the right place or repeatedly in ad hoc ways?
- Can invalid state exist between steps?

Signals:
- Strong designs make invalid states hard to represent.
- Fragile designs rely on callers "remembering" the rules.

## Performance and scaling shape

Ask:
- Where is the likely hot path?
- Is work being repeated unnecessarily?
- Does the structure allow batching, caching, or parallelism if later needed?

Signals:
- Optimize for actual bottlenecks, not imagined ones.
- Simpler code is often the right choice until scale pressure is real.

## Reliability and failure handling

Ask:
- What happens when a dependency fails or slows down?
- Are retries, timeouts, fallbacks, or idempotency relevant?
- Does one component failure spread too widely?

Signals:
- Good boundaries contain failures.
- Hidden retries and side effects often create surprising behavior.

## Operability and observability

Ask:
- Can the team understand what happened in production?
- Are logs, metrics, and traces aligned with meaningful operations?
- Is the system debuggable without reading every layer?

Signals:
- Operational clarity is part of architecture, not an afterthought.

## Cognitive load

Ask:
- How much context must a new engineer hold to change this safely?
- Are abstractions naming real concepts or only moving code around?
- Is indirection paying for itself?

Signals:
- A design can be theoretically elegant and still be costly for a team to maintain.

## Short evaluation template

Use this when the user asks for a direct verdict:

1. The design appears to optimize for...
2. It works well because...
3. It becomes risky when...
4. I would keep/change...
5. The smallest worthwhile next step is...
