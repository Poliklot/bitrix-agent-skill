# Shop-core module inventory — полный снимок модулей интернет-магазина

> Reference для Bitrix-скилла. Загружай, когда нужно понять, какие модули реально есть в shop-core, что уже покрыто reference-слоем, что связано с интернет-магазином/1С, а что требует отдельного глубокого аудита перед обещаниями пользователю.

## Audit note

Truth layer: `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core/www/bitrix/modules`.

Снимок сделан по 49 директориям модулей. Для каждого модуля проверялись:
- `install/version.php` или, для `main`, `classes/general/version.php`;
- `install/components/bitrix/*`;
- `admin/*.php`;
- наличие `lib/*.php`, `classes/*.php`, install/db files;
- shop/1С-сигналы в названиях components/admin entrypoints: `catalog`, `sale`, `1c`, `exchange`, `order`, `basket`, `payment`, `delivery`, `store`, `sender`, `report`, `statistic`, `conversion`, `abtest`, `advertising`, `bizproc`, `workflow`.

Этот файл — **inventory**, а не замена глубоким references. Если модуль ниже помечен как `needs deep audit`, нельзя давать детальные API-рецепты без чтения его core-файлов. После добавления `shop-core-tail-modules.md` хвостовые модули закрыты как code-first routes, но без runtime smoke.

## Главное

Полный shop-core — это не только `catalog + sale + currency`.

В нём есть несколько слоёв:

1. **Runtime магазина** — `main`, `iblock`, `catalog`, `sale`, `currency`, `location`, `ui`, `highloadblock`.
2. **Shop solution / bootstrap** — `bitrix.eshop`, `storeassist`.
3. **1С / exchange** — `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`, sale/catalog admin endpoints, `storeassist_1c_*`; `webservice.sale` отдельно покрыт как SOAP/statistics, не CommerceML.
4. **Маркетинг и коммуникации** — `sender`, `mail`, `messageservice`, `subscribe`, `advertising`, `abtest`.
5. **Analytics / reports** — `report`, `statistic`, `conversion`, `perfmon`, `seo`.
6. **Automation** — `bizproc`, `bizprocdesigner`, `workflow`, `lists`, частично `pull`.
7. **Content/front adjacent** — `landing`, `calendar`, `idea`, `learning`, `support`, `wiki`, `bitrix.sitecorporate`, `form`, `blog`, `forum`, `vote`, `photogallery`, `search`.
8. **Platform/integration/safety** — `rest`, `b24connector`, `clouds`, `bitrixcloud`, `security`, `fileman`, `socialservices`, `mobileapp`, `translate`, `webservice`.

## Coverage status legend

- `covered` — уже есть отдельный reference или устойчивый слой в текущем skill.
- `covered-partial` — есть общий reference, но shop-specific часть не выделена полностью.
- `needs deep audit` — модуль есть в shop-core, но отдельный core-first reference ещё не сделан. После `shop-core-tail-modules.md` таких модулей в shop-core inventory не должно оставаться; если появятся новые, не давать API-рецепты без чтения core.
- `deferred per project` — даже если модуль есть в shop-core, в другом проекте активировать только после проверки `www/bitrix/modules/<module>`.

## Полная таблица модулей shop-core

