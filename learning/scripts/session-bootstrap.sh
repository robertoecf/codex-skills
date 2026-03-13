#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
LEARNING SESSION BOOTSTRAP

Use this lens before analyzing code, architecture, or technical decisions.

1. Scope
- What exact file, module, path, or decision is in focus?
- Is the user asking to understand, evaluate, compare, or improve?

2. Facts first
- Identify entry points, main control flow, data flow, state ownership, dependencies, side effects, and invariants.
- Separate what the code proves from what you are inferring.

3. Explain simply
- Describe the happy path first.
- Then describe key branches, failure modes, and where policy lives versus mechanism.

4. Evaluate architecture
- State what the design appears to optimize for.
- Evaluate only the relevant tradeoffs: cohesion, coupling, boundaries, changeability, correctness, performance, reliability, operability, and cognitive load.

5. Connect to fundamentals
- Map the implementation to durable concepts: control flow, data flow, state, side effects, abstraction boundaries, concurrency, and error handling.

6. Respond with discipline
- Fact: what is directly evidenced.
- Inference: what is likely true from structure or context.
- Recommendation: what should change, if anything.

7. Default output shape
- What this code or design is responsible for.
- How it works.
- Why it may be structured this way.
- Main tradeoff.
- Smallest worthwhile improvement, if needed.
EOF
