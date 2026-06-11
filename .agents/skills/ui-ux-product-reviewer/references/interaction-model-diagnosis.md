# Interaction Model Diagnosis

## Purpose
Diagnose the screen's actual interaction model before listing local findings.

## Required Models
- read-only management table
- bulk-edit table
- form
- dashboard
- approval/review queue
- settings page
- detail page
- wizard/step flow
- modal workflow
- search/browse/listing surface
- creation/editing workflow
- reporting/analytics surface
- custom/unknown

## Diagnosis Questions
1. What is the user goal?
2. What is the current interaction model?
3. What model does the product context require?
4. Does current model match?
5. What risk is created by mismatch?
6. Which local symptoms are downstream of the mismatch?

## Output
Record one `interaction-model.json` file and summarize diagnosis in the report.