| Модуль | Версия | Components | Admin | Shop/1С relevance | Coverage | Читать сейчас | Следующий шаг |
|---|---:|---:|---:|---|---|---|---|
| `abtest` | `26.0.0` | 0 | 5 | A/B тесты, отчёты, связка с conversion | covered | `shop-marketing-analytics.md` | держать вместе с conversion diagnostics |
| `advertising` | `24.200.0` | 2 | 14 | баннеры/реклама, public components `advertising.banner*` | covered | `shop-marketing-analytics.md` | держать связанным с eShop banner calls |
| `b24connector` | `25.0.0` | 2 | 9 | CRM/forms/widgets bridge, косвенно shop leads | covered | `b24connector.md`, `shop-core-tail-modules.md`, `rest.md` | shop lead/forms сценарии проверять по локальному connector route |
| `bitrix.eshop` | `25.0.0` | 3 | 1 | готовое eShop-решение, public/templates/demo data | covered | `shop-standard-components.md`, `commerce-workflows.md`, `templates.md` | держать wizard/templates связанными с shop components |
| `bitrix.sitecorporate` | `26.0.0` | 3 | 0 | corporate wizard, местами `furniture.catalog.*` | covered | `sitecorporate.md` | держать как non-shop с conditional catalog |
| `bitrixcloud` | `25.100.0` | 4 | 5 | backup/monitoring для shop runtime | covered | `bitrixcloud.md`, `operations-runbook.md` | нет срочного shop deep dive |
| `bizproc` | `26.200.0` | 49 | 8 | automation/robots/tasks, workflow engine | covered | `shop-automation-bizproc.md`, `workflow.md` | не обещать sale-order robots без provider-а |
| `bizprocdesigner` | `26.0.0` | 2 | 4 | редактор workflow templates | covered | `shop-automation-bizproc.md`, `workflow.md` | нет срочного shop deep dive |
| `blog` | `26.400.0` | 35 | 6 | комментарии/контент вокруг витрины | covered | `blog-socialnet.md` | нет срочного shop deep dive |
| `calendar` | `25.170.0` | 16 | 3 | mail/calendar side-channel, не core shop | covered | `shop-core-tail-modules.md` | соседний sync/resource/livefeed route; не checkout engine |
| `catalog` | `25.550.0` | 62 | 44 | товары, SKU, цены, склады, 1С catalog exchange | covered | `catalog.md`, `shop-standard-components.md`, `commerce-1c-integration.md`, `shop-integrations-webservice.md` | product subscription/report side effects см. `shop-marketing-analytics.md`; REST hooks см. `shop-integrations-webservice.md` |
| `clouds` | `25.100.0` | 0 | 8 | external file storage для catalog images/imports | covered | `clouds.md`, `file-upload-modern.md` | нет срочного shop deep dive |
| `conversion` | `25.0.0` | 0 | 4 | конверсия магазина, связка с A/B/statistic | covered | `shop-marketing-analytics.md` | держать вместе с A/B/statistic diagnostics |
| `currency` | `26.0.0` | 3 | 6 | валюты/курсы/форматирование денег | covered | `currency.md` | нет срочного shop deep dive |
| `fileman` | `25.200.200` | 11 | 37 | editor/files/maps, вспомогательно для витрины | covered | `fileman.md`, `templates.md` | нет срочного shop deep dive |
| `form` | `26.0.0` | 6 | 17 | формы, CRM bridge, заявки/лиды | covered | `webforms.md`, `b24connector.md` | проверить shop lead forms при задаче |
| `forum` | `26.0.0` | 34 | 20 | comments/discussions, не core checkout | covered | `forum.md` | нет срочного shop deep dive |
| `highloadblock` | `25.100.0` | 3 | 10 | directory props, refs, auxiliary product data | covered | `highloadblock.md`, `iblock-hl-relations.md` | нет срочного shop deep dive |
| `iblock` | `25.300.0` | 55 | 29 | основа public `catalog.*` components, properties/sections | covered | `iblocks.md`, `pagination.md`, `shop-standard-components.md` | нет срочного shop deep dive |
| `idea` | `25.0.0` | 13 | 0 | идеи/feedback/statistic, не core shop | covered | `shop-core-tail-modules.md` | feedback route; не CRM/sale engine |
| `landing` | `26.200.0` | 59 | 5 | landing pages, catalog carousel blocks | covered | `landing.md`, `shop-core-tail-modules.md`, `catalog.md` | catalog blocks are presentation/connectors, not product truth |
| `learning` | `25.0.0` | 15 | 23 | обучение, не core shop | covered | `shop-core-tail-modules.md` | education route; не CommerceML/shop sale без локальной связки |
| `lists` | `25.600.100` | 19 | 0 | processes/lists, связка с bizproc/iblock | covered | `shop-automation-bizproc.md`, `workflow.md` | нет срочного shop deep dive |
| `location` | `25.400.0` | 0 | 0 | адреса и locations для доставки/checkout | covered | `location.md`, `sale.md` | нет срочного shop deep dive |
| `mail` | `26.100.200` | 18 | 14 | mailbox/client/signatures, sender/mail pipeline | covered | `mail-notifications.md`, `shop-marketing-analytics.md` | нет срочного shop deep dive |
| `main` | `26.150.0` | 82 | 112 | runtime, users, sessions, cache, pagination, mail helpers | covered | `modules-loader.md`, `pagination.md`, `session-auth.md` | нет срочного shop deep dive |
| `messageservice` | `25.200.100` | 2 | 2 | SMS providers, sender limits/config | covered | `messageservice.md`, `mail-notifications.md`, `shop-marketing-analytics.md` | нет срочного shop deep dive |
| `mobileapp` | `25.0.100` | 15 | 2 | mobile/admin mobile, sale mobile components используют `sale` | covered | `mobileapp.md`, `shop-core-tail-modules.md`, `sale.md` | sale mobile order components remain in `sale` |
| `perfmon` | `25.300.0` | 0 | 22 | performance diagnostics для магазина | covered | `perfmon.md`, `operations-runbook.md` | нет срочного shop deep dive |
| `photogallery` | `25.100.0` | 17 | 0 | galleries, не core shop | covered | `photogallery.md` | нет срочного shop deep dive |
| `pull` | `25.300.0` | 1 | 0 | realtime/push, counters/watches/transport | covered | `shop-automation-bizproc.md`, `push-pull.md` | runtime server config по задаче |
| `report` | `25.100.0` | 19 | 0 | report builder / visualconstructor | covered | `shop-marketing-analytics.md` | domain-specific helper class по задаче |
| `rest` | `26.0.0` | 42 | 2 | webhooks/OAuth/apps, внешние shop integrations | covered | `rest.md`, `shop-integrations-webservice.md`, `http.md` | runtime scopes/events проверять через `methods`/`method.get` |
| `sale` | `26.0.0` | 78 | 172 | basket/order/checkout/payment/delivery/discounts/1С | covered | `sale.md`, `shop-standard-components.md`, `commerce-workflows.md`, `commerce-1c-integration.md`, `shop-marketing-analytics.md`, `shop-automation-bizproc.md`, `shop-integrations-webservice.md` | order robots требуют provider/CRM/custom module проверки; REST/webservice см. integration reference |
| `search` | `25.200.0` | 6 | 9 | product search/index | covered | `search.md`, `index-cache-diagnostics.md` | нет срочного shop deep dive |
| `security` | `25.0.0` | 3 | 25 | WAF/OTP/security hardening for exchange/admin | covered | `security.md` | проверить 1С security toggles в exchange audit |
| `sender` | `26.0.0` | 65 | 13 | campaigns, triggers, templates, contact segments | covered | `shop-marketing-analytics.md`, `mail-notifications.md`, `messageservice.md` | нет срочного shop deep dive |
| `seo` | `25.100.400` | 2 | 15 | SEO, meta, sitemap, catalog SEO side effects | covered | `seo-cache-access.md`, `catalog.md` | нет срочного shop deep dive |
| `socialservices` | `26.0.0` | 3 | 0 | OAuth/social login | covered | `socialservices.md`, `users.md` | нет срочного shop deep dive |
| `statistic` | `26.0.0` | 1 | 66 | traffic/statistics, reports/conversion | covered | `shop-marketing-analytics.md` | следить за runtime/perf side effects |
| `storeassist` | `24.0.0` | 0 | 15 | shop setup assistant, 1С onboarding pages | covered | `storeassist.md`, `commerce-1c-integration.md` | держать связанным с 1С diagnostics |
| `subscribe` | `25.0.0` | 5 | 12 | legacy subscriptions/mailings | covered | `subscribe.md`, `mail-notifications.md`, `shop-marketing-analytics.md` | нет срочного shop deep dive |
| `support` | `26.0.0` | 5 | 27 | support/tickets/coupons, не core shop | covered | `shop-core-tail-modules.md` | ticket/SLA route; order link только если есть project glue |
| `translate` | `25.100.0` | 2 | 6 | localization/lang files | covered | `translate.md` | нет срочного shop deep dive |
| `ui` | `26.150.0` | 16 | 0 | grid/filter/entity selector/uploader UI | covered | `grid-admin-modern.md`, `file-upload-modern.md` | нет срочного shop deep dive |
| `vote` | `26.0.0` | 11 | 15 | polls/votes | covered | `vote.md` | нет срочного shop deep dive |
| `webservice` | `26.0.0` | 5 | 0 | `webservice.sale`, `webservice.statistic`, SOAP/WSDL, stssync | covered | `shop-integrations-webservice.md`, `http.md`, `sale.md`, `shop-marketing-analytics.md` | не путать с CommerceML/1С exchange |
| `wiki` | `25.0.0` | 9 | 0 | wiki/content, not core shop | covered | `shop-core-tail-modules.md` | content/social route; not shop KB без локального route |
| `workflow` | `26.0.0` | 0 | 10 | legacy workflow, statuses/history/files | covered | `shop-automation-bizproc.md`, `workflow.md` | нет срочного shop deep dive |

