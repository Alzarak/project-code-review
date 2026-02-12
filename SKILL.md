---
name: pcr
description: >
  Project Code Review (PCR) — comprehensive code review skill with two modes.
  Use `/pcr:light` for a fast 5-agent review that catches bugs, security issues, and code quality problems.
  Use `/pcr:full` for the ultimate 8-agent deep review covering bugs, security, performance, architecture, simplification, test coverage, type safety, and convention enforcement with confidence scoring.
  Supports optional focus areas (e.g., "/pcr:full focus on security", "/pcr:light check error handling").
  Returns only high-confidence issues (score ≥80) grouped by severity (Critical, Warning, Simplification).
---

# PCR — Project Code Review

Perform comprehensive code reviews of entire project codebases using specialized AI agent teams. This skill scans all code files in the working directory and identifies bugs, security vulnerabilities, performance issues, architectural concerns, and code quality improvements.

## Two Modes

| Mode | Command | Agents | Best For |
|------|---------|--------|----------|
| **Light** | `/pcr:light` | 5 agents | Quick targeted review — bugs, security, types, compliance, simplification |
| **Full** | `/pcr:full` | 8 agents | Deep comprehensive review — everything in light + performance, architecture, test coverage |

If the user just runs `/pcr` without specifying a mode, **ask them which mode they want** with a brief explanation of the difference.

## Workflow

Follow these steps precisely regardless of mode:

### Phase 0: Discovery

#### Step 1: Discover Code Files

Use the `scripts/find_code_files.py` script to find all reviewable code files in the working directory:

```bash
python3 scripts/find_code_files.py <working_directory> [max_files]
```

The script automatically excludes:
- Common non-code directories (node_modules, .git, dist, build, etc.)
- Binary files and files >1MB
- Hidden directories

If there are more than 100 code files, consider asking the user if they want to:
- Review a specific subdirectory
- Set a max_files limit
- Proceed with reviewing all files (may take significant time)

If no code files are found, inform the user and stop.

#### Step 2: Find CLAUDE.md Files

Search for CLAUDE.md files:
- Look for CLAUDE.md in the root directory
- Look for CLAUDE.md files in subdirectories containing code files

These files contain project-specific coding guidelines that review agents will check against.

#### Step 3: Build Shared Context Brief

Read project configuration files (package.json, requirements.txt, Cargo.toml, go.mod, etc.) and construct a brief containing:
- Project name and description
- Languages and frameworks detected
- Dependency highlights
- Conventions from CLAUDE.md (if found)
- Architecture notes (monorepo, microservice, etc.)

Pass this brief to every agent so they have full project context.

#### Step 4: Optional Focus Area

If the user provided a focus area argument, note it clearly. The focus might be:
- A specific concern (e.g., "focus on security", "check error handling")
- A specific area/module (e.g., "focus on the auth module")
- A specific file type (e.g., "focus on React components")
- A specific method or pattern (e.g., "check async/await usage")

**When a focus is provided**: All review agents should prioritize issues related to the focus area, provide more detailed analysis of focused areas, but still check for critical issues elsewhere.

---

### Phase 0.5: Create Review Team

**IMPORTANT**: Before launching review agents, you MUST create a team using the `TeamCreate` tool. This enables proper agent coordination and message passing.

```python
TeamCreate with:
- team_name: "pcr-review-{timestamp}"  # Use descriptive name
- description: "Project Code Review team for {project_name}"
- agent_type: "general-purpose"
```

After creating the team, note the `team_name` for use in all subsequent agent spawns.

---

### Phase 1: Deploy Review Agents (Parallel)

Launch all agents simultaneously **as teammates** using the `Task` tool with specific parameters. Each agent receives the full file list and the shared context brief.

**Critical: Use correct Task parameters for teammate spawning:**
```python
Task(
  description="{Agent_Role_Name}",  # e.g., "PCR Agent 1: CLAUDE Compliance"
  prompt="{full_agent_prompt_with_context}",
  subagent_type="general-purpose",
  team_name="{name_from_TeamCreate}",  # MUST use team_name from Phase 0.5
  name="{agent_role_name}"  # e.g., "agent1-claude-compliance" - unique name per agent
)
```

**Which agents to launch depends on the mode:**

- **Light mode** (`/pcr:light`): Launch Agents 1–5
- **Full mode** (`/pcr:full`): Launch Agents 1–8

