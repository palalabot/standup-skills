---
name: plan-tasks
description: Break one ticket into small daily steps and save them as tasks.csv in the ticket's folder, with every Acceptance Criterion covered. Use for "/plan-tasks APP-102", "break this ticket down", "plan tasks for a ticket".
---

# /plan-tasks <TICKET-ID>

Turn a ticket into a short list of steps the user can do and Claude can follow day by day.
Written for users who may not be technical: plain words, no jargon in what you show them.

## 1. Find the ticket
- Current sprint = the newest folder in `ticket-data/` by name (ignore `archive/`). Ticket = `ticket-data/<sprint>/<TICKET-ID>/ticket.md`.
- No ID given → list the sprint's tickets that have an empty or missing `tasks.csv` and ask which one.
- Ticket not found → say so and list the IDs that exist.

## 2. Check it's plannable
- Read **Scope & Requirements** and **Acceptance Criteria (AC)**. Number the AC items `AC1`, `AC2`, … in the order they appear.
- If AC is missing or only vague ("works as expected", "TBD"): stop. Tell the user the ticket doesn't say how to know it's done, suggest `/analyze-ticket <ID>`, and offer to plan anyway with tasks marked `<to confirm>`. Never invent thresholds or numbers.
- If `tasks.csv` already has rows: don't replace it. Show it and offer to **add** missing tasks only (go to step 3 for the gaps). Existing ids and statuses stay as they are.

## 3. Draft the tasks in four phases
Plan in this order (the `phase` column). Each phase depends on the one before it.

1. **understand**: debug the flow before building. Trace the feature's workflow step by step (inputs → each step → outputs, including the failure branches). Map the **interdependent tickets**: read every ticket in `blockedBy`, every ticket that is blocked by this one, and any related ticket named in the text (or from `/dep-graph`). Write down the interface each one needs (data shape, field names, who calls whom). 1–2 tasks.
2. **happy-path**: build the main success path end to end, the simplest version that works. Stub what other tickets haven't delivered yet, and note the stub. No edge cases yet.
3. **test**: once the happy path runs, write unit tests **from the Acceptance Criteria**, one or more per AC, covering the failure and edge cases too. The edge-case tests are expected to fail at this point. That's the to-do list for the next phase.
4. **build**: make the failing tests pass one by one (one task per behavior or AC), then the integration test against the real dependencies once the blocking tickets are done.

Rules:
- Each task is one concrete step doable in **one day or less**, starting with a verb ("Add…", "Write…", "Check…").
- Every AC is covered by at least one task (`ac` column). Include the test or check that proves it — tests are tasks too.
- Order by what must happen first; `depends_on` lists task ids from **this** file (`T1;T2`).
- If the ticket is `blockedBy` another ticket, mark the affected tasks `blocked` and say why in `note` (e.g. `waiting on APP-101`).
- Every ticket that has code gets at least one task in each phase. A non-code ticket (an epic, a doc or process task) can skip `test` and `build`. Say so.
- Aim for 4–10 tasks. More than 10 → suggest splitting the ticket.
- Don't add tasks for things outside the ticket's scope.

## 4. Show and confirm
Show the draft as a simple table grouped by phase (id, task, covers, after). Then list AC coverage, e.g. `AC1 ✓ T1 T3 T4 · AC2 ✓ T2 · AC3 ✓ T5 · AC4 ✓ T7`.
Ask: "Save these steps? You can also tell me what to change." Apply edits and show again until they say yes. Save nothing before that.

## 5. Save
Write `ticket-data/<sprint>/<TICKET-ID>/tasks.csv` with exactly this header:
```
id,phase,task,status,ac,depends_on,updated,note
```
- `id`: `T1`, `T2`, … continuing from the highest existing id; never renumber.
- `phase`: `understand`, `happy-path`, `test` or `build`.
- `status`: `todo` (or `blocked` per step 3). Allowed: `todo`, `doing`, `blocked`, `done`, `dropped`.
- `updated`: today, `YYYY-MM-DD`. Lists use `;` (`AC1;AC3`). Quote any field containing a comma.
- Never edit `ticket.md`.

Finish with one line: how many tasks, and the first one to start (first `todo` whose `depends_on` are all `done`).