## Shop-critical modules already deep enough for baseline

### `catalog` 25.550.0

Confirmed signals:
- components: `catalog.import.1c`, `catalog.export.1c`, `catalog.product.grid`, `catalog.productcard.*`, `catalog.store.*`, `catalog.store.document.*`, `catalog.report.store_*`, `catalog.product.subscribe*`, `catalog.viewed.products`;
- admin: `1c_import.php`, `1c_admin.php`, `cat_catalog_*`, `cat_store_*`, `cat_discount_*`, coupon pages;
- reference coverage: `catalog.md`, `currency.md`, `commerce-1c-integration.md`, `commerce-workflows.md`, `shop-integrations-webservice.md` для REST.

Baseline is good for product/SKU/price/store/1С import-export tasks. Component-by-component storefront/admin map for `catalog.section`, `catalog.smart.filter`, compare, viewed/recommended and reports is covered by `shop-standard-components.md`; marketing/report side effects are routed through `shop-marketing-analytics.md`; catalog REST/controllers/events/placement are routed through `shop-integrations-webservice.md`.

### `sale` 26.0.0

Confirmed signals:
- components: `sale.basket.*`, `sale.basket.order.ajax`, `sale.order.ajax`, `sale.order.checkout`, `sale.personal.*`, `sale.export.1c`, `sale.delivery.*`, `sale.discount.coupon.mail`, `sale.bigdata.*.mail`, `sale.mobile.order.*`;
- admin: `1c_exchange.php`, `order_*`, `delivery_*`, `pay_system_*`, `cashbox_*`, `discount_*`, `exchange_log.php`, reports;
- reference coverage: `sale.md`, `commerce-workflows.md`, `commerce-1c-integration.md`, `shop-integrations-webservice.md` для REST/webservice.

