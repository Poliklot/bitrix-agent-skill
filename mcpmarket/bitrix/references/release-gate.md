# Release gate

Открывай перед пушем, тегом, GitHub release или публикацией MCP Market-версии, если изменения затрагивают бытовой слой: `behavior-routing`, `project-intake`, `project-layout-and-includes`, `project-configuration`, `task-playbooks`, `reference-map`, `developer-primitives`, `developer-cards`, `first-answer-pitfalls`, `answer-contracts`, `core-grep-cookbook`, `eval-prompts` или навигацию `SKILL.md`.

## Stop conditions

Не релизить, если:

- `quick_validate.py` падает на `bitrix/` или `mcpmarket/bitrix/`, а repo-local fallback `scripts/validate_skill.py` тоже не проходит;
- `git diff --check` не пустой;
- `mcpmarket/bitrix` содержит больше 50 файлов;
- changelog не отражает новый reference/поведение, `bitrix/VERSION` не имеет секции в `CHANGELOG.md`, `PLAN.md` не упоминает текущую версию;
- runtime smoke templates, `scripts/init_runtime_evidence.py` или `scripts/validate_runtime_evidence.py` отсутствуют после изменений runtime smoke слоя;
- `scripts/bitrix_runtime_preflight.py`, `Makefile`, `.github/workflows/validate.yml` или sample blocked evidence отсутствуют после изменений release/evidence workflow;
- optimization evidence templates, `scripts/init_optimization_evidence.py`, `scripts/validate_optimization_evidence.py` или sample candidate pack отсутствуют после изменений optimization audit слоя;
- бытовой eval даёт `fail > 0`;
- compact `SKILL.md` не ссылается на новый critical reference;
- frontmatter `description` не покрывает новый важный trigger.

## Commands

```bash
make validate
make release-check
python3 scripts/validate_skill.py
python3 scripts/bitrix_runtime_preflight.py --public-root www --base-url http://localhost
python3 scripts/init_runtime_evidence.py --package P1 --output /tmp/bitrix-p1-evidence-check
python3 scripts/init_runtime_evidence.py --all --output /tmp/bitrix-all-evidence-check
python3 scripts/validate_runtime_evidence.py examples/runtime-smoke/blocked-p1 --package P1
python3 scripts/init_optimization_evidence.py --output /tmp/bitrix-optimization-evidence-check --finding-count 2
python3 scripts/validate_optimization_evidence.py examples/optimization-evidence/sample-candidate
python3 scripts/validate_runtime_evidence.py path/to/evidence/YYYY-MM-DD-p1-shop-path --package P1  # если есть runtime evidence pack
python3 /Users/igormajorov/.codex/skills/.system/skill-creator/scripts/quick_validate.py bitrix
python3 /Users/igormajorov/.codex/skills/.system/skill-creator/scripts/quick_validate.py mcpmarket/bitrix
git diff --check
find mcpmarket/bitrix -type f | wc -l
git status -sb
```

Expected:

- `scripts/validate_skill.py`: `All validation checks passed.`;
- `make validate`: repo-local validation, sample blocked evidence и shell syntax check проходят;
- `scripts/init_runtime_evidence.py`: создаёт `summary.md`, `00-preflight.md` и scenario files;
- `scripts/init_runtime_evidence.py --all`: создаёт P1–P4 подкаталоги;
- `scripts/init_optimization_evidence.py`: создаёт `summary.md`, `00-runtime-metrics.md` и `OPT-001-finding.md`;
- `scripts/bitrix_runtime_preflight.py`: печатает Markdown preflight без secrets;
- `scripts/validate_runtime_evidence.py`: `Runtime evidence validation passed.`, если релиз включает runtime evidence pack;
- `scripts/validate_optimization_evidence.py`: `Optimization evidence validation passed.`, если релиз включает optimization audit evidence pack;
- both validates: `Skill is valid!`;
- `git diff --check`: no output;
- file count: `<= 50`;
- status: only intended files.

If `quick_validate.py` fails because the local Python has no `yaml` module, treat that as an environment issue and require `scripts/validate_skill.py` as fallback. It checks frontmatter, `agents/openai.yaml`, MCP file count, internal links, critical-reference sync, runtime smoke templates/validator, eval prompt coverage, forbidden markers and `git diff --check` without third-party packages.

## Optimization evidence gate

Если в релиз входят optimization audit findings или утверждение “исправлено/подтверждено”, запустить:

```bash
python3 scripts/init_optimization_evidence.py --output evidence/YYYY-MM-DD-optimization-audit --finding-count 5
python3 scripts/bitrix_static_optimization_audit.py /path/to/project --output evidence/YYYY-MM-DD-optimization-audit/static-audit.md
python3 scripts/validate_optimization_evidence.py evidence/YYYY-MM-DD-optimization-audit
python3 scripts/validate_optimization_evidence.py examples/optimization-evidence/sample-candidate
```

Структура: `summary.md`, `00-runtime-metrics.md`, `OPT-001-finding.md`. Verdicts: `candidate`, `confirmed`, `blocked`, `fixed`, `accepted-risk`. `candidate/blocked` — не runtime pass.

## Runtime evidence gate

Если в релиз входит runtime evidence pack или утверждение “runtime-проверено”, запустить:

```bash
python3 scripts/init_runtime_evidence.py --package P1 --output evidence/YYYY-MM-DD-p1-shop-path
python3 scripts/bitrix_runtime_preflight.py --public-root www --base-url http://localhost > evidence/YYYY-MM-DD-p1-shop-path/00-preflight.md
python3 scripts/init_runtime_evidence.py --all --output evidence/YYYY-MM-DD-runtime-smoke-all
python3 scripts/validate_runtime_evidence.py evidence/YYYY-MM-DD-p1-shop-path --package P1
python3 scripts/validate_runtime_evidence.py examples/runtime-smoke/blocked-p1 --package P1
```

Для `P2–P4` заменить `--package`. `blocked` — допустимый finding, но не runtime pass; в changelog/reference писать “runtime verification blocked by X”.

## Everyday eval gate

Run at least 15 prompts from `eval-prompts.md` across different domains. Recommended set:

```text
B001, B004, B007, B009, B011, B013, B016, B018,
B021, B023, B025, B028, B030, B031, B043, B046,
B048, B052, B053, B057, B060, B061, B062, B063, B064,
B065, B066, B067, B068, B069, B070, B071, B072, B073, B074
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
sample blocked evidence: pass/fail
eval checked: N
eval fail: N
eval warn: N
```

## Release safety

- Do not commit, push, tag, or publish release without explicit user request.
- Before commit show `git status -sb` / `git diff --stat`.
- Before tag/release, ensure changelog/version are updated and tree is clean after commit.

## Контракт диагностических доказательств

Команды `scripts/*.py` доступны из checkout репозитория навыка; установленная отдельно папка `bitrix/` или compact bundle не включает эти repo-local helpers. Не предполагай их наличие в клиентском проекте. Если checkout отсутствует, используй этот контракт для ручной проверки, не создавая фиктивный результат запуска.

- Preflight только читает файлы: `candidate` не означает готовый sandbox, `blocked` — версия `main` недоступна; `runtime_status` всегда `not_checked`. Код возврата 0 означает сформированный отчёт, а не runtime pass. Модули требуют отдельной проверки регистрации/загрузки. Совместимость: старый `status: pass` заменён на `candidate`, непроверенные строки имеют `missing-or-unreadable`.
- `main/classes/general/version.php` и `SM_VERSION` проверяются первыми, `main/install/version.php` — запасной источник. Это статический разбор известных форм записи, а не PHP parser или запуск ядра.
- Отчёты содержат пути, строки и фиксированные признаки вместо исходного кода. Base URL сохраняется только как HTTP(S) origin: без credentials, пути, query и fragment. Пути/hostname тоже могут быть приватными — вручную проверить перед публикацией.
- Сканеры не следуют символьным ссылкам, исключают кеши/вложения и не доказывают полноту аудита. Для общего ядра за ссылкой выбери его реальный корень явно; не обходи границу автоматически. `--module` принимает только идентификатор, не путь.
- Evidence pack для автоматической проверки — обычные локальные UTF-8 текстовые файлы без NUL, каждый не больше 2 000 000 байт. Нечитаемые файлы, ссылки, бинарные и oversized-вложения означают отказ, а не чистую проверку. Скриншоты/архивы требуют отдельного просмотра; в текстовый pack положи обезличенное описание результата, не переименовывай бинарный файл ради обхода.
- Runtime summary использует таблицу `Scenario / Verdict / Evidence file / Notes`. ID уникальны и известны P1–P4; ссылка относительная и указывает на файл внутри pack. Файл содержит совпадающие `ID сценария` (или `Scenario`) и один `Verdict`. Для `fail`/`blocked` нужна непустая причина; для `pass` — непустой `## Evidence`. Старый free-form summary и поиск файла только по префиксу больше не принимаются.
- Optimization summary требует уникальные ID и локальные finding-файлы с совпадающими `ID`, `Priority`, `Layer`, `Verdict`. Внешняя ссылка может быть дополнительным источником, но не заменяет finding. Для `confirmed`/`fixed` добавить `- Runtime evidence: relative-file.txt` на отдельный непустой локальный artifact и `- Status: pass`; `candidate` не подтверждает ускорение.
- Оба валидатора ищут известные признаки секретов, но не доказывают отсутствие всех секретов/персональных данных и не проверяют подлинность измерений. Успешная структурная проверка не превращает `blocked` или учебную фикстуру в runtime pass.
- Генераторы сначала готовят все шаблоны и проверяют коллизии. Без `--force` существующие назначения не меняются; с `--force` каждый файл заменяется атомарно, но операция над всем каталогом не транзакционна. Ошибка диска/процесса может оставить частичный набор — проверить его перед повтором. Существующий static report не перезаписывается, его имя не может совпадать с generated files.
- `.evidence-init.lock` сериализует запуски генераторов в одном output. После аварии не удалять lock автоматически: сначала убедиться, что владелец завершился. Не запускать другие редакторы/процессы записи одновременно; это локальные инструменты, не защита от враждебной подмены файлов во время проверки.
- `make test` запускает поведенческие и отрицательные тесты без сторонних зависимостей; `make validate` включает их автоматически, поэтому Validate Skill и Publish Release используют тот же gate. Изменение ожидаемого результата теста не заменяет исправление причины.
