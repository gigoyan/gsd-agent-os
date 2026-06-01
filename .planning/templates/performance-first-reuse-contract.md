# Performance-First Reuse Contract

Use this contract during planning, execution, quick tasks, and verification when implementation may change code, data flow, integration behavior, runtime behavior, or workflow infrastructure.

## Priority Order
1. Correctness and acceptance criteria.
2. Performance, scalability, hot-path safety, request-path safety, and resource efficiency.
3. Security, validation boundaries, architecture, dependency direction, and project conventions.
4. Reuse, extension, or composition of existing project-owned code.
5. Minimum new code.
6. Generalization only when evidence justifies it.

## Reuse-First Behavior
- Inspect routed reusable surfaces, canonical examples, extension points, internal APIs, tests, and conventions before creating new code.
- Prefer `reused`, `extended`, or `composed` changes when they satisfy the behavior without weakening boundaries.
- Do not bypass validation, error handling, dependency direction, runtime boundaries, or project conventions for local convenience.

## Minimum-New-Code Behavior
- Add only the code needed for the scoped behavior slice and validation set.
- Keep new code local to the owning area unless the phase justifies a shared extension.
- Remove avoidable duplication created by the change, but do not broaden into unrelated cleanup.

## No Premature Abstraction
- Do not create shared abstraction for one caller, speculative future reuse, naming symmetry, or aesthetic cleanup.
- New abstraction is allowed only when at least two current use cases, a known near-term phase, or an existing extension point justifies it.
- Performance safety outranks minimum-code reduction.

## Performance-Sensitive Path Identification
Mark a path performance-sensitive when it affects request or response latency, startup, render loops, background workers, queues, scheduled jobs, database queries, file scans, network calls, API fanout, large payloads, or repeated agent/runtime operations.

## Hot-Path And Request-Path Safety
- Do not add blocking synchronous filesystem, crypto, compression, parsing, database, network, or CPU-heavy work to hot paths without explicit justification.
- Avoid repeated scans, unbounded loops, N+1 queries, unnecessary serialization, and per-request setup that can be reused safely.
- Preserve existing caching, batching, pagination, streaming, transaction, timeout, retry, and backpressure behavior unless the phase explicitly changes it.

## I/O, API, Database, Network, File, And Queue Risk Awareness
Before changing these surfaces, identify the likely cost and failure mode: latency, throughput, locks, rate limits, retries, idempotency, ordering, fanout, payload size, connection use, transaction scope, file count, queue depth, or worker concurrency.

## Required Execution Evidence
- Reusable surfaces inspected.
- Final reuse decision: `reused | extended | composed | new-local | new-abstraction`.
- New code justification.
- Performance-sensitive paths touched.
- Performance risks checked.
- Performance validation run.
- Minimum-new-code justification.

## Verification Failure Or Partial Conditions
Verification must mark `partial` or `fail` when performance and reuse evidence is missing, superficial, contradicted by the diff, or when implementation:
- creates new local code without inspecting plausible existing surfaces;
- introduces a new abstraction without current-scope justification;
- duplicates an existing reusable pattern without explanation;
- changes a hot path, request path, database/API/I/O/network/file/queue surface, or repeated operation without checking relevant performance risk;
- claims validation that was not run or does not cover changed performance-sensitive behavior.