Baseline is good for basket/order/payment/shipment/delivery/discount/1С order exchange tasks. Basket/order/personal/payment/delivery component routing is covered by `shop-standard-components.md`; marketing side effects are routed through `shop-marketing-analytics.md`; automation/bizproc routing is covered by `shop-automation-bizproc.md`; sale REST/webservice integration extras are covered by `shop-integrations-webservice.md`, but sale-order robots still require a confirmed provider/CRM/custom module.

### `currency` 26.0.0

Confirmed signals:
- components: `currency.field.money`, `currency.money.input`, `currency.rates`;
- admin: currency/rate/classifier pages;
- reference coverage: `currency.md`.

Good enough for catalog prices and sale sums.

## Ordered code-first modules completed

### Completed. Shop standard components

Covered by `shop-standard-components.md`:
- iblock-hosted catalog components: `catalog`, `catalog.section`, `catalog.element`, `catalog.smart.filter`, `catalog.compare.*`, `catalog.search`, `catalog.top`, `catalog.sections.top`;
- sale components: `sale.basket.*`, `sale.basket.order.ajax`, `sale.order.ajax`, `sale.order.checkout`, `sale.personal.*`, `sale.order.payment*`, `sale.store.choose`;
- catalog module components: `catalog.product.grid`, `catalog.productcard.*`, `catalog.store.*`, `catalog.report.store_*`;
- `bitrix.eshop` wizard/template component calls and own `eshop.*` components.

### Completed. Marketing/analytics

Covered by `shop-marketing-analytics.md`:
- `sender` 26.0.0;
- `mail` 26.100.200;
- `messageservice` 25.200.100;
- `subscribe` 25.0.0;
- `advertising` 24.200.0;
- `abtest` 26.0.0;
- `conversion` 25.0.0;
- `report` 25.100.0;
- `statistic` 26.0.0;
- eShop/public hooks and sale-side sender/statistic connectors.

### Completed. Automation

Covered by `shop-automation-bizproc.md`:
- `bizproc` 26.200.0;
- `bizprocdesigner` 26.0.0;
- `workflow` 26.0.0;
- `lists` 25.600.100;
- `pull` 25.300.0 where realtime effects matter;
- iblock/list process routing and sale-order automation boundary.

### Completed. Webservice/integration extras

Covered by `shop-integrations-webservice.md`:
- `webservice` 26.0.0, `webservice.server`, `webservice.checkauth`, `webservice.sale`, `webservice.statistic`, `stssync.server`;
- SOAP/WSDL descriptors, tools/endpoints and security boundaries;
- `rest` 26.0.0 apps/webhooks/events/placements/auth/batch/method discovery;
- sale REST controllers/events and explicit pay_system/delivery/cashbox scopes;
- catalog REST controllers/events and `CATALOG_EXTERNAL_PRODUCT` placement;
- B24 sale exchange/integration boundary vs 1С CommerceML.

## Do not overclaim

- Do not say “все shop-core модули глубоко покрыты” until runtime-smoke is done. Standard shop components are covered by `shop-standard-components.md`, marketing/analytics by `shop-marketing-analytics.md`, automation by `shop-automation-bizproc.md`, webservice/REST by `shop-integrations-webservice.md`; production guidance and smoke format live in `production-best-practices.md`, `pitfalls-matrix.md`, `runtime-smoke-verification.md`.
- Do not activate `bizproc`, `bizprocdesigner`, `workflow`, `lists`, `pull`, `sender`, `report`, `statistic`, `abtest`, `conversion`, `advertising`, `webservice` in another project unless the module exists locally.
- Do not infer `sale/catalog` from `iblock` components alone: `iblock` ships `catalog.*` public components even when the `catalog` module may be missing in another checkout.
- Do not use this inventory as API documentation by itself. For tail modules use `shop-core-tail-modules.md`; for runtime claims use `runtime-smoke-verification.md`.

## Ordered roadmap from this inventory

1. Docker/runtime smoke — because current coverage is code-first and still needs DB/runtime fixtures; use `runtime-smoke-verification.md` as the evidence format.
2. Deferred per-project modules only when a task needs them.
