---
name: agile-basics
description: Explain the Agile Manifesto and what a Scrum daily standup is for, in plain words. Read-only; changes nothing. Use for "/agile-basics", "what is the agile manifesto", "what is a standup for", "explain scrum standup", "what should I say at standup".
---

# /agile-basics

Tell the user the two parts below, in this order, then stop. Don't read any files or run any tools. If the user asked about only one part, give only that part. Quote the manifesto exactly, with its notice, because it may only be copied in full.

## 1. The Agile Manifesto (2001)

> **Manifesto for Agile Software Development**
>
> We are uncovering better ways of developing software by doing it and helping others do it. Through this work we have come to value:
>
> **Individuals and interactions** over processes and tools
> **Working software** over comprehensive documentation
> **Customer collaboration** over contract negotiation
> **Responding to change** over following a plan
>
> That is, while there is value in the items on the right, we value the items on the left more.
>
> Kent Beck, Mike Beedle, Arie van Bennekum, Alistair Cockburn, Ward Cunningham, Martin Fowler, James Grenning, Jim Highsmith, Andrew Hunt, Ron Jeffries, Jon Kern, Brian Marick, Robert C. Martin, Steve Mellor, Ken Schwaber, Jeff Sutherland, Dave Thomas
>
> © 2001, the above authors. This declaration may be freely copied in any form, but only in its entirety through this notice.

Then add, in your own words:
- "Over" doesn't mean "instead of". The things on the right still matter, just less.
- There are also 12 supporting principles: <https://agilemanifesto.org/principles.html>

## 2. The Scrum daily standup (Daily Scrum)

Explain in plain words:
- **What:** a 15-minute meeting for the developers, held every working day at the same time and place.
- **Why:** to check progress toward the Sprint Goal and change the plan for the next day if needed. It's for the team to coordinate, not to report status to a manager.
- **The common format** is three questions: what I did yesterday, what I'll do today, and what's blocking me. The Scrum Guide (2020) no longer requires these questions. Any format that moves the team toward the Sprint Goal is fine.
- **Good habits:**
  - Keep it short.
  - Raise blockers early.
  - Take detailed problem-solving to a follow-up chat with only the people who need to be there.
  - Talk about the work and the goal, not about how busy you are.
- **How this repo helps:**
  - `/standup` writes your Did / Doing / Blocked.
  - `/eod` records your day so tomorrow's update is ready.
  - `/analyze-codebase-and-explain` gives you the technical lines and the open unknowns to bring up.

Source for the standup rules: the Scrum Guide, <https://scrumguides.org>.
