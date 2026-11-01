# План и статус аудита Bitrix-скилла

## Цель

Поддерживать `bitrix-agent-skill` как **core-first** навык для 1C-Bitrix CMS: все утверждения, примеры API и маршруты должны опираться на реально установленное ядро проекта, а не на память, форумы или “типичный Bitrix”.

## Текущий статус

Версия `1.36.0` закрывает 10 подтверждённых пробелов диагностического/evidence-контура; подробности и самопроверка — в разделе «Аудит надёжности 2026-11-01».

На дату этого плана:
- актуальная версия навыка: `1.47.0`;
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
- проектный UX-слой добавлен как рабочий маршрут: `behavior-routing.md`, `project-intake.md`, `task-playbooks.md`, `core-grep-cookbook.md`, `answer-contracts.md`, `first-answer-pitfalls.md`, `developer-cards.md`, `eval-prompts.md` и `release-gate.md`;
- release/evidence workflow усилен в версии `1.30.0`: добавлен CI-gate `.github/workflows/validate.yml`, release workflow запускает validation до публикации, `validate_skill.py` проверяет version/changelog/PLAN sync и full-to-compact coverage manifest;
- runtime evidence kit получил runnable preflight-helper `scripts/bitrix_runtime_preflight.py`, режим `init_runtime_evidence.py --all`, sample blocked evidence pack и короткие команды `make validate`, `make evidence-all`, `make release-check`;
- пагинационный слой переаудирован по `main` 26.150.0 и shop-core: legacy `CDBResult`, D7 `PageNavigation`, `system.pagenavigation`, `main.pagenavigation`, admin/grid и ajax/lazy load.
- composite/cache слой в версии `1.31.0` вынесен в отдельный `composite-cache.md` и сверен по `main` 26.150.0: `setFrameMode` как голосование, `COMPOSITE_FRAME_MODE/TYPE` и `AutomaticArea`, `createFrame`/`FrameHelper` как dynamic boundary, `/bitrix/html_pages/`, `X-Bitrix-Composite`, персонализация и second request/cache pass.
- добавлен следующий слой аудита оптимизаций: `project-optimization-audit.md` связывает кеши, composite, perfmon, SQL/ORM/N+1, templates/frontend, agents/imports и shop side effects в единый audit-report для запроса “как оптимизировать проект”.
- admin UI слой усилен в версии `1.34.0`: `admin-ui.md` фиксирует update-safe стратегию кастомизации админки, core → docs/forums → core методику, `OnAdmin*`/`OnBuildGlobalMenu`, стабильные `table_id`/`grid_id`/tab ids, smoke-чеклист и anti-patterns правки ядра.
- проектный developer UX усилен в версии `1.35.0`: `project-layout-and-includes.md` разводит public root, active template, `.section.php`, page/header/footer/include/component/service/delayed areas; `project-configuration.md` задаёт безопасный выбор между environment, `Option`, constants и stable-key registry с validation, missing/duplicate и protected invalidation contract.

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
- поиск, SEO, component/tagged/composite cache и агенты;
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
4. Магазинные задачи и обмен с 1С в каждом клиентском проекте остаются условными до проверки локальных модулей `catalog`, `sale`, `currency` и связанных runtime-контрактов; shop-core baseline — ориентир, а не доказательство для чужого проекта.
5. После каждой волны ревизии должны синхронно обновляться `SKILL.md`, `VERSION`, а при необходимости `README.md` и `CHANGELOG.md`; при добавлении reference — full и MCP Market compact-навигация.
6. Для commerce/1C-аудита нельзя использовать production-данные, живые ключи и реальные персональные данные клиентов; нужны sandbox и тестовые CommerceML fixtures.
7. Code-first coverage не равен runtime pass: для production-утверждений нужны smoke fixtures/evidence по `runtime-smoke-verification.md`.

## Roadmap v1.35+

### 0. Release/evidence automation — поддержка

Статус: в версии `1.30.0` добавлен первый обязательный automation gate.

Дальше поддерживать:

- `.github/workflows/validate.yml` и `.github/workflows/release.yml` должны запускать один и тот же базовый validation контур;
- `scripts/validate_skill.py` должен ловить рассинхрон `bitrix/VERSION`, `CHANGELOG.md`, `PLAN.md`, critical references, runtime templates, compact manifest и repo automation files;
- `mcpmarket/bitrix/references/reference-map.md` должен явно перечислять, в какой compact bundle попадает каждый full reference;
- sample blocked evidence должен оставаться валидным и не содержать secrets;
- `Makefile` должен оставаться thin wrapper над реальными Python helpers, а не вторым источником логики.

Definition of done: `make validate` и `make release-check` проходят локально; GitHub Validate Skill workflow повторяет тот же gate; релизный workflow не публикует GitHub Release, если validation падает.

### 1. Синхронизировать living-plan

Цель: `PLAN.md` должен отражать реальный текущий слой навыка, а не исторический baseline. При каждом крупном изменении фиксировать:

- текущую версию из `bitrix/VERSION`;
- какие references считаются активными;
- где есть только code-first coverage;
- какие зоны требуют runtime evidence или локальной проверки проекта;
- какие пользовательские workflow уже описаны в README и compact-версии.

Definition of done: версия и roadmap не расходятся с `README.md`, `CHANGELOG.md`, `bitrix/SKILL.md`, `bitrix/references/*` и MCP Market compact-навигацией.

### 2. Docker/runtime smoke evidence

Цель: закрыть главный пробел доверия — доказать на sandbox/fixtures, что магазинные маршруты реально проходят в runtime, а не только подтверждены по core-файлам.

Проверить минимум:

1. public catalog visibility;
2. SKU/offer + price + stock purchaseability;
3. basket/checkout/order в test mode;
4. order lifecycle через API, без прямого SQL;
5. CommerceML catalog import;
6. CommerceML order export;
7. REST event/method/scope smoke;
8. `webservice.sale` / `webservice.statistic` smoke;
9. sender/SMS/marketing/analytics в stub/test mode;
10. bizproc/lists/pull/realtime smoke.

Definition of done: по каждому сценарию есть sandbox facts, fixtures, steps, expected/actual, logs/screenshots/CLI-output и статус `pass`, `fail` или `blocked` в формате `runtime-smoke-verification.md`.

### 3. Docker/sandbox execution kit

Цель: превратить `runtime-smoke-verification.md` из плана проверки в воспроизводимый набор шагов для агента и человека.

Нужно подготовить:

- безопасную структуру sandbox без публикации ядра, secrets, DB dumps и production данных;
- список обязательных env/config-заглушек;
- fixtures для каталога, SKU, цены, остатка, корзины, заказа, CommerceML, REST/webservice, marketing и bizproc;
- read-only и write-mode smoke-команды;
- правила reset/rollback после каждого сценария;
- формат evidence, который можно переносить обратно в reference-файлы.

Статус: базовый kit добавлен — `assets/runtime-smoke/*`, `scripts/init_runtime_evidence.py`, `scripts/validate_runtime_evidence.py`, smoke-пакеты `P1–P4`, release gate и compact-навигация. Следующий уровень — реальные runnable smoke scripts или первый sandbox-run.

Definition of done: агент может взять пустой sandbox checklist, понять prerequisites, выполнить smoke по шагам, зафиксировать pass/fail/blocked и проверить evidence pack без обращения к production.

### 4. Аудит проекта и `BITRIX_PROJECT_CONTEXT.md`

Статус: сценарий уже закреплён в `README.md`, `SKILL.md`, `project-intake.md`, MCP Market compact-версии и template файла. В README добавлена явная команда запуска:

```text
/bitrix Сделай аудит проекта и обнови BITRIX_PROJECT_CONTEXT.md
```

Дальше поддерживать качество:

- держать русскую терминологию “аудит проекта” во всех пользовательских описаниях;
- не переименовывать файл `project-intake.md`, чтобы не ломать ссылки, но внутри писать по-русски;
- поддерживать regression/eval prompts на запуск аудита и повторное чтение `BITRIX_PROJECT_CONTEXT.md`;
- следить, чтобы compact MCP Market-версия не отставала от полной.

Definition of done: новый агент по README понимает, как запустить аудит проекта, где появится `BITRIX_PROJECT_CONTEXT.md`, что в него нельзя писать и когда факты надо перепроверять.

### 5. Version impact layer — поддержка

Статус: базовый слой уже добавлен в `version-impact.md` и связан с module check.

Дальше поддерживать:

- список version-sensitive контрактов по мере новых находок;
- формулировки ответа при mismatch: “контракт проверен на X; в вашем проекте версия Y, поэтому проверяю такие-то файлы”;
- ссылки из доменных references на `version-impact.md`, если появляется риск слепой совместимости;
- compact-версию в `mcpmarket/bitrix/references/version-impact.md`.

Definition of done: агент не обещает совместимость по памяти и всегда указывает локальные файлы, которые проверил при отличии версии.

### 6. Shop-core tail modules — поддержка

Статус: хвостовые модули (`calendar`, `idea`, `learning`, `support`, `wiki`, shop-specific части `b24connector`, `landing`, `mobileapp`) закрыты code-first маршрутом в `shop-core-tail-modules.md`.

Дальше поддерживать:

- честную границу “code-first route есть, runtime pass ещё нет”;
- связи tail modules с shop/1С, REST, mobile, landing и support flows;
- inventory coverage в `shop-core-module-inventory.md`;
- compact-навигацию MCP Market.

Definition of done: хвостовые модули не выглядят слепыми зонами, но агент не выдаёт их за runtime-проверенные без smoke evidence.

## Следующие шаги

### Ближайшие

1. Запустить первый sandbox smoke-пакет `P1`: catalog visibility + SKU/price/stock + basket/order.
2. Если sandbox ещё не готов, использовать `scripts/bitrix_runtime_preflight.py` и sample blocked evidence, чтобы честно зафиксировать blocker без runtime pass.
3. После первого runtime smoke перенести findings обратно в `catalog.md`, `sale.md`, `commerce-1c-integration.md`, `shop-task-matrix.md` и compact bundle.
4. Детализировать runnable fixtures/commands для `P2 CommerceML`, `P3 REST/webservice`, `P4 marketing/automation/realtime`.
5. Перед релизом прогонять `make validate`, `make release-check`, `scripts/validate_runtime_evidence.py` для реальных evidence packs и минимум 15 eval prompts, включая аудит проекта и runtime smoke.

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

### Следующие шаги после code-first baseline

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

## Аудит надёжности 2026-11-01

Область: реальный путь «снять диагностику → собрать доказательства → проверить → выпустить skill». До изменений `make validate` проходил, но перечисленные ниже отрицательные случаи не проверялись. Это аудит инструментов и поведения навыка, не повторная сертификация всех Bitrix API и не тест на живом Bitrix-сайте. Все 10 пунктов реализованы последовательно; по каждому выполнены тесты и отдельный commit.

| № | Чего не хватало / подтверждённая причина | Как правильно добавлено | Самопроверка |
|---|---|---|---|
| 1 | Raw snippets из PHP попадали в Markdown/JSON | Координаты + фиксированные признаки в обоих сканерах, N+1-сигналы сохранены | `test_report_privacy`: секрет на найденной строке отсутствует в обоих форматах |
| 2 | `base_url` выводился без обработки | Только HTTP(S) origin; убрать userinfo/path/query/fragment, обработать ошибочный URL | `test_base_url_exports_only_origin`: обычный host, IPv6, неверный порт |
| 3 | Parser читал только массив версии, а full/compact расходились по main | Распознавать `SM_VERSION` define/const и оба array-формата; main general прежде install | `test_preflight`: четыре записи версии, приоритет/fallback, нечисловое значение |
| 4 | Пустой `bitrix/modules` давал pass | Проверить доступность версии main; явно candidate/blocked и runtime not_checked | Пустой каталог, корректный файл, невалидный UTF-8; ни один случай не даёт runtime pass |
| 5 | Сканеры следовали файловым symlink, module argument мог быть путём | Общий обход обычных файлов; отсечь symlink и path-injection, не обходить весь core для routes | `test_scan_scope`: внешний файл/каталог, цикл, module traversal |
| 6 | Большие файлы молча пропускались, secret patterns расходились | Общая fail-closed проверка текстового evidence, без вывода найденных значений | `test_evidence_safety`: JSON token, Basic auth, URL credentials, binary, invalid UTF-8, oversize, symlink |
| 7 | Runtime summary проверялся отдельно от фактического файла | Точная локальная ссылка, уникальные известные ID, один совпадающий verdict и причина/evidence | `test_runtime_contracts`: дубликат, неверный путь, внешний URL, ID/verdict mismatch, пустое evidence |
| 8 | URL автоматически засчитывался как optimization evidence, метаданные расходились | Локальные finding files, уникальные ID, совпадающие поля, отдельный proof для confirmed/fixed | `test_optimization_contracts`: подмена/дубликаты, synthetic fixed proof; исправлена реальная priority-ошибка генератора/sample |
| 9 | Генераторы записывали summary до обнаружения поздней коллизии | Рендер всего набора, предварительная проверка, lock, exclusive create, atomic per-file force | `test_evidence_initializers`: поздняя коллизия P1/P4/OPT, сохранность файлов/static report, symlink, lock |
| 10 | CI проверял преимущественно happy path и наличие маркеров | `make test` включён в `make validate`; CLI-тесты и B075–B079; контракты full/compact синхронизированы | 23 unittest-метода с подслучаями, оба sample packs и repo gate |

### Ручная регрессия первого ответа

Самопроверка автором изменений, не независимый agent eval. Условия всех ответов: клиентский проект/ядро не предоставлены, поэтому указаны места будущей проверки, а не выдуманные найденные факты. Прочитаны `answer-contracts`, `developer-primitives`, `first-answer-pitfalls`, `developer-cards`, `behavior-routing` и релевантные диагностические references. Ниже сами сокращённые ответы, проверенные по route / bad-first-step / useful-answer. Выполнение PHP не заявляется.

| ID | Проверенный ответ | Итог |
|---|---|---|
| B001 | Для browser title — `SetPageProperty('title', ...)`; в active `header.php` проверить `ShowHead`/`ShowTitle`, затем SEO компонента и кеш. Не вставлять meta вручную. | pass |
| B004 | Для CSS — Asset или `template_styles.css`. Проверить active template и `ShowHead`; исключить повторное подключение и проверить кеш assets. | pass |
| B007 | Редактируемый футер — `IncludeFile` по текущей include convention. Проверить `footer.php`, `SITE_DIR`, edit mode и права, не хардкодить контент. | pass |
| B009 | Добавить через `AddChainItem`, вывести `bitrix:breadcrumb`. Проверить вызов компонента и `ADD_*_CHAIN`, чтобы не получить дубль. | pass |
| B011 | Текущий пользователь — `$USER` после bootstrap, `IsAuthorized`/`GetID`. Проверить контекст вызова, права и персональный кеш; не читать session напрямую. | pass |
| B013 | Request — `Context::getCurrent()->getRequest()`. Проверить controller/component boundary, валидировать тип входа и экранировать вывод. | pass |
| B016 | Проверить локальный module/version и результат `Loader::includeModule`. При false остановить API-путь; наличие каталога не гарантирует регистрацию. | pass |
| B023 | Для свойства проверить `PROPERTY_CODE`, `DISPLAY_PROPERTIES`, фактический arResult и result_modifier. Учитывать тип свойства/кеш; не начинать с SQL. | pass |
| B025 | Сначала определить component/tagged/composite слой, проверить `CACHE_*`, key и invalidation в компоненте. Не отключать весь кеш; проверить второй запрос и права. | pass |
| B028 | Почта — события/шаблоны Bitrix, не `mail()`. Проверить site binding, `CEvent::Send`/`Main\Mail\Event::send`, очередь/агенты и журнал; тестовую отправку согласовать. | pass |
| B030 | Ajax — существующий project controller/component action. Проверить bootstrap, права, sessid и JSON contract; не создавать анонимный write endpoint. | pass |
| B043 | Обновление цены: проверить catalog/currency и их загрузку, тип цены/валюту/сумму. Подготовить изменение через catalog API; прямую запись согласовать, учесть скидки, события и инвалидирование. Не SQL. | pass |
| B046 | Для 1С проверить локальный exchange component и шаги checkauth/init/file/import, XML_ID и повторный импорт. Логи обезличить; production import не запускать без разрешения/rollback. | pass |
| B053 | Полноту runtime не заявлять по static grep. Открыть runtime-smoke-verification, определить sandbox/fixtures/rollback и P1–P4; без стенда зафиксировать blocked. | pass |
| B057 | Из checkout запустить validate_runtime_evidence для P1; сверить summary, локальные сценарии, ID/verdict и приватность. Успех validator — не доказательство выполнения smoke. | pass |

