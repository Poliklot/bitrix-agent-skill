# План и статус аудита Bitrix-скилла

## Цель

Поддерживать `bitrix-agent-skill` как **core-first** навык для 1C-Bitrix CMS: все утверждения, примеры API и маршруты должны опираться на реально установленное ядро проекта, а не на память, форумы или “типичный Bitrix”.

## Текущий статус

На дату этого плана:
- актуальная версия навыка: `1.20.0`;
- точка входа: `bitrix/SKILL.md`;
- reference-слой: `bitrix/references/*.md`;
- non-commerce reference-слой прошёл ревизию против установленного core;
- PHP workflow/testing/quality, legacy modernization, diagnostics, standard components и operations-runbook закрыты как активный non-commerce контур;
- отдельный shop-core установлен и переаудирован inventory-слоем: 49 модулей, включая `catalog` 25.550.0, `sale` 26.0.0, `currency` 26.0.0, `bitrix.eshop` 25.0.0, 1С/CommerceML components;
- магазинный контур активируется только после проверки этих модулей в конкретном проекте;
- полный shop-core module inventory вынесен в `shop-core-module-inventory.md`: versions, component/admin counts, coverage status и ordered roadmap uncovered зон;
- `storeassist` 24.0.0 глубоко разобран как мастер/чеклист магазина и 1С onboarding, а не exchange engine;
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
- обмен с `1С` / `CommerceML`
- магазинные workflow в целом: торговые предложения, цены, остатки, склады, корзина, checkout, оплата, доставка, скидки, заказы, отгрузки, возвраты

Для shop-core-аудита эти домены уже подтверждены и описаны в `catalog.md`, `sale.md`, `currency.md`, `commerce-workflows.md`, `commerce-1c-integration.md`, `shop-task-matrix.md`.

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

## Следующие шаги

### Ближайшие

1. Держать non-commerce reference-слой консистентным при следующих правках.
2. Держать `pagination.md` связанным с `iblocks.md`, `components.md`, `admin-ui.md`, `grid-admin-modern.md`, `sef-urls.md` и `diagnostic-visibility.md` при новых находках.
3. Держать `shop-core-module-inventory.md` как source-of-truth по coverage gaps и не обещать глубокое покрытие uncovered-модулей без отдельного reference.
4. При появлении новых локальных модулей или project overrides добавлять их в маршрут только после проверки по коду.
5. Собрать небольшой набор smoke-задач для ручной проверки качества навыка на текущем non-commerce core.

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
5. Ordered roadmap: `storeassist.md` → `shop-standard-components.md` → `shop-marketing-analytics.md` → `shop-automation-bizproc.md` → `shop-integrations-webservice.md`.

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

### Следующие шаги после baseline 1.20.0

1. Следующим ordered deep-dive сделать `shop-standard-components.md` по public/admin storefront components.
2. Затем сделать `shop-marketing-analytics.md` по `sender`, `mail`, `messageservice`, `report`, `statistic`, `conversion`, `abtest`, `advertising`.
3. Затем сделать `shop-automation-bizproc.md` по `bizproc`, `bizprocdesigner`, `workflow`, `lists`, `pull`.
4. Поднять Docker/runtime shop-core и проверить, есть ли живой DB dump или нужна свежая установка.
5. Собрать smoke fixtures для каталога, offer, цены, остатка, корзины, checkout, заказа и CommerceML.
6. Прогнать ручные smoke-задачи навыка на shop-core.
7. После runtime-smoke при необходимости расширить reference-файлы конкретными DB/runtime findings.

## Definition of done для текущей фазы

Non-commerce фаза считается завершённой, когда:
- reference-файлы не содержат неподтверждённых API без явной пометки;
- `SKILL.md` маршрутизирует задачи только в подтверждённые домены;
- служебные документы репозитория не спорят с фактическим состоянием навыка;
- deferred-домены явно отделены от активного маршрута.

Commerce/1C фаза считается завершённой, когда:
- установлен и задокументирован отдельный shop-core sandbox;
- `catalog`, `sale`, `currency` и обмен с 1С подтверждены по реальному коду;
- `catalog.md`, `sale.md`, `commerce-workflows.md` переаудированы;
- создан или обновлён reference по `1С`/`CommerceML`;
- skill умеет маршрутизировать магазинные задачи без догадок и без смешивания non-commerce core с shop-core;
- есть smoke-задачи для каталога, корзины, checkout, заказа, обмена с 1С, пагинации, lazy load и диагностики цен/остатков/SKU.
