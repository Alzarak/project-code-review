# Project Code Review

A comprehensive code review skill for [Claude Code](https://claude.ai/code) that scans entire project codebases using parallel AI agents to identify bugs, security vulnerabilities, type safety issues, and code simplification opportunities.

## Features

- **Multi-Agent Review System**: 5 specialized agents review code in parallel for comprehensive coverage
- **Confidence Scoring**: Issues are scored (0-100) and only high-confidence findings (≥80) are reported
- **Security Focused**: Scans for OWASP Top 10 vulnerabilities including injection flaws, XSS, and authentication bypass
- **Type Safety**: Detects TypeScript type issues, unsafe `any` usage, and type assertion problems
- **Code Quality**: Identifies opportunities for simplification, performance improvements, and clarity enhancements
- **CLAUDE.md Aware**: Checks code against project-specific guidelines defined in CLAUDE.md files
- **Configurable Scope**: Review entire projects or focus on specific areas (security, error handling, specific modules)

## How It Works

The skill supports two review modes: **Fast** (default) and **Full**.

### Fast Mode (`/pcr:fast`)

- **Single-Pass**: The main agent reviews code directly without spawning sub-agents.
- **Speed**: ~1-2 minutes.
- **Best for**: Quick feedback, iterative development, and smaller changes.

### Full Mode (`/pcr:full`)

- **Multi-Agent**: Spawns 5 specialized sub-agents in parallel.
- **Confidence Scoring**: Uses a dedicated scorer to filter false positives.
- **Speed**: ~5-10 minutes.
- **Best for**: Pre-release audits, security scans, and deep verification.

#### Full Mode Architecture

##### Stage 1: Parallel Analysis

Five specialized Sonnet agents analyze all code files simultaneously:

| Agent | Focus |
| :--- | :--- |
| #1 | CLAUDE.md Compliance Auditor |
| #2 | Bug and Logic Error Scanner |
| #3 | Security Vulnerability Scanner |
| #4 | Type Safety and Performance Auditor |
| #5 | Code Simplification Specialist |

##### Stage 2: Confidence Scoring

Each identified issue is evaluated by **Claude 3 Haiku** agents that score confidence:

- **0**: False positive or pre-existing issue
- **25**: Possible issue, low confidence
- **50**: Real issue but nitpicky or rare
- **75**: Very likely a real issue
- **100**: Definitely a real issue that will occur frequently

Only issues scoring ≥80 are reported, minimizing false positives.

## Installation

This is a Claude Code skill. To install:

1. Clone this repository to your Claude skills directory:

   ```bash
   git clone https://github.com/yourusername/project-code-review.git ~/.claude/skills/project-code-review
   ```

2. The skill will be automatically available when using Claude Code.

## Usage

### Fast Review (Default)

Quickly review the codebase (single-pass, no sub-agents):

```bash
/pcr
# OR
claude-code "Review this project"
```

### Full Review (Deep Scan)

Perform a comprehensive multi-agent review with confidence scoring:

```bash
/pcr:full
# OR
claude-code "Full project code review"
```

### Focused Review

Review with a specific focus area:

```bash
claude-code "Review this project focusing on security"
claude-code "Check the codebase for error handling issues"
claude-code "Review the auth module specifically"
```

### Review Specific Directories

```bash
claude-code "Review the src/ and lib/ directories"
```

## Output Format

Results are grouped by severity:

### Critical (95-100) - Must Fix

```markdown
1. **path/to/file.ts:42** - SQL injection vulnerability

   User input is directly concatenated into SQL query without sanitization.
   This allows attackers to execute arbitrary SQL commands.

   Suggested fix: Use parameterized queries or an ORM.
```

### Warning (80-94) - Should Consider Fixing

```markdown
1. **path/to/file.ts:15** - Missing null check

   Variable `user` could be null/undefined here, causing runtime error.

   Suggested fix: Add null check before accessing user.email.
```

### Simplification (80-100) - Code Clarity

```markdown
1. **path/to/file.ts:28** - Nested ternary operator

   Triple-nested ternary makes logic hard to follow.

   Suggested simplification: Use if/else chain or switch statement.
```

## What Gets Checked

### Security (Agent #3)

- Injection flaws (SQL, command, code, LDAP)
- Cross-Site Scripting (XSS)
- Authentication bypass and session issues
- Sensitive data exposure (hardcoded secrets, API keys)
- Broken access control
- Security misconfigurations
- Server-Side Request Forgery (SSRF)

### Bugs (Agent #2)

- Null/undefined reference issues
- Off-by-one errors
- Race conditions in async code
- Resource leaks
- Error handling gaps
- Incorrect conditional logic

### Type Safety & Performance (Agent #4)

- Missing type annotations
- Unsafe `any` usage
- Type assertion issues
- Inefficient algorithms
- Memory leaks
- N+1 database queries
- Unnecessary re-renders

### Code Simplification (Agent #5)

- Nested ternary operators
- Unnecessary complexity
- Redundant code
- Poor naming
- Violations of project standards

## File Exclusions

The review automatically excludes:

- **Common non-code directories**: `node_modules`, `.git`, `dist`, `build`, `__pycache__`, `.next`, `.nuxt`, `target`, `out`, `tmp`, `temp`, `.DS_Store`
- **IDE directories**: `.idea`, `.vscode`, `.gradle`
- **Dependency directories**: `vendor`, `venv`, `.venv`, `env`, `.env`, `bower_components`
- **Cache directories**: `.cache`, `coverage`, `.pytest_cache`, `.mypy_cache`, `.sass-cache`
- **Files larger than 1MB**

## Supported Languages

Python, JavaScript, TypeScript, JSX, TSX, Java, C, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala, Shell (`.sh`, `.bash`, `.zsh`, `.fish`), SQL, R, Lua, Perl, Vue, Svelte, Astro, Elm, Elixir, Erlang, Clojure, Haskell, OCaml, F#, VB.NET, Groovy, Dart, Objective-C/C++, Config files (`.yaml`, `.json`, `.toml`, `.xml`), Web (`.html`, `.css`, `.scss`, `.less`), Documentation (`.md`, `.rst`, `.tex`), and more.

## Project Structure

```text
project-code-review/
├── SKILL.md                    # Main skill definition
├── CLAUDE.md                   # This repo's development guidelines
├── README.md                   # This file
├── scripts/
│   └── find_code_files.py     # Code file discovery utility
└── references/
    └── review_agents.md        # Agent configurations
```

## Contributing

Contributions are welcome! This is a skill for Claude Code, so improvements can include:

- Additional review agents for specialized checks
- Enhanced confidence scoring algorithms
- Support for more languages
- New exclusion patterns
- Improved reporting formats

## License

MIT License - see LICENSE file for details.

## Related

- [Claude Code Documentation](https://claude.ai/code)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
