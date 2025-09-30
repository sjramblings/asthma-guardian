# Constitution Command

## Description
Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync.

## Usage
```
/constitution [PRINCIPLES_INPUT]
```

## Parameters
- `PRINCIPLES_INPUT` (optional): Direct input of principles to incorporate into the constitution

## Constitution Check
This command MUST align with the Asthma Guardian v3 Constitution principles:
- ✅ Clear Purpose & Focus: Command has clear, specific purpose
- ✅ Readable & Well-Documented: Command is well-documented
- ✅ Automation & Tool Reuse: Command automates constitution management
- ✅ Security & Privacy by Design: Command considers security implications
- ✅ Measurement & Observation: Command tracks changes and versions
- ✅ Continuous Improvement: Command enables iterative improvements

## Process
1. Load existing constitution template
2. Identify placeholder tokens
3. Collect/derive values for placeholders
4. Draft updated constitution content
5. Validate consistency across templates
6. Update dependent artifacts
7. Generate sync impact report

## Output
- Updated constitution file
- Sync impact report
- Updated dependent templates
- Summary of changes

## Dependencies
- `.specify/memory/constitution.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/spec-template.md`
- `.specify/templates/tasks-template.md`
- `.specify/templates/commands/*.md`