Итого ручного regression gate: 15 проверено, fail = 0, warn = 0. Дополнительно просмотрены B075–B079 по новому контракту; их негативные случаи покрыты исполняемыми тестами. Runtime Bitrix smoke: не запускался, sandbox отсутствует. Проверка Windows/PowerShell не заявляется: lifecycle scripts не менялись.

### Локальный release gate 1.36.0

- `make release-check`: pass (включая 23 теста, оба sample packs, syntax/link/version checks).
- `quick_validate.py bitrix` и `quick_validate.py mcpmarket/bitrix`: pass.
- Compact bundle: 35/50 файлов; новые repo-local helpers не увеличивают установленный bundle.
- `git diff 4c2c2b0 --check`: pass.
- Негативные тесты также запущены на изолированной копии исходного `4c2c2b0`: они выявляют старые ошибки; новые контракты там отсутствуют. Исходный checkout при проверке не изменялся.
- Посторонние `.playwright-mcp/` и `assets/bitrix-agent-skill-ship-support.png` оставлены без изменений и не включены в commits/release.
- Публикация выполняется штатным Publish Release workflow после push в master; локальный gate не заменяет проверку итогового CI и опубликованного тега.

## Расширение знаний Bitrix: 10 → 10 → 20 (2026-11-01)

Запрос: только предметные знания, без зачёта инструментария. Базовый commit: d742e16, версия 1.36.0. Этапы: K01–K10 — инфоблоки/ORM; K11–K20 — commerce lifecycle; K21–K40 — прикладная разработка и интеграционные границы (уточняется по аудиту). После каждого этапа — отдельный minor release. Существующие references расширяются по владельцу темы; compact синхронизируется в существующих bundles.

Статус источников: прежняя shop-core копия содержит пустой www; в доступном поиске другое локальное ядро не найдено. Добавления основаны на официальной документации, проверенной 2026-11-01, а не на новом core audit. Ручная самопроверка означает разбор ответа и контрпримера; runtime-сценарии в клиентском Bitrix требуют отдельного стенда/разрешения. Инструменты проверки не меняются и не входят в 40 пунктов.

### K01: Три результата CIBlockElement::GetList

- Пробел до изменения: В iblocks.md и compact пример COUNT передавал false; другой пример вызывал Fetch на скалярном результате.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblockelement/getlist.php).
- Самопроверка B080 — «Как посчитать элементы, не загружая список?»: Передать [] третьим аргументом CIBlockElement::GetList, читать скаляр; сохранить фильтр списка и проверить 0/несколько элементов.
- Контрпример отвергнут: Вызвать Fetch на COUNT или принять обычную выборку за число.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K02: Result внутри транзакции и граница отката

- Пробел до изменения: Пример ORM не проверял результат OrderItemTable::add и ловил только Exception.
- Исправление: [orm.md](bitrix/references/orm.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/db/connection/starttransaction.php).
- Самопроверка B081 — «Дочерняя запись вернула ошибку Result, но родитель сохранился — почему?»: Неуспешный Result не бросает исключение сам; проверить дочерний результат и откатить собственную транзакцию до commit, обработать Throwable.
- Контрпример отвергнут: Коммитить потому, что исключения не было.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K03: OnAfter ORM не равен после commit

- Пробел до изменения: Справочник рекомендовал отправку уведомлений в OnAfter без различения commit внешней транзакции.
- Исправление: [orm.md](bitrix/references/orm.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/pages/orm/entity-operations.html).
- Самопроверка B082 — «Можно отправить webhook из OnAfterAdd внутри транзакции?»: Не считать событие commit: отложить внешний эффект до успешного завершения операции либо использовать согласованный transactional outbox.
- Контрпример отвергнут: OnAfterAdd гарантирует сохранность после любого rollback.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K04: Пагинация объектов со связями 1:N

- Пробел до изменения: Описаны fetchCollection и JOIN, но нет контракта пагинации родительских объектов с несколькими множественными отношениями.
- Исправление: [orm.md](bitrix/references/orm.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/pages/orm/querying-data.html).
- Самопроверка B083 — «Почему ORM LIMIT 20 возвращает меньше 20 карточек?»: JOIN размножает строки до LIMIT; отделить страницу уникальных ID от загрузки отношений, проверить полный набор значений и стабильный порядок.
- Контрпример отвергнут: Добавить DISTINCT ко всему select или увеличить LIMIT наугад.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K05: Публичная ORM-выборка и версии документооборота

- Пробел до изменения: Примеры D7 не объясняли отличие публичной выборки от истории/неопубликованных версий workflow.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblockelement/getpublicelementsormfilter.php).
- Самопроверка B084 — «После перехода на ORM посетителям видны черновики: что проверить?»: Сопоставить со stock public selection, проверить getPublicElementsOrmFilter и отдельно права, активность, даты, сайт и кеш.
- Контрпример отвергнут: Считать ACTIVE=Y полной моделью публикации и доступа.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K06: Частичная запись свойств и явное очищение

- Пробел до изменения: Gotcha ошибочно противопоставлял PROP_ID и PROP_CODE; отсутствовали очистка multiple и возвращаемое значение Ex.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblockelement/setpropertyvaluesex.php).
- Самопроверка B085 — «Как обновить одно свойство и очистить TAGS, не потеряв остальные?»: Использовать SetPropertyValuesEx с нужными ключами, TAGS=false; после записи перечитать значения, не проверять isSuccess у null.
- Контрпример отвергнут: Передать неполный набор в SetPropertyValues без PROPERTY_CODE.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K07: Множественные файлы: ID файла и ID значения

- Пробел до изменения: Чтение file ID описано, но нет модели сохранения/удаления нескольких файлов и смены ID связей.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblockelement/setpropertyvalues.php).
- Самопроверка B086 — «Как удалить два фото и добавить одно в множественное свойство?»: Прочитать связи, проверить принадлежность элементу, сформировать один пакет удаления/добавления и перечитать новые value IDs.
- Контрпример отвергнут: Два последовательных удаления по старым value IDs или прямой CFile::Delete.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K08: Отдельный lifecycle записи свойств

- Пробел до изменения: В справочнике событий инфоблока отсутствовал отдельный property-write путь, поэтому интеграция могла пропускать Ex.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/events/oniblockelementsetpropertyvaluesex.php).
- Самопроверка B087 — «Обработчик OnAfterIBlockElementUpdate не видит запись через Ex — почему?»: Трассировать отдельные property events; выбрать нужную фазу, scope и защиту повторного вызова, не подменять before событие post-save.
- Контрпример отвергнут: Добавить второй Update ради запуска обработчика.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K09: Enum: стабильный внешний ключ и локальный ID

- Пробел до изменения: Есть чтение enum, но нет переноса значения между стендами с защитой scope, масок и duplicate.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblockpropertyenum/getlist.php).
- Самопроверка B088 — «Вариант имеет разные ID на dev/prod: как перенести значение?»: Разрешить XML_ID внутри конкретного свойства, проверить одну точную запись и сохранить её локальный ID; проверить повтор миграции.
- Контрпример отвергнут: Копировать dev ID или искать первый вариант по подписи.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K10: Мутация метаданных свойства и VERSION=2

- Пробел до изменения: Раздел PropertyTable не ограничивал generic CRUD по версии storage и не объяснял выбор CIBlockProperty для schema side effects.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/pages/modules/iblocks/api.html).
- Самопроверка B089 — «Можно добавить свойство VERSION=2 через PropertyTable::add?»: Выбрать CIBlockProperty API, согласовать миграцию схемы/значений и проверить чтение новым процессом; ORM метаданных оставить для чтения.
- Контрпример отвергнут: Прямой INSERT метаданных и ручное создание одной колонки.. Результат ручной проверки ответа: pass; runtime: не запускался.

### Сквозная самопроверка этапа 1

Дополнительно к 10 новым B080–B089 повторены пять коротких маршрутов: B001 — ShowHead/ShowTitle и свойства страницы, без ручного meta; B004 — Asset и active template, без дубля CSS; B011 — текущий пользователь после bootstrap, без чтения session; B016 — Loader с проверкой результата, без предположения об установленном модуле; B053 — static не является runtime, без sandbox статус blocked. Проверены маршрут, отсутствие bad first step и граница фактов. Итого 15 ответов: pass=15, warn=0, fail=0. Это ручная самопроверка, не независимый eval и не запуск PHP на ядре.

### Gate этапа 1 / 1.37.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K11: Корзина заказа сохраняется через агрегат Order

- Пробел до изменения: Есть пример Basket::save без явного ограничения свободной корзиной.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/sale/technique/basket.php).
- Самопроверка B090 — «Можно поменять количество в оформленном заказе и вызвать basket->save?»: Нет: загрузить заказ, изменить его корзину и согласованные зависимые сущности, проверить Result и сохранить Order.
- Контрпример отвергнут: Сохранить только basket заказа или обновить b_sale_basket.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K12: FUSER и пользователь — разные идентификаторы

- Пробел до изменения: Есть вызов Fuser::getId, но нет различения USER_ID, CLI и слияния гостевой корзины.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/api/classes/Bitrix-Sale-Fuser.html).
- Самопроверка B091 — «В CLI подставить userId в loadItemsForFUser — правильно?»: Нет: отдельно разрешить FUSER целевого пользователя и site, обработать отсутствие; web-клиент не выбирает чужого владельца.
- Контрпример отвергнут: Считать USER_ID и FUSER_ID взаимозаменяемыми.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K13: Идентичность строки корзины не равна PRODUCT_ID

- Пробел до изменения: Не описано, как адресовать несколько строк одного товара и новые несохранённые items.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/api/classes/Bitrix-Sale-BasketItem.html).
- Самопроверка B092 — «У одного товара две строки с разной гравировкой: как изменить одну?»: Выбрать конкретную строку в авторизованной корзине, сохранить её свойства; не искать по одному PRODUCT_ID.
- Контрпример отвергнут: Обновить все строки товара или привести basket code к числу.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K14: Системная отгрузка и распределение количества

- Пробел до изменения: Есть isSystem guard, но отсутствует смысл системной отгрузки и инвариант распределения количества.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/sale/technique/shipment.php).
- Самопроверка B093 — «Почему в заказе есть системная отгрузка и можно ли её удалить?»: Это часть модели распределения: не удалять; работать с обычными Shipment и сверять quantities с корзиной.
- Контрпример отвергнут: Удалить системную отгрузку или отметить её как доставленную.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K15: Частичные оплаты и повтор подтверждения

- Пробел до изменения: Пример помечал все payments оплачены и все shipments отгружены без независимых оснований.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/sale/classes/payment/setpaid.php).
- Самопроверка B094 — «Пришло подтверждение одной из двух оплат — отметить весь заказ?»: Подтвердить только найденный Payment после проверки callback и повтора; сохранить Order, не трогать вторую оплату и отгрузки.
- Контрпример отвергнут: foreach всех оплат setPaid(Y), затем DEDUCTED всем отгрузкам.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K16: Финальный пересчёт и сумма неоплаченной оплаты

- Пробел до изменения: Пример ставил SUM=getPrice до явной финализации, игнорировал множество промежуточных Results.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/sale/classes/orderbase/dofinalaction.php).
- Самопроверка B095 — «После купона сумма заказа изменилась, а Payment остался прежним — что делать?»: Проверить final calculation и Result, согласовать неоплаченную часть с итогом; paid сумму не переписывать, затем save/reload.
- Контрпример отвергнут: Считать doFinalAction сохранением или менять уже подтверждённую оплату.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K17: Контекст менеджера купонов

- Пробел до изменения: Купоны упоминались как side effect без жизненного цикла manager и разграничения состояний.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/sale/classes/discountcouponsmanager/init.php).
- Самопроверка B096 — «В одном CLI-процессе создаются заказы разных покупателей: что с купонами?»: Изолировать контекст manager по заказу/владельцу и режиму, проверить переинициализацию и применение; не наследовать предыдущий coupon state.
- Контрпример отвергнут: Один глобальный MODE_CLIENT на весь пакет покупателей.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K18: Существующая доставка не обязательно доступна отгрузке

- Пробел до изменения: Общие restrictions перечислены, но пример брал delivery по ID без объяснения контекста Shipment и режима.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/api/classes/Bitrix-Sale-Delivery-Services-Manager.html).
- Самопроверка B097 — «Доставка существует по ID, но почему её нельзя принять из POST?»: Проверить ограничения для текущей заполненной отгрузки и клиентский режим, затем расчёт; ID из запроса не доказательство доступности.
- Контрпример отвергнут: Считать getById успешной проверкой или принять цену доставки из браузера.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K19: Ручная цена корзины и источник истины

- Пробел до изменения: Есть запрет ручной PRICE без причины, но нет модели CUSTOM_PRICE и восстановления владельца цены.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/pages/modules/sale/architecture.html).
- Самопроверка B098 — «Поставить CUSTOM_PRICE=Y, чтобы цена перестала меняться?»: Только для согласованной ручной котировки; иначе разобраться с provider. Проверить скидки, налоги, валюту, refresh и серверный источник суммы.
- Контрпример отвергнут: Копировать PRICE и CUSTOM_PRICE из POST или отключать provider ради симптома.. Результат ручной проверки ответа: pass; runtime: не запускался.

### K20: События сохранения заказа и повторный save

- Пробел до изменения: Есть REST mapping OnSaleOrderSaved, но нет безопасного PHP-протокола изменения и защиты от повторного save.
- Исправление: [sale.md](bitrix/references/sale.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/sale/events/order_saved.php).
- Самопроверка B099 — «В OnSaleOrderSaved меняю поле и вызываю save: почему цикл?»: Изменение перенести в подходящую before-фазу, реакцию ограничить IS_NEW/VALUES; внешние повторы дедуплицировать устойчивым ключом.
- Контрпример отвергнут: Добавить безусловный save в Saved или считать IS_NEW защитой от любого повтора.. Результат ручной проверки ответа: pass; runtime: не запускался.

### Ручная предметная проверка этапа 2

Проверены 15 ответов: B090–B099 с ответами и отвергнутыми контрпримерами выше; регрессия B001/B004/B011/B016/B053 — сохранены маршруты компонент → owning reference, доступ/кэш и запрет прямой SQL-подмены API. Результат: pass. Это ручная самопроверка документации, не независимый прогон агента и не выполнение Bitrix runtime.

### Gate этапа 2 / 1.38.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K21: Пакет REST не является транзакцией

