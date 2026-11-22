# Standup helper

Get ready for your daily standup and your end-of-day status in about 5 minutes each.

You keep your Jira tickets in a folder. You write your own standup, and an AI assistant (Claude)
checks it against your tasks and keeps your task list in step with what you wrote:

> **Did:** login form works against a fake API.
> **Doing:** writing the unit tests for the login page.
> **Blocked:** still waiting on the Ops team for the users database (3 days). This also holds up 2 other tickets.

You don't need to know how to program.

---

## What you need

1. **Claude Code**, the AI assistant this runs in. Install it from <https://claude.com/claude-code> and sign in.
2. **Your tickets in the `ticket-data` folder.** Your Jira export tool puts them there (see "How your tickets are stored" below).

3. **Install the commands.** They live in this repo's `_claude/skills/` folder. Copy them into your own Claude folder once:
   ```bash
   mkdir -p ~/.claude/skills
   cp -r _claude/skills/* ~/.claude/skills/
   ```
   > **Warning:** if you already have skills with the same names (`standup`, `eod`, `plan-tasks`, `analyze-ticket`, `dep-graph`, `analyze-codebase-and-explain`, `analyze-techdebts`, `agile-basics`), this **overwrites** them. Check first with `ls ~/.claude/skills`, and back up or rename any you want to keep.

   Run the copy again whenever you pull updates to this repo.

To start, open a terminal in this folder and type `claude`. Then type the commands below into Claude.
Every command starts with `/`.

---

## Your day

### Morning, before standup