**Agent naming convention** (use these exact names for consistency):
- Light mode: `agent1-claude-compliance`, `agent2-bug-scanner`, `agent3-security-scanner`, `agent4-type-safety`, `agent5-simplification`
- Full mode (add): `agent6-performance`, `agent7-architecture`, `agent8-test-coverage`

Read `references/review_agents_light.md` for Agent 1–5 configurations.
Read `references/review_agents_full.md` for Agent 6–8 configurations (full mode only).

**Important**: If a focus argument was provided, include it in each agent's prompt so they prioritize that area.

Each agent should:
- Read full file context when needed
- Return a list of issues with: file path, line number, description, reason flagged, suggested fix
- Send results via SendMessage to team lead when complete

---

### Phase 2: Confidence Scoring (Parallel)

For each issue found in Phase 1, launch a parallel Haiku agent that:
- Takes the issue description and CLAUDE.md files
- Returns a confidence score (0-100):
  - **0**: False positive, doesn't stand up to scrutiny, or pre-existing issue
  - **25**: Might be real, but could be false positive or not in CLAUDE.md
  - **50**: Real issue but might be a nitpick or rare in practice
  - **75**: Very likely a real issue that will be hit in practice
  - **100**: Definitely a real issue that will happen frequently

Filter out false positives:
- Pre-existing issues (not in current changes if reviewing diffs)
- Pedantic nitpicks a senior engineer wouldn't call out
- Issues caught by linters/typeCheckers/compilers
- Issues silenced by lint ignore comments
- Intentional functionality changes

### Phase 3: Filter and Present Results

Filter out issues with confidence scores <80.

If no issues meet the threshold, report:
```
# 🔍 Project Code Review — [Light/Full]

**Focus**: <user's focus argument, if provided>

✅ No significant issues found. Code looks good.

Checked N files with [5/8] specialized agents for: [list categories checked].
```

Otherwise, present the full report. Write it to `CODE_REVIEW_REPORT.md` in the project root.

#### Report Structure:

```markdown
# 🔍 Project Code Review Report — [Light/Full]
## Project: [name]
## Date: [date]
## Files Reviewed: [count]
## Mode: [Light (5 agents) / Full (8 agents)]
## Total Issues Found: [count] (filtered from [raw count] raw findings)

---

## 🚨 CRITICAL (Score 95-100) — Must Fix Immediately
[Issues that represent active bugs, security vulnerabilities, or data loss risks]

## ⚠️ HIGH (Score 80-94) — Should Fix Soon
[Issues that will cause problems but aren't immediately dangerous]

## 📊 Summary by Category
| Category | Critical | High | Total |
|----------|----------|------|-------|
| Bugs & Logic Errors | X | X | X |
| Security Vulnerabilities | X | X | X |
| Type Safety & Performance | X | X | X |
| Code Simplification | X | X | X |
| CLAUDE.md Compliance | X | X | X |
| Performance (full only) | X | X | X |
| Architecture (full only) | X | X | X |
| Test Coverage (full only) | X | X | X |

## 📁 Issues by File
[Group all issues by file path so developers can fix file-by-file]

## 🎯 Top 10 Highest-Impact Fixes
[Ranked list of the 10 changes that would most improve the codebase]

## 🏆 What's Done Well
[Acknowledge patterns, practices, and code that is well-written]
```

For each issue in the report, include:
1. File path and line number
2. Clear description of the problem
3. Why it matters (impact)
4. Concrete fix with code snippet
5. Confidence score

### Phase 4: Cleanup

After the report is written and presented to the user, clean up the review team:

```python
TeamDelete()  # Removes team directory and task directories
```

This ensures resources are freed up for future sessions.

---

## Notes

- Do not attempt to build or typecheck the app
- Make a todo list first before starting the review
- For large codebases (>100 files), consider batching or asking user to narrow scope
- This reviews all code files, not just uncommitted changes
- Full mode takes significantly longer than Light mode — set expectations with the user
- **Always use TeamCreate before spawning agents** — this is required for proper teammate coordination
- **Always include `team_name` and `name` parameters** when spawning review agents via Task tool

## Bundled Resources

### Scripts

- `scripts/find_code_files.py` — Discovers all reviewable code files in the project directory

### References

- `references/review_agents_light.md` — Configurations for Agents 1–5 (used in both Light and Full modes)
- `references/review_agents_full.md` — Configurations for Agents 6–8 (used only in Full mode)