- Пробел до изменения: Указана проверка per-method errors, но не разобраны остановка, частичный успех и границы повторного выполнения.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/settings/how-to-call-rest-api/batch.html).
- Самопроверка B100 — «В batch третья команда упала: первые две отменились?»: Нет: разобрать результаты по ключам, учитывать halt; сохранить успешные операции и определить безопасный повтор остальных.
- Контрпример отвергнут: Считать HTTP 200 полным успехом или halt=1 транзакционным откатом. Результат ручной проверки ответа: pass; runtime: не запускался.

### K22: Постраничная REST-выгрузка и условие завершения

- Пробел до изменения: Есть серверный next/total, но нет клиентского протокола обхода и различения вложенного результата.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/settings/how-to-call-rest-api/list-methods-pecularities.html).
- Самопроверка B101 — «В списке нет total: как дочитать все страницы?»: Следовать next → start, разбирать форму result конкретного метода и не менять сортировку/фильтр.
- Контрпример отвергнут: Остановиться после первой страницы или считать count(result) количеством записей. Результат ручной проверки ответа: pass; runtime: не запускался.

### K23: Версия REST определяется маршрутом и схемой метода

- Пробел до изменения: Справочник предполагает единую форму REST и не отделяет новые REST 3.0 методы.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/).
- Самопроверка B102 — «Можно весь старый REST-клиент перевести добавлением /api/ в URL?»: Нет: проверить доступность и схему каждого метода новой версии, затем адаптировать клиент.
- Контрпример отвергнут: Объявить все классические методы доступными в REST 3.0. Результат ручной проверки ответа: pass; runtime: не запускался.

### K24: Входящий вебхук наследует права владельца

- Пробел до изменения: Общие scope перечислены, но нет модели владельца входящего вебхука и её отличия от приложения.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/first-steps/first-rest-api-call.html).
- Самопроверка B103 — «Выбран scope crm, но вебхук не читает чужую сделку — отключить проверку?»: Нет: проверить права владельца на сделку и scope отдельно, использовать разрешённую учётную запись.
- Контрпример отвергнут: Считать scope автоматическим правом на все объекты или опубликовать URL в браузере. Результат ручной проверки ответа: pass; runtime: не запускался.

### K25: Продление OAuth без гонки между обработчиками

- Пробел до изменения: Названия auth-таблиц есть, но протокол обновления пары токенов и конкурентный владелец отсутствуют.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/settings/oauth/auto-renewal.html).
- Самопроверка B104 — «Два воркера одновременно получили expired_token: что делать?»: Сериализовать refresh по записи авторизации, сохранить пару атомарно, ожидающему перечитать и повторить с новым access_token.
- Контрпример отвергнут: Независимо обновлять токены в каждом воркере без ограничения повторов. Результат ручной проверки ответа: pass; runtime: не запускался.

### K26: Портал идентифицируется member_id, а не доменом

- Пробел до изменения: Не описана смена адреса портала без смены идентичности клиента.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/settings/how-to-call-rest-api/change-domen.html).
- Самопроверка B105 — «Портал сменил домен: создавать новую запись клиента?»: Найти установку по member_id и приложению, проверить авторизационные данные и обновить client_endpoint.
- Контрпример отвергнут: Хранить tenant только по domain или отправить секрет на URL из неподтверждённого события. Результат ручной проверки ответа: pass; runtime: не запускался.

### K27: Проверка подлинности REST-события

- Пробел до изменения: Указаны HTTPS/auth, но нет протокола application_token, особенно для удаления приложения.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/events/safe-event-handlers.html).
- Самопроверка B106 — «Пришёл ONAPPUNINSTALL без access_token: удалять данные клиента?»: Только после сверки application_token с сохранённым секретом нужной установки; неизвестное событие отклонить.
- Контрпример отвергнут: Доверять одному имени события, member_id или домену в POST. Результат ручной проверки ответа: pass; runtime: не запускался.

### K28: Офлайн-очередь не является журналом всех изменений

- Пробел до изменения: Есть список offline API, но не указано объединение событий и отсутствие полной истории.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/events/offline-events.html).
- Самопроверка B107 — «Три обновления сделки дали одну offline-запись — события потерялись?»: Одинаковые ключи объединяются; использовать очередь для синхронизации актуального состояния, не как полный аудит.
- Контрпример отвергнут: Считать каждую запись ровно одной бизнес-операцией и восстанавливать всю историю по очереди. Результат ручной проверки ответа: pass; runtime: не запускался.

### K29: Получение офлайн-событий по умолчанию удаляет их

- Пробел до изменения: Не описан разрушающий default clear=1 и сохранение process_id для восстановления.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/events/event-offline-get.html).
- Самопроверка B108 — «Воркер упал сразу после event.offline.get: очередь сохранит события?»: При default clear=1 — нет; использовать разрешённое резервирование clear=0 и отдельное подтверждение.
- Контрпример отвергнут: Считать get чистым чтением или повторять пакет с clear=1 и маленьким limit. Результат ручной проверки ответа: pass; runtime: не запускался.

### K30: Подтверждение офлайн-пакета имеет опасные пустые значения

- Пробел до изменения: Нет границ массового удаления event.offline.clear при пустом process_id или пустом списке.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/events/event-offline-clear.html).
- Самопроверка B109 — «Все записи пакета упали: отправить clear с message_id=[]?»: Нет: пустой список удалит пакет. Не подтверждать ошибки; проверить process_id и фиксировать только успешные записи.
- Контрпример отвергнут: Использовать пустые параметры как безопасный no-op. Результат ручной проверки ответа: pass; runtime: не запускался.

### K31: Повторная обработка ошибочных офлайн-событий

- Пробел до изменения: Метод error перечислен без идентификаторов, режима повторного чтения и опасности неверного пакета.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/events/event-offline-error.html).
- Самопроверка B110 — «event.offline.error вернул true, но ошибка не появилась — почему?»: Проверить MESSAGE_ID, принадлежность process_id и непустой список; читать ошибочную ветку error=1.
- Контрпример отвергнут: Передать ID сделки вместо MESSAGE_ID или чужой process_id и довериться true. Результат ручной проверки ответа: pass; runtime: не запускался.

### K32: Лимиты частоты и ресурсоёмкости REST различаются

- Пробел до изменения: Коды ошибок перечислены, но не определены разные стратегии регулирования нагрузки.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/settings/performance/limits.html).
- Самопроверка B111 — «После operating_reset_at метод всё ещё заблокирован: менять токен?»: Нет: часть временного окна могла остаться; снизить нагрузку и проверить operating, не обходить блокировку токенами.
- Контрпример отвергнут: Ускорить параллельные повторы или объявить единый лимит для любого Битрикс24. Результат ручной проверки ответа: pass; runtime: не запускался.

### K33: Файловое поле REST не равно объекту Диска

- Пробел до изменения: Есть server-side file API, но отсутствует контракт внешней передачи файла по конкретному типу поля.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/files/how-to-upload-files.html).
- Самопроверка B112 — «Можно передать FILE_ID из disk.file.get в любое файловое поле?»: Нет: выяснить нужный тип идентификатора и формат поля, выполнить загрузку/прикрепление по контракту метода.
- Контрпример отвергнут: Подменять Disk ID значением FILE_ID или Base64 локальным путём. Результат ручной проверки ответа: pass; runtime: не запускался.

### K34: Готовность BX24.js не равна готовности DOM

- Пробел до изменения: Placement перечислены, но не описан lifecycle JS-контекста приложения.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/sdk/bx24-js-sdk/system-functions/bx24-init.html).
- Самопроверка B113 — «DOM загрузился, но BX24.isAdmin() false у администратора — что проверить?»: Подключение BX24.js, запуск во фрейме приложения и выполнение после BX24.init.
- Контрпример отвергнут: Считать DOMContentLoaded готовностью авторизации или зашить admin-токен в HTML. Результат ручной проверки ответа: pass; runtime: не запускался.

### K35: Установка приложения и первый запуск пользователя — разные этапы

- Пробел до изменения: Нет причины успешной регистрации событий без доставки до завершения установки приложения.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/sdk/bx24-js-sdk/system-functions/bx24-install-finish.html).
- Самопроверка B114 — «event.bind успешен, но новое приложение не получает события — где причина?»: Проверить завершение установки и INSTALLED; не путать мастер установки с первым запуском пользователя.
- Контрпример отвергнут: Безусловно завершать проваленный мастер или ждать JS finish в REST-only обработчике. Результат ручной проверки ответа: pass; runtime: не запускался.

### K36: Контекст встройки не является разрешением на объект

- Пробел до изменения: Есть серверная регистрация placement, но не разобран контекст виджета и его доверенность.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/widgets/ui-interaction/bx24-placement-info).
- Самопроверка B115 — «В options пришёл ID сделки: можно сразу читать её своим admin-токеном?»: Нет: проверить конкретный placement, тип/ID и права текущего пользователя на backend.
- Контрпример отвергнут: Считать клиентский options доказательством доступа или ожидать callback от placement.info. Результат ручной проверки ответа: pass; runtime: не запускался.

### K37: Общие и пользовательские настройки REST-приложения

- Пробел до изменения: Методы app.option/user.option только перечислены, не определён владелец данных.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/common/settings/user-option-set.html).
- Самопроверка B116 — «Сервер сохранил user.option.set, но второй сотрудник не видит настройку — почему?»: Настройка принадлежит пользователю токена; выбрать персональный либо общий app.option слой осознанно.
- Контрпример отвергнут: Ожидать глобальное действие user.option.set или удаление ключа пустой строкой. Результат ручной проверки ответа: pass; runtime: не запускался.

### K38: feature.get не является булевой проверкой существования API

- Пробел до изменения: Метод перечислен без формы ответа, особенностей коробки и ложноположительных неизвестных кодов.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/common/system/feature-get.html).
- Самопроверка B117 — «feature.get для придуманного CODE вернул Y: функция точно существует?»: Нет: метод не проверяет существование кода. Использовать опубликованные CODE и проверять сам метод.
- Контрпример отвергнут: Привести N к true или объявить поддержку по Y неизвестного кода. Результат ручной проверки ответа: pass; runtime: не запускался.

### K39: Транспортная ошибка HttpClient не доказывает отсутствие записи

- Пробел до изменения: В примере ошибочно утверждалось: любая ошибка соединения/DNS/timeout означает, что запрос не дошёл.
- Исправление: [http.md](bitrix/references/http.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/web/httpclient/index.php).
- Самопроверка B118 — «HttpClient получил timeout после создания заказа во внешней системе: повторить POST?»: Не вслепую: операция могла выполниться; сверить внешний ключ/результат или безопасную идемпотентность.
- Контрпример отвергнут: Считать любой timeout гарантией, что сервер не получил запрос. Результат ручной проверки ответа: pass; runtime: не запускался.

### K40: Idempotency-Key REST 3.0 не заменяет блокировку конкурентных записей

