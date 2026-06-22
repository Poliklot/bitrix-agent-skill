# Режимы поведения

Открывай в начале задачи, если неясно, какой слой нужен. Цель — не грузить все bundles и не превращать простой вопрос в лекцию.

Главное правило: если доступен проект и вопрос практический, сначала прочитать `BITRIX_PROJECT_CONTEXT.md` при наличии, затем получить project fact через `project-intake.md` или `core-grep-cookbook.md`, потом отвечать.

## Decision

1. Bitrix marker есть (`/bitrix`, `/local`, `CIBlock*`, `ShowHead`, `IncludeComponent`, `sale`, `catalog`, `1C`, `Битрикс`) → skill applies.
2. User says “у нас”, “в проекте”, “найди”, “почини”, “почему не работает” → `BITRIX_PROJECT_CONTEXT.md` if present, then `project-intake.md`, then `task-playbooks.md` for common fix routes.
3. Short “как сделать X” → `developer-primitives` + `first-answer-pitfalls` + `developer-cards` + `answer-contracts`.
4. Debug symptom → `core-grep-cookbook` + relevant compact bundle.
5. `sale`/`catalog`/`1C` → module check first, then commerce bundle.
6. “Как правильно/best practices/куда класть” → production sections in `php-architecture`/`core-routing`.
7. Release/publish → `release-gate`.

## Modes

| Mode | Trigger | Load | Output |
|---|---|---|---|
| Everyday answer | meta/title, CSS/JS, includes, breadcrumbs, request, user, image, iblock property, cache, mail | primitives, pitfalls, cards, contracts; project grep if repo exists | Mechanism, project checks, minimal example, side effects. |
| Project-first fix | “найди где”, “почини”, “у нас” | project-intake, task-playbooks, core-grep, domain bundle | Concrete file/layer, reason, patch or next action. |
| Debug chain | “не выводится”, “не обновляется”, “404 200”, “письмо не уходит” | core-grep + diagnostics/domain bundle | Source → params → template/result → cache/rights/index/logs. |
| Component/template | IncludeComponent, template, `$arResult` | components-admin-ui | Params/template/result_modifier/component_epilog/local component. |
| Production practice | “как правильно”, architecture, safe customization | php-architecture/core-routing | local module/service/migration/event, verification. |
| Module-dependent | iblock/form/catalog/sale/currency/rest/bizproc/pull | module check + domain bundle | API route if present; fallback/deferred if missing. |
| Shop/1C | SKU, prices, stocks, basket, order, CommerceML | commerce-shop after module check | API-only route with recalculation/events/exchange side effects. |
| Data mutation | direct DB/content/rights/file/admin change | SKILL confirmation block | Ask confirmation before mutation. |
| Release | push/tag/release/MCP Market | release-gate/eval-prompts | Validate, eval, file count, changelog/version sync. |

## Avoid

- General theory when project facts are available.
- Loading many bundles before choosing mode.
- Long architecture answer for a one-line everyday question.
- Clean PHP/SQL/core edit as first route.
- Assuming optional modules.
- Global cache-off before cache-layer diagnosis.
