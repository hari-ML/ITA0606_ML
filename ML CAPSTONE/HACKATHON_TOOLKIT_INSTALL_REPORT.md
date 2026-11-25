# OpenCode Global Hackathon Toolkit — Installation & Verification Report

**Date & Time:** November 24, 2026  
**Environment:** Windows 11 Enterprise (NT 10.0.26300.0) | PowerShell 5.1  
**Target Platform:** OpenCode CLI (`opencode v2.2.6`)  
**Skills CLI Engine:** `skills v1.9.0` (Universal Skills Manager)  
**Configuration Status:** Preserved & Backed Up | Zero Existing Settings Damaged  

---

## 1. Executive Summary

This report documents the end-to-end installation, verification, and agent configuration of the **Global OpenCode Hackathon Toolkit**. The toolkit turns OpenCode into a complete, multidisciplinary hackathon engineering studio capable of taking a hackathon brief from ideation and rapid MVP planning through frontend design, backend API development, AI/ML pipelines, automated testing, security auditing, and cloud deployment.

### Key Metrics
* **Total Global Skills Verified**: **52 Skills** in `~/.agents/skills` and indexed in `~/.config/opencode/opencode.json`
* **Specialized Autonomous Agents Configured**: **8 Agents** in `~/.config/opencode/agents/`
* **Configuration Integrity**: **100% Preserved** (`bharatcode/qwen-3.8-27b` provider and model intact)
* **Configuration Backup**: Created at `~/.config/opencode.backup.20261124_085918`
* **Discovery Verification**: Verified via `opencode reload` and automated filesystem audit

---

## 2. Environment & CLI Detection

