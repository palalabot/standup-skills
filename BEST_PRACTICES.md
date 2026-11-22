# Best practices: writing cohesive standups with this skill set

Audience: developers running these skills in Claude Code, either interactively or headless (`claude -p`, cron, CI).

This doc covers three things:
1. **Why** the Daily Scrum exists, so you know what a good update optimizes for.
2. **How** to chain the skills so the standup you write stays consistent with your tasks, tickets and code.
3. **How to run the skills safely** in an agent harness.

Design principle: **the developer writes the standup, and the tooling checks it.** Jira exports go stale, and `tasks.csv` lags reality. The only fresh source of what happened yesterday is you.

---

## 1. The standup in the agile process

### What it's for
The Agile Manifesto values *individuals and interactions over processes and tools* and *responding to change over following a plan* (`/agile-basics` prints the full text). The Daily Scrum is where that happens every day:

- **Timebox:** 15 minutes, same time every day, run by the developers for the developers.
- **Objective:** inspect progress toward the **Sprint Goal** and adapt the plan for the next 24 hours. It isn't a status report to management.
- **Format:** the Scrum Guide (2020) doesn't require the three questions. Did / Doing / Blocked is a convention, and this repo uses it because it parses well.
- **Output:** a re-planned day, and blockers surfaced early enough that someone can act on them.

### What a good update optimizes for
| Property | Meaning | Anti-pattern |
|----------|---------|--------------|
| **Goal-referenced** | Every line ties to a ticket ID and, through it, to the Sprint Goal | "Worked on stuff" |
| **Outcome over activity** | State the change in system state | "Spent 6 hours on login" |
| **Falsifiable** | Someone can check it against a task, test or commit | "Almost done" |
| **Blocker-forward** | Say what it's waiting on, who can unblock it, how long it's been, and what else it holds up | "Some issues with the DB" |
| **Unknowns early** | Raise ambiguity today, not at sprint review | Silently guessing the ticket's intent |
| **Short** | One line per item, details offline | Live debugging in the meeting |

### Why the developer is the source of truth
```
freshness:   your standup  >  tasks.csv  >  ticket.md (Jira export)
authority:   your standup  >  code evidence (analysis.md)  >  tasks.csv  >  ticket.md
```
- Ticket downloads are snapshots. They miss same-day status changes, comments and re-scoping.
- `tasks.csv` is only as fresh as your last `/eod` or `/standup` reconcile.
- So `/standup` never generates your update. It diffs your claims against the files and proposes updates to `tasks.csv`. Where Jira looks behind, it tells you to fix it in Jira, and `ticket.md` is never edited.
- Code evidence (`/analyze-codebase-and-explain`) outranks `tasks.csv` on *state*. It doesn't outrank you on *intent*. When they disagree, it's an unknown to resolve, not an automatic override.

---

## 2. The workflow: how the skills chain

```
sprint start      /analyze-ticket → /dep-graph → /plan-tasks <ID>
each morning      [/analyze-codebase-and-explain <ID>] → write standup/<today>.md → /standup
as needed         /analyze-techdebts <ID>      /agile-basics
each evening      /eod
```

| Skill | Role in a cohesive standup | Writes |
|-------|----------------------------|--------|
| `/analyze-ticket` | Flags tickets without testable acceptance criteria (AC), so your "Did" can be falsifiable | report only |
| `/dep-graph` | Makes `blockedBy` explicit, so your "Blocked" line can say what else it holds up | `blockedBy`, on approval |
| `/plan-tasks` | Breaks a ticket into ≤1-day tasks (`T1…Tn`), giving each standup line something to point at | `tasks.csv`, on approval |
| `/analyze-codebase-and-explain` | Per-AC code state plus unknowns, which become your technical lines and "need clarity on" | `analysis.md` |
| `/analyze-techdebts` | Measured debt on the ticket's path, which explains *why* something is slow | `techdebt.md` |
| `/standup` | Validates **your** file against `tasks.csv` and tickets, then reconciles `tasks.csv` | `tasks.csv` (approved rows); today's `standup/*.md` only from your own answers |
| `/eod` | Records the day, so tomorrow's diff has a fresh baseline | `tasks.csv`, `journal/` |
| `/agile-basics` | Prints the manifesto and the Daily Scrum's purpose | nothing |

