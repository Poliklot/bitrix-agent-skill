# План и статус аудита Bitrix-скилла

## Цель

Поддерживать `bitrix-agent-skill` как **core-first** навык для 1C-Bitrix CMS: все утверждения, примеры API и маршруты должны опираться на реально установленное ядро проекта, а не на память, форумы или “типичный Bitrix”.

## Текущий статус

На дату этого плана:
- актуальная версия навыка: `1.26.0`;
- точка входа: `bitrix/SKILL.md`;
- reference-слой: `bitrix/references/*.md`;
- non-commerce reference-слой прошёл ревизию против установленного core;
- PHP workflow/testing/quality, legacy modernization, diagnostics, standard components и operations-runbook закрыты как активный non-commerce контур;
- отдельный shop-core установлен и переаудирован inventory-слоем: 49 модулей, включая `catalog` 25.550.0, `sale` 26.0.0, `currency` 26.0.0, `bitrix.eshop` 25.0.0, 1С/CommerceML components;
- магазинный контур активируется только после проверки этих модулей в конкретном проекте;
- полный shop-core module inventory вынесен в `shop-core-module-inventory.md`: versions, component/admin counts, coverage status и ordered roadmap uncovered зон;
- `storeassist` 24.0.0 глубоко разобран как мастер/чеклист магазина и 1С onboarding, а не exchange engine;
- standard shop components разобраны по shop-core: iblock-hosted `catalog.*`, catalog productcard/store/report/admin components, sale basket/order/personal/payment/delivery components и `bitrix.eshop` wizard layer;
- marketing/analytics слой магазина разобран по shop-core: `sender`, `mail`, `messageservice`, `subscribe`, `advertising`, `abtest`, `conversion`, `report`, `statistic`, eShop hooks и sale-side side effects;
- automation/bizproc слой магазина разобран по shop-core: `bizproc`, `bizprocdesigner`, legacy `workflow`, `lists`, `pull`, templates/states/tasks, robots/triggers, list processes и realtime diagnostics;
- integration/webservice слой магазина разобран по shop-core: `webservice`, `webservice.sale`, `webservice.statistic`, SOAP/WSDL, `stssync`, REST apps/webhooks/events/placements, sale/catalog REST controllers/events и external app handlers;
- production best-practices слой добавлен как cross-cutting маршрут: update-safe кастомизация, D7 vs legacy, boundary/service layer, side effects, cache/index/RBAC, security, performance, pitfalls matrix и runtime smoke verification plan;
- developer-primitives слой добавлен как быстрый бытовой маршрут: meta/title/head, Asset, IncludeFile, breadcrumbs, request/current user, Loader, CFile, Loc и другие типовые Bitrix-примитивы;
- пагинационный слой переаудирован по `main` 26.150.0 и shop-core: legacy `CDBResult`, D7 `PageNavigation`, `system.pagenavigation`, `main.pagenavigation`, admin/grid и ajax/lazy load.

## Активный и условный контур

### Активный non-commerce маршрут

Сейчас навык должен вести задачи прежде всего в подтверждённые домены:
- `main`
- `iblock`
- `blog`
- `forum`
- `vote`
- `form`
- `landing`
- `socialservices`
- `highloadblock`
- `rest`
- `search`
- `seo`
- `subscribe`
- `ui`
- `perfmon`
- `security`
- `clouds`
- `bitrixcloud`
- `fileman`
- `location`
- `messageservice`
- `mobileapp`
- `b24connector`
- `photogallery`
- `translate`
- PHP workflow/testing/quality и legacy modernization
- diagnostics: visibility, pagination, cache/index, component dataflow
- operations: agents/cron/stepper, backup/monitoring, переносы, perf diagnostics
- проектные оверрайды в `local/*`

### Условный commerce/deferred-маршрут

Эти домены становятся активными только после подтверждения соответствующего модуля в `www/bitrix/modules`:
- `catalog`
- `sale`
- `currency`
- `bizproc`
- `pull`
- `socialnet`
- `webservice` / SOAP
- `rest` / внешние app hooks
- обмен с `1С` / `CommerceML`
- магазинные workflow в целом: торговые предложения, цены, остатки, склады, корзина, checkout, оплата, доставка, скидки, заказы, отгрузки, возвраты, REST/webservice integrations

