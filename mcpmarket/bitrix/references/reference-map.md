# Compact reference map

Открывай, когда `behavior-routing.md` выбрал режим, но нужно понять, какой compact bundle загрузить. MCP Market-версия хранит укрупнённые bundles вместо полной карты из full `bitrix/references/`.

| Задача | Bundle |
|---|---|
| Режим работы, аудит проекта, `BITRIX_PROJECT_CONTEXT.md` и типовые маршруты правок | `behavior-routing.md`, `project-intake.md`, `../assets/BITRIX_PROJECT_CONTEXT.template.md`, `task-playbooks.md`, `core-grep-cookbook.md` |
| Бытовой ответ: meta/head/assets/includes/request/user/images/cache/mail | `developer-primitives.md`, `first-answer-pitfalls.md`, `developer-cards.md`, `answer-contracts.md` |
| Release/eval бытового слоя | `eval-prompts.md`, `release-gate.md` |
| Core audit, version mismatch, tail modules, task routing, diagnostics, pitfalls, runtime smoke | `core-routing.md`, `version-impact.md`, `shop-core-tail-modules.md` |
| PHP architecture, production practice, modules, ORM, DB, events, validation, HTTP | `php-architecture.md` |
| Iblock/HL/UF/migrations/import-export/SEF | `content-data.md` |
| Components/templates/pagination/admin UI/file uploader | `components-admin-ui.md` |
| Users/RBAC/auth/session/security/socialservices | `users-security.md` |
| Blog/forum/vote/webforms/mail/subscribe | `content-modules.md` |
| Landing/sitecorporate/photogallery/fileman/location/messageservice/clouds/mobileapp/b24connector/translate | `site-cloud-mobile.md`, `shop-core-tail-modules.md` |
| Search/SEO/cache/update/perf/operations | `search-seo-ops.md` |
| REST/webhooks/apps/events | `integrations-rest.md` |
| Commerce: catalog/sale/currency/shop components/marketing/bizproc/webservice/1C | `commerce-shop.md` |

## Compact guardrails

- Если задача про конкретный repo — сначала `BITRIX_PROJECT_CONTEXT.md` при наличии, затем факты проекта, потом ответ.
- Если модуль optional — сначала module check; если версия отличается от baseline — `version-impact.md`.
- Не отвечать прямым SQL/core edit/global cache-off/manual meta первым вариантом.
- Для shop/1C не использовать commerce route без `catalog`/`sale`/`currency` checks.
- Для подробной полной карты использовать full edition `bitrix/references/reference-map.md`.
