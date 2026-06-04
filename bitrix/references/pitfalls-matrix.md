# Bitrix Pitfalls Matrix — типовые ловушки и диагностика

> Reference для Bitrix-скилла. Загружай, когда пользователь спрашивает о подводных камнях, “почему сломалось”, “в админке есть, а на сайте нет”, “после импорта/обновления/обмена всё странно”, “как не наступить на грабли”. Это routing matrix: конкретные API проверяй в модульных reference-файлах.

## Как пользоваться

1. Найди symptom row.
2. Пройди diagnostic chain слева направо.
3. Открой указанные module references.
4. Не предлагай fix, пока не подтверждён слой поломки.

## Общая цепочка диагностики

```text
module installed → data exists → site/language/rights → component params/filter/sort/pagination → template/result_modifier → cache/index/SEO → JS/AJAX → runtime events/agents/integrations
```

Если симптом магазинный, добавь:

```text
catalog product → offer/SKU → price/currency → stock/store → basket availability → discounts → checkout restrictions → order save → payment/shipment → external exchange/events
```

## Content / visibility

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| В админке есть, на сайте нет | `ACTIVE`, dates, site binding, section chain, rights, component filter, cache | inactive parent section, wrong `IBLOCK_ID`, `CHECK_PERMISSIONS`, stale component cache | `diagnostic-visibility.md`, `iblocks.md`, `components.md` |
| У админа видно, у гостя нет | groups, inherited rights, component params, composite cache | output cached under admin, missing anonymous rights, personal block cached publicly | `access-rbac.md`, `cache-infra.md`, `templates.md` |
| В списке нет, детальная открывается | list filter, section filter, pagination, sort, `INCLUDE_SUBSECTIONS` | unstable sort, wrong section, `PAGEN_N` conflict | `pagination.md`, `component-dataflow-debugging.md` |
| После правки ничего не меняется | component/tagged/managed/composite cache | cleared wrong cache layer, `result_modifier.php` not in cache key, composite static area | `index-cache-diagnostics.md`, `cache-infra.md` |
| Данные есть в `$arResult`, но нет HTML | template condition, JS replacement, CSS hidden, copied template drift | custom template dropped field, ajax rerender empty state | `component-dataflow-debugging.md`, `templates.md` |

## Components/templates

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| Правка stock component исчезла после обновления | location of edited file | edited `www/bitrix/modules/*/install/components` | `production-best-practices.md`, `components.md` |
| Custom template сломался после обновления ядра | compare copied template vs stock template | copied template frozen on old core contract | `templates.md`, `component-dataflow-debugging.md` |
| AJAX работает без прав/CSRF | endpoint path, auth, sessid | inline PHP endpoint, no `check_bitrix_sessid`, no rights | `events-routing.md`, `security.md`, `http.md` |
| Пагинация дублирует элементы | stable sort, count, `NavNum`, ajax params | same `PAGEN_N`, no deterministic sort, changed filter between pages | `pagination.md` |
| Lazy load отдаёт пусто | ajax payload, component params, page number, cache key | missing original filter/section/site/user context | `pagination.md`, `components.md` |

## IBlock / HL / UF

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| Свойство не сохраняется | property code/type, multiplicity, API path | wrong property format, missing file array, direct SQL | `iblocks.md`, `custom-uf-types.md` |
| HL entity не находится | table name, compiled entity, UF metadata cache | wrong HL name, managed cache, migrated numeric ID | `highloadblock.md`, `iblock-hl-relations.md` |
| Импорт плодит дубли | external key, XML_ID/CODE, idempotency | find by name, no external ID, no transaction/checkpoint | `import-export.md`, `operations-runbook.md` |
| После массовой загрузки поиск пустой | search index, `BeforeIndex`, module rights | imported via path without index side effects | `search.md`, `index-cache-diagnostics.md` |
| SEF detail URL ведёт не туда | `DETAIL_PAGE_URL`, `urlrewrite.php`, section code, canonical | mixed old/new URL templates | `sef-urls.md`, `seo-cache-access.md` |

