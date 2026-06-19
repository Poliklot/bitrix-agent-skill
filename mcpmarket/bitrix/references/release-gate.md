# Release gate

Открывай перед пушем, тегом, GitHub release или публикацией MCP Market-версии, если изменения затрагивают бытовой слой: `behavior-routing`, `project-intake`, `task-playbooks`, `reference-map`, `developer-primitives`, `developer-cards`, `first-answer-pitfalls`, `answer-contracts`, `core-grep-cookbook`, `eval-prompts` или навигацию `SKILL.md`.

## Stop conditions

Не релизить, если:

- `quick_validate.py` падает на `bitrix/` или `mcpmarket/bitrix/`, а repo-local fallback `scripts/validate_skill.py` тоже не проходит;
- `git diff --check` не пустой;
- `mcpmarket/bitrix` содержит больше 50 файлов;
- changelog не отражает новый reference/поведение;
- бытовой eval даёт `fail > 0`;
- compact `SKILL.md` не ссылается на новый critical reference;
- frontmatter `description` не покрывает новый важный trigger.

## Commands

```bash
python3 scripts/validate_skill.py
python3 /Users/igormajorov/.codex/skills/.system/skill-creator/scripts/quick_validate.py bitrix
python3 /Users/igormajorov/.codex/skills/.system/skill-creator/scripts/quick_validate.py mcpmarket/bitrix
git diff --check
find mcpmarket/bitrix -type f | wc -l
git status -sb
```

Expected:

- `scripts/validate_skill.py`: `All validation checks passed.`;
- both validates: `Skill is valid!`;
- `git diff --check`: no output;
- file count: `<= 50`;
- status: only intended files.

If `quick_validate.py` fails because the local Python has no `yaml` module, treat that as an environment issue and require `scripts/validate_skill.py` as fallback. It checks frontmatter, `agents/openai.yaml`, MCP file count, internal links, critical-reference sync, eval prompt coverage, forbidden markers and `git diff --check` without third-party packages.

## Everyday eval gate

Run at least 15 prompts from `eval-prompts.md` across different domains. Recommended set:

```text
B001, B004, B007, B009, B011, B013, B016, B018,
B021, B023, B025, B028, B030, B031, B043, B046
```

Threshold:

```text
prompts_checked >= 15
fail = 0
warn <= 3
```

`pass`: correct route, no bad first step, answer follows `answer-contracts.md`.
`warn`: correct but too generic or missing project checks/side effects.
`fail`: clean PHP/SQL/core edit/global cache-off/fake API/optional module assumed.

## Sync checklist

For every new critical reference:

- full file exists in `bitrix/references/`;
- compact file or compact bundle exists in `mcpmarket/bitrix/references/`;
- full and compact `SKILL.md` link it;
- related references mention it if needed;
- `CHANGELOG.md` mentions it;
- MCP Market file count remains below 50.

## Evidence table

```text
repo-local validate_skill: pass/fail
quick_validate bitrix: pass/fail
quick_validate mcpmarket: pass/fail
git diff --check: pass/fail
MCP Market files: N/50
changelog updated: yes/no
full/compact synced: yes/no
eval checked: N
eval fail: N
eval warn: N
```

## Release safety

- Do not commit, push, tag, or publish release without explicit user request.
- Before commit show `git status -sb` / `git diff --stat`.
- Before tag/release, ensure changelog/version are updated and tree is clean after commit.