Для shop-core-аудита эти домены уже подтверждены и описаны в `catalog.md`, `sale.md`, `currency.md`, `commerce-workflows.md`, `commerce-1c-integration.md`, `shop-standard-components.md`, `shop-marketing-analytics.md`, `shop-automation-bizproc.md`, `shop-integrations-webservice.md`, `production-best-practices.md`, `pitfalls-matrix.md`, `runtime-smoke-verification.md`, `shop-task-matrix.md`.

Важно: наличие `catalog.*` standard components внутри `iblock` или шаблонов не доказывает наличие полноценного магазинного core. Активировать commerce-маршрут можно только после проверки реальных модулей и их runtime-контрактов.

## Структура репозитория

```text
bitrix-agent-skill/
├── README.md
├── PLAN.md
├── CHANGELOG.md
├── install.sh
├── bitrix/
│   ├── SKILL.md
│   ├── VERSION
│   ├── update.sh
│   └── references/
│       ├── *.md
│       └── ...
└── LICENSE
```

## Что уже сделано

### Core-first правила

- В `SKILL.md` зафиксирован приоритет локального ядра и проектных оверрайдов.
- Для отсутствующих модулей введено правило “не выдумывать API и не вести туда задачу как в основной путь”.
- Для изменений данных зафиксирован обязательный confirmation-flow.

### Reference-аудит

Проверены и скорректированы текущие non-commerce reference-файлы, включая:
- модель данных и инфоблоки;
- компоненты, шаблоны, ЧПУ и пагинация;
- поиск, SEO, кеш и агенты;
- сессии, авторизацию, доступ и RBAC;
- веб-формы, почту, подписки;
- REST, HTTP, low-level DB;
- admin UI, modern grid, file uploader;
- validation, numerators, steppers, import/export;
- PHP workflow/testing/quality, safe legacy modernization;
- non-commerce diagnostics, standard components и operations-runbook.

### Документация репозитория

- `README.md` синхронизирован с текущим non-commerce и commerce/1С покрытием.
- `CHANGELOG.md` отражает актуальную версию и волну core-аудита.
- install/update слой стал rename-safe для будущего перехода репозитория на `bitrix-agent-skill`.
- Этот `PLAN.md` переведён из исторического roadmap в living-status документ.

## Принципы дальнейшей работы

1. Любое новое утверждение в reference-файлах должно подтверждаться локальным core или явно помечаться как version/module-dependent.
2. Если API найден только в другом Bitrix-стеке, но не в установленном ядре, его нельзя описывать как штатный контракт.
3. Если проектный код расходится со стандартным ядром, приоритет у проектного кода, но с явной пометкой об оверрайде.
4. Магазинные задачи и обмен с 1С не должны становиться частью активного маршрута до установки отдельного shop-core и ревизии по реальному коду.
5. После каждой волны ревизии должны синхронно обновляться `SKILL.md`, `VERSION`, а при необходимости `README.md` и `CHANGELOG.md`.
6. Для commerce/1C-аудита нельзя использовать production-данные, живые ключи и реальные персональные данные клиентов; нужны sandbox и тестовые CommerceML fixtures.
7. Code-first coverage не равен runtime pass: для production-утверждений нужны smoke fixtures/evidence по `runtime-smoke-verification.md`.

## Следующие шаги

### Ближайшие

1. Держать non-commerce reference-слой консистентным при следующих правках.
2. Держать `pagination.md` связанным с `iblocks.md`, `components.md`, `admin-ui.md`, `grid-admin-modern.md`, `sef-urls.md` и `diagnostic-visibility.md` при новых находках.
3. Держать `shop-core-module-inventory.md` как source-of-truth по coverage gaps и не обещать runtime-smoke без отдельной Docker/runtime проверки.
4. Для “как правильно” и “подводные камни” использовать `production-best-practices.md` и `pitfalls-matrix.md` как cross-cutting слой поверх модульных references.
5. При появлении новых локальных модулей или project overrides добавлять их в маршрут только после проверки по коду.
6. Поднять Docker/runtime shop-core и прогнать smoke-задачи из `runtime-smoke-verification.md`.

### Завершённый целевой этап: Production best practices / pitfalls / runtime verification

На версии `1.25.0` добавлены cross-cutting references:

