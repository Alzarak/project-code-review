# How to Spawn Agents in Claude Code

## CRITICAL: READ THIS ENTIRE FILE BEFORE SPAWNING ANY AGENTS

This file contains the EXACT commands to spawn sub-agents in Claude Code.
Do NOT deviate from these patterns. Do NOT use "Task" tools or any other method.

## The ONLY Way to Spawn a Sub-Agent

You spawn agents by running the `claude` CLI as a **bash subprocess**. That is the ONLY method.

### Single Agent Command

```bash
claude -p "YOUR PROMPT HERE" \
  --model claude-sonnet-4-20250514 \
  --output-format text \
  2>/dev/null
```

**Flags explained:**
- `-p` = "print mode" — runs non-interactively, takes the prompt as a string, prints the response, and exits
- `--model claude-sonnet-4-20250514` = use Sonnet (required for review agents)
- `--output-format text` = return plain text output (not JSON)
- `2>/dev/null` = suppress stderr noise

### Running 5 Agents in Parallel

To run all 5 review agents at the same time, use bash background processes (`&`) and `wait`:

```bash
# Create a temp directory for agent outputs
REVIEW_DIR=$(mktemp -d)

# Agent 1: CLAUDE.md Compliance
claude -p "YOUR AGENT 1 PROMPT" \
  --model claude-sonnet-4-20250514 \
  --output-format text \
  2>/dev/null > "$REVIEW_DIR/agent1_compliance.txt" &

# Agent 2: Bug Scanner
claude -p "YOUR AGENT 2 PROMPT" \
  --model claude-sonnet-4-20250514 \
  --output-format text \
  2>/dev/null > "$REVIEW_DIR/agent2_bugs.txt" &

# Agent 3: Security Scanner
claude -p "YOUR AGENT 3 PROMPT" \
  --model claude-sonnet-4-20250514 \
  --output-format text \
  2>/dev/null > "$REVIEW_DIR/agent3_security.txt" &

# Agent 4: Type Safety & Performance
claude -p "YOUR AGENT 4 PROMPT" \
  --model claude-sonnet-4-20250514 \
  --output-format text \
  2>/dev/null > "$REVIEW_DIR/agent4_typesafety.txt" &

# Agent 5: Simplification
claude -p "YOUR AGENT 5 PROMPT" \
  --model claude-sonnet-4-20250514 \
  --output-format text \
  2>/dev/null > "$REVIEW_DIR/agent5_simplification.txt" &

# WAIT for ALL agents to finish
wait

# Read all results
cat "$REVIEW_DIR/agent1_compliance.txt"
cat "$REVIEW_DIR/agent2_bugs.txt"
cat "$REVIEW_DIR/agent3_security.txt"
cat "$REVIEW_DIR/agent4_typesafety.txt"
cat "$REVIEW_DIR/agent5_simplification.txt"

# Cleanup
rm -rf "$REVIEW_DIR"
```

### Running Haiku Scoring Agents in Parallel

For confidence scoring, use the same pattern but with haiku:

```bash
claude -p "YOUR SCORING PROMPT" \
  --model claude-haiku-4-5-20251001 \
  --output-format text \
  2>/dev/null
```

You can run many Haiku agents in parallel using the same `&` and `wait` pattern.

## IMPORTANT RULES

1. **NEVER** use a "Task" tool — it does not exist
2. **NEVER** try to call `subagent()` or `spawn_agent()` or any function — they do not exist
3. **ALWAYS** use `claude -p` via the bash tool — this is the ONLY way
4. **ALWAYS** include `--model` flag — do not rely on defaults
5. **ALWAYS** include `--output-format text` — otherwise you get JSON wrapping
6. **ALWAYS** redirect stderr with `2>/dev/null` — prevents noisy output
7. **ALWAYS** use `wait` after background processes — otherwise you read empty files
8. The prompt string after `-p` can be very long — enclose it in double quotes and escape any internal double quotes with `\"`
9. If your prompt is extremely long, write it to a temp file first and use: `claude -p "$(cat /tmp/agent_prompt.txt)" --model claude-sonnet-4-20250514 --output-format text 2>/dev/null`

## Constructing the Agent Prompt

Each agent prompt MUST include:
1. The agent's role and what to look for (from references/review_agents.md)
2. The full content of all code files to review (read them and paste into the prompt)
3. The CLAUDE.md content (if applicable to that agent)
4. The user's focus area (if provided)
5. Output format instructions — tell the agent to output a structured list of issues

### Example Agent Prompt Template

```
You are a [ROLE NAME]. Review the following code files and identify [WHAT TO LOOK FOR].

[If focus area]: Pay special attention to: [FOCUS AREA]

## CLAUDE.md Guidelines
[CLAUDE.md content here, or "No CLAUDE.md found" if none]

## Code Files to Review

### File: src/index.ts
\`\`\`typescript
[file contents]
\`\`\`

### File: src/utils.ts
\`\`\`typescript
[file contents]
\`\`\`

## Output Format

For each issue found, output EXACTLY this format:

ISSUE:
- File: [filepath]
- Line: [line number]
- Description: [what the issue is]
- Impact: [why it matters]
- Fix: [suggested fix]

If no issues found, output: NO_ISSUES_FOUND
```

## Full Working Example

Here is a complete, copy-paste-ready example of spawning one review agent:

```bash
# First, read the files you need
CODE_CONTENT=$(cat src/index.ts src/utils.ts)
CLAUDE_MD=$(cat CLAUDE.md 2>/dev/null || echo "No CLAUDE.md found")

# Write the prompt to a temp file (safer for long prompts)
cat > /tmp/agent2_prompt.txt << 'PROMPT_END'
You are a Bug and Logic Error Scanner. Review the following code and identify bugs, logic errors, and edge cases that could cause runtime failures.

Check for:
- Null/undefined reference issues
- Off-by-one errors
- Race conditions in async code
- Resource leaks
- Error handling gaps
- Incorrect conditional logic
- Type mismatches
- Boundary conditions and edge cases

## Code Files to Review

PROMPT_END

# Append the actual code content
echo "$CODE_CONTENT" >> /tmp/agent2_prompt.txt

cat >> /tmp/agent2_prompt.txt << 'PROMPT_END'

## Output Format

For each issue found, output EXACTLY this format:

ISSUE:
- File: [filepath]
- Line: [line number]
- Description: [what the issue is]
- Impact: [why it matters]
- Fix: [suggested fix]

If no issues found, output: NO_ISSUES_FOUND
PROMPT_END

# Now spawn the agent
claude -p "$(cat /tmp/agent2_prompt.txt)" \
  --model claude-sonnet-4-20250514 \
  --output-format text \
  2>/dev/null > /tmp/agent2_results.txt &
```