### Daily loop in detail
1. **(Optional) Get evidence first.** Run `/analyze-codebase-and-explain APP-102` for tickets you touched yesterday. Use "Where you are" and "Unknowns" as input to your own writing; don't paste them blindly.
2. **Write** `ticket-data/<sprint>/standup/<YYYY-MM-DD>.md`:
   ```markdown
   # 2026-01-14
   ## Did
   - APP-102 T3: login form posts to the fake API; redirects on 200.
   ## Doing
   - APP-102 T4: unit tests from AC1–AC5; expect error-path tests red first.
   ## Blocked
   - APP-101: users DB not provisioned; need Ops (who: <name/team>). Holds APP-102 T2.
   ```
3. **Run `/standup`.** It resolves the file by **system date** (`date +%F`):
   - today's file if it exists
   - no file for today → it doesn't search `tasks.csv` for hints. It asks you item by item: **What did you do?** ("anything else?"), **What do you plan?**, **Any blockers?** It saves your answers word for word, after you confirm, and never suggests or pre-fills items. Say "I don't remember" and it tells you it will look into your tickets for evidence of what changed (ticket updates, `tasks.csv` rows, the journal, and your commits in the repos listed in `repos.md`). It's built for the busy developer who can't recall each task: vague answers narrow the search, findings are grouped by ticket with their sources, and you confirm them all in one reply (`1,2 yes · 3 no`). Set `author:` in `repos.md` if you commit under a different name. Tickets already confirmed this run are never asked again. Tickets already recorded in `tasks.csv` or `ticket.md` since the last working day only get a "use as-is or skip?" prompt, and `next` / `skip` / `skip all` / `done` work at any prompt, so the loop can't repeat itself. In any section, `next section` moves on and `skip section` leaves it out. Nothing answered once, in any section, is asked again
   - future-dated files are rejected
