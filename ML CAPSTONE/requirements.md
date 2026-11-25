# OpenCode Hackathon Toolkit --- Requirements

**Purpose:** Create a reusable, global OpenCode setup for rapid,
reliable hackathon development across full-stack, AI/ML, and
computer-vision projects.

## 1. Goals

The toolkit should help OpenCode: - Turn a hackathon brief into a clear,
feasible product and technical plan. - Build polished, responsive user
interfaces. - Implement reliable frontend, backend, database, and AI/ML
features. - Integrate APIs and authentication safely. - Test critical
workflows and verify results before claiming completion. - Coordinate
parallel work without conflicting changes. - Prepare projects for
deployment and demo day.

## 2. Installation principles

1.  Prefer skills that explicitly support OpenCode or the Agent Skills
    standard.
2.  Verify each repository, skill name, installation command, and
    license before installing.
3.  Do not assume a skill exists merely because it appears in this
    requirements document.
4.  Avoid duplicate or overlapping skills; choose one strong skill for
    each capability.
5.  Install generally useful skills globally only after checking their
    instructions and dependencies.
6.  Keep project-specific skills inside the relevant repository.
7.  Never install untrusted scripts or execute arbitrary commands
    without reviewing them.
8.  Do not overwrite existing OpenCode configuration, skills, agents, or
    MCP settings.
9.  Record what was installed, its source, version/commit if available,
    and any dependencies.
10. If a skill cannot be verified, mark it as **Not installed --- needs
    review** rather than substituting an unrelated package.

## 3. Required skill capabilities

### A. Product discovery and planning --- Essential

-   `brainstorming`
    -   Clarify the problem, target users, constraints, and value
        proposition.
    -   Compare feasible ideas and identify an MVP.
-   `writing-plans`
    -   Produce milestones, task breakdowns, dependencies, and
        acceptance criteria.

### B. Frontend and UI/UX --- Essential

-   `frontend-design`
    -   Create distinctive, responsive, production-quality interfaces.
    -   Avoid generic layouts and inconsistent visual styling.
-   `web-design-guidelines`
    -   Review usability, accessibility, responsive behavior, and design
        consistency.
-   `ui-ux-pro-max` (or an equivalent verified skill)
    -   Support design systems, typography, color palettes, spacing, and
        component patterns.
-   `shadcn-ui` (or an equivalent verified skill)
    -   Build reusable interfaces with accessible components.
-   `building-accessible-interfaces` (or equivalent)
    -   Check keyboard navigation, semantic structure, labels, and
        contrast.

### C. Engineering workflow --- Essential

-   `systematic-debugging`
    -   Reproduce issues, isolate root causes, and verify fixes.
-   `test-driven-development`
    -   Define tests and acceptance criteria before or alongside
        implementation.
-   `verification-before-completion`
    -   Run relevant tests, builds, and checks before reporting
        completion.
-   `code-review` / `requesting-code-review`
    -   Review correctness, maintainability, security, and regressions.

### D. Testing and quality --- High priority

-   `webapp-testing` / `testing-webapps` (choose one verified
    equivalent)
    -   Test core browser workflows, forms, navigation, and error
        states.
-   `investigating-performance` (or equivalent)
    -   Identify avoidable latency, rendering, and resource issues.
-   Include unit, integration, and end-to-end testing appropriate to the
    project.

### E. Parallel development --- High priority

-   `dispatching-parallel-agents`
-   `subagent-driven-development`

Use parallel agents only for independent tasks. Define file ownership,
shared interfaces, and integration checkpoints. Do not let multiple
agents edit the same files concurrently without coordination.

### F. Security --- Essential

-   `reviewing-security` (or equivalent verified skill)
    -   Review authentication, authorization, input validation, secrets,
        dependencies, and common web vulnerabilities.
-   Never commit API keys, passwords, tokens, private keys, or `.env`
    files.
-   Use environment variables and least-privilege credentials.
-   Do not disable security checks merely to make a demo work.

### G. Backend, data, and AI/ML --- Stack-dependent

Select skills or documented workflows for the technologies actually used
by the project:

-   Python engineering and environment management.
-   FastAPI or the selected backend framework.
-   PostgreSQL, SQLite, Firebase, or Supabase data modeling.
-   REST API design and third-party API integration.
-   LLM application engineering: prompting, structured outputs,
    embeddings, retrieval-augmented generation (RAG), and evaluation.