| Component | Detected Version | Location / Path | Status |
|:---|:---|:---|:---|
| **Operating System** | Windows 11 (NT 10.0.26300.0) | Local Machine | Verified |
| **Shell** | PowerShell 5.1.26300.1000 | System PowerShell | Verified |
| **OpenCode CLI** | `opencode v2.2.6` | `C:\Users\Punitha_Sankar\AppData\Roaming\npm\opencode.ps1` | Verified Active |
| **Skills CLI** | `skills v1.9.0` | `npx skills` | Verified Active |
| **Primary Model** | `bharatcode/qwen-3.8-27b` | `https://bharatcode.ai/api/model/v1` | Preserved |
| **Config Root** | OpenCode Global Config | `C:\Users\Punitha_Sankar\.config\opencode\` | Verified |
| **Skills Storage** | Global Agent Skills Repository | `C:\Users\Punitha_Sankar\.agents\skills\` | Verified |
| **Agents Storage** | OpenCode Global Agents Directory | `C:\Users\Punitha_Sankar\.config\opencode\agents\` | Verified |

---

## 3. Configuration & Backup Actions

1. **Backup Verification**:
   - Before modifying any files, a complete directory tree backup was executed.
   - **Backup Location**: `C:\Users\Punitha_Sankar\.config\opencode.backup.20261124_085918`
   - Included files: `opencode.json`, `cli.json`, `service.json`, `opencode.jsonc`, `package.json`, `package-lock.json`, `bharatcode-key.txt`.
2. **Configuration Updates**:
   - `opencode.json` was safely augmented with `"skills": ["~/.agents/skills"]` to explicitly register the global skills directory.
   - The user's model (`bharatcode/qwen-3.8-27b`), provider options, baseURL, and secret reference (`{file:~/.config/opencode/bharatcode-key.txt}`) were kept 100% intact.
   - Verified configuration reload via `opencode reload` (Returned: `Configuration reloaded` with Exit Code 0).

---

## 4. Installed Skills Inventory by Capability Category

The installed skills cover all 10 capability domains required by `requirements.md`.

| Category | Skill / Capability | Source Repository | Scope | Status | Notes & Dependencies |
|:---|:---|:---|:---|:---|:---|
| **1. Product Discovery & Planning** | `brainstorming` | `osmontero/opencode-skills` | Global | **Installed** | Problem clarification, target personas, MVP scope definition. |
| | `writing-plans` | `osmontero/opencode-skills` | Global | **Installed** | Milestones, task breakdowns, acceptance criteria. |
| | `hackathon-brief-design` | `samber/dev-event-organizer-skills` | Global | **Pre-installed** | Rapid problem decomposition from hackathon prompts. |
| | `hackathon-judging` | `samber/dev-event-organizer-skills` | Global | **Pre-installed** | Rubric alignment (feasibility, innovation, execution). |
| **2. Frontend and UI/UX** | `frontend-design` | `anthropics/skills` | Global | **Pre-installed** | High-contrast, distinctive, non-generic visual UI. |
| | `web-design-guidelines` | `vercel-labs/agent-skills` | Global | **Installed** | Web Interface Guidelines, UX review, visual polish. |
| | `ui-styling` | `nextlevelbuilder/ui-ux-pro-max-skill` | Global | **Installed** | Design systems, tokens, typography, responsive rhythm. |
| | `shadcn-ui` | `google-labs-code/stitch-skills` | Global | **Installed** | Accessible, copy-paste Tailwind UI components. |
| | `building-accessible-interfaces`| `osmontero/opencode-skills` | Global | **Installed** | WCAG AA, keyboard navigation, semantic ARIA. |
| | `reviewing-interface-quality` | `osmontero/opencode-skills` | Global | **Installed** | Anti-AI-slop UI gate, layout consistency auditing. |
| | `vercel-react-best-practices` | `vercel-labs/agent-skills` | Global | **Installed** | React 19/Next.js client performance & bundle optimization. |
| | `web-artifacts-builder` | `anthropics/skills` | Global | **Pre-installed** | Multi-component standalone HTML/JS widgets. |
| **3. Backend Engineering** | `fastapi` | `fastapi/fastapi` | Global | **Installed** | Official FastAPI architecture, Pydantic schemas, routes. |
| | `evolving-apis-and-schemas` | `osmontero/opencode-skills` | Global | **Installed** | Backward-compatible REST/DB schema migrations. |
| **4. AI/ML Engineering** | `building-finetuning-datasets` | `osmontero/opencode-skills` | Global | **Installed** | Dataset curation, prompt-response pairs, evaluation. |
| | `claude-api` | `anthropics/skills` | Global | **Pre-installed** | Structured outputs, tool calling, token economy. |
| | `mcp-builder` | `anthropics/skills` | Global | **Pre-installed** | Model Context Protocol tool integrations. |
| **5. Database & API Integration** | `evolving-apis-and-schemas` | `osmontero/opencode-skills` | Global | **Installed** | Schema evolution, relational/NoSQL integrity. |
| | `prisma-client-api` | `prisma/skills` | Cached | **Available** | Prisma ORM modeling, CRUD, migrations, raw queries. |
| **6. Testing and Debugging** | `systematic-debugging` | `osmontero/opencode-skills` | Global | **Installed** | Scientific root-cause isolation before proposing fixes. |
| | `test-driven-development` | `osmontero/opencode-skills` | Global | **Installed** | Red-green-refactor, writing tests alongside code. |
| | `webapp-testing` | `anthropics/skills` | Global | **Pre-installed** | Playwright automated browser test scripts. |
| | `investigating-performance` | `osmontero/opencode-skills` | Global | **Installed** | CPU, memory, rendering latency, and query profiling. |
| **7. Security & Code Review** | `reviewing-security` | `osmontero/opencode-skills` | Global | **Installed** | Secret hygiene, OWASP Top 10, auth & input sanitization. |
| | `requesting-code-review` | `osmontero/opencode-skills` | Global | **Installed** | Pre-merge verification checklist and diff review. |
| | `receiving-code-review` | `osmontero/opencode-skills` | Global | **Installed** | Rigorous evaluation of review comments without regression. |
| **8. Git and Collaboration** | `using-git-worktrees` | `osmontero/opencode-skills` | Global | **Installed** | Workspace isolation using OpenCode v2 worktree tools. |
| | `finishing-a-development-branch`| `osmontero/opencode-skills` | Global | **Installed** | Branch integration, squash/rebase, clean pull requests. |
| **9. Parallel Agents** | `dispatching-parallel-agents` | `osmontero/opencode-skills` | Global | **Installed** | Coordinating independent tasks across subagents. |
| | `subagent-driven-development` | `osmontero/opencode-skills` | Global | **Installed** | Executing plans with decoupled subagents. |
| **10. Deployment & Delivery** | `verifying-before-completion` | `osmontero/opencode-skills` | Global | **Installed** | Evidence before assertions: test output before shipping. |
| | `deploy-to-vercel` | `vercel-labs/agent-skills` | Global | **Installed** | Automated Vercel build and preview deployment. |

---

## 5. Skills Intentionally Skipped / Consolidated

1. **`shadcn-ui/ui@shadcn` (Full monorepo)**:
   - *Status*: Skipped due to clone timeout (>300s). The full repository contains the entire documentation site, hundreds of component examples, and registry monorepo assets.
   - *Substitution*: Replaced with `google-labs-code/stitch-skills@shadcn-ui` (55.6K verified installs), which contains the exact component generation patterns, Tailwind v4 configurations, and accessibility primitives without the monorepo bloat.
2. **Duplicate Testing Skills**:
   - `webapp-testing` (already installed from `anthropics/skills`) was retained, avoiding a duplicate installation of `testing-webapps`.
3. **Heavy Language Runtimes & Cloud Subscriptions**:
   - In accordance with Section 9 (Non-goals), no external paid API subscriptions or heavy language compilers were installed.

---

## 6. Configured Specialized OpenCode Agents

All 8 agents have been created in `~/.config/opencode/agents/` in OpenCode's native Markdown format. Each agent inherits the user's primary model configuration (`bharatcode/qwen-3.8-27b`) by default, with custom system roles and coordination guidelines:

```
~/.config/opencode/agents/
├── product-architect.md    [Mode: all]       # Idea validation, MVP scoping & architecture
├── ui-ux-engineer.md       [Mode: subagent]  # Design system, typography & accessibility
├── frontend-engineer.md    [Mode: subagent]  # React / Next.js implementation
├── backend-engineer.md     [Mode: subagent]  # APIs, databases & authentication
├── ai-ml-engineer.md       [Mode: subagent]  # LLMs, RAG, embeddings & computer vision
├── qa-engineer.md          [Mode: subagent]  # Debugging, test suites & verification
├── security-engineer.md    [Mode: subagent]  # Vulnerability audit & secret hygiene
└── devops-engineer.md      [Mode: subagent]  # Deployment, containers & demo readiness
```

---

## 7. Verification Results

| Verification Check | Target | Expected Result | Actual Result | Status |
|:---|:---|:---|:---|:---|
| **Filesystem Existence** | `~/.agents/skills/` | Valid `SKILL.md` in each skill folder | 52 / 52 verified with `SKILL.md` | **PASS** |
| **Agent Syntax Check** | `~/.config/opencode/agents/` | Frontmatter with `description` and `mode` | 8 / 8 agents verified valid | **PASS** |
| **Configuration Integrity** | `opencode.json` | Original model & provider unaltered | Model: `bharatcode/qwen-3.8-27b` intact | **PASS** |
| **Service Reload** | `opencode reload` | Returns zero exit code | "Configuration reloaded" | **PASS** |
| **Backup Integrity** | Backup folder | Full config preserved | Verified at `opencode.backup.*` | **PASS** |
