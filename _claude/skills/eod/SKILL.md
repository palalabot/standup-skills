---
name: eod
description: End-of-day check-in. Walks the user through today's tickets and tasks, records done / progress / blocked in tasks.csv and the journal, plans tomorrow, and writes a short end-of-day summary. Use for "/eod", "end of day", "EOD status", "wrap up my day".
---

# /eod

A short guided check-in, about 5 minutes. Ask simple questions one ticket at a time; the user may not be technical.
Tomorrow's standup is still written or answered by the user. `/standup` checks it against what gets saved tonight.

## 1. Gather
- Current sprint = newest folder in `ticket-data/` by name (ignore `archive/`).
- Tickets to ask about, in this order:
  1. Blocked tickets/tasks, and P0s.
  2. Tickets with a `doing` task, or named in today's journal, or in last time's `## Tomorrow` list.
  3. Nothing found → ask "Which ticket did you work on today?" and list the open ones.
- Read each ticket's `tasks.csv` (header `id,phase,task,status,ac,depends_on,updated,note`). Ticket with no tasks → offer `/plan-tasks <ID>` after the check-in, but still ask about it.

## 2. Ask, one ticket at a time
Show: ticket ID + title, its `doing` tasks and the next `todo` task. Ask:

> **APP-102 — Login page**
> T3 "Login form with a fake API" is in progress. How did it go today?
> 1. Done  2. Still working on it  3. Blocked  4. Didn't touch it

Follow-ups, short:
- **Done** → "Anything else finished on this ticket?" and offer the next task.
- **Still working** → "What did you get done? (one line)". For a `test` or `build` task, also ask: "How many tests pass now?" and save that in `note` (e.g. `4/6 tests passing`).
- **Blocked** → "What are you waiting on, and who can unblock it?"
- **Didn't touch** → "Why? (skip if you like)" — no pressure, keep moving.
- Anything else they mention (a new step, a link) → note it.

## 3. Plan tomorrow
Suggest 1–3 items: blocked work first if it can now move, then the next unblocked `todo` tasks on the highest-priority tickets. Ask the user to confirm or change them.

## 4. Show what will be saved, then save
Show a short summary of the changes and ask "Save this?". On yes:

**tasks.csv** (per ticket): update only the rows that changed — `status`, `updated` = today, `note` = their one line. New steps they mentioned → new row with the next id, `status: todo`. Never renumber or delete rows (use `dropped`). Keep the header and all other rows unchanged.

**ticket.md**: only if the user says the whole ticket is done or a new ticket blocks it, ask before changing `status` or `blockedBy`. Change nothing else.

**journal/<today>.md** — create or append, in this format:
```
# 2026-01-14
- APP-102 T3: login form works against the fake API.
- APP-101: still waiting on Ops for the users database.

## Blocked
- APP-101: waiting on the users database (Ops team lead).

## Tomorrow
- APP-102 T4: write the unit tests.
- APP-101: follow up with Ops.
```
Keep any lines already in today's file.

## 5. End-of-day summary
Write a short summary the user can paste into an EOD channel:
```
**Done today:** APP-102 T3 login form working against a fake API.
**In progress:** APP-102 (2 of 8 steps done).
**Blocked / need help:** APP-101, the users database from Ops (3 days).
**Tomorrow:** APP-102 unit tests; chase Ops about APP-101.
```
"In progress" counts `done` vs total tasks (ignore `dropped`). Use only what the user said and what's in the files.