- Пробел до изменения: Нет платформенного механизма безопасного последовательного повтора и его строгих границ.
- Исправление: [rest.md](bitrix/references/rest.md) и [integrations-rest.md](mcpmarket/bitrix/references/integrations-rest.md); источник: [Официальный контракт](https://apidocs.bitrix24.ru/api-reference/rest-v3.html).
- Самопроверка B119 — «Два воркера одновременно создали объект с одним Idempotency-Key — дубль невозможен?»: Возможен: заголовок не является конкурентным lock. Сериализовать и учитывать версию REST, тело и срок хранения.
- Контрпример отвергнут: Обещать exactly-once навсегда или использовать заголовок как защиту классического REST. Результат ручной проверки ответа: pass; runtime: не запускался.

### Ручная предметная проверка этапа 3 и итог 40 пунктов

- B100–B119: для каждого проверены правильный ответ, отвергаемый контрпример и соответствие официальному источнику; решения внесены в owning reference и compact. Проектные меры (блокировки, журнал неопределённых исходов, проверка доверия) не выдаются за встроенные гарантии Bitrix.
- B001: meta title через SetPageProperty/ShowTitle и шаблон, не ручной meta-тег — pass.
- B004: Asset::addCss/template_styles.css и ShowHead, не echo link из компонента — pass.
- B011: пользователь через $USER/IsAuthorized/GetID, не сырая сессия; отдельно права — pass.
- B016: Loader::includeModule и обработка false до обращения к API — pass.
- B053: документация и code-first анализ не означают runtime pass; для него нужны отдельные P1–P4 evidence — pass.
- Итоговая сверка: ровно K01–K40, по одному разделу в полной и компактной версиях, по одному B080–B119 в обоих eval-наборах, источник и решение для каждого. Проверены удаление противоречивых примеров и отсутствие изменений tests/scripts в этой задаче.
- Это ручная самопроверка 25 сценариев третьего этапа и структурная сверка всех 40, не независимый запуск агента. Живое ядро/стенд недоступны; проверки на стенде в каждом пункте — инструкции для будущего runtime-прогона, не выполненные действия.
- Релизы первых двух этапов v1.37.0 (fd101e4) и v1.38.0 (1924b28) опубликованы; оба Validate Skill и Publish Release завершились success для каждого.

### Gate этапа 3 / 1.39.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K41: HTML-кеш компонента уже выводится на cache hit

- Пробел до изменения: Оба примера вызывали includeComponentTemplate вне cache miss, хотя использовали HTML-кеш.
- Исправление: [components.md](bitrix/references/components.md) и [components-admin-ui.md](mcpmarket/bitrix/references/components-admin-ui.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cbitrixcomponent/startresultcache.php).
- Самопроверка B120 — «Почему второй запрос компонента выводит HTML дважды?»: Проверить шаблон вне StartResultCache: на hit HTML уже выведен. Разделить HTML и data-only режимы.
- Контрпример отвергнут: Безусловно исполнять шаблон после выдачи HTML-кеша. Результат ручной проверки ответа: pass; runtime: не запускался.

### K42: SetResultCacheKeys не удаляет персональные данные из HTML

- Пробел до изменения: Комментарий обещал некеширование CURRENT_USER только за счёт списка ключей arResult.
- Исправление: [components.md](bitrix/references/components.md) и [components-admin-ui.md](mcpmarket/bitrix/references/components-admin-ui.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cbitrixcomponent/setresultcachekeys.php).
- Самопроверка B121 — «Убрал CURRENT_USER из cache keys: имя теперь безопасно в общем HTML?»: Нет: HTML уже содержит имя; изменить границу/ключ кеша, не только состав arResult.
- Контрпример отвергнут: Считать cache keys механизмом очистки персонального HTML. Результат ручной проверки ответа: pass; runtime: не запускался.

### K43: Эпилог и сохранённые данные вместо вымышленного component_prolog

- Пробел до изменения: Показан component_prolog.php с arResult, ниже утверждалось, что arResult там недоступен; автоматический hook не обоснован.
- Исправление: [templates.md](bitrix/references/templates.md) и [components-admin-ui.md](mcpmarket/bitrix/references/components-admin-ui.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&CHAPTER_ID=02975).
- Самопроверка B122 — «Где ставить заголовок из результата, чтобы он работал при тёплом кеше?»: В component_epilog, предварительно сохранив нужные значения; не в result_modifier или недоказанном component_prolog.
- Контрпример отвергнут: Обещать автоматический вызов component_prolog с готовым arResult. Результат ручной проверки ответа: pass; runtime: не запускался.

### K44: Шаблон сайта переопределяет встроенный шаблон компонента

- Пробел до изменения: У пути local/components стояла неверная пометка о большем приоритете над site-template.
- Исправление: [templates.md](bitrix/references/templates.md) и [components-admin-ui.md](mcpmarket/bitrix/references/components-admin-ui.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&LESSON_ID=2829).
- Самопроверка B123 — «Правлю local/components/.../templates, но сайт показывает старый вид: почему?»: Проверить переопределение в активном site-template и шаблоне комплексного родителя, затем кеш.
- Контрпример отвергнут: Утверждать, что любой local/components template всегда приоритетнее site-template. Результат ручной проверки ответа: pass; runtime: не запускался.

### K45: Дополнительные зависимости ключа компонента

- Пробел до изменения: Перечислен готовый ключ, но пример читает user_id из запроса лишь внутри miss и не изолирует результат.
- Исправление: [components.md](bitrix/references/components.md) и [components-admin-ui.md](mcpmarket/bitrix/references/components-admin-ui.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cbitrixcomponent/startresultcache.php).
- Самопроверка B124 — «У компонента один arParams, но разные региональные цены: почему смешались?»: Добавить нормализованный регион/контекст доступа в additionalCacheID и проверять права до кеша.
- Контрпример отвергнут: Читать контекст только внутри miss и считать CACHE_GROUPS автоматической защитой. Результат ручной проверки ответа: pass; runtime: не запускался.

### K46: Подписанные параметры компонента: целостность, не право доступа

- Пробел до изменения: Есть список ключей подписи без ограничений доверия, хранения и чтения в ajax.php.
- Исправление: [components.md](bitrix/references/components.md) и [components-admin-ui.md](mcpmarket/bitrix/references/components-admin-ui.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&LESSON_ID=2192).
- Самопроверка B125 — «ID подписан компонентом: можно пропустить проверку прав в AJAX?»: Нет: проверить актуального пользователя и объект; подпись защищает целостность параметров, не полномочия.
- Контрпример отвергнут: Поместить секрет в подпись или доверять всему data рядом с ней. Результат ручной проверки ответа: pass; runtime: не запускался.

### K47: Действие компонента и действие модуля имеют разные маршруты

- Пробел до изменения: Нет выбора runComponentAction mode=class/ajax; есть только модульный runAction.
- Исправление: [components.md](bitrix/references/components.md) и [components-admin-ui.md](mcpmarket/bitrix/references/components-admin-ui.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/js_lib/ajax/bx_ajax_runcomponentaction.php).
- Самопроверка B126 — «Вызвал vendor:widget через runAction: почему action не найден?»: Разделить модульный и компонентный диспетчер, выбрать mode по месту реализации действия.
- Контрпример отвергнут: Подменить компонентный маршрут модульным либо обращаться напрямую к файлу ajax.php. Результат ручной проверки ответа: pass; runtime: не запускался.

### K48: Authentication не ограничивает выборку объектами владельца

- Пробел до изменения: Пример принимал userId для создания, читал произвольный ID и считал все строки независимо от доступа.
- Исправление: [events-routing.md](bitrix/references/events-routing.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/pages/security/access-control.html).
- Самопроверка B127 — «Авторизованный пользователь передал чужой userId/id: допустимо?»: Нет без отдельного разрешения; ограничить запись/чтение серверным правилом и тем же правилом count.
- Контрпример отвергнут: Доверять userId клиента или возвращать глобальный total приватного списка. Результат ручной проверки ответа: pass; runtime: не запускался.

### K49: Метод запроса BX.ajax и обработка отклонённого Promise

- Пробел до изменения: Пример getList разрешает только GET, а runAction без method отправляет POST; нет ветки reject.
- Исправление: [events-routing.md](bitrix/references/events-routing.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/js_lib/ajax/bx_ajax_runaction.php).
- Самопроверка B128 — «getList не проходит HttpMethod, хотя имя верное — причина?»: Сверить default POST клиента с GET фильтром; явно указать GET и обработать reject.
- Контрпример отвергнут: Убрать серверный фильтр ради несовпадения клиента или бесконечно повторять мутацию. Результат ручной проверки ответа: pass; runtime: не запускался.

### K50: PHP-тип параметра действия не задаёт бизнес-диапазон

- Пробел до изменения: В примере limit/page типизированы int, но отрицательные/огромные значения сразу попадали в SQL.
- Исправление: [events-routing.md](bitrix/references/events-routing.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/pages/framework/validation.html).
- Самопроверка B129 — «У limit тип int — значит -1 и миллион уже безопасны?»: Нет: проверить бизнес-диапазон и остановить запрос при нарушении, типизацию не считать валидацией.
- Контрпример отвергнут: Передать любой integer в limit/offset без ограничений. Результат ручной проверки ответа: pass; runtime: не запускался.

### Повтор цикла: этап 1 / K41–K50

База повторного цикла — 7c18d24 / 1.39.0. Новые знания не повторяют K01–K40. Разрешения на git add, commit, push, теги и GitHub Releases для трёх этапов получены.

Ручная самопроверка 15 ответов: B120–B129 (ответы и контрпримеры выше), B001 (title через API), B004 (Asset CSS), B011 (текущий пользователь и права), B016 (includeModule/false), B053 (не выдавать code-first за runtime). Pass. В изолированной копии проверен PHP-синтаксис полного примера Engine-контроллера; все 10 изменений повторно прошли make validate в рабочем репозитории перед отдельными коммитами. Это не независимый агентный и не live Bitrix прогон.

### Gate этапа 4 / 1.40.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K51: Штатный тег инфоблока и проектные теги

- Пробел до изменения: Теги элемента, раздела и каталога объявлены стандартными без подтверждения автоматического сброса.
- Исправление: [cache-infra.md](bitrix/references/cache-infra.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&LESSON_ID=2978).
- Самопроверка B130 — «Будет ли iblock_id_el_17 сам сброшен после Update?»: Без подтверждённого invalidator нет; выбрать штатный тег инфоблока или реализовать парный проектный сброс.
- Контрпример отвергнут: Считать любое похожее имя встроенным тегом. Результат ручной проверки ответа: pass; runtime: не запускался.

### K52: Явная область чтения Option

- Пробел до изменения: Пример утверждал, что пропуск siteId читает только общую настройку.
- Исправление: [modules-loader.md](bitrix/references/modules-loader.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/coption/getoptionstring.php).
- Самопроверка B131 — «Почему Option::get без siteId вернул значение текущего сайта?»: Не считать пропуск аргумента глобальным чтением; задать сайт либо пустую общую область явно.
- Контрпример отвергнут: Убирать четвёртый аргумент ради гарантированно общего значения. Результат ручной проверки ответа: pass; runtime: не запускался.

### K53: Отсутствующая настройка и сохранённая пустая строка

- Пробел до изменения: Нет способа отличить несохранённую настройку от значения, подставленного default_option.php.
- Исправление: [modules-loader.md](bitrix/references/modules-loader.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/config/option/getrealvalue.php).
- Самопроверка B132 — «Как не перезаписать сохранённый ноль при установке default?»: Получить реальное значение и сравнить с null строго; get с fallback не доказывает наличие записи.
- Контрпример отвергнут: Если empty(Option::get(...)), записать default. Результат ручной проверки ответа: pass; runtime: не запускался.

### K54: Макросы D7 почты передаются через C_FIELDS

- Пробел до изменения: Три примера Event::send/sendImmediate передавали FIELDS вместо документированного C_FIELDS.
- Исправление: [mail-notifications.md](bitrix/references/mail-notifications.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/mail/event/send.php).
- Самопроверка B133 — «Письмо поставилось в очередь, но ORDER_ID пуст — что проверить первым?»: Ключ C_FIELDS в D7 и соответствие макросу шаблона; успешная очередь не подтверждает содержимое.
- Контрпример отвергнут: Передавать FIELDS по аналогии с другим API. Результат ручной проверки ответа: pass; runtime: не запускался.

### K55: Список сайтов в Legacy и D7 почте различается

- Пробел до изменения: Нет контракта переноса многосайтовой отправки CEvent в D7.
- Исправление: [mail-notifications.md](bitrix/references/mail-notifications.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/mail/event/send.php).
- Самопроверка B134 — «Можно ли без изменений передать массив lid из CEvent в Event::send?»: Нет по документированному контракту: D7 LID — строка с ID через запятую.
- Контрпример отвергнут: Считать массив сайтов одинаковым аргументом обоих API. Результат ручной проверки ответа: pass; runtime: не запускался.

### K56: Совместимая регистрация OnBeforeEventSend

- Пробел до изменения: Обработчик с несколькими ссылочными аргументами зарегистрирован через объектный addEventHandler.
- Исправление: [mail-notifications.md](bitrix/references/mail-notifications.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/functions/module/addeventhandler.php).
- Самопроверка B135 — «Почему callback OnBeforeEventSend с массивами не совместим с регистрацией?»: Согласовать legacy-сигнатуру и addEventHandlerCompatible; не заменять callback объектом Event вслепую.
- Контрпример отвергнут: Оставить объектный режим для ссылочных массивов. Результат ручной проверки ответа: pass; runtime: не запускался.

### K57: Отмена постановки письма до очереди

- Пробел до изменения: Описана только стадия шаблонной отправки, но не отмена создания события.
- Исправление: [mail-notifications.md](bitrix/references/mail-notifications.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/events/onbeforeeventadd.php).
- Самопроверка B136 — «Нужно не создавать событие определённого типа — какой hook?»: OnBeforeEventAdd, ограниченный типом события; проверить отсутствие новой записи и сохранение прочих типов.
- Контрпример отвергнут: Использовать OnBeforeEventSend как запрет записи b_event. Результат ручной проверки ответа: pass; runtime: не запускался.

### K58: Явный почтовый шаблон и языковой фильтр

- Пробел до изменения: Нет правил MESSAGE_ID при нескольких шаблонах и языках.
- Исправление: [mail-notifications.md](bitrix/references/mail-notifications.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/events/onbeforeeventadd.php).
- Самопроверка B137 — «Почему с MESSAGE_ID письмо пришло не на выбранном языке?»: Языковой фильтр не выполняется при явном ID; проверить язык выбранного шаблона и mapping окружения.
- Контрпример отвергнут: Считать languageId гарантией языка при любом MESSAGE_ID. Результат ручной проверки ответа: pass; runtime: не запускался.

### K59: DUPLICATE управляет копией, а не идемпотентностью

- Пробел до изменения: Нет значения duplicate, которое легко ошибочно принять за защиту от повторных писем.
- Исправление: [mail-notifications.md](bitrix/references/mail-notifications.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cevent/send.php).
- Самопроверка B138 — «Защитит duplicate=N от двух одинаковых CEvent::Send?»: Нет: это копия на адрес из настроек, два вызова могут создать два события.
- Контрпример отвергнут: Использовать duplicate как ключ дедупликации. Результат ручной проверки ответа: pass; runtime: не запускался.

### K60: Вложение по ID и по пути имеет разную стоимость

- Пробел до изменения: Пример смешивал ID и путь без объяснения повторного сохранения файла и имени вложения.
- Исправление: [mail-notifications.md](bitrix/references/mail-notifications.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cevent/send.php).
- Самопроверка B139 — «Почему при отправке сохранённого файла по пути появилась ещё одна копия?»: Путь сохраняется повторно; использовать разрешённый ID CFile и согласовать срок жизни с очередью.
- Контрпример отвергнут: Передавать GetPath как локальный путь или сразу удалять файл асинхронного письма. Результат ручной проверки ответа: pass; runtime: не запускался.

### Повтор цикла: этап 2 / K51–K60

Релиз предыдущего этапа v1.40.0 опубликован на d876822; Validate Skill и Publish Release завершились успешно.

Ручная самопроверка: B130–B139, затем регрессионные B001 (SetPageProperty('title') / ShowTitle), B004 (Asset CSS), B011 (текущий пользователь), B016 (includeModule), B053 (разделение доказательств). Проверены предметные ответы и отказ от контрпримеров, а не только наличие строк. Исправлены исходные ошибочные примеры в full/compact: ложные штатные теги, область Option, FIELDS, регистрация legacy hook. Каждая из 10 правок прошла make validate и diff check до отдельного коммита. Pass для документации; live Bitrix/доставка реального письма не запускались.

### Gate этапа 5 / 1.41.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K61: MIME из браузера не подтверждает содержимое

- Пробел до изменения: Загрузка разрешалась только по uploadedFile[type], который сообщает клиент.
- Исправление: [import-export.md](bitrix/references/import-export.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cfile/checkfile.php).
- Самопроверка B140 — «Можно ли разрешить загрузку по type=image/jpeg из запроса?»: Нет: это поле клиента; проверить содержимое на сервере и политику расширений/размеров.
- Контрпример отвергнут: Считать MIME браузера доказательством JPEG. Результат ручной проверки ответа: pass; runtime: не запускался.

### K62: CheckFile возвращает текст ошибки, а не success boolean

- Пробел до изменения: Не показан штатный предварительный контроль CFile и его строковый результат.
- Исправление: [import-export.md](bitrix/references/import-export.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cfile/checkfile.php).
- Самопроверка B141 — «CheckFile вернул строку: можно сохранять?»: Нет: остановить сохранение; пустой результат допускает следующий этап проверки.
- Контрпример отвергнут: Трактовать непустой текст CheckFile как успешную проверку. Результат ручной проверки ответа: pass; runtime: не запускался.

### K63: Размеры ResizeImageGet нужно запросить явно

- Пробел до изменения: Пример читает width/height, но не включает четвёртый аргумент bInitSizes.
- Исправление: [import-export.md](bitrix/references/import-export.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cfile/resizeimageget.php).
- Самопроверка B142 — «Почему после ResizeImageGet отсутствует width?»: Проверить bInitSizes=true и успешность вызова; не подменять размеры файла рамкой.
- Контрпример отвергнут: Читать width/height без bInitSizes или растягивать до рамки. Результат ручной проверки ответа: pass; runtime: не запускался.

### K64: Папка upload сама не регистрирует файл в b_file

- Пробел до изменения: Gotcha утверждал, что временный файл попадёт в БД просто из-за размещения в upload.
- Исправление: [import-export.md](bitrix/references/import-export.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cfile/savefile.php).
- Самопроверка B143 — «Появится ли запись b_file после обычного copy в upload?»: Нет по контракту SaveFile; для регистрации нужен соответствующий API.
- Контрпример отвергнут: Считать размещение в upload автоматической регистрацией. Результат ручной проверки ответа: pass; runtime: не запускался.

### K65: MakeFileArray различает путь, URL и ID

- Пробел до изменения: Локальный пример выдавал /local/import/photo.jpg за гарантированный DOCUMENT_ROOT-relative путь.
- Исправление: [import-export.md](bitrix/references/import-export.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cfile/makefilearray.php).
- Самопроверка B144 — «Можно ли передать любой путь из формы в MakeFileArray?»: Нет: определить разрешённый тип источника и корень; сайт-relative путь явно преобразовать.
- Контрпример отвергнут: Полагаться на автоматическое добавление DOCUMENT_ROOT или разрешать любой URL/путь. Результат ручной проверки ответа: pass; runtime: не запускался.

### K66: Картинка элемента записывается файловым дескриптором

- Пробел до изменения: Импорт сохранял CFile заранее и передавал один ID в PREVIEW_PICTURE и DETAIL_PICTURE.
- Исправление: [import-export.md](bitrix/references/import-export.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblockelement/add.php).
- Самопроверка B145 — «Как прикрепить новое изображение при Add элемента?»: Передать проверенный файловый массив; дать API элемента сохранить файл, проверить ID/LAST_ERROR.
- Контрпример отвергнут: Предварительно SaveFile и передать его ID как новый DETAIL_PICTURE. Результат ручной проверки ответа: pass; runtime: не запускался.

### K67: old_file и del нельзя переносить из запроса без нормализации

- Пробел до изменения: Нет разбора служебных ключей файлового массива, способных удалить прежний файл.
- Исправление: [import-export.md](bitrix/references/import-export.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cfile/savefile.php).
- Самопроверка B146 — «Безопасно ли слить POST с файловым массивом, включая old_file/del?»: Нет: служебные ключи задаёт сервер после проверки владельца и намерения удаления.
- Контрпример отвергнут: Доверять old_file из POST или передавать del=N как ложь. Результат ручной проверки ответа: pass; runtime: не запускался.

### K68: CheckImageFile ограничивает геометрию до обработки

- Пробел до изменения: В загрузке изображений не было отдельного контроля ширины и высоты.
- Исправление: [import-export.md](bitrix/references/import-export.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cfile/checkimagefile.php).
- Самопроверка B147 — «Маленький по байтам файл имеет огромные dimensions — достаточно CheckFile?»: Нет: ограничить геометрию CheckImageFile и ресурсы обработки до ресайза.
- Контрпример отвергнут: Считать лимит байтов ограничением числа пикселей. Результат ручной проверки ответа: pass; runtime: не запускался.

### K69: Uploader не должен присваивать себе все входящие файлы

- Пробел до изменения: Кастомный пример разрешал все операции и вызывал markAsOwn для каждого входного файла.
- Исправление: [file-upload-modern.md](bitrix/references/file-upload-modern.md) и [components-admin-ui.md](mcpmarket/bitrix/references/components-admin-ui.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/api/classes/Bitrix-UI-FileUploader-UploaderController.html).
- Самопроверка B148 — «Можно ли после IsAuthorized пометить все fileId как свои?»: Нет: подтвердить каждый файл и операции по серверному объекту-владельцу; не выдумывать разрешающую модель.
- Контрпример отвергнут: Безусловный markAsOwn и canRemove=true. Результат ручной проверки ответа: pass; runtime: не запускался.

### K70: CSV требует исходных значений, а не HTML из GetNext

- Пробел до изменения: CSV-экспорт читал GetNext и сериализовал HTML-экранированное имя в файл. Кроме того, flush вызывался до формирования тела CSV.
- Исправление: [import-export.md](bitrix/references/import-export.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblockresult/getnext.php).
- Самопроверка B149 — «Почему название A & B выгрузилось как A &amp; B?»: GetNext преобразовал HTML; выбрать Fetch и сериализовать исходное значение.
- Контрпример отвергнут: Использовать GetNext как универсальный raw fetch. Результат ручной проверки ответа: pass; runtime: не запускался.

### K71: Формат DateTime нельзя угадывать по строке

- Пробел до изменения: ISO-подобные строки в примерах передавались без явного формата, завися от culture сайта.
- Исправление: [http.md](bitrix/references/http.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/type/datetime/index.php).
- Самопроверка B150 — «Почему new DateTime с Y-m-d строкой работает на одном сайте и падает на другом?»: Не задан format, используется culture; указать Y-m-d H:i:s либо нужный контракт строки.
- Контрпример отвергнут: Полагаться на автоматическое распознавание ISO конструктором. Результат ручной проверки ответа: pass; runtime: не запускался.

### K72: format использует зону объекта, не всегда сервера

- Пробел до изменения: Справочник безусловно приравнивал format к серверному времени даже после setTimeZone.
- Исправление: [http.md](bitrix/references/http.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/type/datetime/settimezone.php).
- Самопроверка B151 — «Вернёт ли format серверное время после setTimeZone(UTC)?»: Нет, он форматирует в установленной зоне объекта; для серверной зоны установить её явно.
- Контрпример отвергнут: Считать format или disableUserTime принудительной серверной зоной. Результат ручной проверки ответа: pass; runtime: не запускался.

### K73: Арифметика Bitrix DateTime изменяет исходный объект

- Пробел до изменения: Примеры add не объясняли, что присваивание даты второй переменной не создаёт копию.
- Исправление: [http.md](bitrix/references/http.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://docs.1c-bitrix.ru/api/classes/Bitrix-Main-Type-DateTime.html).
- Самопроверка B152 — «Почему после расчёта deadline изменился createdAt?»: Обе переменные ссылались на один DateTime; клонировать перед add.
- Контрпример отвергнут: Присвоить объект второй переменной и считать его immutable. Результат ручной проверки ответа: pass; runtime: не запускался.

### K74: Сутки в ORM задаются двумя границами в согласованной зоне

- Пробел до изменения: Нет рецепта фильтра календарного дня без потери границы и ошибок длительности суток.
- Исправление: [http.md](bitrix/references/http.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/type/date/add.php).
- Самопроверка B153 — «Как выбрать все записи пользовательского дня на переходе DST?»: Построить календарные границы в нужной зоне, привести к storage-контракту, использовать >= и <.
- Контрпример отвергнут: Прибавить 86400 или сравнивать локализованные строки. Результат ручной проверки ответа: pass; runtime: не запускался.

### K75: createFromUserTime зависит от текущего пользователя

- Пробел до изменения: Метод перечислен без различения интерактивного ввода и фонового импорта времени.
- Исправление: [http.md](bitrix/references/http.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/type/datetime/createfromusertime.php).
- Самопроверка B154 — «Можно ли одинаково импортировать UTC через createFromUserTime в web и cron?»: Нет: контексты различаются; использовать явный машинный контракт времени.
- Контрпример отвергнут: Повторно применять пользовательский сдвиг к UTC. Результат ручной проверки ответа: pass; runtime: не запускался.

### K76: Составной primary передаётся целиком

- Пробел до изменения: CRUD показывал только числовой ID, не связи с составным первичным ключом.
- Исправление: [orm.md](bitrix/references/orm.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&LESSON_ID=4803).
- Самопроверка B155 — «Можно ли удалить связь с ключом LEFT_ID+RIGHT_ID по одному LEFT_ID?»: Нет: нужен полный primary либо отдельный явно ограниченный сценарий удаления набора.
- Контрпример отвергнут: Передать один scalar или неполный ключ. Результат ручной проверки ответа: pass; runtime: не запускался.

### K77: Незагруженное поле объекта не равно NULL в базе

- Пробел до изменения: Нет поведения get/require после частичного select в объектном ORM.
- Исправление: [orm.md](bitrix/references/orm.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&LESSON_ID=11695).
- Самопроверка B156 — «getTitle вернул null после select ID — надо очистить TITLE в БД?»: Нет: сначала загрузить TITLE; null неполной проекции не доказывает значение в БД.
- Контрпример отвергнут: Сохранить null из незагруженного getter обратно. Результат ручной проверки ответа: pass; runtime: не запускался.

### K78: ExpressionField не параметризует произвольный SQL-текст

- Пробел до изменения: Фраза «безопасно, экранируется» создавала ложную гарантию для всего SQL-выражения.
- Исправление: [orm.md](bitrix/references/orm.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/entity/expressionfield/__construct.php).
- Самопроверка B157 — «Защитит ли %s выражение, в которое уже вставлен текст пользователя?»: Нет: отказаться от конкатенации; значения передать фильтром, поля выбрать по allowlist.
- Контрпример отвергнут: Считать ExpressionField универсальным prepared statement. Результат ручной проверки ответа: pass; runtime: не запускался.

### K79: LIKE-паттерн задаётся явно, wildcard не является SQL injection

- Пробел до изменения: Таблица обещала автоматический prefix/suffix поиск через =% и %= без явной маски.
- Исправление: [orm.md](bitrix/references/orm.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&LESSON_ID=3030).
- Самопроверка B158 — «Почему подчёркивание в коде сопоставилось с другим символом?»: Это wildcard LIKE; определить буквальный или шаблонный поиск и явно задать его.
- Контрпример отвергнут: Считать underscore буквальным символом или гарантировать prefix без маски. Результат ручной проверки ответа: pass; runtime: не запускался.

### K80: TTL ORM-кеша не включает кеширование JOIN автоматически

- Пробел до изменения: Нет отдельного контракта кеша ORM-запросов с JOIN и его принудительной очистки.
- Исправление: [orm.md](bitrix/references/orm.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&LESSON_ID=5753).
- Самопроверка B159 — «Почему JOIN-запрос снова обращается к БД при заданном ttl?»: Проверить cache_joins и настройки кеширования; включать лишь с корректной инвалидизацией зависимостей.
- Контрпример отвергнут: Считать ttl достаточным для любого JOIN и любого способа записи. Результат ручной проверки ответа: pass; runtime: не запускался.

### Поправка итоговой самопроверки

В примере дат после tryParse добавлен явный отказ при null до format/add; исправление поддерживает K71, не считается дополнительным пробелом. Уточнена сокращённая запись B001 в журнале этапа 2: meta title через SetPageProperty/ShowTitle, не обещание SetTitle как универсальной замены.

### Повтор цикла: этап 3 / K61–K80

Предыдущий релиз v1.41.0 опубликован на 9c4020d; Validate Skill и Publish Release — success. Последние 20 пунктов расширяют файловый контур, даты и ORM, без повторения K01–K60.

**Ручная предметная самопроверка:** B140–B159 — правильные решения и отвергнутые контрпримеры записаны по каждому пункту выше. Дополнительно проверены 15 бытовых ответов:

| Сценарий | Проверенный ответ | Результат |
|---|---|---|
| B001 | SetPageProperty('title'), ShowTitle/ShowHead активного шаблона; не ручной meta title и не смешение с H1. | pass |
| B004 | Asset::addCss и вывод head; исключить дубли в шаблоне. | pass |
| B007 | IncludeFile в проектной include area, SITE_DIR и права редактора. | pass |
| B009 | AddChainItem, существующий breadcrumb и параметры цепочки компонента; не второй ручной HTML. | pass |
| B011 | USER после bootstrap, IsAuthorized/GetID; ID не заменяет проверку прав. | pass |
| B013 | Context/getRequest/getQuery, затем тип и допустимый диапазон; request wrapper не делает значение доверенным. | pass |
| B016 | Loader::includeModule и ветка false до обращения к API. | pass |
| B018 | Статус 404 и проектный обработчик/ERROR_404 без подмены редиректом на главную. | pass |
| B021 | CFile/ResizeImageGet, проверка результата; размеры только при bInitSizes, права на источник отдельно. | pass |
| B023 | Проверить PROPERTY_CODE и фактический arResult, тип свойства и кеш; не SQL в таблицы свойств. | pass |
| B025 | Разделить кеш компонента/теги/composite и проверить второй запрос; не глобальный cache-off. | pass |
| B028 | Почтовое событие и шаблон; C_FIELDS в D7; успех очереди не доставка. | pass |
| B030 | Принятый component/Engine action, согласованный HTTP-метод, CSRF и объектные права. | pass |
| B031 | EventManager в модуле/php_interface, compatible для legacy-сигнатуры; не регистрация в шаблоне. | pass |
| B053 | Без Bitrix runtime нет runtime pass: документация, PHP lint и sample evidence его не заменяют. | pass |

Итого для финального этапа: 35 ручных ответов, pass=35, warn=0, fail=0. Это самопроверка, не независимый агентный eval.

**Дополнительные доказательства:**

- 8 полных PHP-примеров (upload, MakeFileArray, ResizeImageGet, ResizeImage, импорт картинки, CSV, абстрактный uploader, даты) прошли php -l после итогового исправления.
- 5 проверок на нативном PHP: clone сохраняет исходную дату; календарный день DST бывает 23 часа; смена зоны сохраняет timestamp; CSV round-trip исходных значений; finfo отличает подложный JPEG. Это проверка предпосылок, не выполнение Bitrix API.
- Все 40 новых контрактов K41–K80 найдены ровно по одному в full и compact; B120–B159 присутствуют в обоих eval. Различия K01–K40 проверены по предметному содержанию.
- Инструменты проверки и CI в этом цикле не изменялись. Каждый предметный пункт прошёл существующий make validate перед отдельным коммитом; дополнительно создан один коммит исправления, найденного итоговой самопроверкой.
- Preflight локального www: blocked, runtime not_checked, ядро отсутствует. Шаблоны P1–P4 и optimization evidence создаются в /tmp; это не заполненные доказательства исполнения.
- Исходные посторонние .playwright-mcp/ и assets/bitrix-agent-skill-ship-support.png не добавлялись в Git.

### Gate этапа 6 / 1.42.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K81: Группы изменяемого пользователя не равны группам оператора

- Пробел до изменения: Пример добавления в группу читал группы текущего USER и записывал их произвольному userId.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cuser/getusergroup.php).
- Самопроверка B160 — «Администратор добавляет клиента в группу: откуда брать существующий набор?»: Из записи клиента по целевому userId, не из USER оператора; проверить право назначения.
- Контрпример отвергнут: Копировать группы администратора клиенту. Результат ручной проверки ответа: pass; runtime: не запускался.

### K82: Замена групп должна сохранять временные членства

- Пробел до изменения: Merge массива ID теряет интервалы активности и может потерять будущие назначения.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cuser/getusergrouplist.php).
- Самопроверка B161 — «Как добавить постоянную группу, не сделать временную бессрочной?»: Считать полный GetUserGroupList и сохранить интервалы при записи структурированного groups.
- Контрпример отвергнут: Свести все членства к одним ID. Результат ручной проверки ответа: pass; runtime: не запускался.

