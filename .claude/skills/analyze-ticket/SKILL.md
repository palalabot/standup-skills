---
name: analyze-ticket
description: Check downloaded ticket data in ticket-data/ for quality, flagging tickets with no real Acceptance Criteria and other missing parts (context, scope, links). Use for "/analyze-ticket", "which tickets have no acceptance criteria", "check ticket quality", "are these tickets ready".
---

# /analyze-ticket

Goal: flag tickets that aren't ready to work on, mainly ones without **testable Acceptance Criteria (AC)**.

Takes an optional ticket ID or path. With none, checks every `ticket-data/<sprint>/<TICKET-ID>/ticket.md` (skip `archive/`, `graph/`, `graphify-out/`). Read-only: never edit a ticket unless the user asks.

Tickets may be Markdown, plain text, or JSON exported from Jira. For JSON, read `summary`, `description`, and any field whose name contains "acceptance". In Jira's own export, AC is often inside the description.

## What a good ticket looks like
See `references/good-ticket-example.md`. Its sections:
Summary, Issue Type, Context & Intent, Scope & Requirements, Acceptance Criteria, Resources & Links.

## Checks (per ticket)

### 1. Acceptance Criteria — main check
Find an AC section: a heading or label like "Acceptance Criteria", "AC", "Definition of Done", "DoD", or a JSON field for it.

| Result | Rule |
|--------|------|
| **MISSING** | No AC section, or it is empty. |
| **NOT REAL** | Section exists but every item is vague or untestable: "works as expected", "should work", "done when finished", "looks good", "TBD", "N/A", repeats the summary, or only restates requirements with no observable outcome. |
| **WEAK** | Some items are testable, others are vague; or no failure/edge case is covered. |
| **OK** | Each item describes an observable result someone can verify: Given/When/Then, a measurable threshold (e.g. "429 for 10 minutes after 5 failed attempts"), a clear pass/fail behavior, or a named test that must exist. |

A real AC item answers "how would I prove this is done?" Quote the weakest item as evidence.

### 2. Other sections (flag, lower severity)
- **Context / why** missing: no reason or user problem stated.
- **Scope** missing: no requirements or bullets of what's in.
- **Links** missing: no related epic, ticket, doc or repo link.
- **Unbounded wording**: "etc.", "and more", "all edge cases", "make it better" in scope.
- **Too big**: many unrelated requirements; suggest splitting.

### 3. Patterns across tickets
After the per-ticket checks, look across the whole set:
- Share of tickets with MISSING / NOT REAL AC, by issue type and by epic if present.
- Repeated vague phrases (the same filler line in many tickets).
- Tickets that others are `blockedBy` but have no real AC — these are the riskiest, so list them first.
- Duplicate or near-duplicate summaries.

## Output
1. One table, worst first:

| Ticket | AC | Other flags | Evidence |
|--------|----|-------------|----------|
| APP-104 | MISSING | no links | — |
| APP-103 | NOT REAL | unbounded scope ("etc."), no links | "Remember me works as expected." |
| APP-102 | OK | — | Given/When/Then x5 |

2. A short "Patterns" list from check 3.
3. Counts: total checked, OK, WEAK, NOT REAL, MISSING.
4. Offer (don't do): draft AC for the flagged tickets in the example's Given/When/Then style, as suggestions the user can paste into Jira. Drafts must come from the ticket's own scope — never invent thresholds or numbers; mark anything unknown as `<to confirm>`.
