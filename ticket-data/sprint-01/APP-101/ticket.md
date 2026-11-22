---
id: APP-101
title: Login API
type: Story
status: doing
priority: P0
blockedBy: []
link: https://your-tracker.example.com/browse/APP-101
---
**Summary**
Add a login API that checks email and password

**Issue Type**
Story

**Context & Intent**
The login page needs a server endpoint that says whether an email and password are correct.

**Scope & Requirements**
- `POST /api/login` with `{ email, password }`.
- Passwords stored hashed, never in plain text.
- Returns a session token on success.
- Waiting on the Ops team to create the users database.

**Acceptance Criteria**
- Given a correct email and password, the API returns 200 and a session token.
- Given a wrong password or unknown email, the API returns 401 with the same message for both (no hint which one was wrong).
- Given 5 failed attempts in 10 minutes for one email, further attempts return 429 for 10 minutes.
- No password appears in logs or the database in plain text.

**Resources & Links**
- Related Epic: APP-100