1. `production-best-practices.md`: update-safe кастомизация, truth stack, где держать код, D7 vs legacy, boundary/service layer, side effects, cache/index/RBAC, performance, security и verification matrix.
2. `pitfalls-matrix.md`: симптомные маршруты по visibility, components/templates, iblock/HL, catalog/SKU, basket/checkout/order, 1С/CommerceML, REST/webservice, search/SEO/cache, users/auth, mail/SMS, automation и release/update pitfalls.
3. `runtime-smoke-verification.md`: sandbox safety, fixture set, smoke-сценарии для catalog/sale/1С/REST/webservice/marketing/bizproc, evidence format и pass/fail/block criteria.
4. Зафиксирована граница: code-first reference coverage не является runtime-smoke evidence. Нельзя утверждать “весь core production-проверен”, пока нет sandbox/fixtures smoke.

### Завершённый целевой этап: Shop integrations/webservice

На версии `1.24.0` добавлен отдельный reference `shop-integrations-webservice.md`. Закрыты:

1. `webservice` 26.0.0: SOAP/WSDL infrastructure, `webservice.server`, `webservice.checkauth`, `webservice.sale`, `webservice.statistic`, `stssync.server`, tools and safety boundaries.
2. `rest` 26.0.0: REST apps/webhooks/events/placements/auth/batch/method discovery and `b_rest_*` DB layer.
3. Sale REST: Engine controllers for order/payment/shipment/basket/status/properties, explicit pay_system/delivery/cashbox scopes and sale REST events.
4. Catalog REST: Engine controllers for products/prices/stores/documents/sections, event-bind classes and `CATALOG_EXTERNAL_PRODUCT` placement.
5. Зафиксирована граница: `webservice.sale`/`webservice.statistic` — не CommerceML/1С exchange и не полноценный order/product CRUD.

### Завершённый целевой этап: Shop automation/bizproc

На версии `1.23.0` добавлен отдельный reference `shop-automation-bizproc.md`. Закрыты:

1. `bizproc` 26.200.0: workflow templates, states/instances, tasks/users, tracking/history, robots/triggers, scripts, debugger, globals, REST activities/providers and cleanup agents.
2. `bizprocdesigner` 26.0.0: `bizproc.workflow.edit`, `bizprocdesigner.editor`, template save/import/export, rights and pull dependency.
3. `workflow` 26.0.0: legacy document workflow, statuses, locks, history/preview/files, admin pages and cleanup options.
4. `lists` 25.600.100: list/process components, iblock-backed data, list rights, livefeed/user processes, REST list CRUD and bizproc routes.
5. `pull` 25.300.0: channels, stack, watches, push queue, pull server config, REST methods and realtime diagnostics.
6. Зафиксирована важная граница: наличие `bizproc` не доказывает sale-order robots; order automation требует локального provider-а/CRM/custom module проверки.

### Завершённый целевой этап: Shop marketing/analytics

На версии `1.22.0` добавлен отдельный reference `shop-marketing-analytics.md`. Закрыты:

1. `sender` 26.0.0: contacts, lists/segments, campaigns/letters, posting queue, triggers, opens/clicks/unsub, UTM, consent, counters, access roles, agents and conversion hooks.
2. `mail` 26.100.200, `messageservice` 25.200.100 и `subscribe` 25.0.0: mailbox/client/log layer, SMS/provider queues/limits, legacy rubrics/subscriptions/postings и различие `sender.subscribe` vs `subscribe.*`.
3. `advertising` 24.200.0, `abtest` 26.0.0, `conversion` 25.0.0, `report` 25.100.0, `statistic` 26.0.0: banners, A/B hooks, conversion day context, report/visualconstructor layer и legacy runtime statistic hooks.
4. eShop/sale side effects: `bitrix:sender.subscribe` в template/public includes, `advertising.banner`, sale buyer/target sale sender connectors, sale statistic events и catalog product subscription separation.
5. Диагностика: рассылка не ушла, форма подписки не работает, SMS limits, баннер/клик не считается, A/B не переключает шаблон, conversion/report/statistic пустые или тормозят сайт.

### Завершённый целевой этап: Shop standard components

На версии `1.21.0` добавлен отдельный reference `shop-standard-components.md`. Закрыты:

