---
name: dep-graph
description: Build and validate the dependency graph between tickets in ticket-data/. Uses graphify (graphifyy) for semantic relationships and an HTML graph if the user has it or agrees to install it; otherwise scans ticket text for dependencies written in the descriptions. Use for "/dep-graph", "what blocks what", "build the dependency graph", "find hidden dependencies".
---

# /dep-graph

Goal: every ticket in `ticket-data/` has an exact `blockedBy: [IDs]` in its frontmatter, and the user can see which tickets are related by meaning.

The explicit `blockedBy` list is the source of truth. Nothing found by graphify or text scanning is written to a ticket until the user confirms it.

## 1. Load tickets
- Read every `ticket-data/<sprint>/<TICKET-ID>/ticket.md` (skip `archive/` unless the user asks for cross-sprint, and skip `graph/` and `graphify-out/`).
- For each ticket, note its ID (frontmatter `id`, else the folder name), status, and current `blockedBy`.
- If there are no tickets, say so and stop.

## 2. Choose the semantic path
Check whether graphify is installed:
```bash
command -v graphify && graphify --version
```
- **Installed** → go to 3A.
- **Not installed** → ask the user once:
  "graphify (PyPI package `graphifyy`, double y) can map related tickets by meaning and draw an HTML graph. Install it?"
  - Yes → install with the first tool available, then `graphify install` (registers its Claude Code skill):
    ```bash
    uv tool install graphifyy || pipx install graphifyy
    graphify install
    ```
    Check `command -v graphify` again. If it still fails, tell the user (it may need `uv tool update-shell` and a new shell) and fall back to 3B.
  - No → 3B.

Never install anything without that yes.

## 3A. Graphify path
1. Build the graph over the tickets folder: run the `/graphify ticket-data --update` skill (first run: `/graphify ticket-data`). Output lands in `graphify-out/` (`graph.html`, `graph.json`).
2. For ticket pairs that look related, query it, for example:
   ```bash
   graphify query "which tickets depend on <TICKET-ID>?"
   graphify path <TICKET-A> <TICKET-B>
   ```
3. Collect pairs connected by graphify that have **no** `blockedBy` link between them. Keep its confidence tag (`EXTRACTED` / `INFERRED`).
4. Also run 3B — it catches dependencies written plainly in the text that graphify may tag only as related.

## 3B. Text scan path (no graphify)
Search each ticket's description, notes and comments for dependencies stated in words:
- "blocked by", "blocks", "depends on", "dependent on", "waiting on/for", "requires", "after", "needs … first", "prerequisite", "follow-up to", "related to", "see also"
- Any ticket ID pattern (e.g. `ABC-123`) or a link to another ticket in the same text.

For each hit, record: source ticket, target ticket, the exact quoted sentence, and the direction:
- "X is blocked by / depends on / waits on Y" → `X.blockedBy += Y`
- "X blocks Y" → `Y.blockedBy += X`
- "related to / see also" → related only, not a blocker.

Ignore IDs that don't exist in `ticket-data/` but list them as **unknown references**.

## 4. Validate the explicit graph
Report, from the current `blockedBy` lists:
- **Missing IDs**: a `blockedBy` entry with no ticket file.
- **Cycles**: A → B → … → A (show the full loop).
- **Stale blocks**: blocked by a ticket whose status is done.
- **Self-blocks**: a ticket listing itself.

## 5. Show and confirm
Print one table:

| # | Ticket | Proposed change | Evidence | Source |
|---|--------|-----------------|----------|--------|
| 1 | APP-103 | add `blockedBy: APP-102` | "Depends on APP-102 being done first." | text |
| 2 | APP-101 | outside blocker: Ops team (not a ticket) | "Waiting on the Ops team…" | text |
| 3 | APP-102 | remove `APP-090` (done) | status: done | validate |

Then ask which numbers to apply ("all", "1,3", "none"). Only apply what was chosen:
- Edit just the `blockedBy` line in the frontmatter; keep the rest of the file byte-for-byte.
- Related-only pairs are not written as blockers. If the user wants them kept, add `related: [IDs]` to frontmatter.

## 6. Finish
- Re-run step 4 on the result and confirm: no cycles, no missing IDs.
- Print the blocker chains for not-done tickets, longest first, e.g. `APP-103 ← APP-102 ← APP-101`.
- If graphify ran, give the path to `graphify-out/graph.html` to open in a browser.
