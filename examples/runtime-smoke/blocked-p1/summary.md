# Runtime smoke evidence summary — blocked P1 sample

> Пример безопасного evidence pack без secrets и без реального ядра. Используй как образец честного `blocked`, а не как runtime pass.

- Дата: 2026-06-29
- Агент/оператор: sample
- Sandbox/project: sample sandbox unavailable
- Branch/commit: sample
- Public root: `www`
- Base URL: `http://localhost`
- Evidence directory: `examples/runtime-smoke/blocked-p1`
- Smoke package: `P1`
- Runtime scope: write-mode sandbox blocked

## Окружение

| Факт | Значение |
|---|---|
| PHP version/extensions | not checked |
| DB type/version/charset | not checked |
| Web server | not checked |
| Site IDs/languages/templates | not checked |
| Agent mode hit/cron | not checked |
| Mail/SMS mode | not checked |
| Payment/delivery/cashbox mode | not checked |
| Composite/cache mode | not checked |

## Модули и версии

| Module | Status | Version | Notes |
|---|---|---:|---|
| `main` | missing | | public root unavailable |
| `iblock` | missing | | public root unavailable |
| `catalog` | missing | | public root unavailable |
| `currency` | missing | | public root unavailable |
| `sale` | missing | | public root unavailable |
| `rest` | missing | | public root unavailable |
| `webservice` | missing | | public root unavailable |
| `sender` | missing | | public root unavailable |
| `bizproc` | missing | | public root unavailable |
| `pull` | missing | | public root unavailable |

## Вердикты сценариев

| Scenario | Verdict | Evidence file | Notes |
|---|---|---|---|
| P1-01 | blocked | P1-01-modules.md | write-mode sandbox не подтверждён |
| P1-02 | blocked | P1-02-catalog-list-detail.md | write-mode sandbox не подтверждён |
| P1-03 | blocked | P1-03-price-stock.md | write-mode sandbox не подтверждён |
| P1-04 | blocked | P1-04-offer-selection.md | write-mode sandbox не подтверждён |
| P1-05 | blocked | P1-05-guest-basket.md | write-mode sandbox не подтверждён |
| P1-06 | blocked | P1-06-auth-basket.md | write-mode sandbox не подтверждён |
| P1-07 | blocked | P1-07-order-save.md | write-mode sandbox не подтверждён |
| P1-08 | blocked | P1-08-cache-pass.md | write-mode sandbox не подтверждён |

## Findings

### Подтверждённые контракты

- Нет: это sample blocked pack, runtime pass не заявляется.

### Сломанные контракты

- Нет данных: sandbox не запущен.

### Заблокированные проверки

- P1 write-mode smoke заблокирован, потому что нет безопасного Bitrix sandbox с test catalog/order fixtures.
- Нельзя подключать production 1С, реальные оплаты, доставки, кассы, SMS/email или клиентские данные ради smoke.

## Нужные обновления references

- [ ] `bitrix/references/runtime-smoke-verification.md` — если blocker повторяется в реальном проекте.
- [ ] MCP Market compact bundle — если меняется общий runtime workflow.

## Cleanup

- Rollback/reset completed: not needed
- Remaining test data: none
- Follow-up risks: нужен отдельный sandbox перед write-mode P1