| Step | Type this | What happens |
|------|-----------|--------------|
| 1 | *(run your Jira export tool)* | Your latest tickets land in `ticket-data`. |
| 2 | `/analyze-ticket` | Claude flags tickets that are unclear, for example ones that don't say how you'd know they're done. |
| 3 | `/dep-graph` | Claude finds which tickets are waiting on other tickets, including ones nobody wrote down. You approve each one. |
| 4 | *(write `ticket-data/<sprint>/standup/<today>.md`)* | Your own **Did / Doing / Blocked**. You are the source of truth, because Jira downloads can be out of date. |
| 5 | `/standup` | Claude checks what you wrote against `tasks.csv` (using today's date from your computer). No file for today? It asks you, one item at a time, what you did, what you plan and any blockers, and saves your answers as written. If you can't remember, it tells you it will look through your tickets for evidence of what changed, then asks you to confirm each thing it finds.. It lists what doesn't match and offers to update `tasks.csv`. It never rewrites your standup. |

### End of day

| Step | Type this | What happens |
|------|-----------|--------------|
| 1 | `/eod` | Claude goes through your tickets one by one and asks: done, still working, blocked (on what?), or not touched? |
| 2 | | Claude asks what you plan to do tomorrow. |
| 3 | | Claude writes a short end-of-day summary for you to paste. |

Your end-of-day answers become tomorrow morning's "Did". So if you do the end of day, the morning takes almost no time.

### Once per new ticket

| Type this | What happens |
|-----------|--------------|
| `/plan-tasks APP-102` | Claude breaks the ticket into small steps (one day or less each) and shows them to you. Nothing is saved until you say yes. |

Claude then checks these steps every day, so nothing gets forgotten.

The steps always come in the same four phases:
1. **Understand**: work out how the feature flows and which other tickets it depends on, before building anything.
2. **Happy path**: get the main "everything goes right" version working.
3. **Test**: write tests from the ticket's Acceptance Criteria (its "how we know it's done" list). Some will fail at first, and that's expected.
4. **Build**: fix things until every test passes.

This also makes your standup easy to say: "APP-102: happy path done, 3 of 5 tests passing." 

---

## How your tickets are stored

```
ticket-data/
  sprint-01/                 one folder per sprint
    APP-102/                 one folder per ticket
      ticket.md              the ticket from Jira (your export tool writes this)
      tasks.csv              the small steps for this ticket (Claude writes this, with your OK)
    journal/
      2026-01-13.md          your notes for each day
    standup/
      2026-01-14.md          the standup you wrote that morning
```

- **`ticket.md`**: the ticket text from Jira. Your export tool updates it, and Claude only changes the "blocked by" line if you say yes.
- **`tasks.csv`**: a small table of steps. You can open it in Excel or Google Sheets. Each row has a step, its status (`todo`, `doing`, `blocked`, `done`), and a short note.
- **`journal/`**: one file per day with what you did and any links you saved.
- **`standup/`**: the standup you write each morning. When your standup and `tasks.csv` disagree, your standup wins.

There is a sample sprint in `ticket-data/sprint-01/` you can try the commands on: a simple login feature (login API, login page, "remember me"). It has a few problems on purpose, such as a blocker nobody wrote down and a ticket with vague Acceptance Criteria, so the commands have something to find.

---

## Good to know

- **Claude asks before it changes anything.** It shows you what it wants to change and waits for your yes.
- **Nothing is sent to Jira.** These commands only read and write the files in this folder.
- **`/dep-graph` can use an optional extra tool called graphify** to draw a clickable map of how tickets connect. Claude will ask before installing it. Say no and it still works, just without the map.
- **No Claude account?** The `embedder/` folder has a different setup for technical users. See `SPEC.md`.

For tips on getting good updates, see `BEST_PRACTICES.md`. For the full design and open questions, see `SPEC.md`.

---

## Full workflow

How the commands fit together, from a new sprint to the end of each day.

### One-time setup
1. Install Claude Code and open it in this folder (`claude`).
2. Fill in `ticket-data/repos.md`: one section per code repo, with its folder path (or URL), its default branch, and what it covers. Claude only looks at the repos you list there.

### New sprint
| Step | Type this | What you get |
|------|-----------|--------------|
| 1 | *(run your Jira export tool)* | Tickets in `ticket-data/<sprint>/`. |
| 2 | `/analyze-ticket` | A list of unclear tickets. Ask your lead about them early. |
| 3 | `/dep-graph` | Which tickets wait on which, and the blockers nobody wrote down. You approve each change. |
| 4 | `/plan-tasks APP-102` (per ticket) | Small daily steps in `tasks.csv`, covering every Acceptance Criterion. |

### Each morning
| Step | Type this | What you get |
|------|-----------|--------------|
| 1 | `/analyze-codebase-and-explain APP-102` | **Where you are** on the ticket, based on the code itself rather than the ticket's status. Plus **unknowns** to clear up early, a few technical lines for standup, and tech debt you could clean up while you're in that code. Saved as `analysis.md` in the ticket folder. |
| 2 | *(write today's standup file)* | Your own **Did / Doing / Blocked**. Use step 1 for technical lines and the top unknown. |
| 3 | `/standup` | Checks your standup against `tasks.csv`, flags where Jira looks behind, and updates `tasks.csv` rows you approve. |

### Each evening
| Step | Type this | What you get |
|------|-----------|--------------|
| 1 | `/eod` | Each ticket marked done, progress, or blocked, plus your plan for tomorrow and a summary to paste. |

### About `/analyze-codebase-and-explain`
- **It doesn't take the ticket's word for it.** It compares what the ticket says with what the code shows, and lists the differences. When something isn't clear it asks you (or writes it down as an unknown) instead of guessing.
- **It never changes your code.** It only reads git history and files: no commits, pushes, branch switches, installs, or running builds. The only file it writes is `analysis.md`. It adds to `tasks.csv` or drafts follow-up tickets only if you pick that at the end.
- **It can run unattended**, for example on a schedule before standup. Then it doesn't stop to ask questions. It lists them under "Unknowns to clarify", and the report is marked `UNATTENDED`. It does stop if it can't find the ticket or `repos.md`, or can't tell which repo holds the code.
- **graphify is optional.** With it, you get a map of which code depends on which. Without it, Claude searches the code instead.
- **Want a guarantee on top of the instructions?** Add deny rules for `git commit`, `git push`, and `git checkout` in `.claude/settings.json`.