### K83: SetUserGroup не обновляет уже авторизованную сессию

- Пробел до изменения: После записи групп не объяснялась разница БД и уже авторизованного посетителя.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cuser/setusergroup.php).
- Самопроверка B162 — «Группу удалили, но открытая сессия ещё видит доступ — почему?»: Запись членства не равна обновлению активной сессии; проверить механизм отзыва и повторную авторизацию.
- Контрпример отвергнут: Обещать немедленный отзыв во всех сессиях по SetUserGroup. Результат ручной проверки ответа: pass; runtime: не запускался.

### K84: Отмена OnBeforeUserAdd требует false вместе с ThrowException

- Пробел до изменения: Callback имел void и только ThrowException вместо документированного отказа.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/events/onbeforeuseradd.php).
- Самопроверка B163 — «Достаточно ли ThrowException внутри void-обработчика до Add?»: Нет: документированный отказ — сообщение и return false; сигнатура должна разрешать этот результат.
- Контрпример отвергнут: Оставить void и считать ThrowException остановкой исполнения PHP. Результат ручной проверки ответа: pass; runtime: не запускался.

### K85: OnAfterUserAdd вызывается после попытки, а не только успеха

- Пробел до изменения: Примеры выполняли welcome-логику без проверки результата попытки Add.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/events/onafteruseradd.php).
- Самопроверка B164 — «Можно ли отправлять welcome при каждом OnAfterUserAdd?»: Нет: проверить успешный результат и положительный ID; ошибка попытки тоже достигает after hook.
- Контрпример отвергнут: Считать сам вызов after гарантией создания. Результат ручной проверки ответа: pass; runtime: не запускался.

### K86: Register не является административным Add

- Пробел до изменения: Есть только Add и Login; не разграничены создание учётки и публичная регистрация.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cuser/register.php).
- Самопроверка B165 — «Чем создавать пользователей импортом, не меняя сессию администратора?»: CUser::Add; Register относится к публичному потоку с дополнительными эффектами.
- Контрпример отвергнут: Подменить Add методом Register в административном импорте. Результат ручной проверки ответа: pass; runtime: не запускался.

### K87: Email не гарантирует уникальную учётную запись

- Пробел до изменения: getRow по email выдавал первую запись без оговорки о настройках уникальности.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/user_help/settings/settings/settings.php).
- Самопроверка B166 — «Можно ли взять первый UserTable::getRow по email и связать заказ/аккаунт?»: Не без проверки уникальности кандидата и политики идентификации; email не универсальный ключ.
- Контрпример отвергнут: Молча выбрать первого пользователя с общим email. Результат ручной проверки ответа: pass; runtime: не запускался.