1. Iblock-hosted public catalog components: `bitrix:catalog`, `catalog.section`, `catalog.element`, `catalog.smart.filter`, compare/search/top/list helpers.
2. Catalog module components: 62 component directories, включая `catalog.productcard.*`, `catalog.store.*`, `catalog.store.document.*`, `catalog.report.store_*`, viewed/recommended/bigdata и 1С import/export.
3. Sale module components: 78 component directories, включая basket, checkout/order, personal cabinet, payment, delivery/location, gifts/recommendations, mobile order и `sale.export.1c`.
4. `bitrix.eshop` solution layer: wizard/templates/public skeleton, own `eshop.*` components и подтверждённые component calls в eShop template layer.
5. Quick map параметров для `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`; диагностика пустого каталога, фильтра, add-to-basket, checkout и personal orders.

### Завершённый целевой этап: StoreAssist

На версии `1.20.0` добавлен отдельный reference `storeassist.md`. Закрыты:

1. Установка модуля: autoload, JS extension, copy admin/js/panel/tools, `OnPrologAdminTitle`, `OnBuildGlobalMenu`, daily agent.
2. `CStoreAssist`: task whitelist, `setSettingOption`, `getDocumentationLink`, admin toolbar, menu hook, progress percent и order-count agent.
3. Admin wizard structure: `MAIN`, `WORK`, `HEALTH`, включая блок `Интеграция с 1С:Предприятие 8`.
4. Разведены `storeassist_1c_*` onboarding pages и реальный CommerceML exchange в `catalog`/`sale`.
5. Диагностика: task completion, toolbar/menu visibility, progress agent, ложное ожидание exchange в StoreAssist.

### Завершённый целевой этап: Shop-core module inventory

На версии `1.19.0` добавлен полный inventory 49 модулей shop-core. Закрыты:

1. Версии всех модулей из `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core/www/bitrix/modules`.
2. Counts по standard components, admin entrypoints, `lib`, `classes`, install/db files.
3. Shop/1С relevance по модулям: runtime, solution/bootstrap, 1С/exchange, marketing/analytics, automation, content/front adjacent, platform/integration/safety.
4. Coverage status: `covered`, `covered-partial`, `needs deep audit`, `deferred per project`.
5. Ordered roadmap: `storeassist.md` → `shop-standard-components.md` → `shop-marketing-analytics.md` → `shop-automation-bizproc.md` → `shop-integrations-webservice.md` → `production-best-practices.md`/`pitfalls-matrix.md`/`runtime-smoke-verification.md`. После версии `1.25.0` code-first и production-guidance пункты закрыты; дальше нужен фактический Docker/runtime smoke.

### Завершённый целевой этап: Pagination core-layer

На версии `1.18.0` добавлен отдельный pagination-layer по `main` 26.150.0 и shop-core. Закрыты:

1. Legacy DB result: `CDBResult::NavStart`, `GetNavParams`, `GetNavPrint`, `GetPageNavStringEx`, `PAGEN_N`, `SIZEN_N`, `SHOWALL_N`, `NavNum`, session-сохранение и reverse paging.
2. Visual components: `bitrix:system.pagenavigation` и `bitrix:main.pagenavigation`, их параметры, result-поля и stock templates.
3. D7 navigation: `Bitrix\Main\UI\PageNavigation`, `AdminPageNavigation`, `ReversePageNavigation`, `getLimit()`, `getOffset()`, `addParams()` и `clearParams()`.
4. Admin/grid слой: `CAdminResult::NavStart`, `CAdminList::NavText`, `CAdminUiList::getPageNavigation`, `main.ui.grid` + `NAV_OBJECT`.
5. Iblock/catalog component слой: `nPageSize` vs `nTopCount`, `PAGEN_<NavNum>` в ajax/lazy load и диагностика пустых/дублирующих страниц.

### Завершённый целевой этап: Commerce + 1С Integration

Цель этапа — превратить deferred commerce-контур в подтверждённый active-route после аудита живого ядра интернет-магазина. На версии `1.17.0` baseline выполнен по локальному shop-core.

#### Подготовка sandbox

1. Отдельный Bitrix shop-core sandbox найден/подключён: `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core`, где реально присутствуют `catalog`, `sale`, `currency` и связанные магазинные модули.
2. Держать sandbox отдельно от репозитория `bitrix-agent-skill`: отдельная директория, контейнер или VM.
3. Зафиксировать версию продукта, состав `www/bitrix/modules`, активные сайты, выбранный wizard/solution и PHP/DB окружение.
4. Не подключать production 1С, реальные платежи, реальные службы доставки и данные клиентов; использовать тестовые настройки и fixtures.

