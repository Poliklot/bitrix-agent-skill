# Runtime smoke evidence summary

> Summary одного smoke-прохода. Этот файл можно коммитить только после удаления secrets, cookies, session ids, реальных клиентских данных, production XML/дампов, tokens, license keys и приватных payloads.

- Дата:
- Агент/оператор:
- Sandbox/project:
- Branch/commit:
- Public root:
- Base URL:
- Evidence directory:
- Smoke package: `P1` / `P2` / `P3` / `P4` / mixed
- Runtime scope: read-only / write-mode sandbox

## Окружение

| Факт | Значение |
|---|---|
| PHP version/extensions | |
| DB type/version/charset | |
| Web server | |
| Site IDs/languages/templates | |
| Agent mode hit/cron | |
| Mail/SMS mode | |
| Payment/delivery/cashbox mode | |
| Composite/cache mode | |

## Модули и версии

| Module | Status | Version | Notes |
|---|---|---:|---|
| `main` | found/missing | | |
| `iblock` | found/missing | | |
| `catalog` | found/missing | | |
| `currency` | found/missing | | |
| `sale` | found/missing | | |
| `rest` | found/missing | | |
| `webservice` | found/missing | | |
| `sender` | found/missing | | |
| `bizproc` | found/missing | | |
| `pull` | found/missing | | |

## Вердикты сценариев

| Scenario | Verdict | Evidence file | Notes |
|---|---|---|---|
| P1-01 | pass/fail/blocked | | |
| P1-02 | pass/fail/blocked | | |
| P1-03 | pass/fail/blocked | | |
| P1-04 | pass/fail/blocked | | |
| P1-05 | pass/fail/blocked | | |
| P1-06 | pass/fail/blocked | | |
| P1-07 | pass/fail/blocked | | |
| P1-08 | pass/fail/blocked | | |

## Findings

### Подтверждённые контракты

-

### Сломанные контракты

-

### Заблокированные проверки

-

## Нужные обновления references

- [ ] `bitrix/references/catalog.md`
- [ ] `bitrix/references/sale.md`
- [ ] `bitrix/references/commerce-1c-integration.md`
- [ ] `bitrix/references/shop-task-matrix.md`
- [ ] `bitrix/references/runtime-smoke-verification.md`
- [ ] MCP Market compact bundle

## Cleanup

- Rollback/reset completed: yes/no/not needed
- Remaining test data:
- Follow-up risks:
