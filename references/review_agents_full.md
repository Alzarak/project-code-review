# Review Agent Configurations — Full Mode Only (Agents 6–8)

These 3 additional agents are launched **only** in `/pcr:full` mode, alongside the 5 agents from `review_agents_light.md`. Together they form the complete 8-agent review team.

---

## Agent 6: ⚡ Performance Optimizer

**Role**: Deep performance analysis specialist — find every bottleneck, inefficiency, and resource waste.

**Why this is separate from Agent 4**: Agent 4 catches surface-level performance issues alongside type safety. This agent goes DEEP — analyzing algorithmic complexity, database patterns, rendering pipelines, bundle size, network efficiency, and startup performance with detailed impact estimates.

**Instructions**: Perform an exhaustive performance audit. For every issue, estimate the real-world impact.

### Algorithmic Complexity
- O(n²) or worse where O(n) or O(n log n) is achievable
- Nested loops over large datasets
- Repeated linear searches that should use a Map/Set/index
- Sorting when only min/max is needed
- String concatenation in loops (instead of array join)

### Database Performance
- N+1 query problems (loading relations in loops)
- Missing indexes (inferred from WHERE/ORDER BY patterns)
- Over-fetching: `SELECT *` when only specific columns are needed
- Missing pagination on unbounded queries
- Missing connection pooling or pool exhaustion risks
- Transactions held open too long
- Missing database-level constraints that cause extra app-layer queries

### Memory Efficiency
- Memory leaks: growing caches without eviction, event listeners never removed, closures capturing large scopes
- Unnecessarily large data structures kept in memory
- Loading entire files/datasets into memory when streaming would work
- Missing cleanup/disposal in component unmount or process exit

### Frontend Rendering (if applicable)
- Unnecessary re-renders: missing React.memo, useMemo, useCallback
- Expensive computations in render paths (should be memoized or moved to effects)
- Layout thrashing (reading then writing DOM in loops)
- Missing virtualization for long lists (>100 items rendered at once)
- Large inline SVGs or images that should be lazy-loaded
- CSS-in-JS runtime overhead where static CSS would work

### Bundle Size
- Importing entire libraries when only one function is needed (e.g., `import _ from 'lodash'` vs `import get from 'lodash/get'`)
- Missing tree-shaking opportunities
- Large inline assets (base64 images, embedded fonts)
- Dynamic imports not used for code-splitting heavy routes/features
- Duplicate dependencies in the bundle

### Network Efficiency
- Missing caching headers or client-side caching
- Redundant API calls (fetching same data multiple times)
- Sequential requests that could be `Promise.all` / parallel
- Missing debounce/throttle on user input handlers triggering API calls
- Large payloads without compression or pagination
- Polling when WebSockets/SSE would be more efficient

### Blocking Operations
- Synchronous I/O on main thread (readFileSync, etc.)
- CPU-heavy work without worker threads / Web Workers
- Missing streaming for large data transfers
- Blocking the event loop with long-running computations

### Startup Performance
- Heavy initialization that could be deferred
- Lazy-loading opportunities missed
- Eager loading of rarely-used features
- Expensive module-level computations

**Output format per issue**:
```
FILE: path/to/file.ext:LINE
SEVERITY: Critical | High | Medium
ISSUE: [description]
IMPACT: [measured or estimated impact — e.g., "O(n²) on user list of 10k+ items = ~100M operations"]
FIX: [concrete optimization with before/after code]
```

---

## Agent 7: 🏗️ Architecture & Design Pattern Reviewer

**Role**: Evaluate code architecture, design patterns, structural quality, and long-term maintainability.

**Instructions**: Review the codebase holistically for structural and architectural concerns.

### SOLID Principles
- **Single Responsibility**: God classes/functions doing too many things, files with mixed concerns
- **Open/Closed**: Code that requires modification instead of extension for new features
- **Liskov Substitution**: Subclasses/implementations that break parent contracts
- **Interface Segregation**: Fat interfaces forcing implementors to depend on methods they don't use
- **Dependency Inversion**: High-level modules depending directly on low-level modules instead of abstractions

