---
name: standup
description: Check the standup the user wrote (Did / Doing / Blocked) against tasks.csv and tickets in ticket-data/. The user's file is the source of truth; /standup flags mismatches and offers to update tasks.csv to match. It never writes the standup for the user. Use for "/standup", "check my standup", "validate my standup", "prep my standup".
argument-hint: [path/to/standup-file]
---

# /standup

**The user writes the standup. You check it.**
- The user's file is the source of truth for what happened.
- `tasks.csv` and `ticket.md` are secondary: Jira downloads can be out of sync or out of date.
- When the user's file and the other files disagree, assume the files are behind, not the user.

Never write or rewrite the standup text (step 1b only saves the user's own answers, verbatim). Never edit `ticket.md`, because the Jira export owns it. Besides that file, the only file you may change is `tasks.csv`, and only for the rows the user approves.

## 1. Find the standup file
1. Get today's date from the system: `date +%F`. Don't trust dates written inside files to tell you what day it is.
2. Current sprint = newest folder in `ticket-data/` by name (ignore `archive/`).
3. Find the file:
   - A path was passed → use it.
   - Otherwise, look in `ticket-data/<sprint>/standup/` for files named `YYYY-MM-DD.md`.
4. Pick the file:
   - **Today's file exists** → use it.
   - **No file for today** → go to step 1b. An older file isn't today's standup.
   - **The filename date and the modified time disagree** (`stat -c '%y %n'`; for example, yesterday's file was edited this morning) → say so and ask which one counts as today's.
   - **A filename date is in the future** → flag it and don't use it.

## 1b. No standup for today: ask the user
Don't look in `tasks.csv`, the journal or older standup files for hints. Ask the user what they remember. The one exception is the "I don't remember" option in step 3.

Assume the user is a busy developer juggling many tasks. Vague or partial answers ("some login stuff", "reviews, I think") are normal, not a failure. Keep the questions short, and make "I don't remember" a one-word answer that leads straight to the evidence.
1. If the last working day's standup is also missing, say so: "No standup for <date> or today."
2. Ask one question at a time, one item per answer:
   - **What did you do** since the last standup? After each answer, ask "Anything else you remember doing?" until they say no.
   - **What do you plan** to do today? Same loop: "Anything else?"
   - **Any blockers?** For each one: what is it waiting on, and who from? Same loop.
   For each item, if they didn't name a ticket, ask "Which ticket is that?" They may answer "none".
3. Never suggest items, never pre-fill answers, and never answer for the user.
   **If the user says they don't remember**, tell them: "I'll look into your tickets and check for any evidence of what changed since <last working day>." Then look, read-only, since the last working day:
   - `ticket.md`: status and `updated` changes, and new comments
   - `tasks.csv`: rows whose `updated` is in that range, with their `note`
   - the journal lines for those days
   - code, only if `ticket-data/repos.md` exists: `git log --since=<last working day> --author=<author>` in the listed repos, matching commits to ticket IDs. Use the `author:` from `repos.md` if set, otherwise `git config user.name`, and say which one you used
   A vague answer ("some login stuff") narrows the search: look only at the evidence that matches it.
   Group the findings by ticket and number them, each marked "evidence, not confirmed" with its source (file and line, or commit):
   ```
   APP-102
     1. T3 marked doing → tasks.csv:4, updated 2026-01-13
     2. commit a1b2c3 "APP-102 login form submit" (login-api)
   APP-101
     3. new comment "pinged Ops again" → ticket.md:31
   ```
   Ask for one reply covering all of them, so the user isn't answering twenty separate questions. For example: "1,2 yes · 3 no · or reword: 2 = wired the form to the fake API". Use their wording when they give it, otherwise a short neutral phrasing of the evidence, and show the result before saving. Save only what they confirmed.
   If no evidence turns up, say so and offer to write `- (doesn't remember)` for that section or to stop without saving. Never fill a section from evidence the user didn't confirm.
4. Save the answers in the user's own words to `ticket-data/<sprint>/standup/<today>.md`:
   ```markdown
   # <today>
   ## Did
   - <user's words>
   ## Doing
   - <user's words>
   ## Blocked
   - <user's words, or "Nothing blocked.">
   ```
   Show the file and ask "Save this?" before writing it. This is the only time you may create a standup file.
5. Continue to step 2 with that file. The user's answers win over `tasks.csv`.

## 2. Read the user's claims
- Split the file into **Did**, **Doing** and **Blocked**. Each line is one claim.
- Note any ticket IDs (`ABC-123`) and task IDs (`T3`) in each line. If a line has no ticket ID, ask which ticket it's about; don't guess from the wording.
- Read `tasks.csv` (`id,phase,task,status,ac,depends_on,updated,note`) and the `ticket.md` frontmatter (`status`, `blockedBy`) for each ticket mentioned.
- Read the journal entries since the last standup as extra evidence only.

## 3. Compare
For each claim, check the files:

| User says | Files show | Result |
|-----------|-----------|--------|
| Did X | the task is `done` | ✓ matches |
| Did X | the task is `todo` or `doing` | **tasks.csv behind** → propose `status: done` |
| Doing X | the task is `todo` | **tasks.csv behind** → propose `status: doing` |
| Blocked on Y | the task isn't `blocked` | **tasks.csv behind** → propose `status: blocked` and a `note` |
| Says it's unblocked | `blockedBy` is still set | **Jira behind** → tell the user to update Jira |
| Claim with no matching task | — | **untracked work** → propose a new task row, or a note on the closest one |
| Ticket status in `ticket.md` disagrees | — | **Jira behind** → flag only |

Also list things in the files that the user **didn't mention**. These are information, not errors:
- tasks `doing` for 3+ days
- tickets still blocked
- tasks marked `done` since the last standup that the user's Did doesn't mention

Ask about them. Don't add them to the standup.

For blockers the user names, add facts the files can give: how many days it has been blocked (from `updated`), and which other tickets are waiting on it (from the `blockedBy` chains).

## 4. Report
```
Checked: ticket-data/sprint-01/standup/2026-01-14.md (today)

✓ 3 lines match tasks.csv

tasks.csv is behind your standup:
| # | Ticket | Task | Now | Your standup says | Proposed change |
|---|--------|------|-----|-------------------|-----------------|
| 1 | APP-102 | T3 | doing | Did: login form done | status → done, updated → 2026-01-14 |

Jira looks behind (update it in Jira; I won't edit ticket.md):
- APP-101: you say it's unblocked, but blockedBy still lists the Ops database.

Questions:
- "fixed the flaky test": which ticket is that?
- APP-102 T2 has been "doing" for 3 days and isn't in your standup. Still going?

Facts for your Blocked line:
- APP-101: blocked 3 days; holds up APP-102 and APP-103.
```
Then ask: "Apply which tasks.csv changes? (all / 1,3 / none)"

## 5. Apply (only what was picked)
- Edit only the chosen rows. Change `status`, set `updated` to today's system date, and add the user's wording to `note`. Keep every other row and column exactly as it was.
- New task rows get the next free `T<n>` ID, and their `phase` is left empty for the user to fill in.
- Re-read the file and confirm it parses, with the same columns.
- Don't touch the standup file.
