# OpenCode Global Hackathon Toolkit — Comprehensive Developer Guide

Welcome to your **Global OpenCode Hackathon Toolkit**. This guide explains how to leverage the installed skills and specialized agent profiles to rapidly design, build, test, secure, and ship high-impact hackathon projects using OpenCode.

---

## 1. Architectural Overview & Philosophy

Hackathons present a unique software engineering challenge: **extreme time constraints combined with high evaluation bars**. Teams fail when they:
1. Build unfeasible scopes that cannot be finished in 24–48 hours.
2. Produce generic, AI-templated UIs that fail visual scrutiny.
3. Waste hours debugging regressions caused by uncoordinated changes.
4. Experience broken demos due to unverified features or exposed secrets.

This toolkit solves these problems by structuring OpenCode around **8 specialized agent roles**, **52 verified capability skills**, and a **disciplined shared implementation plan (`PLAN.md`)**.

---

## 2. The 8 Specialized Autonomous Agents

The toolkit installs 8 purpose-built agent definitions into `~/.config/opencode/agents/`. Each agent is configured to inherit your primary model (`bharatcode/qwen-3.8-27b`) while applying a tailored persona, color code, and execution boundaries.

```
+--------------------------------------------------------------------------------+
|                             PRODUCT ARCHITECT                                  |
|               (Scoping, User Journeys, PLAN.md, Team Handoffs)                 |
+--------------------------------------------------------------------------------+
        |                                                                |
        v                                                                v
+--------------------------+                                  +--------------------------+
|      UI/UX ENGINEER      |                                  |     BACKEND ENGINEER     |
| (Design Tokens, WCAG AA) |                                  | (APIs, Schemas, Auth)    |
+--------------------------+                                  +--------------------------+
        |                                                                |
        v                                                                v
+--------------------------+                                  +--------------------------+
|    FRONTEND ENGINEER     |                                  |      AI/ML ENGINEER      |
| (Next.js, React, UI)     |                                  | (LLMs, RAG, PyTorch, CV) |
+--------------------------+                                  +--------------------------+
        \                                                                /
         \-------------------------------+------------------------------/
                                         |
                                         v
                      +-------------------------------------+
                      |             QA ENGINEER             |
                      |  (TDD, Systematic Debugging, E2E)   |
                      +-------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |          SECURITY ENGINEER          |
                      |   (Vulnerabilities, Secrets, OWASP) |
                      +-------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |           DEVOPS ENGINEER           |
                      |   (Deployment, Logs, Demo Checklist)|
                      +-------------------------------------+
```

### Agent Roster & Invocation

| Agent Name | OpenCode Agent ID | Mode | Primary Focus | How to Invoke |
|:---|:---|:---|:---|:---|
| **Product Architect** | `product-architect` | `all` | Idea validation, MVP scoping, and architecture roadmap | `opencode -a product-architect` or `"Use the product-architect agent to..."` |
| **UI/UX Engineer** | `ui-ux-engineer` | `subagent` | Design systems, aesthetics, Tailwind tokens, and accessibility | `"Use the ui-ux-engineer subagent to design..."` |
| **Frontend Engineer** | `frontend-engineer` | `subagent` | React 19, Next.js, shadcn/ui components, and client state | `"Use the frontend-engineer subagent to build..."` |
| **Backend Engineer** | `backend-engineer` | `subagent` | FastAPI / Express APIs, database modeling, and authentication | `"Use the backend-engineer subagent to implement..."` |
| **AI/ML Engineer** | `ai-ml-engineer` | `subagent` | LLM prompting, RAG pipelines, embeddings, and Python models | `"Use the ai-ml-engineer subagent to build the model..."` |
| **QA Engineer** | `qa-engineer` | `subagent` | Test-driven development, Playwright tests, and bug diagnosis | `"Use the qa-engineer subagent to test and debug..."` |
| **Security Engineer** | `security-engineer` | `subagent` | Vulnerability scanning, secret hygiene, and permission checks | `"Use the security-engineer subagent to audit..."` |
| **DevOps Engineer** | `devops-engineer` | `subagent` | Deployment to Vercel/cloud, Docker, and demo checklists | `"Use the devops-engineer subagent to prepare deployment..."` |

---

## 3. How to Invoke Skills in OpenCode

OpenCode v2 features native, on-demand skill loading. Skills are **not** dumped into the prompt upfront; instead, OpenCode advertises their IDs and descriptions, and loads the full instructions only when needed.

### Method 1: Natural Language Invocation
Simply describe what you want done. OpenCode's router matches the trigger descriptions:
```text
"Review this page for accessibility and keyboard navigation."
→ OpenCode loads `building-accessible-interfaces`
```

### Method 2: Explicit Mention (`@skill-id`)
You can force any skill to load in your prompt using the `@` syntax:
```text
"Please use @systematic-debugging to investigate this failing API test."
"Apply @frontend-design to restyle this dashboard with high-contrast slate aesthetics."
```

### Method 3: Subagent Skill Delegation
When launching a specialized subagent, prompt it to invoke matching domain skills:
```text
"Launch the frontend-engineer subagent to implement the user profile dialog using @shadcn-ui and @vercel-react-best-practices."
```

---

## 4. The 24-Hour Hackathon Playbook