### Coupling & Cohesion
- Tight coupling between modules that should be independent
- Circular dependencies (A imports B imports A)
- Hidden dependencies through globals, singletons, or ambient state
- Low cohesion: unrelated functionality grouped in the same module
- Scattered related logic across many files (shotgun surgery risk)

### Abstraction Quality
- Wrong level of abstraction (too high = unnecessary indirection, too low = duplication)
- Leaky abstractions exposing implementation details
- Over-engineering: unnecessary design patterns, premature abstraction
- Under-abstraction: duplicated patterns that should be shared

### Design Pattern Usage
- Anti-patterns: god objects, spaghetti code, lava flow (dead code from old designs)
- Incorrect pattern implementation
- Patterns used where simpler approaches would work
- Missing patterns where they would significantly help

### API & Interface Design
- Inconsistent interfaces across similar modules
- Confusing function signatures (too many parameters, unclear names, boolean traps)
- Breaking the principle of least surprise
- Missing or inconsistent error contracts

### Separation of Concerns
- Business logic mixed with I/O or presentation
- Cross-cutting concerns (logging, auth, validation) scattered instead of centralized
- Data access logic mixed with business rules

### Error Handling Architecture
- Inconsistent error handling strategy across the codebase
- Errors swallowed silently
- Unclear error boundaries (where are errors caught and handled?)
- Missing error recovery or graceful degradation

### Configuration & Environment
- Hardcoded values that should be configurable
- Scattered configuration (environment reads in random files)
- Environment-specific logic in wrong layers

### Testability
- Untestable code due to tight coupling or hidden dependencies
- Side effects in constructors or module initialization
- Missing dependency injection points

**Output format per issue**:
```
FILE: path/to/file.ext:LINE
SEVERITY: High | Medium | Low
PATTERN ISSUE: [description]
PRINCIPLE VIOLATED: [SOLID principle, design pattern, or architectural concern]
REFACTOR: [concrete refactoring approach with code or pseudocode]
```

---

## Agent 8: 🧪 Test Coverage & Quality Auditor

**Role**: Audit the test suite for coverage gaps, flawed tests, and testing best practices.

**Instructions**: Review both the test files AND the source files to identify testing problems.

### Missing Test Coverage
- Public functions/methods with no corresponding test
- Critical business logic paths untested
- Error/exception paths untested (only happy path covered)
- Edge cases untested (empty inputs, boundary values, null/undefined)
- API endpoints without integration tests
- Database operations without integration tests
- Critical user flows without E2E coverage

### Flawed Tests
- Tests that always pass regardless of implementation (no real assertions, or assertions on constants)
- Tests that test implementation details instead of behavior (brittle to refactoring)
- Tests with hardcoded timestamps, dates, or random values that will break
- Flaky test patterns: timing-dependent assertions, order-dependent tests, network-dependent tests
- Tests that mock the unit under test (testing the mock, not the code)

### Test Quality
- Missing or weak assertions (e.g., `toBeTruthy()` on an object — always true)
- Overly broad assertions that pass even when behavior is wrong
- Snapshot tests too large to meaningfully review
- Missing `describe` / `context` blocks for organization
- Unclear test names that don't describe the expected behavior
- Arrange-Act-Assert structure not followed

### Mock Quality
- Over-mocking: mocking everything including the unit under test
- Mocks that don't match real interfaces (interface drift)
- Missing mock cleanup between tests (shared mutable state)
- Manual mocks that are out of date with the real implementation

### Test Anti-Patterns
- Testing private methods directly (couple tests to implementation)
- Shared mutable state between tests (test interdependence)
- Tests that depend on execution order
- Setup/teardown doing too much (hiding test context)
- Ignoring or skipping tests without explanation

### Error Case Coverage
- API error responses not tested (4xx, 5xx scenarios)
- Network failure handling not tested
- Invalid input handling not tested
- Concurrent access scenarios not tested
- Timeout and retry logic not tested

**Output format per issue**:
```
FILE: path/to/file.ext (or "MISSING TEST FOR: path/to/source.ext:FUNCTION_NAME")
TYPE: Missing Coverage | Flawed Test | Quality | Mock Issue | Anti-Pattern
ISSUE: [description]
RECOMMENDATION: [specific test to add or fix to make, with code example]
```
