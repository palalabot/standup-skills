# Example: a ticket with real Acceptance Criteria

**Summary**
Add a login page with email and password

**Issue Type**
Story

**Context & Intent**
Users need a simple page to sign in. Errors should be clear without revealing whether an email is registered.

**Scope & Requirements**
- Email and password fields, and a "Sign in" button.
- Calls `POST /api/login` (APP-101).
- On success, go to the home page.
- On failure, show "Email or password is incorrect."
- Button disabled while the request is in progress.
- Works with keyboard only, and labels are read by screen readers.

**Acceptance Criteria**
- Given a correct email and password, the user lands on the home page.
- Given a wrong email or password, the page shows "Email or password is incorrect." and keeps the email filled in.
- Given an empty field, the "Sign in" button does nothing and the empty field is highlighted.
- Given too many attempts (API returns 429), the page shows "Too many attempts, try again in 10 minutes."
- Unit tests cover success, wrong password, empty fields and too many attempts.

**Resources & Links**
- Login API: APP-101
- Design: https://your-design-tool.example.com/login
- Related Epic: APP-100

## Why these Acceptance Criteria are real
- Each one can be checked: you land on a page, an exact message appears, a button does nothing, tests exist.
- They cover the failure cases (wrong password, empty field, too many attempts), not just success.
- None says "works as expected". Each says what you'd see.
