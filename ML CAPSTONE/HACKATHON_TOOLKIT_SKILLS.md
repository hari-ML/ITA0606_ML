# OpenCode Global Hackathon Toolkit — Master Skills Catalog

This document is the complete reference catalog of all **52 verified skills** available globally in OpenCode across your development environment.

---

## Quick Navigation Index

1. [Product Planning & Brainstorming](#1-product-planning--brainstorming)
2. [Frontend & UI/UX Design](#2-frontend--uiux-design)
3. [Backend & API Engineering](#3-backend--api-engineering)
4. [AI/ML & LLM Engineering](#4-aiml--llm-engineering)
5. [Database & Data Modeling](#5-database--data-modeling)
6. [Testing & Quality Assurance](#6-testing--quality-assurance)
7. [Security & Code Review](#7-security--code-review)
8. [Git, Worktrees & Collaboration](#8-git-worktrees--collaboration)
9. [Parallel Agents & Subagent Execution](#9-parallel-agents--subagent-execution)
10. [Deployment, Verification & Presentation](#10-deployment-verification--presentation)

---

## 1. Product Planning & Brainstorming

### `brainstorming`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "brainstorm", "explore ideas", "what should we build", "feature concept", "MVP ideation"
* **Use Case**: Run this before writing a line of code. It forces a rigorous analysis of user needs, technical constraints, competing angles, and selects a realistic MVP scope.
* **Core Rule**: Never start coding without establishing user persona, core job-to-be-done, and minimum viable surface area.

### `writing-plans`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "plan", "roadmap", "milestones", "breakdown", "implementation spec"
* **Use Case**: Takes a validated idea and outputs `PLAN.md`. Creates concrete milestones, task dependencies, non-overlapping file ownership, and testable acceptance criteria.
* **Core Rule**: Every task must have a binary testable definition of done before handoff to an implementer.

### `hackathon-brief-design`
* **Source**: `samber/dev-event-organizer-skills`
* **Trigger Keywords**: "hackathon prompt", "interpret brief", "competition rules", "event theme"
* **Use Case**: Decomposes hackathon problem statements, prize categories, and sponsor track requirements into high-scoring technical objectives.

### `hackathon-judging`
* **Source**: `samber/dev-event-organizer-skills`
* **Trigger Keywords**: "judging criteria", "rubric", "how will this be graded", "judge perspective"
* **Use Case**: Audits your project proposal against standard hackathon rubrics: Innovation, Technical Complexity, Execution & Polish, and Business / Social Impact.

---

## 2. Frontend & UI/UX Design

### `frontend-design`
* **Source**: `anthropics/skills`
* **Trigger Keywords**: "design system", "UI layout", "styling", "make this look professional", "anti-slop"
* **Use Case**: Leads visual identity design. Selects intentional typography, disciplined color palettes, and avoids generic AI tells (e.g. warm cream backgrounds with terracotta accents or identical rounded SaaS cards).
* **Core Rule**: Spend boldness in one memorable place; keep everything around it disciplined and functional.

### `web-design-guidelines`
* **Source**: `vercel-labs/agent-skills`
* **Trigger Keywords**: "check UI", "design audit", "Web Interface Guidelines", "UX compliance"
* **Use Case**: Enforces official Web Interface Guidelines on padding, button sizing, responsive breakpoints, typography hierarchies, and mobile touch targets.

### `ui-styling` (UI-UX Pro Max)
* **Source**: `nextlevelbuilder/ui-ux-pro-max-skill`
* **Trigger Keywords**: "modern styling", "CSS variables", "Tailwind theme", "dark mode tokens"
* **Use Case**: Generates full design token systems, harmonious CSS custom properties, and Tailwind configurations tailored to modern web aesthetics.

### `shadcn-ui`
* **Source**: `google-labs-code/stitch-skills`
* **Trigger Keywords**: "shadcn", "Radix UI", "accessible components", "dialog", "dropdown", "data table"
* **Use Case**: Direct code generation of accessible, composable UI components using Tailwind CSS and Radix primitives without heavy external component libraries.

### `building-accessible-interfaces`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "accessibility", "a11y", "WCAG", "keyboard navigation", "screen reader", "ARIA"
* **Use Case**: Audits markup for semantic HTML, focus traps, aria-expanded states, proper contrast ratios, and complete keyboard accessibility.

### `reviewing-interface-quality`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "UI critique", "why does this look cheap", "does this feel AI-generated", "UI polish"
* **Use Case**: Final visual gate before demo day. Identifies misaligned grids, awkward whitespace, jarring layout shifts, and inconsistent fonts.

### `vercel-react-best-practices`
* **Source**: `vercel-labs/agent-skills`
* **Trigger Keywords**: "React performance", "Next.js optimization", "Server Components", "bundle size"
* **Use Case**: Eliminates unnecessary re-renders, leverages React 19 primitives, optimizes image loading, and ensures optimal data-fetching boundaries.

### `web-artifacts-builder`
* **Source**: `anthropics/skills`
* **Trigger Keywords**: "standalone widget", "HTML artifact", "interactive canvas", "SVG demo"
* **Use Case**: Builds isolated, interactive single-file client demonstrations suitable for embeds or instant live previews.

---

## 3. Backend & API Engineering

### `fastapi`
* **Source**: `fastapi/fastapi`
* **Trigger Keywords**: "FastAPI", "Python backend", "REST API", "Pydantic", "OpenAPI docs"
* **Use Case**: Architecting asynchronous Python backends with automatic OpenAPI documentation, dependency injection, and strict request/response data validation.
* **Core Rule**: Always use Pydantic models for request bodies and response models to ensure type safety and schema generation.

### `evolving-apis-and-schemas`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "API migration", "breaking change", "schema evolution", "backward compatibility"
* **Use Case**: Designing API versions and database schema alterations so existing clients and persistent data are not broken by rapid hackathon iterations.

---

## 4. AI/ML & LLM Engineering

### `building-finetuning-datasets`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "fine-tuning", "dataset preparation", "LoRA", "synthetic data", "evaluation benchmark"
* **Use Case**: Creating structured JSONL instruction-tuning and preference datasets, filtering low-quality examples, and designing rigorous evaluation sets.

### `claude-api`
* **Source**: `anthropics/skills`
* **Trigger Keywords**: "prompt engineering", "tool use", "function calling", "structured JSON output"
* **Use Case**: Crafting high-accuracy system prompts, multi-turn reasoning loops, and structured output parsing across any modern LLM provider.

### `mcp-builder`
* **Source**: `anthropics/skills`
* **Trigger Keywords**: "Model Context Protocol", "MCP server", "LLM tools", "external tool integration"
* **Use Case**: Creating custom MCP servers to give LLMs direct access to specialized APIs, databases, local filesystems, or hardware devices.

---

## 5. Database & Data Modeling

### `evolving-apis-and-schemas`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "database schema", "migrations", "PostgreSQL", "SQLite", "foreign keys"
* **Use Case**: Enforces relational data integrity, index strategies on queried foreign keys, and migration scripts.

### `prisma-client-api`
* **Source**: `prisma/skills`
* **Trigger Keywords**: "Prisma", "PrismaClient", "findMany", "upsert", "$transaction", "ORM"
* **Use Case**: Complete guide to TypeScript database querying, relations, interactive transactions, and query optimization using Prisma.

---

## 6. Testing & Quality Assurance

### `systematic-debugging`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "bug", "failing test", "error", "exception", "unexpected behavior"
* **Use Case**: Prohibits speculative "guess-and-check" bug fixing. Enforces scientific root-cause isolation: formulate hypothesis -> reproduce with minimal test -> confirm cause -> patch -> verify regression-free.
* **Core Rule**: Never modify application code to fix a bug without first creating a reproduction case that demonstrates the failure.

### `test-driven-development`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "write tests first", "TDD", "unit test", "integration test", "Pytest", "Jest"
* **Use Case**: Guides implementation via red-green-refactor cycles. Ensures all edge cases and expected behaviors are codified as executable tests.

### `webapp-testing`
* **Source**: `anthropics/skills`
* **Trigger Keywords**: "browser test", "Playwright", "test web app", "E2E test", "click button test"
* **Use Case**: Writing and executing headless Playwright scripts in Python/Node to verify critical user paths, form submissions, and authentication sessions.

### `investigating-performance`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "too slow", "latency", "memory leak", "CPU spike", "database bottleneck"
* **Use Case**: Profiling applications under load to locate avoidable database queries (N+1 issues), heavy loops, unindexed searches, or bloated JavaScript bundles.

---

## 7. Security & Code Review

### `reviewing-security`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "security audit", "vulnerability scan", "is this safe", "check secrets", "OWASP"
* **Use Case**: Auditing code before committing or shipping. Checks for hardcoded secrets, SQL injection, XSS vectors, unauthenticated routes, and insecure CORS headers.
* **Core Rule**: Never commit `.env` files or API keys. Never disable security checks or encryption merely to bypass demo friction.

### `requesting-code-review`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "review my changes", "pre-merge check", "PR review", "code quality check"
* **Use Case**: Pre-merge verification checklist. Compares the pull request against the task acceptance criteria and identifies unintended regressions.

### `receiving-code-review`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "review comments", "feedback on PR", "handle reviewer notes"
* **Use Case**: Structured approach to handling review feedback: verify suggestions technically before applying them, avoiding performative agreement that breaks working code.

---

## 8. Git, Worktrees & Collaboration

### `using-git-worktrees`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "git worktree", "isolate workspace", "branch isolation", "parallel branches"
* **Use Case**: Uses native OpenCode v2 worktree tools to spawn clean, isolated working copies so parallel agents or subagents can develop features without file collisions.

### `finishing-a-development-branch`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "merge branch", "finish feature", "squash commit", "prepare PR"
* **Use Case**: Runs final test suites, cleans up intermediate commits, updates the changelog, and creates clean merge commits back to the main branch.

---

## 9. Parallel Agents & Subagent Execution

### `dispatching-parallel-agents`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "parallel subagents", "independent tasks", "concurrent execution"
* **Use Case**: Identifies completely independent tasks (e.g. backend API and standalone UI components) and dispatches child subagents with strict file ownership boundaries.

### `subagent-driven-development`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "subagent plan execution", "execute with subagents", "delegated tasks"
* **Use Case**: Orchestrates an entire multi-step project plan by delegating milestone tasks to specialized child sessions and reviewing outputs upon completion.

---

## 10. Deployment, Verification & Presentation

### `verifying-before-completion`
* **Source**: `osmontero/opencode-skills`
* **Trigger Keywords**: "ready to ship", "done", "confirm working", "task complete"
* **Use Case**: **Evidence before assertions**. Prohibits marking a task complete until live tests, builds, and verification commands have been executed and their successful exit codes verified.

### `deploy-to-vercel`
* **Source**: `vercel-labs/agent-skills`
* **Trigger Keywords**: "deploy to Vercel", "push live", "preview deployment", "publish site"
* **Use Case**: Automating Vercel CLI deployment, configuring environment secrets, and retrieving live HTTPS URLs for hackathon submissions.

---

## Additional Productivity Skills Pre-Installed in Global Environment
* `find-skills`: Interactive skill directory explorer (`vercel-labs/skills`)
* `skill-creator`: Creating new standardized OpenCode skills (`anthropics/skills`)
* `reverse-engineer-anything`: Static and binary disassembly suite
* `docx`, `pdf`, `pptx`, `xlsx`: Native programmatic document manipulation (`anthropics/skills`)
* `internal-comms`: Drafting status reports, release notes, and team handoffs (`anthropics/skills`)