Follow this battle-tested playbook during hackathon weekend:

### Phase 1: Hours 0–2 — Discovery, Scoping & Architecture
* **Goal**: Define a feasible, high-impact MVP and lock the project plan.
* **Commands / Workflow**:
  ```text
  opencode -a product-architect
  "Here is our hackathon challenge brief: [Paste prompt].
   1. Use @brainstorming to analyze 3 distinct angles and propose a killer MVP.
   2. Use @writing-plans to create a structured PLAN.md with milestones, technical stack, file ownership boundaries, and testable acceptance criteria."
  ```
* **Deliverable**: `PLAN.md` committed to the repository root.

### Phase 2: Hours 2–5 — Foundation & Backend Services
* **Goal**: Establish the repository structure, database schemas, and core backend endpoints.
* **Commands / Workflow**:
  ```text
  "Use the backend-engineer subagent to:
   1. Set up the FastAPI / database structure using @fastapi and @evolving-apis-and-schemas.
   2. Implement authentication and the core data models.
   3. Expose testable endpoints with mock seeds."
  ```

### Phase 3: Hours 5–9 — AI/ML Pipelines & Core Intelligence
* **Goal**: Implement the core LLM / ML differentiator.
* **Commands / Workflow**:
  ```text
  "Use the ai-ml-engineer subagent to:
   1. Build the RAG pipeline with vector embeddings and prompt templates using @claude-api.
   2. Ensure all LLM outputs follow strict Pydantic JSON schemas.
   3. Create a benchmark evaluation script to verify accuracy."
  ```

### Phase 4: Hours 9–15 — Frontend & UI/UX Design
* **Goal**: Build an intuitive, distinctive, and responsive user experience.
* **Commands / Workflow**:
  ```text
  "Use the ui-ux-engineer subagent to establish our design tokens, color palette, and layout rhythm using @frontend-design and @ui-styling."
  
  "Use the frontend-engineer subagent to:
   1. Assemble the interface with @shadcn-ui and @vercel-react-best-practices.
   2. Implement realistic loading skeletons, optimistic UI, and error boundaries.
   3. Verify keyboard navigation with @building-accessible-interfaces."
  ```

### Phase 5: Hours 15–19 — Testing & Bug Triage
* **Goal**: Ensure zero embarrassing crashes during the live demo.
* **Commands / Workflow**:
  ```text
  "Use the qa-engineer subagent to:
   1. Write end-to-end tests for the critical user flow using @webapp-testing.
   2. Use @systematic-debugging on any failing tests to find root causes before patching.
   3. Profile and eliminate slow rendering or query latency using @investigating-performance."
  ```

### Phase 6: Hours 19–21 — Security Audit & Secret Scrubbing
* **Goal**: Ensure no API keys, private credentials, or obvious OWASP flaws exist in the project.
* **Commands / Workflow**:
  ```text
  "Use the security-engineer subagent to perform an audit with @reviewing-security:
   1. Check all git history for leaked keys or .env secrets.
   2. Verify input validation on all external endpoints.
   3. Ensure CORS and authentication middleware are locked down."
  ```

### Phase 7: Hours 21–24 — Deployment, Polish & Demo Checklist
* **Goal**: Deploy to a live public URL and prepare the submission package.
* **Commands / Workflow**:
  ```text
  "Use the devops-engineer subagent to:
   1. Verify production build output with @verifying-before-completion.
   2. Deploy to Vercel using @deploy-to-vercel.
   3. Generate a demo-day README.md, environment variable template (.env.example), and 3-minute pitch walkthrough checklist."
  ```

---

## 5. Parallel Development & Worktrees Protocol

When multiple subagents or team members work in parallel, follow the **Worktree Isolation Protocol**:
1. **Never edit overlapping files concurrently**: Ensure `PLAN.md` clearly assigns directory ownership (e.g. `src/frontend` vs `src/api`).
2. **Use Git Worktrees for Isolated Features**:
   ```text
   "Use @using-git-worktrees to branch into an isolated worktree for the AI pipeline implementation."
   ```
3. **Merge Cleanly**:
   ```text
   "Use @finishing-a-development-branch to run test checks, squash commits, and merge the feature branch."
   ```

---

## 6. Troubleshooting & Diagnostics

| Issue | Root Cause | Solution |
|:---|:---|:---|
| **Skill not loading automatically** | Prompt lacked triggering keywords | Explicitly mention `@<skill-id>` in your prompt, or check if the skill has a valid `description:` in its `SKILL.md`. |
| **Agent not discovered by OpenCode** | Agent Markdown file missing or in wrong path | Verify agent file exists in `~/.config/opencode/agents/<name>.md` and run `opencode reload`. |
| **Configuration syntax error** | Damaged JSON in `opencode.json` | Restore from the automatic backup: `cp ~/.config/opencode.backup.*/opencode.json ~/.config/opencode/opencode.json` and reload. |
| **Worktree lock or collision** | Uncommitted changes in working tree | Commit or stash changes before running `@using-git-worktrees`. |
| **Model provider timeout** | Remote API gateway latency | Your configured model is `bharatcode/qwen-3.8-27b`. Verify connectivity to `https://bharatcode.ai/api/model/v1` and ensure `~/.config/opencode/bharatcode-key.txt` contains your valid API key. |
