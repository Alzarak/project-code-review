---
name: project-code-review
description: Comprehensive code review skill for entire project codebases using parallel AI agents. Supports two modes — /pcr:fast (quick single-pass review, no sub-agents) and /pcr:full (5 parallel Sonnet agents + Haiku confidence scoring). Also triggered by "review all code", "scan the codebase", "audit code quality", or "full project code review". Supports optional focus areas (e.g., "focus on security", "check error handling").
---

# Project Code Review

Perform comprehensive code reviews of entire project codebases. Supports two modes for different speed/depth tradeoffs.

## Mode Selection

| Command | Mode | What It Does | Agents | Speed |
|---------|------|-------------|--------|-------|
| `/pcr:fast` or `/pcr` | **Fast** | Single-pass review by YOU (no sub-agents spawned) | 0 | ~1-2 min |
| `/pcr:full` | **Full** | 5 parallel Sonnet review agents + Haiku confidence scoring | 5 Sonnet + N Haiku | ~5-10 min |

**Default behavior**: If the user just says `/pcr` with no mode qualifier, use **Fast** mode.

---

## CRITICAL: How Sub-Agents Are Spawned (Full Mode Only)

**Sub-agents are spawned ONLY by running `claude -p` via the bash tool.**

There is NO "Task" tool. There is NO `subagent()` function. There is NO other way.

**BEFORE starting Full mode**, you MUST read the spawning reference:

```
references/spawn_agents.md
```

**Read that file FIRST. It contains the exact bash commands you must copy.**

Quick summary: `claude -p "prompt" --model claude-sonnet-4-20250514 --output-format text 2>/dev/null`. For parallel agents, add `&` after each and `wait`. Full details in `references/spawn_agents.md`.

---

# FAST MODE (`/pcr:fast` or `/pcr`)

Fast mode does NOT spawn any sub-agents. YOU perform the review directly.

## Fast Mode Workflow

### Fast Step 1: Discover Code Files

```bash
python3 scripts/find_code_files.py <working_directory> [max_files]
```

If >100 files, ask the user to narrow scope or set a limit.

### Fast Step 2: Find and Read CLAUDE.md

Look for CLAUDE.md in root and subdirectories. Read contents for context.

### Fast Step 3: Read and Review All Code Files

Read each code file yourself. As you read, look for:
- **Bugs & Logic Errors**: null refs, off-by-one, race conditions, error handling gaps
- **Security Issues**: injection flaws, XSS, hardcoded secrets, auth bypass, SSRF
- **CLAUDE.md Violations**: any project guideline violations
- **Code Clarity**: nested ternaries, unnecessary complexity, dead code

If the user provided a focus area, prioritize that.

**Skip confidence scoring** — just use your own judgment. Only report issues you are confident about (things a senior engineer would flag).

### Fast Step 4: Present Results

Use the same output format as Full mode (see "Output Format" section below).

---

# FULL MODE (`/pcr:full`)

Full mode spawns 5 parallel Sonnet review agents and Haiku confidence scoring agents.

## Full Mode Workflow

### Full Step 0: Read the Spawning Reference

**MANDATORY.** Read `references/spawn_agents.md` NOW. It has the exact bash commands.

Do NOT proceed without reading it. Do NOT try to use a "Task" tool or `subagent()`.

### Full Step 1: Discover Code Files

```bash
python3 scripts/find_code_files.py <working_directory> [max_files]
```

If >100 files, ask the user to narrow scope or set a limit.

### Full Step 2: Find and Read CLAUDE.md

Look for CLAUDE.md in root and subdirectories. Read contents.

### Full Step 3: Read All Code File Contents

Read every discovered code file. You will paste these into each agent's prompt. For large codebases, write file contents to temp files.

### Full Step 4: Note Focus Area (if provided)

If the user gave a focus area, you will include it in every agent prompt.

### Full Step 5: Launch 5 Parallel Review Agents

**Follow the EXACT spawning pattern from `references/spawn_agents.md`.**

Step-by-step:

1. Create a temp directory:
```bash
REVIEW_DIR=$(mktemp -d)
```

