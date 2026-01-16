---
applyTo: '**'
description: This file describes the Git commit protocol for the project.
---

# Git Instructions
## Git Commit Protocol

**Follow Conventional Commits standard with atomic commits:**

1. **Commit after each completed task** - don't batch multiple tasks
2. **Format:** `<type>(<scope>): <description>`

**Types:**
| Type | Use for |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes nor adds |
| `test` | Adding or updating tests |
| `chore` | Build, config, tooling changes |

**Examples:**
```bash
git commit -m "chore(config): add Pydantic settings with multi-provider LLM support"
git commit -m "feat(agents): implement supervisor routing logic"
git commit -m "fix(api): handle missing thread_id in resume endpoint"
```

**Scope suggestions:** `config`, `agents`, `graph`, `api`, `tools`, `security`, `db`, `docker`