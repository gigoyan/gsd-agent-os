# Document-First Intake Reference

Use this reference with `$gsd-new-project` when intake needs to choose the right starting point before milestone planning.

## Route-To-Surface Matrix
| Intake route | Start from | Populate first | Follow-up rule |
| --- | --- | --- | --- |
| `placeholder_bootstrap` | Placeholder `PROJECT.md` and `.planning/REQUIREMENTS.md` | Bootstrap charter and requirements | Ask only for missing bootstrap essentials after checking repo evidence. |
| `document_first_intake` | Supplied docs, notes, transcripts, briefs, or files | The highest artifact surfaces the material can already support: bootstrap docs first, then Project Idea Document or Technical Specification when the material is already specific enough | Extract before re-asking. Keep contradictions and gaps explicit. |
| `partial_maturity_continuation` | Existing project artifacts and supplied materials | The highest valid readiness artifact that is stale, incomplete, or missing | Continue forward from the strongest current artifact instead of restarting earlier work. |

## Evidence Handling
- Mark inputs as `Confirmed` when directly supported by repo evidence, supplied material, or an explicit user decision.
- Mark inputs as `Suggested` when they are inferred, recommended, or useful prefills derived from evidence.
- Mark inputs as `Unknown` when the material is missing, contradictory, or not strong enough to confirm.
- Do not silently upgrade `Suggested` to `Confirmed`.

## Document-First Extraction Rules
1. Read supplied material before asking bootstrap or readiness questions.
2. Extract facts into the correct artifact surface rather than dumping raw notes into the nearest file.
3. Preserve contradictions inline so later planning can resolve them without losing source context.
4. Ask only focused residual questions that materially unblock the next artifact.
5. Use UI options whenever the residual question can be answered through structured choices, confirmations, or recommended combinations.

## Continuation Rules
- If `PROJECT.md` and `.planning/REQUIREMENTS.md` are usable but the Project Idea Document is missing, continue into the Project Idea Document instead of redoing bootstrap.
- If the Project Idea Document is current and the Technical Specification is partial, continue the Technical Specification from the existing content.
- If supplied material clearly answers an open field in an existing artifact, refresh that field from the material and keep the evidence status visible.
- Preserve the normal project-facing Spec-First readiness gate for later milestone planning and implementation.