### K88: CUser::GetList принимает сортировку по ссылке

- Пробел до изменения: Вызов передавал присваивания выражениями вместо отдельных переменных by/order.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cuser/getlist.php).
- Самопроверка B167 — «Как исправить ошибку передачи первого аргумента CUser::GetList по ссылке?»: Объявить by/order отдельно и передать переменные; не выражения присваивания.
- Контрпример отвергнут: Передать строковый литерал или assignment expression в ссылочный аргумент. Результат ручной проверки ответа: pass; runtime: не запускался.

### K89: LOGIN в legacy-фильтре не равно точному поиску

- Пробел до изменения: Нет различения LOGIN и LOGIN_EQUAL для поиска учётной записи.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cuser/getlist.php).
- Самопроверка B168 — «Поиск LOGIN=ivan вернул ivan_petrov — ошибка ядра?»: Нет: LOGIN — подстрока; для точного поиска LOGIN_EQUAL или GetByLogin.
- Контрпример отвергнут: Выбирать первую строку подстрочного поиска как точную учётку. Результат ручной проверки ответа: pass; runtime: не запускался.

### K90: SendPassword отправляет контрольную строку, а не новый пароль

- Пробел до изменения: Комментарий обещал новый пароль и обязательное совпадение login+email.
- Исправление: [users.md](bitrix/references/users.md) и [users-security.md](mcpmarket/bitrix/references/users-security.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cuser/sendpassword.php).
- Самопроверка B169 — «Получен OK от SendPassword — пароль уже сменён?»: Нет: создан запрос с контрольной строкой; отдельно выполняется подтверждённая смена.
- Контрпример отвергнут: Обещать новый пароль или считать login+email независимой проверкой личности. Результат ручной проверки ответа: pass; runtime: не запускался.

### Третий цикл / K81–K90: Пользователи и группы

База цикла — 8375b06 / 1.42.0. Разрешения на add, commit, push, теги и GitHub Releases для всех трёх этапов прямо получены. Новые пункты сверены с K01–K80 и ранее выполненными пунктами этого цикла: повторов предметных контрактов нет.

Ручная предметная самопроверка B160–B169: ответы и отвергнутые контрпримеры записаны выше; исходные ошибочные примеры исправлены в owning full/compact. Регрессия: B001 — SetPageProperty('title')/ShowTitle, не ручной meta; B004 — Asset и active template, без дублей; B011 — USER после bootstrap и права, не session; B016 — Loader и обработка false; B053 — отсутствие ядра не runtime pass. Итого 15 ручных ответов: pass, warn=0, fail=0. Это самопроверка, не независимый агентный прогон. Каждая правка прошла make validate и diff check до отдельного коммита. Новые инструменты проверки не добавлялись.

### Gate этапа 7 / 1.43.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K91: Периодический агент догоняет пропущенные интервалы

- Пробел до изменения: Совет выбирать Y для фиксированного расписания не учитывал многократные запуски после простоя.
- Исправление: [cache-infra.md](bitrix/references/cache-infra.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cagent/addagent.php).
- Самопроверка B170 — «После часа простоя десятиминутный агент внезапно повторяется — почему?»: Проверить IS_PERIOD=Y и догоняющие интервалы; выбрать N для пересчёта только текущего состояния.
- Контрпример отвергнут: Назначать Y всем задачам ради точности времени. Результат ручной проверки ответа: pass; runtime: не запускался.

### K92: Агент не наследует надёжный контекст посетителя

- Пробел до изменения: Нет явного контракта USER/SITE_ID/языка в фоне.
- Исправление: [cache-infra.md](bitrix/references/cache-infra.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&LESSON_ID=3436).
- Самопроверка B171 — «Почему письмо агента уходит с языком/сайтом случайного хита?»: Фоновому заданию нужен явный сайт и язык; USER/SITE_ID не считать гарантированными.
- Контрпример отвергнут: Авторизовать клиента внутри агента ради контекста. Результат ручной проверки ответа: pass; runtime: не запускался.

### K93: NAME агента является кодом, а не параметризованным заданием

- Пробел до изменения: Указано eval, но нет правила конструирования вызова с внешними данными.
- Исправление: [cache-infra.md](bitrix/references/cache-infra.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cagent/addagent.php).
- Самопроверка B172 — «Как передать текст клиента агенту без включения текста в eval?»: Сохранить данные в серверном задании и передать фиксированному методу проверенный ID.
- Контрпример отвергнут: Конкатенировать PHP-вызов из POST с именем метода и аргументами. Результат ручной проверки ответа: pass; runtime: не запускался.

### K94: DATE_CHECK не заменяет NEXT_EXEC при первом запуске

- Пробел до изменения: Комментарий AddAgent называл DATE_CHECK датой начала вместо первой проверки.
- Исправление: [cache-infra.md](bitrix/references/cache-infra.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cagent/addagent.php).
- Самопроверка B173 — «Как отложить первый запуск агента, не перепутав аргументы дат?»: Задать next_exec в требуемом языковом формате; datecheck имеет другой смысл.
- Контрпример отвергнут: Использовать datecheck как единственный контракт времени первого исполнения. Результат ручной проверки ответа: pass; runtime: не запускался.

### K95: loadMessages регистрирует отложенную загрузку

- Пробел до изменения: Справочник описывал немедленное чтение файла рядом с вызывающим PHP.
- Исправление: [modules-loader.md](bitrix/references/modules-loader.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/localization/loc/loadmessages.php).
- Самопроверка B174 — «Почему helper не нашёл перевод компонента после loadMessages(__FILE__)?»: Проверить, чей путь передан: lazy loading привязано к исходному файлу регистрации.
- Контрпример отвергнут: Считать getMessage поиском рядом с местом каждого вызова. Результат ручной проверки ответа: pass; runtime: не запускался.

### K96: Коды Loc не изолированы PHP-файлом

- Пробел до изменения: Нет предупреждения о глобальной уникальности кода сообщения.
- Исправление: [modules-loader.md](bitrix/references/modules-loader.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/localization/loc/getmessage.php).
- Самопроверка B175 — «Можно ли в каждом файле объявлять собственный MESS[TITLE]?»: Нет гарантированной изоляции; использовать уникальные префиксные коды.
- Контрпример отвергнут: Полагаться на приватность lang-файла для общего ключа. Результат ручной проверки ответа: pass; runtime: не запускался.

### K97: Подстановка Loc не экранирует значение для HTML

- Пробел до изменения: Вывод с заменой #NAME# не объяснял границу текста и HTML.
- Исправление: [modules-loader.md](bitrix/references/modules-loader.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/localization/loc/getmessage.php).
- Самопроверка B176 — «Безопасно ли echo Loc::getMessage с именем из формы?»: Подстановка не sanitizer; экранировать результат для конкретного контекста вывода.
- Контрпример отвергнут: Считать переведённую строку автоматически HTML-безопасной. Результат ручной проверки ответа: pass; runtime: не запускался.

### K98: Явный язык передаётся документированному getMessage

- Пробел до изменения: Пример вызывал не подтверждённый getMessageByLang и загружал язык после чтения.
- Исправление: [modules-loader.md](bitrix/references/modules-loader.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/localization/loc/getmessage.php).
- Самопроверка B177 — «Как получить английский текст без выдуманного getMessageByLang?»: Загрузить нужный файл и вызвать getMessage(code, replacements, en).
- Контрпример отвергнут: Вызывать getMessageByLang как гарантированный публичный метод. Результат ручной проверки ответа: pass; runtime: не запускался.

### K99: Версия модуля читается из arModuleVersion

- Пробел до изменения: Конструктор инсталлятора ожидал version вместо стандартного arModuleVersion.
- Исправление: [modules-loader.md](bitrix/references/modules-loader.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=101&LESSON_ID=2902).
- Самопроверка B178 — «Почему версия модуля пустая после include стандартного version.php?»: Читать arModuleVersion, а не version; проверить оба обязательных значения.
- Контрпример отвергнут: Считать имя локальной переменной произвольным при штатном формате. Результат ручной проверки ответа: pass; runtime: не запускался.

### K100: includeSharewareModule возвращает состояние лицензии

- Пробел до изменения: Нет отличия enum-состояний партнёрского модуля от bool includeModule.
- Исправление: [modules-loader.md](bitrix/references/modules-loader.md) и [php-architecture.md](mcpmarket/bitrix/references/php-architecture.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/loader/includesharewaremodule.php).
- Самопроверка B179 — «Можно ли проверять includeSharewareModule только на truthy?»: Нет: разобрать константы установленного, demo, истёкшего и отсутствующего состояния.
- Контрпример отвергнут: Считать любое ненулевое состояние успешной загрузкой. Результат ручной проверки ответа: pass; runtime: не запускался.

### Третий цикл / K91–K100: Агенты, локализация и модули

База цикла — 8375b06 / 1.42.0. Разрешения на add, commit, push, теги и GitHub Releases для всех трёх этапов прямо получены. Новые пункты сверены с K01–K80 и ранее выполненными пунктами этого цикла: повторов предметных контрактов нет.

Ручная предметная самопроверка B170–B179: ответы и отвергнутые контрпримеры записаны выше; исходные ошибочные примеры исправлены в owning full/compact. Регрессия: B001 — SetPageProperty('title')/ShowTitle, не ручной meta; B004 — Asset и active template, без дублей; B011 — USER после bootstrap и права, не session; B016 — Loader и обработка false; B053 — отсутствие ядра не runtime pass. Итого 15 ручных ответов: pass, warn=0, fail=0. Это самопроверка, не независимый агентный прогон. Каждая правка прошла make validate и diff check до отдельного коммита. Новые инструменты проверки не добавлялись.

### Gate этапа 8 / 1.44.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K101: UF-поля раздела требуют области инфоблока

- Пробел до изменения: Не описан обязательный IBLOCK_ID для UF в выборке разделов.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblocksection/getlist.php).
- Самопроверка B180 — «Почему UF_COLOR раздела не выбирается?»: Задать IBLOCK_ID в фильтре и UF_COLOR в select.
- Контрпример отвергнут: Искать его как PROPERTY_COLOR элемента. Результат ручной проверки ответа: pass; runtime: не запускался.

### K102: ELEMENT_CNT зависит от политики подсчёта

- Пробел до изменения: Пример обещал SECTION_CNT и не задавал семантику числа элементов.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblocksection/getlist.php).
- Самопроверка B181 — «Почему счётчик раздела больше списка товаров?»: Согласовать вложенность, активность и даты; не ждать SECTION_CNT.
- Контрпример отвергнут: Считать bIncCnt числом только активных прямых элементов. Результат ручной проверки ответа: pass; runtime: не запускался.

### K103: Пустая навигация разделов ограничивает десятью

- Пробел до изменения: Не раскрыто отличие [] от false в пятом аргументе GetList разделов.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblocksection/getlist.php).
- Самопроверка B182 — «Почему экспорт с пятым аргументом [] теряет разделы?»: Это лимит десяти; использовать осознанную полную или постраничную выборку.
- Контрпример отвергнут: Считать [] синонимом отсутствия лимита. Результат ручной проверки ответа: pass; runtime: не запускался.

### K104: Проверка прав разделов от имени заданного пользователя

- Пробел до изменения: Не было контракта PERMISSIONS_BY при диагностике чужого доступа.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblocksection/getlist.php).
- Самопроверка B183 — «Как проверить дерево, доступное гостю, из админской сессии?»: PERMISSIONS_BY=0 при включённой проверке прав.
- Контрпример отвергнут: CHECK_PERMISSIONS=N как режим гостя. Результат ручной проверки ответа: pass; runtime: не запускался.

### K105: Порядок дерева не равен глобальной сортировке SORT

- Пробел до изменения: Не объяснено, почему SORT первым ключом ломает обход полного дерева.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblocksection/gettreelist.php).
- Самопроверка B184 — «Почему ребёнок в меню оказывается раньше родителя?»: Проверить порядок дерева: LEFT_MARGIN ASC, не общий SORT.
- Контрпример отвергнут: Восстанавливать иерархию только по отсортированному SORT. Результат ручной проверки ответа: pass; runtime: не запускался.

### K106: GetNavChain: область и форма результата

- Пробел до изменения: Не раскрыты проверка принадлежности и массивный режим хлебных крошек.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblocksection/getnavchain.php).
- Самопроверка B185 — «Можно ли вызвать Fetch на GetNavChain(..., true)?»: Нет, это массив; сохранить проверку IBLOCK_ID и не ждать UF.
- Контрпример отвергнут: Передавать ноль вместо области и считать результат авторизацией. Результат ручной проверки ответа: pass; runtime: не запускался.

### K107: Перемещение раздела сохраняет вычисляемые границы

- Пробел до изменения: Нет правила безопасного перемещения и ограничений bResort.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblocksection/update.php).
- Самопроверка B186 — «Можно ли ускорить перенос раздела, записав LEFT_MARGIN напрямую?»: Нет; Update родителя с пересчётом и проверкой результата.
- Контрпример отвергнут: Писать границы SQL или bResort=false без восстановления дерева. Результат ручной проверки ответа: pass; runtime: не запускался.

### K108: Удаление раздела затрагивает больше одной строки

- Пробел до изменения: Не описаны каскад раздела и влияние на элементы/свойства.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblocksection/delete.php).
- Самопроверка B187 — «Безопасно ли удалить раздел, ожидая только отвязки товаров?»: Нет; сначала оценить каскад и сохранить нужные связи/данные.
- Контрпример отвергнут: Обещать, что все элементы останутся без изменений. Результат ручной проверки ответа: pass; runtime: не запускался.

### K109: Связи элемента с разделами меняются публичным Update

- Пробел до изменения: Нет предупреждения о служебном SetElementSection и главном разделе.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblockelement/setelementsection.php).
- Самопроверка B188 — «Как добавить второй раздел, не потеряв первый и основной?»: Прочитать текущие связи, сформировать полный набор и вызвать Update с основным разделом.
- Контрпример отвергнут: SetElementSection([$newId]) как безусловное добавление. Результат ручной проверки ответа: pass; runtime: не запускался.

### K110: GetElementGroups включает связи из свойств

- Пробел до изменения: Не различались принадлежность разделам и значения свойств типа G.
- Исправление: [iblocks.md](bitrix/references/iblocks.md) и [content-data.md](mcpmarket/bitrix/references/content-data.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/iblock/classes/ciblockelement/getelementgroups.php).
- Самопроверка B189 — «Почему чтение разделов вернуло раздел из свойства RELATED_SECTION?»: По умолчанию включены связи свойств; для принадлежности нужен true.
- Контрпример отвергнут: Записать все найденные разделы обратно как принадлежность. Результат ручной проверки ответа: pass; runtime: не запускался.

### K111: bOverWrite не создаёт второй документ индекса

- Пробел до изменения: Gotcha ошибочно обещала дубли при bOverWrite=false.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/indexs.php).
- Самопроверка B190 — «Создаёт ли Index(..., false) дубль того же MODULE_ID/ITEM_ID?»: Нет; для принудительной перезаписи использовать true с прежней идентичностью.
- Контрпример отвергнут: Каждый false добавляет отдельный документ. Результат ручной проверки ответа: pass; runtime: не запускался.

### K112: Дата поискового документа — DATE_CHANGE

