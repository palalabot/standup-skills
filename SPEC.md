# SPEC — jirasoft standup

Original idea (kept): *"a simple way to track tasks and report where you are and what you need to do."*

## Goal
Be ready for a standup in under a minute. Each day, answer three things:
1. **Yesterday** — what got done
2. **Today** — top priority items
3. **Blockers** — what's stuck, and what it depends on

## Sample data
`ticket-data/sprint-01/` is a generic login feature: APP-100 (epic), APP-101 (login API, blocked by an outside team), APP-102 (login page, blocked by APP-101, good Acceptance Criteria, phased `tasks.csv`) and APP-103 ("remember me", vague AC, a dependency stated only in its text). Nothing in the skills depends on this data. Swap in your own tickets in the same format.

## Approach: no app — skills + a small MCP
Not a web app. Two ways to use the same `ticket-data/` folder:

1. **With Claude (primary)**: Claude Code skills + a small **`standups-mcp`** server.
   - **Explicit dependency graph**: skills keep `blockedBy` in each ticket's frontmatter exact and consistent (no cycles, no missing IDs).
   - **Semantic relationships**: **graphify** runs over `ticket-data/` to find related tickets by meaning, output as an HTML graph view.
2. **Without Claude (alternative)**: `embedder/` — Hugging Face sentence-transformers (`all-MiniLM-L6-v2`) on a **RunPod serverless** endpoint. A script embeds the ticket files and answers similarity/search queries, so the folder stays searchable with no Claude account.

