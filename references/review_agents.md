# Review Agent Checklists

Agent prompts for project code review. Each agent is spawned as a Task with `subagent_type: "general-purpose"`. Agents use Glob/Read/Grep to access code files directly.

## Common Prompt Preamble

Every agent prompt should start with:

```
You are a code reviewer. Your working directory is: {working_directory}
Review the following code files: {file_list}

Project guidelines (CLAUDE.md):
{claude_md_contents or "No CLAUDE.md found"}

{focus_area if provided: "Pay special attention to: {focus_area}"}

Use Glob and Read to access the files. Do NOT ask for permission — just read and review.
```

Then append the agent-specific checklist and output format from below.

---

## Full Mode: 5 Specialist Agents

### Agent 1: CLAUDE.md Compliance Auditor

Review code against CLAUDE.md project guidelines. Not all CLAUDE.md instructions apply to review (some are for code generation). Focus on:
- Code style and formatting requirements
- Architectural patterns and conventions
- Project-specific best practices
- Technology-specific guidelines (e.g., "use ES modules", "prefer function keyword")

For each issue, cite the specific CLAUDE.md guideline being violated.

### Agent 2: Bug and Logic Error Scanner

Scan for significant bugs that could cause runtime failures. Avoid nitpicks. Check for:
- Null/undefined reference issues
- Off-by-one errors in loops and array access
- Race conditions in async code
- Resource leaks (unclosed files, connections)
- Error handling gaps (missing try-catch, unhandled promise rejections)
- Incorrect conditional logic
- Type mismatches and coercion issues
- Boundary conditions and edge cases

### Agent 3: Security Vulnerability Scanner

Scan for OWASP Top 10 and common security issues:
- **Injection**: SQL, command, code, LDAP injection
- **XSS**: Reflected, stored, DOM-based
- **Auth bypass**: Weak authentication, session management
- **Sensitive data**: Hardcoded secrets, API keys, PII leakage
- **XXE**: Unsafe XML parsing
- **Broken access control**: Missing authorization, privilege escalation
- **Misconfiguration**: Default credentials, verbose errors
- **SSRF**: Unsafe URL handling

### Agent 4: Type Safety and Performance Auditor

Review for type safety, performance, and code quality:

**Type Safety** (TypeScript/typed languages): `any` usage, unsafe assertions, implicit coercion, generic misuse

**Performance**: O(n^2) where O(n) possible, memory leaks, blocking main thread, N+1 queries, unnecessary re-renders

**Code Quality**: Dead code, duplicate code, high cyclomatic complexity, poor separation of concerns

### Agent 5: Code Simplification Specialist

Focus on clarity and maintainability while preserving exact functionality:
- Reduce unnecessary complexity and nesting
- Eliminate redundant code and abstractions
- Flag nested ternary operators (prefer if/else or switch)
- Flag CLAUDE.md coding standard violations
- Choose clarity over brevity — explicit > compact
- Do NOT over-simplify: keep helpful abstractions, don't combine too many concerns

---

## Fast Mode: 3 Combined Agents

Fast mode merges the 5 specialists into 3 agents:

| Fast Agent | Combines | Checklist |
|-----------|----------|-----------|
| 1 | Agent 2 + Agent 3 | Bug/Logic + Security checklists above |
| 2 | Agent 1 + Agent 5 | CLAUDE.md Compliance + Simplification checklists above |
| 3 | Agent 4 | Type Safety + Performance checklist above |

Use the same checklists — just combine them in the agent prompt.

---

## Issue Output Format

Append this to every agent prompt:

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