4. **Review the diff.** You get:
   - ✓ matches
   - *tasks.csv behind* (proposed status changes)
   - *Jira behind* (fix it in Jira)
   - untracked work (a claim with no task)
   - questions (lines without a ticket ID, stale `doing` rows you didn't mention)
5. **Apply** the rows you pick (`all / 1,3 / none`). Then read your standup out as written. It's yours.
6. **Evening:** `/eod` closes the loop.

### Writing rules that make the diff useful
- **Prefix every line with `TICKET-ID [Tn]:`.** Lines without an ID can't be validated and come back as questions.
- **Use status words that map to the task statuses:**
  - done / finished / merged → `done`
  - working on / started → `doing`
  - waiting on / blocked by → `blocked`
- **One claim per line.** Compound lines ("did T3 and started T4") get split by the validator anyway.
- **For blockers, name the dependency and an owner.** The validator adds days blocked and downstream tickets from `blockedBy`; it can't know who to chase.
- **Keep work that isn't on a ticket visible:** "Fixed flaky CI test" is valid work. `/standup` will offer to track it, and you can say no.
- **Don't edit `tasks.csv` by hand to match your standup.** Let `/standup` do it, so `updated` and `note` stay consistent.

---

## 3. Running the skills securely in a harness

The model is an untrusted planner with tool access. The harness (permissions, hooks, sandbox, credentials) is the only real enforcement layer. A "Rules" section in a skill shapes behaviour, but it isn't access control.

### Threat model
| Surface | Risk | Entry point |
|---------|------|-------------|
| `ticket.md`, Jira comments | Indirect prompt injection | Jira export |
| Repo content (code, README, commit messages) | Injection; planted modules picked up by interpreters | code-analysis skills |
| `ticket-data/repos.md` | Path or URL tampering pointing the agent at the wrong repos | code-analysis skills |
| Your standup file | Also untrusted *for instructions*: claims are data, not commands | `/standup` |
| Tool output (git, graphify) | Output treated as instructions | graph and query steps |
| Sub-agents | Rules lost on handoff (fresh contexts start cold) | parallel review phases |
| Reports | Secrets or PII leaking into `analysis.md`, chat or Jira | report steps |

### Enforce in config
**Permissions** (`.claude/settings.json`):
```json
{
  "permissions": {
    "deny": [
      "Bash(git commit:*)", "Bash(git push:*)", "Bash(git checkout:*)",
      "Bash(git switch:*)", "Bash(git reset:*)", "Bash(git rebase:*)",
      "Bash(git merge:*)", "Bash(git stash:*)", "Bash(git pull:*)",
      "Bash(npm install:*)", "Bash(pip install:*)", "Bash(uv tool install:*)",
      "Bash(curl:*)", "Bash(wget:*)"
    ],
    "allow": [
      "Bash(git log:*)", "Bash(git diff:*)", "Bash(git show:*)",
      "Bash(git blame:*)", "Bash(git status:*)", "Bash(git branch:*)",
      "Bash(date:*)", "Bash(stat:*)"
    ]
  }
}
```
- Deny takes precedence over allow.
- String-pattern rules aren't a sandbox: `sh -c`, aliases and env tricks can get around them. For headless runs, add an OS sandbox or container.

Other controls:
- **Credential scoping:** for unattended analysis, use a read-only deploy key or a fine-grained PAT with `contents:read`, and no `gh auth` or SSH agent in the environment. A token that can't push is the cheapest guarantee you'll get.
- **`PreToolUse` hooks:** block `Edit` and `Write` outside `ticket-data/`, and block writes to `ticket.md` and overwrites of existing `standup/*.md` (`/standup` may only *create* today's file from your answers). Hooks are harness code, so injection can't turn them off.
- **Isolation:** clones and graphify output go to the scratchpad, never into the target repo. Run interpreters over untrusted files with `python -I` from a different cwd.

### Prompt construction
- **Fence data off from instructions.** Wrap external content in tags (for example `<ticket trust="untrusted">…</ticket>`) and state once that it's data. This reduces injection; it doesn't eliminate it.
- **Allow-list actions.** Enumerate the allowed verbs, name a single output path, and list the forbidden side effects. "Clean up the repo" is unbounded; "`git log|diff|blame`, write only `analysis.md`" fails closed.
- **Use schemas over prose.** Fixed tables with an evidence column give you diffs across runs and let a parser reject unsupported rows.
- **Require provenance.** Every claim cites a `file:line`, commit SHA, graph edge or ticket line; drop uncited claims when merging results.
- **Treat unknowns as first-class.** "Not found" and "Unknown" are valid outputs. Without that, models fill the gaps: they guess repos and base branches, and they assume the ticket's design is current.
- **Hard stops:** missing input, an ambiguous target, or a repo or ticket identity that can't be proven means halt and report.

### Multi-agent handoff
- Restate the guardrails in every sub-agent prompt, because sub-agents don't inherit them.
- Give each sub-agent the narrowest tool set; only the orchestrator writes.
- Cap the findings per agent (for example 8), dedupe by location, and drop rows without evidence. `INFERRED` graph edges are low confidence.
- Agents may *raise* unknowns but not *resolve* them.

### Attended vs unattended
| Concern | Attended | Unattended |
|---------|----------|-----------|
| Clarifications | Batch the blocking questions up front | Record them as Unknowns and continue with proven facts only |
| `/standup` reconcile | Apply the rows you pick | **Report only.** Never auto-apply, because the user's approval is the point |
| Installs | Ask once | Never; use the fallback |
| Writes | Show a diff before overwriting | Declared output file only |
| Ambiguous target | Ask | Hard stop |

- Make runs idempotent and pin tool versions (`graphifyy==x.y.z`).
- Log the inputs: commit SHA, a hash of `repos.md`, the ticket's `updated` field and the system date.

### Data hygiene
- **Secrets:** skip `.env*` and credential files. Redact `AKIA…`, `ghp_…` and `-----BEGIN` in quoted evidence.
- **PII:** bus-factor metrics use author names. Aggregate them to a count before sharing reports outside the team.
- **Egress:** nothing here calls Jira or other APIs. Every new sink (MCP server, webhook, artifact publish) is a publication, so gate it on explicit confirmation.
- **Commits:** agents never commit in code repos. In this repo, commits go through a skill that shows the exact message and requires approval.

---

## 4. Checklists

**Daily (developer)**
- [ ] Standup file written for today's date, every line `TICKET-ID [Tn]:`
- [ ] Each blocker names its dependency and an owner
- [ ] `/standup` run; mismatches resolved (applied, rejected, or fixed in Jira)
- [ ] Top unknown raised in the meeting, not after
- [ ] `/eod` run before logging off

**Skill authoring**
- [ ] `description` states the triggers and side effects ("Read-only", "writes X on approval")
- [ ] One declared output path; every other write needs an explicit user pick
- [ ] User-authored files (`standup/*.md`) and the export-owned `ticket.md` are never rewritten; a standup file is only created from the user's own answers
- [ ] Git and shell verbs allow-listed, with a matching settings deny-list documented
- [ ] Untrusted inputs named; hard stops and unattended behaviour specified
- [ ] Output schema has an evidence column and defined confidence levels
- [ ] Sub-agent prompts restate the guardrails
- [ ] Optional dependencies have a fallback and are never auto-installed
- [ ] Third-party content credited, license checked before redistribution