2. Write each agent's prompt to a temp file (safer for long prompts):
```bash
cat > /tmp/agent1_prompt.txt << 'PROMPT_END'
[Agent role + instructions from references/review_agents.md]
[All code file contents]
[CLAUDE.md contents]
[Focus area if provided]
[Output format instructions]
PROMPT_END
```

3. Spawn each agent with this EXACT command:
```bash
claude -p "$(cat /tmp/agent1_prompt.txt)" \
  --model claude-sonnet-4-20250514 \
  --output-format text \
  2>/dev/null > "$REVIEW_DIR/agent1.txt" &
```

4. Repeat for all 5 agents, then:
```bash
wait
```

5. Read all output files:
```bash
cat "$REVIEW_DIR/agent1.txt"
cat "$REVIEW_DIR/agent2.txt"
# ... etc
```

**The 5 agents are:**

| # | Agent Name | What It Reviews |
|---|-----------|-----------------|
| 1 | CLAUDE.md Compliance Auditor | Code vs CLAUDE.md guidelines |
| 2 | Bug and Logic Error Scanner | Bugs, logic errors, edge cases, race conditions |
| 3 | Security Vulnerability Scanner | OWASP Top 10, injection, XSS, secrets, auth |
| 4 | Type Safety and Performance Auditor | Types, performance, code quality |
| 5 | Code Simplification Specialist | Clarity, complexity, nested ternaries |

See `references/review_agents.md` for each agent's complete instructions.

**Reminder: Do NOT use a "Task" tool. Do NOT call `subagent()`. Use `claude -p` via bash.**

### Full Step 6: Confidence Scoring

For each issue found, spawn a Haiku agent to score it:

```bash
claude -p "Score this issue 0-100 for confidence. 0=false positive, 50=nitpick, 75=likely real, 100=definitely real.

Issue: [ISSUE DESCRIPTION]
Code context: [RELEVANT CODE]
CLAUDE.md: [GUIDELINES IF RELEVANT]

Return ONLY a single number 0-100, nothing else." \
  --model claude-haiku-4-5-20251001 \
  --output-format text \
  2>/dev/null > "$REVIEW_DIR/score_N.txt" &
```

Run all scoring agents in parallel with `&`, then `wait`.

Filter criteria — discard issues that are:
- Pre-existing (not from current changes)
- Pedantic nitpicks a senior engineer wouldn't flag
- Caught by linters/type checkers/compilers
- Silenced by lint ignore comments

### Full Step 7: Filter and Present Results

Only keep issues with confidence score ≥80. Present using the output format below.

---

## Output Format (Both Modes)

If no issues found:
```
### Project Code Review (MODE)

**Focus**: <focus area, if provided>

No significant issues found. Code looks good.

Checked N files for: bugs, security vulnerabilities, CLAUDE.md compliance, type safety, code clarity.
```

If issues found:
```
### Project Code Review (MODE)

**Focus**: <focus area, if provided>

Reviewed N files, found M issues:

**Critical** - Must fix

1. **path/to/file.ts:42** - SQL injection vulnerability
   
   User input is directly concatenated into SQL query without sanitization.
   
   Suggested fix: Use parameterized queries or an ORM.

**Warning** - Should consider fixing

1. **path/to/file.ts:15** - Missing null check
   
   Variable `user` could be null/undefined here, causing runtime error.
   
   Suggested fix: Add null check before accessing user.email.

**Simplification** - Code clarity improvements

1. **path/to/file.ts:28** - Nested ternary operator
   
   Triple-nested ternary makes logic hard to follow.
   
   Suggested simplification: Use if/else chain or switch statement.
```

Replace `(MODE)` with either `Fast` or `Full`.

For each issue include: file path, line number, brief description, why it matters, suggested fix.

---

## Notes

- Do not attempt to build or typecheck the app
- Make a todo list first before starting the review
- For large codebases (>100 files), consider batching or asking user to narrow scope
- This reviews all code files, not just uncommitted changes

## Bundled Resources

### Scripts

- `scripts/find_code_files.py` - Discovers all reviewable code files in the project directory

### References

- `references/spawn_agents.md` - **READ THIS FIRST (Full mode only)** — Exact bash commands for spawning Claude Code sub-agents. Copy-paste-ready. Do NOT skip.
- `references/review_agents.md` - Complete configurations and instructions for all 5 specialized review agents (Full mode only)
