---
name: standup
description: Write the morning standup update (Did / Doing / Blocked) from the journal, tasks.csv files and tickets in ticket-data/. Use for "/standup", "write my standup", "what do I say at standup", "prep my standup".
---

# /standup

Write a short update the user can paste into chat or read out loud. Read-only — changes no files.
Plain words; the user may not be technical.

## 1. Gather
- Current sprint = newest folder in `ticket-data/` by name (ignore `archive/`).
- **Journal**: `journal/<date>.md`. Use the most recent entry **before today** (last working day, may be a Friday) as "last time", and today's file if it exists.
- **Tasks**: every `<TICKET-ID>/tasks.csv`. Columns: `id,phase,task,status,ac,depends_on,updated,note`.
- **Tickets**: every `<TICKET-ID>/ticket.md` frontmatter: `status`, `priority`, `blockedBy`, `title`.
- If there is no journal and no task changes since last time: say so, and suggest running `/eod` tonight so tomorrow's standup writes itself. Then build from ticket statuses only.

## 2. Build the three parts
**Did** — finished since last time:
- Task rows with `status: done` and `updated` = last journal date or later.
- Journal lines from last time that say something was finished.
- Tickets that moved to done.

**Doing** — today's plan:
- The `## Tomorrow` list from last time's journal, if there is one (that's what the user planned).
- Otherwise: tasks with `status: doing`, then the next `todo` task whose `depends_on` are all `done`, on the highest-priority tickets (P0 first). At most 3 items.

**Blocked** — what's stuck:
- Task rows with `status: blocked`, and tickets whose `blockedBy` includes a ticket that isn't done.
- For each: what it's waiting on (from `note`, the journal, or `blockedBy`), **how many days** (from `updated` or the first journal mention), and **what else it holds up** (tickets whose `blockedBy` chain includes it).
- Nothing blocked → write "Nothing blocked."

Every line names its ticket ID. One line per item; merge items on the same ticket.
Don't invent progress — only use what's in the files.

## 3. Output
```
**Did**
- APP-101: password hashing done and tested.

**Doing**
- APP-102: login form working against a fake API (T3).

**Blocked**
- APP-101: waiting on the Ops team for the users database (2 days). Holds up APP-102 and APP-103.
```
Then, only if they apply, up to 3 short **heads-ups** under the update (not part of what to paste):
- A blocker 2+ days old → "Raise this in standup and name who you need."
- A P0 ticket that's blocked.
- A task `doing` for 3+ days → maybe split it.
- `build` or `test` work started while `understand` tasks are not done → the flow or its dependencies may not be clear yet.
- All `test` tasks done but `build` tests still failing for 2+ days → raise it.
- Work in the journal on a ticket still marked `todo`.
