---
name: project-code-review
description: Comprehensive code review skill for entire project codebases using parallel AI agents. Use when the user asks to review all code in a project, scan the codebase for issues, audit code quality across the project, or perform a full project code review. Also use when asked to review specific directories or sets of files. Supports optional focus areas (e.g., "focus on security", "check error handling"). Returns only high-confidence issues (score ≥80) grouped by severity (Critical, Warning, Simplification).
---

# Project Code Review

Perform comprehensive code reviews of entire project codebases using specialized AI agents. This skill scans all code files in the working directory and identifies bugs, security vulnerabilities, type safety issues, CLAUDE.md compliance violations, and code simplification opportunities.

## Overview

This skill uses a multi-agent review system:

- **5 parallel Sonnet agents** perform specialized reviews (CLAUDE.md compliance, bugs, security, type safety, simplification)
- **GLM-4.5-Air agents** score each issue for confidence (0-100)
- Only issues scoring ≥80 are reported to filter false positives

## Workflow

Follow these steps precisely:

### Step 1: Discover Code Files

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

### Step 2: Find CLAUDE.md Files

Use a GLM-4.5-Air agent to search for CLAUDE.md files:

- Look for CLAUDE.md in the root directory
- Look for CLAUDE.md files in subdirectories containing code files

These files contain project-specific coding guidelines that Agent #1 will check against.

### Step 3: Optional Focus Area

If the user provided a focus area argument, note it clearly. The focus might be:

- A specific concern (e.g., "focus on security", "check error handling")
- A specific area/module (e.g., "focus on the auth module")
- A specific file type (e.g., "focus on React components")
- A specific method or pattern (e.g., "check async/await usage")

**When a focus is provided**: All review agents should prioritize issues related to the focus area, provide more detailed analysis of focused areas, but still check for critical issues elsewhere.

### Step 4: Launch 5 Parallel Review Agents

Read `references/review_agents.md` for complete agent configurations. Launch 5 parallel Sonnet agents, each reviewing all code files:

**Agent #1**: CLAUDE.md Compliance Auditor

- Check code against CLAUDE.md guidelines
- Focus on project-specific conventions

**Agent #2**: Bug and Logic Error Scanner  

- Find bugs, logic errors, edge cases
- Check for null/undefined, off-by-one, race conditions, error handling gaps

**Agent #3**: Security Vulnerability Scanner

- Scan for OWASP Top 10 vulnerabilities
- Check for injection flaws, XSS, auth bypass, data exposure, insecure dependencies

**Agent #4**: Type Safety and Performance Auditor

- Check TypeScript type safety
- Identify performance problems
- Flag code quality concerns

**Agent #5**: Code Simplification Specialist

- Find opportunities to improve clarity
- Flag unnecessary complexity
- Identify violations of project standards
- Flag nested ternaries and suggest clearer alternatives

**Important**: If a focus argument was provided, include it in each agent's prompt so they prioritize that area.

Each agent should:

- Read full file context when needed
- Return a list of issues with: file path, line number, description, reason flagged

### Step 5: Confidence Scoring

For each issue found in Step 4, launch a parallel GLM-4.5-Air agent that:

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

### Step 6: Filter and Present Results

Filter out issues with confidence scores <80.

If no issues meet the threshold, report:

```
### Project Code Review

**Focus**: <user's focus argument, if provided>

No significant issues found. Code looks good.

Checked N files for: bugs, security vulnerabilities, CLAUDE.md compliance, type safety, code clarity.
```

Otherwise, present filtered issues grouped by severity:

```
### Project Code Review

**Focus**: <user's focus argument, if provided>

Reviewed N files, found M issues:

**Critical** (score 95-100) - Must fix

1. **path/to/file.ts:42** - SQL injection vulnerability
   
   User input is directly concatenated into SQL query without sanitization.
   This allows attackers to execute arbitrary SQL commands.
   
   Suggested fix: Use parameterized queries or an ORM.

**Warning** (score 80-94) - Should consider fixing

1. **path/to/file.ts:15** - Missing null check
   
   Variable `user` could be null/undefined here, causing runtime error.
   
   Suggested fix: Add null check before accessing user.email.

**Simplification** (score 80-100) - Code clarity improvements

1. **path/to/file.ts:28** - Nested ternary operator
   
   Triple-nested ternary makes logic hard to follow.
   
   Suggested simplification: Use if/else chain or switch statement.
```

For each issue, include:

- File path and line number
- Brief description
- Why it matters
- Suggested fix with code snippet if helpful

## Notes

- Do not attempt to build or typecheck the app
- Make a todo list first before starting the review
- For large codebases (>100 files), consider batching or asking user to narrow scope
- This reviews all code files, not just uncommitted changes (unlike local-review workflow)

## Bundled Resources

### Scripts

- `scripts/find_code_files.py` - Discovers all reviewable code files in the project directory, excluding common non-code directories

### References

- `references/review_agents.md` - Complete configurations and instructions for all 5 specialized review agents