- Пробел до изменения: Таблица и пример использовали неподтверждённое LAST_MODIFIED с D7 DateTime.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/indexs.php).
- Самопроверка B191 — «Почему сортировка по изменению не отражает дату источника?»: Проверить DATE_CHANGE и формат даты, не LAST_MODIFIED.
- Контрпример отвергнут: Передавать произвольный DateTime в вымышленное поле. Результат ручной проверки ответа: pass; runtime: не запускался.

### K113: PERMISSIONS поиска — список читателей, не карта R/D

- Пробел до изменения: Пример путал список групп с картой прав и называл группу 2 авторизованными.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/changepermission.php).
- Самопроверка B192 — «Защищает ли PERMISSIONS=[G2=>R] частный документ?»: Нет; получить реальный список групп читателей, не публиковать группе 2 частные данные.
- Контрпример отвергнут: G2 означает только авторизованных, G1 — всех. Результат ручной проверки ответа: pass; runtime: не запускался.

### K114: Изменение прав источника синхронизируется с индексом

- Пробел до изменения: Нет отдельного жизненного цикла ACL индекса; custom sync игнорировал права.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/changepermission.php).
- Самопроверка B193 — «Текст не менялся, но доступ отозван: достаточно скрыть ссылку на странице?»: Нет; обновить ACL индекса в точной области и проверить выдачу отозванного пользователя.
- Контрпример отвергнут: Ждать полной переиндексации или массово менять права модуля. Результат ручной проверки ответа: pass; runtime: не запускался.

### K115: ChangeSite изменяет привязки и пути индекса

- Пробел до изменения: Не было пути обновления сайтов/URL без удаления всего индекса.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/changesite.php).
- Самопроверка B194 — «Как перенести URL одного индексированного документа на другой сайт?»: Использовать ChangeSite с картой путей и точным ITEM_ID; проверить оба сайта.
- Контрпример отвергнут: Путать ChangeSite с ChangePermission из опечатки документации. Результат ручной проверки ответа: pass; runtime: не запускался.

### K116: ReIndexAll возвращает состояние или итоговый счётчик

- Пробел до изменения: Примеры вызывали переиндексацию без сохранения состояния и выдавали NS за фильтр.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/reindexall.php).
- Самопроверка B195 — «ReIndexAll вернул 0 — запускать снова с пустым NS?»: Нет, число — завершение; только массив задаёт следующий шаг.
- Контрпример отвергнут: Считать 0 ошибкой, а третий аргумент произвольным фильтром. Результат ручной проверки ответа: pass; runtime: не запускался.

### K117: ReIndexAll нельзя вкладывать в незавершённую транзакцию импорта

- Пробел до изменения: Не описана внутренняя транзакция глобальной переиндексации.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/reindexall.php).
- Самопроверка B196 — «Можно ли включить ReIndexAll в транзакцию импорта для общей атомарности?»: Нет; отделить задание индексации, не коммитить транзакцию вызывающего кода внутри helper.
- Контрпример отвергнут: Считать вложенный вызов общей атомарной транзакцией. Результат ручной проверки ответа: pass; runtime: не запускался.

### K118: OnReindex использует callback поискового модуля

- Пробел до изменения: Пример выдумывал сигнатуру max_execution_time и возвращал NS вместо курсора callback-контракта.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/events/onreindex.php).
- Самопроверка B197 — «Должен ли OnReindex принимать max_execution_time и возвращать NS?»: Нет; использовать документированный callback-протокол с ID/false.
- Контрпример отвергнут: Копировать сигнатуру ReIndexAll в обработчик события. Результат ручной проверки ответа: pass; runtime: не запускался.

### K119: Ограничение поиска задаётся MODULE_ID

- Пробел до изменения: Пример и таблица называли фильтр MODULE вместо MODULE_ID.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/search.php).
- Самопроверка B198 — «Почему поиск с MODULE=iblock не ограничивается нужным источником?»: Исправить ключ на MODULE_ID и согласовать параметры с индексатором.
- Контрпример отвергнут: MODULE и MODULE_ID взаимозаменяемы. Результат ручной проверки ответа: pass; runtime: не запускался.

### K120: aParamsEx объединяет альтернативные области через ИЛИ

- Пробел до изменения: Не описана логика третьего аргумента Search для нескольких источников.
- Исправление: [search.md](bitrix/references/search.md) и [search-seo-ops.md](mcpmarket/bitrix/references/search-seo-ops.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/search.php).
- Самопроверка B199 — «Как искать в одном форуме или одном инфоблоке, не требуя оба модуля сразу?»: Две области в aParamsEx; общий SITE_ID и доступ не расширять.
- Контрпример отвергнут: Считать массивы aParamsEx логическим И. Результат ручной проверки ответа: pass; runtime: не запускался.

Самопроверка K112 перед релизом: обязательность DATE_CHANGE не выводится из одного официального примера. Заголовок таблицы уточнён: поле задано явно в нашем примере; универсальная обязательность без ядра не заявлена.

### Третий цикл / K101–K120: Разделы инфоблоков и внутренний поиск

База цикла — 8375b06 / 1.42.0. Разрешения на add, commit, push, теги и GitHub Releases для всех трёх этапов прямо получены. Новые пункты сверены с K01–K80 и ранее выполненными пунктами этого цикла: повторов предметных контрактов нет.

Ручная предметная самопроверка B180–B199: ответы и отвергнутые контрпримеры записаны выше; исходные ошибочные примеры исправлены в owning full/compact. Регрессия: B001 — SetPageProperty('title')/ShowTitle, не ручной meta; B004 — Asset и active template, без дублей; B011 — USER после bootstrap и права, не session; B016 — Loader и обработка false; B053 — отсутствие ядра не runtime pass. Итого 25 ручных ответов: pass, warn=0, fail=0. Это самопроверка, не независимый агентный прогон. Каждая правка прошла make validate и diff check до отдельного коммита. Новые инструменты проверки не добавлялись.

### Дополнительные доказательства третьего цикла

- K81–K120: 40 уникальных разделов в owning full/compact и 40 парных сценариев B160–B199; для каждого сохранён успешный локальный make validate до коммита.
- K101–K120 проверены по исходной версии 8375b06: GetNavChain приложения уже описан, но новый K106 относится к CIBlockSection; GLOBAL_ACTIVE и идентичность поискового документа уже известны и не посчитаны отдельными новыми пунктами. K111 исправляет отдельную ложную семантику bOverWrite.
- PHP lint изменённых полных примеров: пользовательские события, конструктор модуля, Loc, агент и OnReindex — pass. Локальная PHP-фикстура протокола OnReindex: остановка на ID=2, продолжение с ID=3, сброс чужого курсора модуля — pass. Это проверка примера с подставным callback, не установленного Bitrix.
- Релиз v1.43.0 опубликован на f842dce8755b38a2a09d6752eeade625e283bcef; v1.44.0 — на a600f98ed860d9f981e6d93c83b93eeb0f7e843b. Для каждого подтверждены draft=false, prerelease=false, правильные пункты changelog и успешные Publish Release/Validate Skill на том же SHA.
- Предсуществующие .playwright-mcp/ и assets/bitrix-agent-skill-ship-support.png не включались в коммиты этой задачи.

### Gate этапа 9 / 1.45.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K121: HTML-имена ответов зависят от типа вопроса

- Пробел до изменения: Не было схемы имён входных полей form; SID и ID ответа легко перепутать.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/htmlnames.php).
- Самопроверка B200 — «Почему form_text_CONTACT не сохраняет имя, а radio сохраняет?»: Текст требует ID ответа в имени, radio — SID вопроса и ID варианта в значении.
- Контрпример отвергнут: Все типы имеют ключ form_тип_SID. Результат ручной проверки ответа: pass; runtime: не запускался.

### K122: values=false читает REQUEST, а не пустую форму

- Пробел до изменения: Пример отдавал весь POST в persistence без явной границы входных данных.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/classes/cformresult/add.php).
- Самопроверка B201 — «Как создать результат из подготовленного пустого набора, не подхватив GET?»: Передать явный массив, не false; контролировать вход на границе обработчика.
- Контрпример отвергнут: false означает отсутствие ответов. Результат ручной проверки ответа: pass; runtime: не запускался.

### K123: Check возвращает ошибки и знает редактируемый результат

- Пробел до изменения: Не был описан штатный validation flow и массив ошибок по SID.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/classes/cform/check.php).
- Самопроверка B202 — «Check вернул массив с ошибкой EMAIL — это успешная проверка?»: Нет; показать ошибку и не сохранять, при редактировании передать текущий RESULT_ID.
- Контрпример отвергнут: Непустой результат Check означает success. Результат ручной проверки ответа: pass; runtime: не запускался.

### K124: user_id в Add задаёт автора, не субъекта проверки прав

- Пробел до изменения: Не раскрыта роль четвёртого аргумента при импорте результатов.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/classes/cformresult/add.php).
- Самопроверка B203 — «Достаточно передать ID администратора четвёртым аргументом Add?»: Нет, это автор; права текущего субъекта и разрешение импорта проверяются отдельно.
- Контрпример отвергнут: user_id подменяет текущего пользователя для проверки доступа. Результат ручной проверки ответа: pass; runtime: не запускался.

### K125: Неактивный вопрос может молча не сохранить ответ

- Пробел до изменения: Не было диагностики успешного результата с потерянным отдельным ответом.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/classes/cformresult/add.php).
- Самопроверка B204 — «ID результата получен, но один переданный ответ пропал — это кеш?»: Сначала проверить активность вопроса и соответствие входа схеме.
- Контрпример отвергнут: Успех Add доказывает сохранение каждого входного ключа. Результат ручной проверки ответа: pass; runtime: не запускался.

### K126: GetDataByID даёт две разные индексации ответов

- Пробел до изменения: Возвращаемое значение и выходной параметр answers не различались.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/classes/cformresult/getdatabyid.php).
- Самопроверка B205 — «Почему answers[SID][0] отсутствует, хотя ответ существует?»: Выходной answers индексируется ID ответа, не нулём; различать его с return.
- Контрпример отвергнут: Возврат и оба выходных массива имеют одинаковую структуру. Результат ручной проверки ответа: pass; runtime: не запускался.

### K127: Update управляет дополнительными полями отдельным флагом

- Пробел до изменения: Не раскрыты update_fields и отличие полного Update от точечного SetField.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/classes/cformresult/update.php).
- Самопроверка B206 — «Почему служебное поле ADDITIONAL не меняется при Update по умолчанию?»: Нужен осознанный update_fields=Y и проверка прав; не отключать check_rights.
- Контрпример отвергнут: Третий аргумент всегда означает права, как у Add. Результат ручной проверки ответа: pass; runtime: не запускался.

### K128: SetField принимает значения по ID ответа, false очищает

- Пробел до изменения: Упоминался SetField без формата аргумента и опасного default.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/classes/cformresult/setfield.php).
- Самопроверка B207 — «Можно ли не передавать value в SetField, чтобы оставить ответ прежним?»: Нет, false очищает; отсутствие изменения означает не вызывать метод.
- Контрпример отвергнут: SetField принимает тот же payload, что Add, и пропуск безопасен. Результат ручной проверки ответа: pass; runtime: не запускался.

### K129: Фильтр ответов результата вложен в FIELDS

- Пробел до изменения: Не было поиска по ответам; пример имел присваивания в ссылочных аргументах.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/classes/cformresult/getlist.php).
- Самопроверка B208 — «Как отфильтровать результаты по введённому EMAIL, а не подписи ответа?»: FIELDS с нужным SID, PARAMETER_NAME=USER и подходящим FILTER_TYPE.
- Контрпример отвергнут: Искать пользовательский ввод через ANSWER_TEXT либо PROPERTY_EMAIL. Результат ручной проверки ответа: pass; runtime: не запускался.

### K130: GetDataByIDForHTML возвращает данные для имён полей, не готовую разметку

- Пробел до изменения: Название helper могло трактоваться как готовый безопасный HTML или полный набор служебных полей.
- Исправление: [webforms.md](bitrix/references/webforms.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/form/classes/cformresult/getdatabyidforhtml.php).
- Самопроверка B209 — «Можно ли echo всего результата GetDataByIDForHTML и передать файл как новый upload?»: Нет; это массив значений с HTML-ключами, файл — сохранённый ID, вывод экранируется по контексту.
- Контрпример отвергнут: ForHTML означает готовую безопасную HTML-строку. Результат ручной проверки ответа: pass; runtime: не запускался.

### Четвёртый цикл / K121–K130: Веб-формы: ввод, ответы и результаты

База — d620bc2 / 1.45.0. Разрешения на add, commit, push, теги и GitHub Releases получены для всех трёх этапов. Новые контракты сверены с K01–K120 и ранее выполненными пунктами текущего цикла; упоминание API без его отсутствующего контракта не засчитывалось как готовое решение. Дубли исправлений из прежних циклов не посчитаны новыми пунктами.

Предметная самопроверка B200–B209: ответы и отвергнутые контрпримеры выше, 10 pass. Дополнительно 15 бытовых ответов разных доменов проверены вручную:

| Сценарий | Проверенный ответ | Итог |
|---|---|---|
| B001 | SetPageProperty title и штатный вывод head, не ручной meta title | pass |
| B004 | Asset/addCss и активный шаблон, не echo link из компонента | pass |
| B007 | IncludeFile/include area с правами, не хардкод футера | pass |
| B009 | AddChainItem/штатный breadcrumb без двойной цепочки | pass |
| B011 | USER после bootstrap, IsAuthorized/GetID и отдельные права | pass |
| B013 | Request GET плюс проверка типа/диапазона, не сырой REQUEST | pass |
| B016 | Loader includeModule и отказ при false | pass |
| B018 | HTTP 404 + проектная страница, не только текст 404 | pass |
| B021 | CFile GetPath/ResizeImageGet и проверка существования | pass |
| B023 | PROPERTY_CODE и arResult, не прямой SQL в шаблоне | pass |
| B025 | Определить слой кеша, проверить повторный запрос; не выключать всё | pass |
| B028 | Почтовое событие и шаблон; постановка в очередь не доставка | pass |
| B030 | Штатный AJAX-контракт, sessid/авторизация, JSON | pass |
| B031 | EventManager в модуле/init, совместимый контракт, не шаблон | pass |
| B053 | Без живого ядра нет runtime pass, документации недостаточно | pass |

Итого 25 ручных сценариев: pass; warn=0, fail=0. Это самопроверка, не независимый агентный прогон. Каждый пункт прошёл make validate и diff check до коммита; новые инструменты проверки в репозиторий не добавлены.

### Gate этапа 10 / 1.46.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K131: Публичная подписка не должна сама устанавливать CONFIRMED=Y

- Пробел до изменения: Основной пример обходил подтверждение адреса по умолчанию.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptionadd.php).
- Самопроверка B210 — «Можно ли сразу ставить CONFIRMED=Y при отправке публичной формы?»: Нет; оставить подтверждение адреса штатному потоку, импорт выделить отдельно.
- Контрпример отвергнут: Введённый email и ACTIVE=Y доказывают подтверждение. Результат ручной проверки ответа: pass; runtime: не запускался.

### K132: EMAIL подписки уникален, существующая запись не принадлежит заявителю автоматически

- Пробел до изменения: Не раскрыт конфликт уникальности подписки и безопасное продолжение.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptiongeneralfields.php).
- Самопроверка B211 — «Add не создал подписку из-за существующего EMAIL — можно сразу обновить её?»: Только после проверки доступа к найденной подписке; не раскрывать приватные данные.
- Контрпример отвергнут: Совпадение введённого email даёт право менять USER_ID и RUB_ID. Результат ручной проверки ответа: pass; runtime: не запускался.

### K133: Обновление RUB_ID требует явной области сайта