## Daily workflow
1. **Ingest (user, outside these skills)** — the user pulls tickets from Jira (their own Jira MCP / API script) into `ticket-data/<sprint>/<TICKET-ID>/ticket.md` in the ticket format (frontmatter + Summary / Context / Scope / Acceptance Criteria / Links).
2. **Check** — `/dep-graph` finds possible dependencies; `/analyze-ticket` flags the traps.
3. **Prep** — `/standup-prep` walks the user through each open ticket, asks its status, and writes today's journal.
4. **Tell** — the user writes Did / Doing / Blocked in `standup/<today>.md` (or answers `/standup`'s three questions); `/standup` validates it against `tasks.csv` and reconciles `tasks.csv`. The user's standup is the source of truth, since Jira exports can be stale.

## Meeting routines

### Morning standup (~5 min before the meeting)
| Step | Skill | Output |
|------|-------|--------|
| 1. Refresh tickets | user's own Jira ingest | Latest tickets in `ticket-data/` |
| 2. Spot what changed overnight | `/changes` | Tickets moved, new comments, new tickets, blockers resolved by others |
| 3. Check traps | `/analyze-ticket`, `/dep-graph` | New hidden dependencies, missing AC on tickets you'll start today |
| 4. Pick today's focus | `/priorities` | Top 3 unblocked tickets, with reason; P0s that are blocked |
| 5. Tell the story | user + `/standup` | User writes (or answers) Did / Doing / Blocked; `/standup` flags mismatches with `tasks.csv`, adds blocker age and what it holds up, updates approved rows |
| During the meeting | `/note` | Capture anything raised ("talk to X after", new blocker) |

### End-of-day status (~5 min)
| Step | Skill | Output |
|------|-------|--------|
| 1. Walk open tickets | `/eod` (uses `/standup-prep`) | Asks per ticket touched or planned today: done / progress / blocked (on what, who) / not touched (why) |
| 2. Update blockers | `/block`, `/dep-graph` | New/cleared blockers recorded with owner + since-date; what got unblocked |
| 3. Check story vs tickets | `/story-gaps` | Work logged on "todo" tickets, "doing" tickets with no note, status to push back to Jira |
| 4. Plan tomorrow | `/eod` | 1–3 items for tomorrow, saved to journal (tomorrow's standup is still the user's own) |
| 5. Status report | `/eod` | Short EOD summary: done today, in progress (%), blockers + asks, tomorrow's plan — ready to paste |
| 6. Sync back (optional) | `/jira-sync` | Proposes Jira status/comment updates; writes only after user confirms |

The EOD journal and `tasks.csv` are what the next morning's standup is checked against, not the standup itself; the user's own words win.

### Skills these routines add
| Skill | Status | Does |
|-------|--------|------|
| `/plan-tasks` | written | Ticket → `<TICKET-ID>/tasks.csv`, every AC covered, user approves |
| `/next-task` | to build | Next unblocked task across priority tickets |
| `/task-health` | to build | Coverage + stale/blocked task checks |
| `/changes` | to build | Diff ticket files vs previous ingest (git diff or stored snapshot) |
| `/priorities` | to build | Unblocked, not-done tickets by priority; flags blocked P0s |
| `/block` | to build | Record/clear a blocker: ticket, waiting on (ticket/person/team), since date |
| `/story-gaps` | to build | Journal vs ticket status mismatches |
| `/eod` | written | EOD walk-through, tomorrow plan, EOD summary |
| `/jira-sync` | to build | Push confirmed status/comments back to Jira (write access — confirm each) |

## Tasks per ticket (core)
Each ticket gets a task list the AI helps create and then follows day by day:
`ticket-data/<sprint>/<TICKET-ID>/tasks.csv`, next to `ticket.md`. The Jira ingest only writes `ticket.md`, never `tasks.csv`.

| Column | Meaning |
|--------|---------|
| `id` | `T1`, `T2`, … (stable, never renumbered) |
| `phase` | `understand` / `happy-path` / `test` / `build` (see SDLC below) |
| `task` | one concrete step, doable in ≤ 1 day |
| `status` | `todo` / `doing` / `blocked` / `done` / `dropped` |
| `ac` | which Acceptance Criteria it proves (`AC1;AC3`) — every AC must be covered by ≥ 1 task |
| `depends_on` | other task ids (`T1;T2`); blocked-by-ticket goes in `note` + ticket `blockedBy` |
| `updated` | last date status changed (`YYYY-MM-DD`) |
| `note` | short free text: what happened, what it's waiting on |

Example: `ticket-data/sprint-01/APP-102/tasks.csv`.

How the AI follows through:
- **`/plan-tasks <TICKET>`** — reads Scope + Acceptance Criteria, proposes the CSV (every AC covered, ordered by `depends_on`). User edits/approves before it's written. Ticket with no real AC → run `/analyze-ticket` first, don't invent tasks.
- **`/eod`** — per ticket touched today, asks status of its `doing` tasks and the next `todo`; updates `status` / `updated` / `note`.
- **`/standup`** — validates the user's Did / Doing / Blocked against task rows; with no file for today it asks the user item by item (did / plan / blockers), without reading task rows for hints, unless the user says they don't remember. Then it announces it will look for evidence in tickets, `tasks.csv`, the journal and the user's commits since the last working day, and has the user confirm each finding in their own words.
- **`/next-task`** — first `todo` task whose `depends_on` are all `done`, across today's priority tickets.
- **`/task-health`** — flags: AC with no task, tasks `doing` > 2 days, `blocked` with no reason, all tasks done but ticket not done (or the reverse), stale `updated`.

## SDLC per ticket (how tasks are ordered)
Every code ticket is planned and followed in four phases. `/plan-tasks` writes them, and `/standup` and `/eod` track them.

1. **Understand (debug the flow first).** Before writing code, trace the feature's workflow end to end (inputs → steps → outputs, including the failure branches) and map its **interdependent tickets**: what this ticket is blocked by, what it blocks, and what each one needs from the other (data shape, interface). Most "blocked" surprises come from skipping this.
2. **Happy path.** Build the main success flow end to end, the simplest version that works. Stub what other tickets haven't delivered yet, and record the stub in the task note.
3. **Tests (after the happy path).** Write unit tests from the **Acceptance Criteria**, one or more per criterion, including failure and edge cases. The happy-path tests pass, and the edge-case tests are expected to fail.
4. **Build against the tests.** Make the failing tests pass one at a time. Then swap the stubs for the real dependencies and run the integration test once the blocking tickets are done.

Why this order: the flow and its dependencies decide what "done" looks like. The happy path proves the shape works before you invest in it. The tests then turn every Acceptance Criterion into a pass/fail check, and that becomes the build to-do list. Standups can then report progress as "4/6 tests passing" instead of "still working on it".

Example: `ticket-data/sprint-01/APP-102/tasks.csv` (login page).

## Data (as-is, plain files)
```
ticket-data/
  <sprint-id>/
    <TICKET-ID>/
      ticket.md              # from Jira ingest; frontmatter: id, title, status, priority, blockedBy, link
      tasks.csv              # AI-planned task list (see above); never touched by ingest
    journal/<YYYY-MM-DD>.md  # free-form daily notes + bookmarks (links)
  archive/                   # closed sprints moved here
```
- `graphify-out/` (repo root) holds generated `graph.html` / `graph.json`; not hand-edited.
- Git is the backup/history; closing a sprint = move its folder to `archive/`.
- Notes are stored exactly as written, no DB. Vectors (embedder path only) are a generated cache, never the source of truth.

## `standups-mcp` tools (MVP)
| Tool | Does |
|------|------|
| `add_note(text, ticket?)` | append to today's journal (and the ticket file if given) |
| `upsert_ticket(id, fields)` | create/update a ticket's frontmatter |
| `list_tickets(status?, sprint?)` | tickets with status, priority, blockedBy |
| `blockers()` | tickets blocked by an unfinished ticket, plus the chain |
| `top_priorities(n=3)` | unblocked, not-done tickets sorted by priority |
| `standup(date?)` | Yesterday / Today / Blockers built from journal + ticket changes |
| `close_sprint()` | move current sprint to `archive/`, carry over unfinished tickets |

## Skills (in workflow order)
| Skill | Status | Does |
|-------|--------|------|
| `/dep-graph` | written | Possible dependencies: stated in text, Jira issue links, graphify (optional). User confirms each. |
| `/analyze-ticket` | written | Traps: missing/untestable AC, vague scope, no links. To add: external waits not recorded as blockers, status that contradicts the journal, P0 sitting blocked, blocker chains ending outside the team. |
| `/standup-prep` | to build | For each open ticket (blocked + P0 first): show title, last journal line, blockers → ask "status? done / doing / blocked (on what?) / not touched". Writes answers to `journal/<today>.md` and updates `status` / `blockedBy` after the user confirms. |
| `/standup` | written | Validates the user-written `standup/<today>.md` (system date) against `tasks.csv` / tickets; missing → asks did / plan / blockers item by item, saves answers verbatim. Proposes `tasks.csv` updates; flags Jira-behind; never edits `ticket.md`. |
| `/note` | later | Quick capture during the day. |
| `/sprint-close` | later | Summary + archive + carry-over. |

`standups-mcp` is optional — start with skills reading the files directly.

## Without-Claude path (`embedder/`)
- RunPod serverless worker: `embed(texts)` and `similarity(a, b)` (see `embedder/handler.py`, `embedder/Dockerfile`).
- Setup: build + push image, create endpoint (min 0 / max 1 workers, CPU if available), set `RUNPOD_API_KEY`.
- Missing: a small local client script that reads `ticket-data/`, embeds tickets, caches vectors, and runs search/"related tickets" queries.

## Out of scope (for now)
- Web UI, hosting, IP allowlists, Redis, multiple users, Jira sync.

## To analyze
- [x] **Ingest contract** (handled by the user's own tool): the ingest writes the agreed frontmatter (id, title, status, priority, blockedBy, link). Jira issue links (`blocks` / `is blocked by`) should land in `blockedBy`.
- [x] **Re-ingest merge** (handled by the user's own tool): the ingest does not wipe `blockedBy` / `related` confirmed via `/dep-graph`. Skills still ask when Jira status ≠ status given in `/standup-prep`.
- [ ] **Do we need the MCP at all?** Skills alone can read/write the Markdown files directly. The MCP only earns its place for exact logic (blocker chains, priority sorting, standup diff). Start with skills only?
- [ ] **MCP language**: Python (`mcp` SDK) or TypeScript; stdio transport, local only.
- [ ] **Ticket frontmatter**: exact fields; `priority` scale (P0–P3?); status set (todo/doing/blocked/done).
- [ ] **"Yesterday" detection**: from journal entries only, or also git diff of ticket files?
- [ ] **Data location**: `ticket-data/` inside this repo, or a separate private repo (notes may be sensitive)? gitignore `graphify-out/`?
- [ ] **Jira links**: plain URLs vs expand `ABC-123` from a configured base URL.
- [ ] **Graphify**: confirm real commands, that its HTML output works for this, run cost per rebuild, and whether to include `archive/` (cross-sprint links).
- [ ] **Semantic → explicit**: graphify/embedder suggestions never write `blockedBy` on their own; user confirms each one.
- [ ] **Embedder client**: language (Python), where vectors are cached (`ticket-data/.vectors.json`?), re-embed only changed files.