-   Computer vision: OpenCV, YOLO, image/video processing, and model
    evaluation.
-   Deployment: the chosen hosting platform, environment configuration,
    logs, and rollback.

These are capability requirements, not guaranteed exact skill IDs.
Verify a suitable source before installing anything.

### H. Git and delivery --- High priority

-   `git-workflow` (or equivalent)
    -   Use clear branches, focused commits, and safe merge practices.
-   Deployment workflow for the selected platform.
-   Prepare a reproducible README, setup instructions,
    environment-variable template, and demo checklist.

## 4. Suggested sources to inspect

These are discovery starting points, not blanket approval to install
every skill in each repository:

-   Superpowers: `obra/superpowers`
-   Anthropic skills: `anthropics/skills`
-   Vercel agent skills: `vercel-labs/agent-skills`
-   OpenCode-oriented skills: `osmontero/opencode-skills`
-   Skills directory: https://skills.sh/
-   OpenCode documentation: https://opencode.ai/docs/

Before installation, inspect the repository README and the exact skill
directory. Confirm the current installation syntax supported by the
installed `skills` CLI and OpenCode version.

## 5. Installation and compatibility requirements

-   Detect the operating system, shell, OpenCode version, and `skills`
    CLI version.
-   Determine whether global installation is supported and use the
    documented global flag.
-   Prefer OpenCode-specific installation targets where supported.
-   If the command syntax has changed, use current official
    documentation rather than guessing.
-   Install in small batches and verify after each batch.
-   Keep a backup of relevant configuration before any change.
-   Do not modify model/provider settings, API keys, MCP servers, or
    unrelated user configuration.
-   Do not install language runtimes or large dependencies unless the
    user approves.

## 6. OpenCode operating rules

When working on a hackathon project, OpenCode should:

1.  Read the project README, requirements, and existing code before
    changing files.
2.  Ask only for missing information that blocks progress.
3.  Start with a concise problem statement, user personas, MVP, and
    success criteria.
4.  Create an implementation plan with milestones and testable
    acceptance criteria.
5.  Inspect the existing stack and preserve working architecture unless
    a change is justified.
6.  Build the smallest complete end-to-end MVP before adding optional
    features.
7.  Use realistic loading, empty, success, and error states.
8.  Validate all user input and handle API failures.
9.  Keep secrets out of source control.
10. Run tests, linting, type checks, and production builds where
    applicable.
11. Verify the actual user journey, not just whether the application
    starts.
12. Document setup, architecture, APIs, environment variables, and
    deployment.
13. Report what was tested, what passed, what failed, and what remains
    incomplete.
14. Never claim a feature is complete or deployed unless it has been
    verified.

## 7. Acceptance criteria

The toolkit is ready when:

-   [ ] Every installed skill has a verified source and documented
    purpose.
-   [ ] No duplicate skill has been installed without a clear reason.
-   [ ] OpenCode can discover and use the installed skills.
-   [ ] Existing OpenCode configuration remains intact.
-   [ ] A sample project plan can be generated from a short hackathon
    brief.
-   [ ] A sample UI can be implemented and checked for responsive
    behavior.
-   [ ] A sample bug can be investigated and fixed using a reproducible
    process.
-   [ ] Tests/build checks are run and their results are reported
    accurately.
-   [ ] Security basics and secret-handling rules are documented.
-   [ ] A README and demo/deployment checklist can be generated.

## 8. Installation report format

Create `HACKATHON_TOOLKIT_INSTALL_REPORT.md` containing:

  ---------------------------------------------------------------------------------
  Skill/capability   Source         Scope            Status         Notes
  ------------------ -------------- ---------------- -------------- ---------------
  Skill name         Repository and Global/project   Installed /    Version,
                     path                            skipped /      dependencies,
                                                     needs review   reason

  ---------------------------------------------------------------------------------

Also list: - OpenCode and CLI versions detected. - Configuration files
inspected or changed. - Backups created. - Commands executed. -
Verification results. - Skills intentionally skipped and why.

## 9. Non-goals

-   Installing every available skill.
-   Replacing the user's preferred model or provider.
-   Changing billing, cloud resources, or API subscriptions.
-   Installing unverified tools or running opaque scripts.
-   Rewriting existing projects just to match a preferred template.
-   Claiming that a skill automatically provides a runtime, API, model,
    or external service.