## Catalog / product / SKU

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| Товар есть, но не виден | product active, section active chain, site binding, rights, component filter, cache | no active section, wrong catalog iblock, stale cache | `catalog.md`, `shop-standard-components.md`, `diagnostic-visibility.md` |
| Товар виден, но нельзя купить | price, currency, stock, `AVAILABLE`, offer selection, sale module, basket props | no price for group, zero stock, offer not selected, `CAN_BUY_ZERO` mismatch | `catalog.md`, `sale.md`, `commerce-workflows.md` |
| SKU/offer сломал карточку | offers iblock, `CML2_LINK`, offer props, selected offer id | product has no purchasable offer, deleted link property, template expects old SKU tree | `catalog.md`, `shop-standard-components.md` |
| Цена не обновилась | price type, currency, group rights, component price codes, cache | import wrote wrong price type, old component cache, base price mismatch | `catalog.md`, `currency.md`, `index-cache-diagnostics.md` |
| Остаток не совпадает | `b_catalog_product`, store stock, reservation, shipment/order lifecycle | total quantity vs store quantity, reserved quantity not considered | `catalog.md`, `sale.md` |
| Smart filter пустой/ломает URL | property index, section, filter params, SEF | index not rebuilt, wrong `FILTER_NAME`, property not enabled | `shop-standard-components.md`, `iblocks.md` |

## Basket / checkout / order

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| Add to basket не работает | product availability, offer id, basket props, site/fuser, AJAX response | adding product instead of offer, missing props, stale JS | `sale.md`, `catalog.md`, `shop-standard-components.md` |
| Корзина пустая после добавления | FUSER/session/site, basket storage, cache/composite | guest/session issue, site mismatch, personal block cached | `sale.md`, `session-auth.md`, `cache-infra.md` |
| Checkout не показывает доставку | location, person type, delivery restrictions, basket dimensions/price | wrong location code, restrictions by payment/price/site | `sale.md`, `commerce-workflows.md`, `location.md` |
| Checkout не показывает оплату | person type, payment restrictions, pay system active/site/currency | pay system not bound, currency mismatch | `sale.md`, `currency.md` |
| Заказ создаётся без письма | mail event, status/event handlers, queue, template, site | mail disabled, wrong event name/site, handler error | `sale.md`, `mail-notifications.md` |
| Заказ создан, но статус/отгрузка неверны | order lifecycle, payment/shipment save, event handlers | direct field update, missing shipment collection logic | `sale.md`, `commerce-workflows.md` |
| Скидка не применялась | coupon manager, user group, basket refresh, compatible discount layer | coupon not initialized, old basket state, group rights | `sale.md`, `catalog.md` |

## 1С / CommerceML

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| 1С не проходит `checkauth` | credentials, site, exchange option, session/cookie | wrong user/group rights, WAF/session issue | `commerce-1c-integration.md`, `session-auth.md`, `security.md` |
| `file` step грузит, `import` падает | temp dir, chunk/zip, XML validity, memory/time | broken XML, large file, old temp chunks | `commerce-1c-integration.md`, `operations-runbook.md` |
| Товары продублировались | XML_ID mapping, iblock mapping, external IDs | import matched by name/code, missing old XML_ID | `commerce-1c-integration.md`, `catalog.md` |
| Цены/остатки не обновились после обмена | price type/store mapping, offer mapping, import mode | wrong price type from 1С, store disabled, offer not linked | `commerce-1c-integration.md`, `catalog.md`, `currency.md` |
| Заказы не уходят в 1С | `sale.export.1c`, status filter, date filter, permissions | wrong export params, order not eligible, custom handler conflict | `commerce-1c-integration.md`, `sale.md` |
| StoreAssist “не обменялся” | module role | StoreAssist is checklist/onboarding, not exchange engine | `storeassist.md`, `commerce-1c-integration.md` |

## REST / webservice / integrations

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| REST method not found | module installed, scope, `methods`, `method.get`, controller route | method version mismatch, module disabled, wrong scope | `rest.md`, `shop-integrations-webservice.md` |
| REST event не прилетел | app binding, event table, offline events, auth, sale/catalog event fired | event not registered, order changed through path without event, webhook disabled | `shop-integrations-webservice.md`, `rest.md`, `sale.md` |
| External payment/delivery/cashbox app disappeared | app uninstall cleanup, handler tables | `onRestAppDelete` cleanup removed handlers | `shop-integrations-webservice.md`, `sale.md` |
| `webservice.sale` не даёт заказы | service contract | it returns aggregate sale statistics, not order CRUD | `shop-integrations-webservice.md`, `sale.md` |
| `webservice.statistic` пустой | statistic module/tables/options | no legacy statistic data, traffic not collected | `shop-integrations-webservice.md`, `shop-marketing-analytics.md` |
| SOAP endpoint leaks auth/test | endpoint access/logging | public test/checkauth exposure | `shop-integrations-webservice.md`, `security.md` |