#### Аудит shop-core

1. Подтвердить реальные contracts для:
   - `catalog`: товары, SKU/торговые предложения, свойства, цены, типы цен, остатки, склады, measure/unit слой, import/export;
   - `sale`: basket, order, shipment, payment, delivery, discounts, coupons, status lifecycle, user profiles;
   - `currency`: валюты, курсы, форматирование, связь с ценами;
   - standard components и stock templates магазина;
   - admin UI/grid/actions для каталога, заказов и настроек магазина.
2. Переаудированы `bitrix/references/catalog.md`, `bitrix/references/sale.md`, `bitrix/references/commerce-workflows.md`.
3. Добавлен отдельный reference-файл для обмена с 1С: `bitrix/references/commerce-1c-integration.md`.
4. Сформирован `shop-task-matrix.md`: каталог, SKU, цены, остатки, корзина, checkout, оплаты, доставки, скидки, заказы, обмен с 1С, диагностика CommerceML.

#### Аудит обмена с 1С

1. Найдены в shop-core реальные endpoints, компоненты, обработчики и настройки обмена с 1С.
2. Разведены импорт каталога, экспорт/обмен заказами, файлы CommerceML, zip/chunk-upload, авторизация и progressive import steps.
3. Описана диагностика типовых проблем:
   - 1С выгрузила товар, но он не виден на сайте;
   - товар виден, но не покупается;
   - цены/остатки не обновились;
   - SKU/предложения сломали карточку;
   - exchange падает на больших файлах или повторных чанках;
   - заказы не уходят обратно в 1С;
   - конфликтует кастомный обработчик/override.
4. Зафиксирован безопасный verification-flow: логи, временные файлы, таблицы, agents/events, component cache, managed/tagged cache, search/index/SEO side effects.

### Следующие шаги после baseline 1.25.0

1. Поднять Docker/runtime shop-core и проверить, есть ли живой DB dump или нужна свежая установка.
2. Подготовить fixtures по `runtime-smoke-verification.md`: catalog/offer/price/stock, basket/checkout/order, CommerceML, `webservice.sale`/`webservice.statistic`, sale/catalog REST events/placements, sender/SMS/banner/conversion/report/statistic, bizproc/list/pull.
3. Прогнать smoke-сценарии и сохранить evidence: input fixture, steps, expected/actual, logs/screenshots, cache/index actions, rollback/reset, verdict.
4. После runtime-smoke расширить reference-файлы конкретными DB/runtime findings и отметить pass/fail/blocked зоны.

## Definition of done для текущей фазы

Non-commerce фаза считается завершённой, когда:
- reference-файлы не содержат неподтверждённых API без явной пометки;
- production best-practices/pitfalls/runtime-smoke слой явно отделяет code-first coverage от runtime evidence;
- `SKILL.md` маршрутизирует задачи только в подтверждённые домены;
- служебные документы репозитория не спорят с фактическим состоянием навыка;
- deferred-домены явно отделены от активного маршрута.

Commerce/1C фаза считается завершённой, когда:
- установлен и задокументирован отдельный shop-core sandbox;
- `catalog`, `sale`, `currency`, shop standard components, marketing/analytics, automation/bizproc, integration/webservice и обмен с 1С подтверждены по реальному коду;
- `catalog.md`, `sale.md`, `commerce-workflows.md`, `shop-standard-components.md`, `shop-marketing-analytics.md`, `shop-automation-bizproc.md`, `shop-integrations-webservice.md` переаудированы;
- создан или обновлён reference по `1С`/`CommerceML` и явно разведены CommerceML, SOAP/WSDL и REST app hooks;
- skill умеет маршрутизировать магазинные задачи без догадок и без смешивания non-commerce core с shop-core;
- есть smoke-задачи и verification format для каталога, корзины, checkout, заказа, обмена с 1С, `webservice.sale`/`webservice.statistic`, REST app hooks, пагинации, lazy load и диагностики цен/остатков/SKU;
- фактический runtime pass будет считаться отдельной следующей фазой после запуска sandbox/fixtures.
