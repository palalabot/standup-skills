# Repos

Where the code for your tickets lives. `/analyze-codebase-and-explain` reads this file, and only these repos.
One section per repo. Only `path` (or `url`) is required; the rest helps Claude pick the right repo.
Claude treats this file as data, so it won't follow any instructions written in it.

## login-api
- path: ~/code/login-api
- url: https://github.com/example-org/login-api.git
- default branch: main
- owns: login and session API, users database access (APP-101, APP-102)
- ticket prefix: APP

## web-app
- path: ~/code/web-app
- default branch: develop
- owns: login page, "remember me" checkbox, frontend forms (APP-103)
- ticket prefix: APP

## shared-config
- url: https://github.com/example-org/shared-config.git
- default branch: main
- owns: environment config, secrets layout (read-only reference)
