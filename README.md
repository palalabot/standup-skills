# Standup helper

Get ready for your daily standup and your end-of-day status in about 5 minutes each.

You keep your Jira tickets in a folder. An AI assistant (Claude) reads them, asks you a few
questions, and writes your update for you:

> **Did:** login form works against a fake API.
> **Doing:** writing the unit tests for the login page.
> **Blocked:** still waiting on the Ops team for the users database (3 days). This also holds up 2 other tickets.

You don't need to know how to program.

---

## What you need

1. **Claude Code**, the AI assistant this runs in. Install it from <https://claude.com/claude-code> and sign in.
2. **Your tickets in the `ticket-data` folder.** Your Jira export tool puts them there (see "How your tickets are stored" below).

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
| 4 | `/standup` | Claude writes your **Did / Doing / Blocked** update. Copy it into chat or read it out loud. |

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
```

- **`ticket.md`**: the ticket text from Jira. Your export tool updates it, and Claude only changes the "blocked by" line if you say yes.
- **`tasks.csv`**: a small table of steps. You can open it in Excel or Google Sheets. Each row has a step, its status (`todo`, `doing`, `blocked`, `done`), and a short note.
- **`journal/`**: one file per day with what you did and any links you saved.

There is a sample sprint in `ticket-data/sprint-01/` you can try the commands on: a simple login feature (login API, login page, "remember me"). It has a few problems on purpose, such as a blocker nobody wrote down and a ticket with vague Acceptance Criteria, so the commands have something to find.

---

## Good to know

- **Claude asks before it changes anything.** It shows you what it wants to change and waits for your yes.
- **Nothing is sent to Jira.** These commands only read and write the files in this folder.
- **`/dep-graph` can use an optional extra tool called graphify** to draw a clickable map of how tickets connect. Claude will ask before installing it. Say no and it still works, just without the map.
- **No Claude account?** The `embedder/` folder has a different setup for technical users. See `SPEC.md`.

For the full design and open questions, see `SPEC.md`.
