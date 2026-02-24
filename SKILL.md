---
name: project-code-review
argument-hint: "[fast|full] [focus area]"
description: Comprehensive code review skill for entire project codebases using parallel AI agents. Supports two modes — fast (3 parallel agents, default) and full (5 specialist agents + Haiku confidence scoring). Also triggered by "review all code", "scan the codebase", "audit code quality", or "full project code review". Supports optional focus areas (e.g., "/project-code-review fast focus on security").
---

# Project Code Review

Review entire project codebases using parallel Task agents.

**Invocation**: `/project-code-review [fast|full] [focus area]`

| Argument | Mode | Agents | Speed |
|----------|------|--------|-------|
| `fast` (default) | 3 parallel review agents | 3 | ~2-3 min |
| `full` | 5 specialist agents + Haiku scoring | 5 + N | ~5-10 min |

Parse `$ARGUMENTS` — first word is mode (`fast`/`full`, default `fast`), remaining words are the focus area.

---

## Fast Mode (default)

3 parallel agents with combined review areas.

### Workflow

1. **Discover files**: `python3 scripts/find_code_files.py <working_directory> [max_files]` — if >100 files, ask user to narrow scope
2. **Read CLAUDE.md** from root and subdirectories for project context
3. **Spawn 3 Task agents in parallel** using the Task tool with `subagent_type: "general-purpose"` and `model: "sonnet"`. Send all 3 in a single message for parallel execution. Each agent gets:
   - The working directory path and file list
   - CLAUDE.md contents (if found)
   - User's focus area (if provided)
   - Its review checklist (see `references/review_agents.md` for details)
   - The issue output format (below)

   | Agent | Combined Review Areas |
   |-------|----------------------|
   | 1 | Bugs & Logic Errors + Security Vulnerabilities |
   | 2 | CLAUDE.md Compliance + Code Clarity/Simplification |
   | 3 | Type Safety + Performance |

   Each agent prompt should instruct it to: use Glob to find code files, use Read to read them, then review according to its checklist. Agents can read files themselves — do NOT paste file contents into prompts.

4. **Merge and present** results using the output format below. Deduplicate overlapping issues. Only keep issues a senior engineer would flag.

---

## Full Mode (`full`)

5 specialist agents + Haiku confidence scoring for maximum rigor.

### Workflow

1. **Discover files**: `python3 scripts/find_code_files.py <working_directory> [max_files]`
2. **Read CLAUDE.md** from root and subdirectories
3. **Spawn 5 Task agents in parallel** using the Task tool with `subagent_type: "general-purpose"` and `model: "sonnet"`. Send all 5 in a single message. Each agent gets:
   - The working directory path and file list
   - CLAUDE.md contents (if found)
   - User's focus area (if provided)
   - Its specialist checklist from `references/review_agents.md`
   - The issue output format (below)

   | # | Agent | Specialty |
   |---|-------|-----------|
   | 1 | CLAUDE.md Compliance Auditor | Code vs project guidelines |
   | 2 | Bug and Logic Error Scanner | Bugs, edge cases, race conditions |
   | 3 | Security Vulnerability Scanner | OWASP Top 10, injection, secrets |
   | 4 | Type Safety and Performance Auditor | Types, perf, code quality |
   | 5 | Code Simplification Specialist | Clarity, complexity, maintainability |

4. **Confidence scoring**: For each issue found across all agents, spawn Task agents with `model: "haiku"` to score confidence 0-100. Run in parallel (batch into groups). Discard issues scoring <80 or that are pedantic nitpicks / caught by linters.
5. **Merge and present** results using output format below. Deduplicate overlapping issues across agents.

---

## Issue Output Format (for agent prompts)

Include this in every agent prompt so results are parseable:

```
For each issue, output EXACTLY:
ISSUE:
- Severity: Critical | Warning | Simplification
- File: [filepath]
- Line: [line number]
- Description: [what the issue is]
- Impact: [why it matters]
- Fix: [suggested fix]

If no issues found, output: NO_ISSUES_FOUND
```

---

## Final Output Format (presented to user)

If no issues:
```
### Project Code Review (MODE)
**Focus**: <if provided>
No significant issues found. Code looks good.
Checked N files for: bugs, security vulnerabilities, CLAUDE.md compliance, type safety, code clarity.
```

If issues found:
```
### Project Code Review (MODE)
**Focus**: <if provided>
Reviewed N files, found M issues:

**Critical** - Must fix
1. **path/to/file.ts:42** - SQL injection vulnerability
   User input directly concatenated into SQL query.
   Suggested fix: Use parameterized queries.

**Warning** - Should consider fixing
1. **path/to/file.ts:15** - Missing null check
   Variable `user` could be null here.
   Suggested fix: Add null check before accessing user.email.

**Simplification** - Code clarity improvements
1. **path/to/file.ts:28** - Nested ternary operator
   Suggested simplification: Use if/else chain.
```

---

## Notes

- Agents read files themselves via Read/Glob/Grep — do not paste code into prompts
- Do not build or typecheck the app
- For >100 files, batch or ask user to narrow scope
- Reviews all code files, not just uncommitted changes

## Bundled Resources

- `scripts/find_code_files.py` - Discovers reviewable code files in a directory
- `references/review_agents.md` - Detailed checklists for all 5 specialist agents (Full mode) and combined mappings (Fast mode)