## Search / SEO / cache

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| В поиске нет нового элемента | index, `BeforeIndex`, rights/site/url | write path skipped indexing, rights filter hides result | `search.md`, `index-cache-diagnostics.md` |
| SEO дубль страниц | SEF/urlrewrite/canonical/sort/filter pages | pagination/filter canonical missing/wrong | `seo-cache-access.md`, `sef-urls.md`, `pagination.md` |
| Sitemap не обновился | sitemap generation, site, iblock/SEO options | URL template mismatch, generation not rerun | `seo-cache-access.md` |
| Composite shows wrong personal data | dynamic areas, cache key, auth state | personal block in static cache | `templates.md`, `cache-infra.md`, `session-auth.md` |

## Users / auth / rights

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| Пользователь авторизован, но “нет доступа” | group membership, operations/tasks, inherited rights | stale session/groups, wrong task/operation | `users.md`, `access-rbac.md`, `session-auth.md` |
| После смены прав эффект не виден | session/cache, managed cache, user group reload | cached auth state | `session-auth.md`, `access-rbac.md`, `cache-infra.md` |
| Social login не работает | provider settings, callback URL, site, SSL | wrong redirect/callback, disabled provider | `socialservices.md` |
| OTP/WAF блокирует сценарий | security module rules, IP restrictions, redirects | security setting mistaken for app bug | `security.md` |

## Mail / SMS / marketing

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| Письмо не ушло | event type/template/site, mail queue, SMTP, handler errors | wrong event/site, disabled template, queue not processed | `mail-notifications.md` |
| SMS не ушла | provider, limits, phone normalization, queue/logs | provider inactive, bad phone format, rate/limit | `messageservice.md`, `shop-marketing-analytics.md` |
| Sender не отправляет | segment, consent, posting queue, agents | no contacts in segment, unsubscribe/consent, agent not running | `shop-marketing-analytics.md` |
| Баннер/клик не считается | advertising component, statistic/conversion hooks | statistic disabled, wrong banner contract | `shop-marketing-analytics.md` |

## Automation / agents / realtime

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| Agent не запускается | hit vs cron mode, schedule, module installed | agents disabled, long task in hit mode | `operations-runbook.md`, `update-stepper.md` |
| Stepper завис | state/checkpoint, batch size, error log | no resume state, memory/time limit | `update-stepper.md`, `operations-runbook.md` |
| Bizproc task не появился | provider/document type, template state, user rights | no provider for entity, template inactive, user mismatch | `shop-automation-bizproc.md` |
| Pull/realtime не обновляет | pull server config, channel/watch, JS init | pull not configured, no watch, websocket fallback issue | `shop-automation-bizproc.md`, `push-pull.md` |

## Release / update pitfalls

| Симптом | Главные проверки | Частые причины | Читать |
|---|---|---|---|
| После обновления ядра сломалась витрина | copied templates vs stock, component params, JS assets | stock contract changed, old copied template | `production-best-practices.md`, `components.md`, `templates.md` |
| После переноса стенда всё “почти работает” | module versions, site ids, iblock IDs/XML_ID, options, agents, files/clouds | numeric IDs differ, missing options/files | `operations-runbook.md`, `entities-migrations.md` |
| CI зелёный, runtime сломан | smoke route missing | only lint/tests, no Bitrix runtime check | `runtime-smoke-verification.md`, `php-testing.md` |

## Что нельзя делать

- Не фиксить симптом без определения слоя.
- Не менять права/кеш/SQL “наугад”.
- Не считать админскую видимость доказательством публичной видимости.
- Не считать successful import доказательством корректной карточки/checkout.
- Не считать созданный order доказательством корректной оплаты/доставки/обмена.
- Не обещать “всё покрыто” без runtime smoke evidence.

## С чем читать вместе

- Best practices — [production-best-practices.md](production-best-practices.md)
- Runtime smoke — [runtime-smoke-verification.md](runtime-smoke-verification.md)
- Visibility — [diagnostic-visibility.md](diagnostic-visibility.md)
- Component dataflow — [component-dataflow-debugging.md](component-dataflow-debugging.md)
- Cache/index — [index-cache-diagnostics.md](index-cache-diagnostics.md)
- Shop routing — [shop-task-matrix.md](shop-task-matrix.md)