- Пробел до изменения: ALL_SITES был перечислен без объяснения области изменения рубрик.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptionupdate.php).
- Самопроверка B212 — «Почему изменение рубрик одного сайта затронуло другой?»: Проверить SITE_ID/ALL_SITES и полный желаемый набор рубрик в выбранной области.
- Контрпример отвергнут: ALL_SITES=Y безопасно включать для любого Update. Результат ручной проверки ответа: pass; runtime: не запускался.

### K134: Authorize с false безусловно открывает доступ к подписке

- Пробел до изменения: Не описан опасный default кода авторизации подписки.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptionauthorize.php).
- Самопроверка B213 — «Можно ли восстановить доступ к подписке вызовом Authorize(ID) из формы email?»: Нет, default false безусловно авторизует; использовать проверенный код/владельца.
- Контрпример отвергнут: Authorize без кода безопасно сам проверит владельца. Результат ручной проверки ответа: pass; runtime: не запускался.

### K135: Смена EMAIL снимает подтверждение подписки

- Пробел до изменения: Пример Update заново устанавливал CONFIRMED=Y без нового доказательства владения адресом.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptionupdate.php).
- Самопроверка B214 — «Можно ли сохранить подтверждение старого адреса после изменения EMAIL?»: Нет; штатный Update запускает новое подтверждение, не подменять его флагом.
- Контрпример отвергнут: Успешный Update или SENT означает подтверждённый новый email. Результат ручной проверки ответа: pass; runtime: не запускался.

### K136: Статусы posting изменяют очередь, а не только метку

- Пробел до изменения: Не описаны сохранение/очистка очереди при pause/retry и неверный старт в P.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/cpostinggeneral/cpostingchangestatus.php).
- Самопроверка B215 — «Как продолжить остановленную рассылку, не собрать список заново?»: W→P; не переводить в D для обычного продолжения.
- Контрпример отвергнут: Статус можно писать напрямую, D — безопасная пауза. Результат ручной проверки ответа: pass; runtime: не запускался.

### K137: SendMessage имеет три исхода, CONTINUE не является успехом

- Пробел до изменения: Пример не разбирал частичную отправку и ошибочно называл метод тестовым.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/cpostinggeneral/cpostingsendmessage.php).
- Самопроверка B216 — «Если SendMessage вернул CONTINUE, можно показать «готово»?»: Нет; сохранить продолжение и проверить причину, не сбрасывая очередь.
- Контрпример отвергнут: Любая непустая строка означает успешную полную отправку. Результат ручной проверки ответа: pass; runtime: не запускался.

### K138: DIRECT_SEND задаёт персональную отправку, а не синхронность

- Пробел до изменения: Поле было показано без семантики и связи с пакетными ограничениями.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/cpostinggeneral/cpostingfields.php).
- Самопроверка B217 — «DIRECT_SEND=Y обходит очередь и немедленно отправляет письмо?»: Нет; это персональный режим, очередь и запуск управляются отдельно.
- Контрпример отвергнут: DIRECT_SEND означает прямую синхронную отправку. Результат ручной проверки ответа: pass; runtime: не запускался.

### K139: Счётчики очереди используют Y как ожидание и N как отправку

- Пробел до изменения: Не было правильной интерпретации статистики получателей.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/cpostinggeneral/getemailstatuses.php).
- Самопроверка B218 — «В GetEmailStatuses нет Y, но есть E — выпуск успешен?»: Нет; остались ошибки, а отсутствие ожидающих само по себе не доказывает успех.
- Контрпример отвергнут: Y значит успешно отправлено, N — не отправлено. Результат ручной проверки ответа: pass; runtime: не запускался.

### K140: Вложение posting связывается через SaveFile

- Пробел до изменения: Не описана регистрация вложения в lifecycle конкретного выпуска.
- Исправление: [subscribe.md](bitrix/references/subscribe.md) и [content-modules.md](mcpmarket/bitrix/references/content-modules.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/cpostinggeneral/cpostingsavefile.php).
- Самопроверка B219 — «Файл уже есть в b_file — автоматически ли он приложен к posting?»: Нет; нужна штатная привязка вложения к выпуску и проверка результата.
- Контрпример отвергнут: Один CFile::SaveFile гарантирует вложение рассылки. Результат ручной проверки ответа: pass; runtime: не запускался.

### Четвёртый цикл / K131–K140: Подписки и очередь рассылок

База — d620bc2 / 1.45.0. Разрешения на add, commit, push, теги и GitHub Releases получены для всех трёх этапов. Новые контракты сверены с K01–K120 и ранее выполненными пунктами текущего цикла; упоминание API без его отсутствующего контракта не засчитывалось как готовое решение. Дубли исправлений из прежних циклов не посчитаны новыми пунктами.

Предметная самопроверка B210–B219: ответы и отвергнутые контрпримеры выше, 10 pass. Дополнительно 15 бытовых ответов разных доменов проверены вручную:

| Сценарий | Проверенный ответ | Итог |
|---|---|---|
| B001 | SetPageProperty title и штатный вывод head, не ручной meta title | pass |
| B004 | Asset/addCss и активный шаблон, не echo link из компонента | pass |
| B007 | IncludeFile/include area с правами, не хардкод футера | pass |
| B009 | AddChainItem/штатный breadcrumb без двойной цепочки | pass |
| B011 | USER после bootstrap, IsAuthorized/GetID и отдельные права | pass |
| B013 | Request GET плюс проверка типа/диапазона, не сырой REQUEST | pass |
| B016 | Loader includeModule и отказ при false | pass |
| B018 | HTTP 404 + проектная страница, не только текст 404 | pass |
| B021 | CFile GetPath/ResizeImageGet и проверка существования | pass |
| B023 | PROPERTY_CODE и arResult, не прямой SQL в шаблоне | pass |
| B025 | Определить слой кеша, проверить повторный запрос; не выключать всё | pass |
| B028 | Почтовое событие и шаблон; постановка в очередь не доставка | pass |
| B030 | Штатный AJAX-контракт, sessid/авторизация, JSON | pass |
| B031 | EventManager в модуле/init, совместимый контракт, не шаблон | pass |
| B053 | Без живого ядра нет runtime pass, документации недостаточно | pass |

Итого 25 ручных сценариев: pass; warn=0, fail=0. Это самопроверка, не независимый агентный прогон. Каждый пункт прошёл make validate и diff check до коммита; новые инструменты проверки в репозиторий не добавлены.

### Gate этапа 11 / 1.47.0

`make release-check`, 23 существующих теста инструментов и quick_validate обеих версий: pass. Эти тесты не доказывают знания API; предметная самопроверка записана для каждого K-пункта. Compact: 35/50 файлов. Live Bitrix runtime не выполнялся. Публикация — штатный Publish Release после push в master.

### K141: Запись цены через Model сохраняет автоматические действия каталога

- Пробел до изменения: Справочник безусловно предпочитал PriceTable для записи цены, не учитывая model lifecycle.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/catalog/model/price/add.php).
- Самопроверка B220 — «Почему запись PRICE в таблицу не обновила связанные значения каталога?»: Проверить обход Model\Price и его автоматических действий, а не только очистить кеш.
- Контрпример отвергнут: Любой DataManager write эквивалентен коммерческому model API. Результат ручной проверки ответа: pass; runtime: не запускался.

### K142: Price::update принимает ID цены, не ID товара

- Пробел до изменения: Не различались primary цены и её PRODUCT_ID при изменении.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/catalog/model/price/update.php).
- Самопроверка B221 — «Можно ли передать PRODUCT_ID первым аргументом Price::update?»: Нет; это ID цены, найденной и проверенной в нужном товаре/типе/диапазоне.
- Контрпример отвергнут: ID товара, типа и цены взаимозаменяемы. Результат ручной проверки ответа: pass; runtime: не запускался.

### K143: PRICE_SCALE — производное значение в базовой валюте

- Пробел до изменения: Поле PRICE_SCALE не объяснялось и могло заполняться исходной ценой другой валюты.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/catalog/pricetable/index.php?print=Y).
- Самопроверка B222 — «Можно ли при импорте USD записать PRICE_SCALE равным числу PRICE?»: Нет; сохранять исходную цену/валюту и использовать штатный пересчёт.
- Контрпример отвергнут: PRICE_SCALE всегда совпадает с PRICE. Результат ручной проверки ответа: pass; runtime: не запускался.

### K144: Границы количественной цены обновляются парой

- Пробел до изменения: Упоминались quantity ranges без контракта их изменения.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/catalog/model/price/update.php).
- Самопроверка B223 — «Достаточно обновить только QUANTITY_FROM у существующей цены?»: Нет; передать согласованную пару границ и проверить пограничные количества.
- Контрпример отвергнут: Вторая граница сама всегда перестроится безопасно. Результат ручной проверки ответа: pass; runtime: не запускался.

### K145: Пересчёт наценок не означает изменение всех цен товара

- Пробел до изменения: Не описаны область и результат recountPricesFromBase.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/catalog/model/price/recountpricesfrombase.php).
- Самопроверка B224 — «Метод вернул true — можно считать все цены товара пересчитанными?»: Нет; проверить наличие наценок, диапазон и фактические изменённые строки.
- Контрпример отвергнут: true означает обновление каждой цены и каждого диапазона. Результат ручной проверки ответа: pass; runtime: не запускался.

### K146: Product::add дополняет существующий элемент, а не создаёт карточку инфоблока

- Пробел до изменения: Не описан порядок двух сущностей при создании товара.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/catalog/model/product/add.php).
- Самопроверка B225 — «Создаст ли Product::add с NAME новый элемент и назначит ID?»: Нет; нужен уже существующий элемент каталога и проверка отдельного результата записи.
- Контрпример отвергнут: Product::add заменяет CIBlockElement::Add. Результат ручной проверки ответа: pass; runtime: не запускался.

### K147: Единицы веса и габаритов каталога фиксированы

- Пробел до изменения: Не объяснялись единицы полей, из-за чего данные внешней доставки можно передать без пересчёта.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/user_help/content/iblock/iblock_element_admin.php?print=Y).
- Самопроверка B226 — «Источник отдаёт 2 кг и длину 30 см — что сохранить в catalog?»: 2000 граммов и LENGTH=300 миллиметров после проверки единиц источника.
- Контрпример отвергнут: MEASURE автоматически преобразует вес и габариты. Результат ручной проверки ответа: pass; runtime: не запускался.

### K148: D в настройках товара означает наследование, не false

- Пробел до изменения: Флаги QUANTITY_TRACE/CAN_BUY_ZERO/SUBSCRIBE перечислялись без семантики D.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/catalog/producttable/index.php).
- Самопроверка B227 — «Можно ли считать QUANTITY_TRACE=D отключённым учётом?»: Нет; разрешить настройку модуля и не переписать наследование постоянным N.
- Контрпример отвергнут: Любое значение кроме Y равно N. Результат ручной проверки ответа: pass; runtime: не запускался.

### K149: getOffersList возвращает вложенную карту и требует области для свойств

- Пробел до изменения: Не описан пакетный контракт выборки SKU и ограничение property-фильтра.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/catalog/classes/catalogsku/getofferslist.php).
- Самопроверка B228 — «Почему в пакетной выборке предложений нет NAME и ключа одного товара?»: Запросить fields явно и учитывать отсутствие предложений; разобрать вложенную карту.
- Контрпример отвергнут: Пустой fields возвращает всё, результат всегда плоский и полный. Результат ручной проверки ответа: pass; runtime: не запускался.

### K150: GetProductInfo принимает инфоблок предложения, возвращает инфоблок родителя

- Пробел до изменения: Не различались входная и выходная области обратного поиска SKU.
- Исправление: [catalog.md](bitrix/references/catalog.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/catalog/classes/catalogsku/getproductinfo.php?print=Y).
- Самопроверка B229 — «Какой IBLOCK_ID передавать в GetProductInfo и какой получим назад?»: Передать offers-ИБ, получить parent-ИБ; false обработать до чтения массива.
- Контрпример отвергнут: Входной и выходной IBLOCK_ID всегда относятся к одному ИБ. Результат ручной проверки ответа: pass; runtime: не запускался.

### K151: RATE_CNT задаёт номинал валютного курса

- Пробел до изменения: Курс читался без объяснения количества единиц в котировке.
- Исправление: [currency.md](bitrix/references/currency.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencyrates/ccurrencyrates__add.a9ea23d5.php).
- Самопроверка B230 — «Если за 100 единиц указано RATE=250, сколько стоит одна?»: 2.5 базовых единицы; сохранить RATE_CNT=100 и RATE=250.
- Контрпример отвергнут: Умножить любую сумму на 250 без номинала. Результат ручной проверки ответа: pass; runtime: не запускался.

### K152: Историческая конвертация требует даты, а не последней строки курса

- Пробел до изменения: Пример выбирал последнюю запись без ограничения даты, что могло взять будущий курс.
- Исправление: [currency.md](bitrix/references/currency.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencyrates/getconvertfactorex.php).
- Самопроверка B231 — «Можно ли пересчитать прошлый документ по последней строке CurrencyRateTable?»: Нет; передать дату расчёта, проверить покрытие курсов и не брать будущую запись.
- Контрпример отвергнут: Самая новая строка всегда верна для любой даты. Результат ручной проверки ответа: pass; runtime: не запускался.

### K153: CurrencyFormat форматирует, но не переводит между валютами

- Пробел до изменения: Не проведена граница между валютой значения и валютой оформления.
- Исправление: [currency.md](bitrix/references/currency.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencylang/currencyformat.php?print=Y).
- Самопроверка B232 — «Превратит ли CurrencyFormat(100, EUR) сто USD в EUR?»: Нет, только оформит 100 как EUR; сначала нужна конвертация с валютой источника.
- Контрпример отвергнут: Код валюты в форматировании автоматически конвертирует сумму. Результат ручной проверки ответа: pass; runtime: не запускался.

### K154: Большие суммы форматируются десятичной строкой с учётом версии

- Пробел до изменения: Нет контракта сохранения точности больших чисел при форматировании.
- Исправление: [currency.md](bitrix/references/currency.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencylang/formatvalue.php).
- Самопроверка B233 — «Как вывести сумму длиннее точности float без потери цифр?»: Сохранить десятичную строку и проверить версию formatValue; не преобразовывать заранее.
- Контрпример отвергнут: float перед форматированием без потерь подходит для любой суммы. Результат ручной проверки ответа: pass; runtime: не запускался.

### K155: HIDE_ZERO различает публичный и административный вывод

- Пробел до изменения: Не объяснено штатное различие дробных нулей между витриной и админкой.
- Исправление: [currency.md](bitrix/references/currency.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencylang/getformatdescription.php).
- Самопроверка B234 — «В админке 10.00, на витрине 10 — потеряна точность цены?»: Не обязательно; проверить HIDE_ZERO и формат, исходную сумму не менять.
- Контрпример отвергнут: Для совпадения вида переписать цену без дробной части. Результат ручной проверки ответа: pass; runtime: не запускался.

### K156: Обработчик CurrencyFormat может заменить штатный результат

- Пробел до изменения: Не был описан приоритет пользовательского обработчика форматирования.
- Исправление: [currency.md](bitrix/references/currency.md) и [commerce-shop.md](mcpmarket/bitrix/references/commerce-shop.md); источник: [Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/events/currencyformat.php?print=Y).
- Самопроверка B235 — «Почему правильный FORMAT_STRING не влияет на вывод цены?»: Проверить обработчик CurrencyFormat, который возвращает собственную строку.
- Контрпример отвергнут: Изменять FORMAT_STRING вслепую, игнорируя обработчики. Результат ручной проверки ответа: pass; runtime: не запускался.
