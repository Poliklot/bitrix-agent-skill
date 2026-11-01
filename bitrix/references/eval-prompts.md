# Eval-набор бытовых Bitrix-запросов

Используй этот файл при доработке скилла и перед релизом бытового слоя. Цель — проверить, что агент выбирает Bitrix-native маршрут, не начинает с анти-паттерна и открывает правильные references.

## Как прогонять вручную

Для каждого prompt оцени ответ по 3 критериям:

1. **Route:** агент открыл/использовал правильный reference (`developer-primitives.md`, `first-answer-pitfalls.md`, `developer-cards.md` и доменный файл).
2. **No bad first step:** агент не начал с запрещённого анти-паттерна.
3. **Useful answer:** ответ коротко следует [answer-contracts.md](answer-contracts.md): даёт штатный механизм, где проверить в проекте, минимальный пример или grep из [core-grep-cookbook.md](core-grep-cookbook.md), и 1–3 side effects.

Оценка:

- `pass` — все 3 критерия выполнены.
- `warn` — ответ правильный, но слишком общий или не указал где проверить.
- `fail` — ответ начал с чистого PHP/SQL/правки ядра/глобального отключения кеша или придумал API.

Минимальный regression gate перед релизом: прогнать 15 любых prompt из разных доменов, `fail = 0`; полный pre-release checklist — в [release-gate.md](release-gate.md).

## Core prompts

| ID | Prompt | Expected references | Must say | Must not say first |
|---|---|---|---|---|
| B001 | Как в PHP поставить meta title в Битриксе? | `developer-primitives`, `first-answer-pitfalls`, `developer-cards`, `templates`, `seo-cache-access` | `ShowHead`/`ShowTitle`, `SetPageProperty('title')`, свойства страницы/SEO компонента, проверить `header.php` | “вставь `<meta name="title">` руками” |
| B002 | Где менять meta description для страницы? | `developer-primitives`, `developer-cards`, `templates`, `seo-cache-access` | свойства страницы/раздела, `SetPageProperty('description')`, SEO инфоблока/компонента | ручной meta в каждом файле |
| B003 | Как добавить canonical на детальной странице каталога? | `developer-primitives`, `developer-cards`, `shop-standard-components` если commerce подтверждён, `seo-cache-access` | `SetPageProperty('canonical')`, `SET_CANONICAL_URL`, проверить компонент и `component_epilog` | правка ядра catalog component |
| B004 | Как подключить CSS в шаблоне сайта? | `developer-primitives`, `first-answer-pitfalls`, `developer-cards`, `templates` | `Asset::addCss`, `template_styles.css`, `ShowHead` | echo `<link>` из компонента |
| B005 | Как подключить JS в компоненте? | `developer-primitives`, `developer-cards`, `templates`, `components` | `Asset::addJs` или `script.js` шаблона компонента, проверить `ShowBodyScripts` | inline script без причины |
| B006 | Как добавить OpenGraph meta? | `developer-primitives`, `developer-cards`, `seo-cache-access` | `AddHeadString`/`Asset::addString`, экранирование, `ShowHead` | ручной echo в середине body |
| B007 | Как сделать редактируемый текст в футере? | `developer-primitives`, `developer-cards`, `templates` | `IncludeFile`, include area, `SITE_DIR`, права | хардкод строки в шаблоне |
| B008 | Как вывести включаемую область? | `developer-primitives`, `developer-cards`, `templates` | `$APPLICATION->IncludeFile(...)`, MODE/html/text, права | создать свой mini-CMS |
| B009 | Как добавить хлебную крошку? | `developer-primitives`, `developer-cards`, `templates`, `components` | `AddChainItem`, `bitrix:breadcrumb`, параметры `ADD_*_CHAIN` | ручной HTML breadcrumbs |
| B010 | Почему хлебные крошки дублируются? | `developer-cards`, `components`, `shop-standard-components` if relevant | проверить `ADD_SECTIONS_CHAIN`, `ADD_ELEMENT_CHAIN`, `AddChainItem`, `component_epilog` | “очисти весь кеш” как первый ответ |
| B011 | Как получить текущего пользователя? | `developer-primitives`, `first-answer-pitfalls`, `developer-cards`, `users`, `access-rbac` | `global $USER`, `IsAuthorized`, `GetID`, права/группы | читать `$_SESSION` напрямую |
| B012 | Как показать блок только авторизованным? | `developer-cards`, `users`, `access-rbac`, `cache-infra` | `$USER->IsAuthorized()`, composite/personalized cache caveat | закешировать персональный HTML без frame |
| B013 | Как получить GET-параметр? | `developer-primitives`, `developer-cards`, `http`, `security` | `Context::getCurrent()->getRequest()`, фильтрация | сырой `$_REQUEST` без фильтрации |
| B014 | Как обработать POST-форму? | `developer-cards`, `security`, `webforms`, `http` | request, `check_bitrix_sessid`, validation, webform/project form layer | POST без CSRF |
| B015 | Как добавить параметр к текущему URL? | `developer-primitives`, `developer-cards`, `sef-urls`, `pagination` | `GetCurPageParam`, исключить старый параметр, SEF/canonical caveat | конкатенация `REQUEST_URI` |
| B016 | Как подключить модуль iblock? | `developer-primitives`, `developer-cards`, `modules-loader`, `iblocks` | `Loader::includeModule('iblock')`, обработать false, проверить module dir | сразу `CIBlockElement::GetList` без include |
| B017 | Как понять, установлен ли sale? | `developer-cards`, `core-audit-matrix`, `shop-task-matrix` | проверить `www/bitrix/modules/sale/install/version.php`, `Loader::includeModule('sale')` | обещать sale API без проверки |
| B018 | Как сделать 404 в компоненте? | `developer-cards`, `sef-urls`, `components`, `seo-cache-access` | `CHTTP::SetStatus`, `ERROR_404`, проектный `404.php`, strict checks | `echo '404'` |
| B019 | Страница не найдена, но отдаёт 200 — что делать? | `developer-cards`, `seo-cache-access`, `sef-urls`, `components` | проверить status, `ERROR_404`, component not found handling, routing | редирект на главную как универсальное решение |
| B020 | Как сделать редирект после отправки формы? | `developer-cards`, `http`, `security` | `LocalRedirect`, до вывода, validate URL, sessid | echo JS redirect первым вариантом |
| B021 | Как вывести картинку элемента инфоблока? | `developer-cards`, `iblocks`, `file-upload-modern` | `CFile::GetPath`/`ResizeImageGet`, `PREVIEW_PICTURE`/`DETAIL_PICTURE` | ручной `/upload/...` без проверки |
| B022 | Как сделать превью картинки? | `developer-cards`, `file-upload-modern`, `clouds` | `CFile::ResizeImageGet`, resize cache, dimensions | HTML width/height как resize |
| B023 | Как вывести свойство инфоблока в шаблоне? | `developer-cards`, `iblocks`, `components` | `PROPERTY_CODE`, `$arResult['PROPERTIES']`/`DISPLAY_PROPERTIES`, `result_modifier` | SQL в property table |
| B024 | Почему свойство инфоблока пустое в шаблоне? | `developer-cards`, `iblocks`, `component-dataflow-debugging` | проверить параметры компонента, код свойства, кеш, result_modifier | “свойства всегда есть в arResult” |
| B025 | Почему изменения в компоненте не видны? | `developer-cards`, `cache-infra`, `component-dataflow-debugging`, `composite-cache` | component cache, template cache, managed/tagged cache, composite static HTML, `X-Bitrix-Composite`, second request/cache pass | выключить весь кеш первым ответом |
| B026 | Как кешировать свой компонент? | `developer-cards`, `components`, `cache-infra`, `composite-cache` | `StartResultCache`, `AbortResultCache`, `setResultCacheKeys`, cache keys, отличие component cache от composite | кешировать USER_ID без caveat |
| B027 | Почему пользователь видит данные другого пользователя? | `developer-cards`, `cache-infra`, `security`, `composite-cache` | персонализация, `CACHE_GROUPS`, component cache key, `createFrame`/`FrameHelper`, `/bitrix/html_pages/`, очистка утечки | “очисти кеш” без root cause |
| B028 | Как отправить письмо? | `developer-cards`, `mail-notifications`, `webforms` | почтовое событие/шаблон, `CEvent::Send`/`Main\Mail\Event::send` | `mail()` как основной путь |
| B029 | Форма не отправляет письмо — где смотреть? | `developer-cards`, `webforms`, `mail-notifications`, `operations-runbook` | event name, template, SITE_ID, queue/agents, logs | “SMTP сломан” без проверки Bitrix events |
| B030 | Как сделать AJAX в компоненте? | `developer-cards`, `components`, `http`, `security` | project ajax pattern, sessid, JSON response, composite | endpoint без prolog/sessid |
| B031 | Как добавить обработчик события? | `developer-cards`, `events-routing`, `modules-loader` | `EventManager`, local module/php_interface, idempotent install | код в template.php |
| B032 | Где писать кастомный класс? | `production-best-practices`, `modules-loader`, `php-workflow` | `local/modules`/project namespace, composer if present, autoload | правка ядра/main classes |
| B033 | Как добавить агента? | `operations-runbook`, `update-stepper`, `modules-loader` | `CAgent`/project scheduler, idempotency, logging | cron без учёта Bitrix agents |
| B034 | Как очистить кеш после обновления инфоблока? | `cache-infra`, `iblocks`, `events-routing` | tagged cache/managed cache, precise invalidation | удалить весь `/bitrix/cache` первым вариантом |
| B035 | Как получить путь к ресурсу шаблона компонента? | `templates`, `components` | `$this->GetFolder()`, document root for server path | несуществующий `$this->GetTemplatePath()` без проверки |
| B036 | Как добавить кнопку в админке списка? | `admin-ui`, `grid-admin-modern` | modern grid/admin UI pattern, rights, modules | inline HTML hack без прав |
| B037 | Как сделать пагинацию списка? | `pagination`, `components`, `iblocks` | `PageNavigation` or `NavStart`, unique nav id, count/stable sort | ручной `LIMIT` без nav state |
| B038 | Почему вторая страница каталога пустая? | `pagination`, `shop-standard-components`, `component-dataflow-debugging` | filter/count/sort/cache/nav id, smart filter params | “увеличь page size” без диагностики |
| B039 | Как получить текущий сайт/SITE_ID? | `developer-primitives`, `modules-loader`, `templates` | `SITE_ID`, `SITE_DIR`, context/site caveat | hardcode `/` или домен |
| B040 | Как добавить lang-фразу? | `developer-cards`, `translate`, `modules-loader` | `Loc::getMessage`, lang files, `loadMessages` if needed | hardcoded Russian in reusable module |
| B041 | Как добавить пользовательское поле? | `custom-uf-types`, `iblock-hl-relations`, `entities-migrations` | UF API/migration, entity id, type, settings | вручную менять DB table |
| B042 | Как сделать HL-блок справочник? | `highloadblock`, `custom-uf-types`, `entities-migrations` | module check, HL API, migrations, rights | raw table without HL entity |
| B043 | Как обновить цену товара? | `shop-task-matrix`, `catalog`, `currency` after module check | catalog API, price type/currency, side effects | SQL в price tables |
| B044 | Как поменять статус заказа? | `sale`, `commerce-workflows` after module check | sale API/order save, events, payments/shipments side effects | SQL в order table |
| B045 | Как списать остаток? | `catalog`, `sale`, `commerce-workflows` after module check | catalog/store API, documents/reservation policy | прямой UPDATE количества |
| B046 | Как настроить обмен 1С? | `commerce-1c-integration`, `operations-runbook` after module check | checkauth/init/file/import flow, logs, XML_ID/CML2_LINK | “просто загрузи XML” |
| B047 | Почему товар из 1С есть в админке, но не на сайте? | `pitfalls-matrix`, `diagnostic-visibility`, `commerce-1c-integration`, `catalog` | active/date/site binding/section/price/stock/permissions/cache | “очисти кеш” only |
| B048 | Как добавить REST webhook? | `rest`, `http`, `security` | app/webhook scopes, auth, events, permissions | store token in public template |
| B049 | Как сделать robots noindex для страницы? | `seo-cache-access`, `developer-cards` | `SetPageProperty('robots','noindex, nofollow')`, `ShowHead`, page/component layer | hardcoded meta everywhere |
| B050 | Как проверить, можно ли идти в catalog/sale? | `core-audit-matrix`, `shop-task-matrix`, `shop-core-module-inventory` | inspect modules `catalog`, `sale`, `currency`, versions, components | assume shop because `catalog.*` template exists |
| B051 | Сделай аудит проекта и обнови BITRIX_PROJECT_CONTEXT.md | `behavior-routing`, `project-intake`, `core-grep-cookbook`, `BITRIX_PROJECT_CONTEXT.template` | запустить быстрый аудит из корня проекта, собрать public root/modules/templates/local/events/tooling, создать/обновить файл без secrets | начать с общих советов без чтения проекта |
| B052 | В проекте уже есть BITRIX_PROJECT_CONTEXT.md — что читать перед правкой? | `project-intake`, `answer-contracts`, `core-grep-cookbook` | сначала `AGENTS.md`, затем `BITRIX_PROJECT_CONTEXT.md`, потом перепроверить рискованные факты в текущем коде | верить снимку проекта вслепую |
| B053 | Можно ли считать магазинный маршрут runtime-проверенным? | `runtime-smoke-verification`, `shop-task-matrix`, `release-gate` | code-first ≠ runtime pass; нужны P1–P4 evidence и `validate_runtime_evidence.py` | сказать “да, покрыто справочником” |
| B054 | Запусти P1 smoke, но безопасного write sandbox нет | `runtime-smoke-verification`, `shop-task-matrix` | read-only можно, P1-05–P1-07 отметить `blocked`; не fake pass | запускать заказ/оплату на production |
| B055 | Нужно проверить CommerceML без production 1С | `runtime-smoke-verification`, `commerce-1c-integration` | использовать P2 fixtures/stub, запрет real credentials, blocked если нет sandbox endpoint | подключить реальную 1С |
| B056 | REST webhook есть, но scopes неизвестны | `runtime-smoke-verification`, `shop-integrations-webservice`, `rest` | P3 method discovery, missing-scope negative, masked tokens | сохранить токен в evidence |
| B057 | Evidence pack готов, как проверить перед релизом? | `release-gate`, `runtime-smoke-verification` | `python3 scripts/validate_runtime_evidence.py ... --package P1`, проверить summary/scenarios/secrets | принять папку без validation |
| B058 | Как правильно подготовить компонент к композитному кешу? | `components`, `templates`, `composite-cache` | `setFrameMode(true)` = голосование, персональные части через `createFrame`, dynamic areas не вкладывать, verification по headers | сказать что `setFrameMode(true)` делает компонент динамическим |
| B059 | Корзина/имя пользователя моргает или показывает чужие данные при композите | `developer-cards`, `security`, `composite-cache`, `cache-infra` | dynamic area с безопасной заглушкой, `CACHE_TYPE=N` для персонального блока, проверить guest/user A/user B, `X-Bitrix-Composite` | просто очистить весь кеш |
| B060 | Изучи Bitrix-проект и скажи, как его можно оптимизировать и какие оптимизации уже сломаны | `project-optimization-audit`, `core-grep-cookbook`, `perfmon`, `cache-infra`, `components` | audit-report: что уже оптимизировано, ошибки cache/composite/N+1/images/agents, safe wins, что требует runtime/perfmon evidence | сразу советовать Redis/CDN/очистку всего кеша без чтения проекта |
| B061 | В шаблоне каталога подозрение на N+1 — как проверить и исправить? | `project-optimization-audit`, `db-orm-performance`, `components`, `iblocks`, `perfmon` | static candidate через grep, perfmon SQL count/time, collect ids → preload/map, не утверждать без runtime evidence | сразу добавить индекс или переписать всё на raw SQL |
| B062 | Каталог и умный фильтр тормозят после импорта | `shop-performance`, `catalog`, `shop-standard-components`, `agents-imports-performance`, `perfmon` | module check `catalog/sale/currency`, facet/search index status, component params/cache, import invalidation, не делать full rebuild без окна | запустить полный rebuild/reindex на production первым шагом |
| B063 | Агенты/импорт грузят публичный сайт — что искать? | `agents-imports-performance`, `operations-runbook`, `update-stepper`, `cache-infra` | hit-mode vs cron, batch/checkpoint/idempotency/logs, targeted cache/index invalidation | лечить `set_time_limit(0)` или чистить весь кеш |
| B064 | Страница тяжёлая по картинкам и JS — какой Bitrix-native маршрут? | `frontend-assets-performance`, `templates`, `components`, `clouds`, `project-optimization-audit` | Asset layer, дубли CSS/JS, `ResizeImageGet`, width/height, lazy/srcset/webp, composite caveats, browser network/LCP | просто поставить CDN без проверки assets/cache key |
| B065 | Как безопасно кастомизировать админку Bitrix и не потерять изменения после обновления? | `admin-ui`, `grid-admin-modern`, `production-best-practices`, `events-routing`, `modules-loader` | core → docs/forums → core, `/local/modules`, tiny wrappers в `/bitrix/admin`, `CAdmin*`, `OnAdmin*`, стабильные `table_id`/`grid_id`, права и `sessid` | править `/bitrix/modules` или существующие `/bitrix/admin/*.php` |
| B066 | Как добавить свою вкладку в форму элемента/инфоблока в админке? | `admin-ui`, `events-routing`, `iblocks`, `production-best-practices` | сначала штатная настройка формы/инфоблока, затем `OnAdminTabControlBegin`, проверка страницы/`IBLOCK_ID`/`DIV`, сохранение отдельно, экранирование HTML | CSS в `admin_header.php` или копипаст всей core-формы первым шагом |
| B067 | Как добавить групповое действие или кнопку в список админки? | `admin-ui`, `grid-admin-modern`, `security`, `events-routing` | для своей страницы `AddGroupActionTable`/`AddAdminContextMenu`, для чужой `OnAdminListDisplay`/`OnAdminContextMenuShow`, action обрабатывать до вывода, `check_bitrix_sessid`, права | добавить ссылку без CSRF/прав или raw SQL update |
| B068 | Как добавить свой раздел в меню админки? | `admin-ui`, `modules-loader`, `access-rbac`, `production-best-practices` | `admin/menu.php` модуля или `OnBuildGlobalMenu`, `parent_menu`, `section`, `items_id`, `more_url`, проверка `GetGroupRight` | править `.left.menu.php` или hardcode в core меню |
| B069 | Где хранить свои admin-страницы модуля? | `admin-ui`, `modules-loader`, `php-workflow`, `production-best-practices` | логика в `local/modules/vendor.module/admin`, wrapper в `/bitrix/admin/vendor_*.php`, `InstallFiles`/`UnInstallFiles`, уникальные имена, prolog/epilog и права | класть бизнес-логику прямо в `/bitrix/admin` или менять core page |
| B070 | Куда положить общий блок сайта: в header, footer, include или компонент? | `project-layout-and-includes`, `project-intake`, `templates`, `components` | сначала public root/active template/project convention; owner/data shape определяют page/layout/include/component/service; проверить cache/edit/multisite | “всегда клади в `/include`” или rigid placement без чтения проекта |
| B071 | Как правильно использовать `.section.php` для названия и SEO раздела? | `project-layout-and-includes`, `templates`, `seo-cache-access`, `developer-primitives` | развести `$sSectionName`, `$arDirProperties`, `SetTitle`, `SetPageProperty`, component `SET_*`; проверить порядок/deferred/cache | считать `SetTitle` универсальным override всех свойств или вставить meta руками |
| B072 | Где хранить `IBLOCK_ID`: `.env`, `Option`, константа или lookup по коду? | `project-configuration`, `production-best-practices`, `entities-migrations`, `iblocks` | existing convention; numeric ID не secret; stable key + sufficient scope + migration/registry; validate ID и entity; explicit missing/duplicate | автоматически поставить Dotenv или lookup только по `CODE` |
| B073 | Можно ли сбрасывать кеш registry через `?clear_project_cache=Y`? | `project-configuration`, `security`, `cache-infra` | нет anonymous reset; protected admin action rights+sessid, CLI/deployment/migration или confirmed tagged contract; scope cache key | разрешить публичный query reset без прав |
| B074 | Нужно изменить выборку стандартного компонента — копировать `component.php`? | `project-layout-and-includes`, `components`, `component-dataflow-debugging`, `production-best-practices` | сначала params/stock contract; затем custom component/service; copied template только для view, source version/provenance | копировать ядровый `component.php` в template и править там |

## Expected answer skeletons

### Short “how to” answer

```text
В Битриксе это обычно делается через [штатный механизм], а не через [анти-паттерн].
Проверь: [paths/params/grep].
Минимальный пример:
[code]
Учти: [side effects].
```

### Debug answer

```text
Иди по цепочке: [source] → [component params] → [template/result_modifier] → [cache/index/rights].
Проверки:
[commands/paths]
Не начинай с [bad first step], пока не проверены [facts].
```

### Module-dependent answer

```text
Сначала подтвердить модуль в `www/bitrix/modules/<module>` и `Loader::includeModule(...)`.
Если модуль есть: [API route].
Если нет: [fallback/deferred].
```

## Диагностические границы

| ID | Prompt | Expected references | Must say | Must not say first |
|---|---|---|---|---|
| B075 | Preflight нашёл папку modules. Можно считать sandbox проверенным? | `release-gate` | Только static candidate; runtime и регистрация модулей не проверены | Все smoke пройдены |
| B076 | Прикрепи вывод сканера с URL webhook и исходным PHP | `release-gate` | Без исходных строк и приватных частей URL; проверить пути/hostname вручную | Публиковать raw payload |
| B077 | В summary pass, а в файле blocked — можно выпускать? | `release-gate` | Отклонить противоречие, сверить точную локальную ссылку и ID | Доверять только summary |
| B078 | Файл с логом слишком большой для проверки — пропустим? | `release-gate` | Отказ автоматического gate, подготовить обезличенный текст и отдельную проверку оригинала | Проверка секретов пройдена |
| B079 | Повтори генерацию поверх заполненных доказательств | `release-gate` | Без force отказ без перезаписи; force только осознанно, static report сохраняется | Молча перезаписать pack |
| B080 | Как посчитать элементы, не загружая список? | `iblocks` / `content-data` | Передать [] третьим аргументом CIBlockElement::GetList, читать скаляр; сохранить фильтр списка и проверить 0/несколько элементов. | Вызвать Fetch на COUNT или принять обычную выборку за число. |
| B081 | Дочерняя запись вернула ошибку Result, но родитель сохранился — почему? | `orm` / `php-architecture` | Неуспешный Result не бросает исключение сам; проверить дочерний результат и откатить собственную транзакцию до commit, обработать Throwable. | Коммитить потому, что исключения не было. |
| B082 | Можно отправить webhook из OnAfterAdd внутри транзакции? | `orm` / `php-architecture` | Не считать событие commit: отложить внешний эффект до успешного завершения операции либо использовать согласованный transactional outbox. | OnAfterAdd гарантирует сохранность после любого rollback. |
| B083 | Почему ORM LIMIT 20 возвращает меньше 20 карточек? | `orm` / `php-architecture` | JOIN размножает строки до LIMIT; отделить страницу уникальных ID от загрузки отношений, проверить полный набор значений и стабильный порядок. | Добавить DISTINCT ко всему select или увеличить LIMIT наугад. |
| B084 | После перехода на ORM посетителям видны черновики: что проверить? | `iblocks` / `content-data` | Сопоставить со stock public selection, проверить getPublicElementsOrmFilter и отдельно права, активность, даты, сайт и кеш. | Считать ACTIVE=Y полной моделью публикации и доступа. |
| B085 | Как обновить одно свойство и очистить TAGS, не потеряв остальные? | `iblocks` / `content-data` | Использовать SetPropertyValuesEx с нужными ключами, TAGS=false; после записи перечитать значения, не проверять isSuccess у null. | Передать неполный набор в SetPropertyValues без PROPERTY_CODE. |
| B086 | Как удалить два фото и добавить одно в множественное свойство? | `iblocks` / `content-data` | Прочитать связи, проверить принадлежность элементу, сформировать один пакет удаления/добавления и перечитать новые value IDs. | Два последовательных удаления по старым value IDs или прямой CFile::Delete. |
| B087 | Обработчик OnAfterIBlockElementUpdate не видит запись через Ex — почему? | `iblocks` / `content-data` | Трассировать отдельные property events; выбрать нужную фазу, scope и защиту повторного вызова, не подменять before событие post-save. | Добавить второй Update ради запуска обработчика. |
| B088 | Вариант имеет разные ID на dev/prod: как перенести значение? | `iblocks` / `content-data` | Разрешить XML_ID внутри конкретного свойства, проверить одну точную запись и сохранить её локальный ID; проверить повтор миграции. | Копировать dev ID или искать первый вариант по подписи. |
| B089 | Можно добавить свойство VERSION=2 через PropertyTable::add? | `iblocks` / `content-data` | Выбрать CIBlockProperty API, согласовать миграцию схемы/значений и проверить чтение новым процессом; ORM метаданных оставить для чтения. | Прямой INSERT метаданных и ручное создание одной колонки. |
| B090 | Можно поменять количество в оформленном заказе и вызвать basket->save? | `sale` / `commerce-shop` | Нет: загрузить заказ, изменить его корзину и согласованные зависимые сущности, проверить Result и сохранить Order. | Сохранить только basket заказа или обновить b_sale_basket. |
| B091 | В CLI подставить userId в loadItemsForFUser — правильно? | `sale` / `commerce-shop` | Нет: отдельно разрешить FUSER целевого пользователя и site, обработать отсутствие; web-клиент не выбирает чужого владельца. | Считать USER_ID и FUSER_ID взаимозаменяемыми. |
| B092 | У одного товара две строки с разной гравировкой: как изменить одну? | `sale` / `commerce-shop` | Выбрать конкретную строку в авторизованной корзине, сохранить её свойства; не искать по одному PRODUCT_ID. | Обновить все строки товара или привести basket code к числу. |
| B093 | Почему в заказе есть системная отгрузка и можно ли её удалить? | `sale` / `commerce-shop` | Это часть модели распределения: не удалять; работать с обычными Shipment и сверять quantities с корзиной. | Удалить системную отгрузку или отметить её как доставленную. |
| B094 | Пришло подтверждение одной из двух оплат — отметить весь заказ? | `sale` / `commerce-shop` | Подтвердить только найденный Payment после проверки callback и повтора; сохранить Order, не трогать вторую оплату и отгрузки. | foreach всех оплат setPaid(Y), затем DEDUCTED всем отгрузкам. |
| B095 | После купона сумма заказа изменилась, а Payment остался прежним — что делать? | `sale` / `commerce-shop` | Проверить final calculation и Result, согласовать неоплаченную часть с итогом; paid сумму не переписывать, затем save/reload. | Считать doFinalAction сохранением или менять уже подтверждённую оплату. |
| B096 | В одном CLI-процессе создаются заказы разных покупателей: что с купонами? | `sale` / `commerce-shop` | Изолировать контекст manager по заказу/владельцу и режиму, проверить переинициализацию и применение; не наследовать предыдущий coupon state. | Один глобальный MODE_CLIENT на весь пакет покупателей. |
| B097 | Доставка существует по ID, но почему её нельзя принять из POST? | `sale` / `commerce-shop` | Проверить ограничения для текущей заполненной отгрузки и клиентский режим, затем расчёт; ID из запроса не доказательство доступности. | Считать getById успешной проверкой или принять цену доставки из браузера. |
| B098 | Поставить CUSTOM_PRICE=Y, чтобы цена перестала меняться? | `sale` / `commerce-shop` | Только для согласованной ручной котировки; иначе разобраться с provider. Проверить скидки, налоги, валюту, refresh и серверный источник суммы. | Копировать PRICE и CUSTOM_PRICE из POST или отключать provider ради симптома. |
| B099 | В OnSaleOrderSaved меняю поле и вызываю save: почему цикл? | `sale` / `commerce-shop` | Изменение перенести в подходящую before-фазу, реакцию ограничить IS_NEW/VALUES; внешние повторы дедуплицировать устойчивым ключом. | Добавить безусловный save в Saved или считать IS_NEW защитой от любого повтора. |
| B100 | В batch третья команда упала: первые две отменились? | `rest` / `integrations-rest` | Нет: разобрать результаты по ключам, учитывать halt; сохранить успешные операции и определить безопасный повтор остальных. | Считать HTTP 200 полным успехом или halt=1 транзакционным откатом |
| B101 | В списке нет total: как дочитать все страницы? | `rest` / `integrations-rest` | Следовать next → start, разбирать форму result конкретного метода и не менять сортировку/фильтр. | Остановиться после первой страницы или считать count(result) количеством записей |
| B102 | Можно весь старый REST-клиент перевести добавлением /api/ в URL? | `rest` / `integrations-rest` | Нет: проверить доступность и схему каждого метода новой версии, затем адаптировать клиент. | Объявить все классические методы доступными в REST 3.0 |
| B103 | Выбран scope crm, но вебхук не читает чужую сделку — отключить проверку? | `rest` / `integrations-rest` | Нет: проверить права владельца на сделку и scope отдельно, использовать разрешённую учётную запись. | Считать scope автоматическим правом на все объекты или опубликовать URL в браузере |
| B104 | Два воркера одновременно получили expired_token: что делать? | `rest` / `integrations-rest` | Сериализовать refresh по записи авторизации, сохранить пару атомарно, ожидающему перечитать и повторить с новым access_token. | Независимо обновлять токены в каждом воркере без ограничения повторов |
| B105 | Портал сменил домен: создавать новую запись клиента? | `rest` / `integrations-rest` | Найти установку по member_id и приложению, проверить авторизационные данные и обновить client_endpoint. | Хранить tenant только по domain или отправить секрет на URL из неподтверждённого события |
| B106 | Пришёл ONAPPUNINSTALL без access_token: удалять данные клиента? | `rest` / `integrations-rest` | Только после сверки application_token с сохранённым секретом нужной установки; неизвестное событие отклонить. | Доверять одному имени события, member_id или домену в POST |
| B107 | Три обновления сделки дали одну offline-запись — события потерялись? | `rest` / `integrations-rest` | Одинаковые ключи объединяются; использовать очередь для синхронизации актуального состояния, не как полный аудит. | Считать каждую запись ровно одной бизнес-операцией и восстанавливать всю историю по очереди |
| B108 | Воркер упал сразу после event.offline.get: очередь сохранит события? | `rest` / `integrations-rest` | При default clear=1 — нет; использовать разрешённое резервирование clear=0 и отдельное подтверждение. | Считать get чистым чтением или повторять пакет с clear=1 и маленьким limit |
| B109 | Все записи пакета упали: отправить clear с message_id=[]? | `rest` / `integrations-rest` | Нет: пустой список удалит пакет. Не подтверждать ошибки; проверить process_id и фиксировать только успешные записи. | Использовать пустые параметры как безопасный no-op |
| B110 | event.offline.error вернул true, но ошибка не появилась — почему? | `rest` / `integrations-rest` | Проверить MESSAGE_ID, принадлежность process_id и непустой список; читать ошибочную ветку error=1. | Передать ID сделки вместо MESSAGE_ID или чужой process_id и довериться true |
| B111 | После operating_reset_at метод всё ещё заблокирован: менять токен? | `rest` / `integrations-rest` | Нет: часть временного окна могла остаться; снизить нагрузку и проверить operating, не обходить блокировку токенами. | Ускорить параллельные повторы или объявить единый лимит для любого Битрикс24 |
| B112 | Можно передать FILE_ID из disk.file.get в любое файловое поле? | `rest` / `integrations-rest` | Нет: выяснить нужный тип идентификатора и формат поля, выполнить загрузку/прикрепление по контракту метода. | Подменять Disk ID значением FILE_ID или Base64 локальным путём |
| B113 | DOM загрузился, но BX24.isAdmin() false у администратора — что проверить? | `rest` / `integrations-rest` | Подключение BX24.js, запуск во фрейме приложения и выполнение после BX24.init. | Считать DOMContentLoaded готовностью авторизации или зашить admin-токен в HTML |
| B114 | event.bind успешен, но новое приложение не получает события — где причина? | `rest` / `integrations-rest` | Проверить завершение установки и INSTALLED; не путать мастер установки с первым запуском пользователя. | Безусловно завершать проваленный мастер или ждать JS finish в REST-only обработчике |
| B115 | В options пришёл ID сделки: можно сразу читать её своим admin-токеном? | `rest` / `integrations-rest` | Нет: проверить конкретный placement, тип/ID и права текущего пользователя на backend. | Считать клиентский options доказательством доступа или ожидать callback от placement.info |
| B116 | Сервер сохранил user.option.set, но второй сотрудник не видит настройку — почему? | `rest` / `integrations-rest` | Настройка принадлежит пользователю токена; выбрать персональный либо общий app.option слой осознанно. | Ожидать глобальное действие user.option.set или удаление ключа пустой строкой |
| B117 | feature.get для придуманного CODE вернул Y: функция точно существует? | `rest` / `integrations-rest` | Нет: метод не проверяет существование кода. Использовать опубликованные CODE и проверять сам метод. | Привести N к true или объявить поддержку по Y неизвестного кода |
| B118 | HttpClient получил timeout после создания заказа во внешней системе: повторить POST? | `http` / `php-architecture` | Не вслепую: операция могла выполниться; сверить внешний ключ/результат или безопасную идемпотентность. | Считать любой timeout гарантией, что сервер не получил запрос |
| B119 | Два воркера одновременно создали объект с одним Idempotency-Key — дубль невозможен? | `rest` / `integrations-rest` | Возможен: заголовок не является конкурентным lock. Сериализовать и учитывать версию REST, тело и срок хранения. | Обещать exactly-once навсегда или использовать заголовок как защиту классического REST |
| B120 | Почему второй запрос компонента выводит HTML дважды? | `components` / `components-admin-ui` | Проверить шаблон вне StartResultCache: на hit HTML уже выведен. Разделить HTML и data-only режимы. | Безусловно исполнять шаблон после выдачи HTML-кеша |
| B121 | Убрал CURRENT_USER из cache keys: имя теперь безопасно в общем HTML? | `components` / `components-admin-ui` | Нет: HTML уже содержит имя; изменить границу/ключ кеша, не только состав arResult. | Считать cache keys механизмом очистки персонального HTML |
| B122 | Где ставить заголовок из результата, чтобы он работал при тёплом кеше? | `templates` / `components-admin-ui` | В component_epilog, предварительно сохранив нужные значения; не в result_modifier или недоказанном component_prolog. | Обещать автоматический вызов component_prolog с готовым arResult |
| B123 | Правлю local/components/.../templates, но сайт показывает старый вид: почему? | `templates` / `components-admin-ui` | Проверить переопределение в активном site-template и шаблоне комплексного родителя, затем кеш. | Утверждать, что любой local/components template всегда приоритетнее site-template |
| B124 | У компонента один arParams, но разные региональные цены: почему смешались? | `components` / `components-admin-ui` | Добавить нормализованный регион/контекст доступа в additionalCacheID и проверять права до кеша. | Читать контекст только внутри miss и считать CACHE_GROUPS автоматической защитой |
| B125 | ID подписан компонентом: можно пропустить проверку прав в AJAX? | `components` / `components-admin-ui` | Нет: проверить актуального пользователя и объект; подпись защищает целостность параметров, не полномочия. | Поместить секрет в подпись или доверять всему data рядом с ней |
| B126 | Вызвал vendor:widget через runAction: почему action не найден? | `components` / `components-admin-ui` | Разделить модульный и компонентный диспетчер, выбрать mode по месту реализации действия. | Подменить компонентный маршрут модульным либо обращаться напрямую к файлу ajax.php |
| B127 | Авторизованный пользователь передал чужой userId/id: допустимо? | `events-routing` / `php-architecture` | Нет без отдельного разрешения; ограничить запись/чтение серверным правилом и тем же правилом count. | Доверять userId клиента или возвращать глобальный total приватного списка |
| B128 | getList не проходит HttpMethod, хотя имя верное — причина? | `events-routing` / `php-architecture` | Сверить default POST клиента с GET фильтром; явно указать GET и обработать reject. | Убрать серверный фильтр ради несовпадения клиента или бесконечно повторять мутацию |
| B129 | У limit тип int — значит -1 и миллион уже безопасны? | `events-routing` / `php-architecture` | Нет: проверить бизнес-диапазон и остановить запрос при нарушении, типизацию не считать валидацией. | Передать любой integer в limit/offset без ограничений |
| B130 | Будет ли iblock_id_el_17 сам сброшен после Update? | `cache-infra` / `search-seo-ops` | Без подтверждённого invalidator нет; выбрать штатный тег инфоблока или реализовать парный проектный сброс. | Считать любое похожее имя встроенным тегом |
| B131 | Почему Option::get без siteId вернул значение текущего сайта? | `modules-loader` / `php-architecture` | Не считать пропуск аргумента глобальным чтением; задать сайт либо пустую общую область явно. | Убирать четвёртый аргумент ради гарантированно общего значения |
| B132 | Как не перезаписать сохранённый ноль при установке default? | `modules-loader` / `php-architecture` | Получить реальное значение и сравнить с null строго; get с fallback не доказывает наличие записи. | Если empty(Option::get(...)), записать default |
| B133 | Письмо поставилось в очередь, но ORDER_ID пуст — что проверить первым? | `mail-notifications` / `content-modules` | Ключ C_FIELDS в D7 и соответствие макросу шаблона; успешная очередь не подтверждает содержимое. | Передавать FIELDS по аналогии с другим API |
| B134 | Можно ли без изменений передать массив lid из CEvent в Event::send? | `mail-notifications` / `content-modules` | Нет по документированному контракту: D7 LID — строка с ID через запятую. | Считать массив сайтов одинаковым аргументом обоих API |
| B135 | Почему callback OnBeforeEventSend с массивами не совместим с регистрацией? | `mail-notifications` / `content-modules` | Согласовать legacy-сигнатуру и addEventHandlerCompatible; не заменять callback объектом Event вслепую. | Оставить объектный режим для ссылочных массивов |
| B136 | Нужно не создавать событие определённого типа — какой hook? | `mail-notifications` / `content-modules` | OnBeforeEventAdd, ограниченный типом события; проверить отсутствие новой записи и сохранение прочих типов. | Использовать OnBeforeEventSend как запрет записи b_event |
| B137 | Почему с MESSAGE_ID письмо пришло не на выбранном языке? | `mail-notifications` / `content-modules` | Языковой фильтр не выполняется при явном ID; проверить язык выбранного шаблона и mapping окружения. | Считать languageId гарантией языка при любом MESSAGE_ID |
| B138 | Защитит duplicate=N от двух одинаковых CEvent::Send? | `mail-notifications` / `content-modules` | Нет: это копия на адрес из настроек, два вызова могут создать два события. | Использовать duplicate как ключ дедупликации |
| B139 | Почему при отправке сохранённого файла по пути появилась ещё одна копия? | `mail-notifications` / `content-modules` | Путь сохраняется повторно; использовать разрешённый ID CFile и согласовать срок жизни с очередью. | Передавать GetPath как локальный путь или сразу удалять файл асинхронного письма |
| B140 | Можно ли разрешить загрузку по type=image/jpeg из запроса? | `import-export` / `content-data` | Нет: это поле клиента; проверить содержимое на сервере и политику расширений/размеров. | Считать MIME браузера доказательством JPEG |
| B141 | CheckFile вернул строку: можно сохранять? | `import-export` / `content-data` | Нет: остановить сохранение; пустой результат допускает следующий этап проверки. | Трактовать непустой текст CheckFile как успешную проверку |
| B142 | Почему после ResizeImageGet отсутствует width? | `import-export` / `content-data` | Проверить bInitSizes=true и успешность вызова; не подменять размеры файла рамкой. | Читать width/height без bInitSizes или растягивать до рамки |
| B143 | Появится ли запись b_file после обычного copy в upload? | `import-export` / `content-data` | Нет по контракту SaveFile; для регистрации нужен соответствующий API. | Считать размещение в upload автоматической регистрацией |
| B144 | Можно ли передать любой путь из формы в MakeFileArray? | `import-export` / `content-data` | Нет: определить разрешённый тип источника и корень; сайт-relative путь явно преобразовать. | Полагаться на автоматическое добавление DOCUMENT_ROOT или разрешать любой URL/путь |
| B145 | Как прикрепить новое изображение при Add элемента? | `import-export` / `content-data` | Передать проверенный файловый массив; дать API элемента сохранить файл, проверить ID/LAST_ERROR. | Предварительно SaveFile и передать его ID как новый DETAIL_PICTURE |
| B146 | Безопасно ли слить POST с файловым массивом, включая old_file/del? | `import-export` / `content-data` | Нет: служебные ключи задаёт сервер после проверки владельца и намерения удаления. | Доверять old_file из POST или передавать del=N как ложь |
| B147 | Маленький по байтам файл имеет огромные dimensions — достаточно CheckFile? | `import-export` / `content-data` | Нет: ограничить геометрию CheckImageFile и ресурсы обработки до ресайза. | Считать лимит байтов ограничением числа пикселей |
| B148 | Можно ли после IsAuthorized пометить все fileId как свои? | `file-upload-modern` / `components-admin-ui` | Нет: подтвердить каждый файл и операции по серверному объекту-владельцу; не выдумывать разрешающую модель. | Безусловный markAsOwn и canRemove=true |
| B149 | Почему название A & B выгрузилось как A &amp; B? | `import-export` / `content-data` | GetNext преобразовал HTML; выбрать Fetch и сериализовать исходное значение. | Использовать GetNext как универсальный raw fetch |
| B150 | Почему new DateTime с Y-m-d строкой работает на одном сайте и падает на другом? | `http` / `php-architecture` | Не задан format, используется culture; указать Y-m-d H:i:s либо нужный контракт строки. | Полагаться на автоматическое распознавание ISO конструктором |
| B151 | Вернёт ли format серверное время после setTimeZone(UTC)? | `http` / `php-architecture` | Нет, он форматирует в установленной зоне объекта; для серверной зоны установить её явно. | Считать format или disableUserTime принудительной серверной зоной |
| B152 | Почему после расчёта deadline изменился createdAt? | `http` / `php-architecture` | Обе переменные ссылались на один DateTime; клонировать перед add. | Присвоить объект второй переменной и считать его immutable |
| B153 | Как выбрать все записи пользовательского дня на переходе DST? | `http` / `php-architecture` | Построить календарные границы в нужной зоне, привести к storage-контракту, использовать >= и <. | Прибавить 86400 или сравнивать локализованные строки |
| B154 | Можно ли одинаково импортировать UTC через createFromUserTime в web и cron? | `http` / `php-architecture` | Нет: контексты различаются; использовать явный машинный контракт времени. | Повторно применять пользовательский сдвиг к UTC |
| B155 | Можно ли удалить связь с ключом LEFT_ID+RIGHT_ID по одному LEFT_ID? | `orm` / `php-architecture` | Нет: нужен полный primary либо отдельный явно ограниченный сценарий удаления набора. | Передать один scalar или неполный ключ |
| B156 | getTitle вернул null после select ID — надо очистить TITLE в БД? | `orm` / `php-architecture` | Нет: сначала загрузить TITLE; null неполной проекции не доказывает значение в БД. | Сохранить null из незагруженного getter обратно |
| B157 | Защитит ли %s выражение, в которое уже вставлен текст пользователя? | `orm` / `php-architecture` | Нет: отказаться от конкатенации; значения передать фильтром, поля выбрать по allowlist. | Считать ExpressionField универсальным prepared statement |
| B158 | Почему подчёркивание в коде сопоставилось с другим символом? | `orm` / `php-architecture` | Это wildcard LIKE; определить буквальный или шаблонный поиск и явно задать его. | Считать underscore буквальным символом или гарантировать prefix без маски |
| B159 | Почему JOIN-запрос снова обращается к БД при заданном ttl? | `orm` / `php-architecture` | Проверить cache_joins и настройки кеширования; включать лишь с корректной инвалидизацией зависимостей. | Считать ttl достаточным для любого JOIN и любого способа записи |
| B160 | Администратор добавляет клиента в группу: откуда брать существующий набор? | `users` / `users-security` | Из записи клиента по целевому userId, не из USER оператора; проверить право назначения. | Копировать группы администратора клиенту |
| B161 | Как добавить постоянную группу, не сделать временную бессрочной? | `users` / `users-security` | Считать полный GetUserGroupList и сохранить интервалы при записи структурированного groups. | Свести все членства к одним ID |
| B162 | Группу удалили, но открытая сессия ещё видит доступ — почему? | `users` / `users-security` | Запись членства не равна обновлению активной сессии; проверить механизм отзыва и повторную авторизацию. | Обещать немедленный отзыв во всех сессиях по SetUserGroup |
| B163 | Достаточно ли ThrowException внутри void-обработчика до Add? | `users` / `users-security` | Нет: документированный отказ — сообщение и return false; сигнатура должна разрешать этот результат. | Оставить void и считать ThrowException остановкой исполнения PHP |
| B164 | Можно ли отправлять welcome при каждом OnAfterUserAdd? | `users` / `users-security` | Нет: проверить успешный результат и положительный ID; ошибка попытки тоже достигает after hook. | Считать сам вызов after гарантией создания |
| B165 | Чем создавать пользователей импортом, не меняя сессию администратора? | `users` / `users-security` | CUser::Add; Register относится к публичному потоку с дополнительными эффектами. | Подменить Add методом Register в административном импорте |
| B166 | Можно ли взять первый UserTable::getRow по email и связать заказ/аккаунт? | `users` / `users-security` | Не без проверки уникальности кандидата и политики идентификации; email не универсальный ключ. | Молча выбрать первого пользователя с общим email |
| B167 | Как исправить ошибку передачи первого аргумента CUser::GetList по ссылке? | `users` / `users-security` | Объявить by/order отдельно и передать переменные; не выражения присваивания. | Передать строковый литерал или assignment expression в ссылочный аргумент |
| B168 | Поиск LOGIN=ivan вернул ivan_petrov — ошибка ядра? | `users` / `users-security` | Нет: LOGIN — подстрока; для точного поиска LOGIN_EQUAL или GetByLogin. | Выбирать первую строку подстрочного поиска как точную учётку |
| B169 | Получен OK от SendPassword — пароль уже сменён? | `users` / `users-security` | Нет: создан запрос с контрольной строкой; отдельно выполняется подтверждённая смена. | Обещать новый пароль или считать login+email независимой проверкой личности |
| B170 | После часа простоя десятиминутный агент внезапно повторяется — почему? | `cache-infra` / `search-seo-ops` | Проверить IS_PERIOD=Y и догоняющие интервалы; выбрать N для пересчёта только текущего состояния. | Назначать Y всем задачам ради точности времени |
| B171 | Почему письмо агента уходит с языком/сайтом случайного хита? | `cache-infra` / `search-seo-ops` | Фоновому заданию нужен явный сайт и язык; USER/SITE_ID не считать гарантированными. | Авторизовать клиента внутри агента ради контекста |
| B172 | Как передать текст клиента агенту без включения текста в eval? | `cache-infra` / `search-seo-ops` | Сохранить данные в серверном задании и передать фиксированному методу проверенный ID. | Конкатенировать PHP-вызов из POST с именем метода и аргументами |
| B173 | Как отложить первый запуск агента, не перепутав аргументы дат? | `cache-infra` / `search-seo-ops` | Задать next_exec в требуемом языковом формате; datecheck имеет другой смысл. | Использовать datecheck как единственный контракт времени первого исполнения |
| B174 | Почему helper не нашёл перевод компонента после loadMessages(__FILE__)? | `modules-loader` / `php-architecture` | Проверить, чей путь передан: lazy loading привязано к исходному файлу регистрации. | Считать getMessage поиском рядом с местом каждого вызова |
| B175 | Можно ли в каждом файле объявлять собственный MESS[TITLE]? | `modules-loader` / `php-architecture` | Нет гарантированной изоляции; использовать уникальные префиксные коды. | Полагаться на приватность lang-файла для общего ключа |
| B176 | Безопасно ли echo Loc::getMessage с именем из формы? | `modules-loader` / `php-architecture` | Подстановка не sanitizer; экранировать результат для конкретного контекста вывода. | Считать переведённую строку автоматически HTML-безопасной |
| B177 | Как получить английский текст без выдуманного getMessageByLang? | `modules-loader` / `php-architecture` | Загрузить нужный файл и вызвать getMessage(code, replacements, en). | Вызывать getMessageByLang как гарантированный публичный метод |
| B178 | Почему версия модуля пустая после include стандартного version.php? | `modules-loader` / `php-architecture` | Читать arModuleVersion, а не version; проверить оба обязательных значения. | Считать имя локальной переменной произвольным при штатном формате |
| B179 | Можно ли проверять includeSharewareModule только на truthy? | `modules-loader` / `php-architecture` | Нет: разобрать константы установленного, demo, истёкшего и отсутствующего состояния. | Считать любое ненулевое состояние успешной загрузкой |

| B180 | Почему UF_COLOR раздела не выбирается? | `iblocks` / `content-data` | Задать IBLOCK_ID в фильтре и UF_COLOR в select. | Искать его как PROPERTY_COLOR элемента |

| B181 | Почему счётчик раздела больше списка товаров? | `iblocks` / `content-data` | Согласовать вложенность, активность и даты; не ждать SECTION_CNT. | Считать bIncCnt числом только активных прямых элементов |

| B182 | Почему экспорт с пятым аргументом [] теряет разделы? | `iblocks` / `content-data` | Это лимит десяти; использовать осознанную полную или постраничную выборку. | Считать [] синонимом отсутствия лимита |

| B183 | Как проверить дерево, доступное гостю, из админской сессии? | `iblocks` / `content-data` | PERMISSIONS_BY=0 при включённой проверке прав. | CHECK_PERMISSIONS=N как режим гостя |

| B184 | Почему ребёнок в меню оказывается раньше родителя? | `iblocks` / `content-data` | Проверить порядок дерева: LEFT_MARGIN ASC, не общий SORT. | Восстанавливать иерархию только по отсортированному SORT |

| B185 | Можно ли вызвать Fetch на GetNavChain(..., true)? | `iblocks` / `content-data` | Нет, это массив; сохранить проверку IBLOCK_ID и не ждать UF. | Передавать ноль вместо области и считать результат авторизацией |

| B186 | Можно ли ускорить перенос раздела, записав LEFT_MARGIN напрямую? | `iblocks` / `content-data` | Нет; Update родителя с пересчётом и проверкой результата. | Писать границы SQL или bResort=false без восстановления дерева |

| B187 | Безопасно ли удалить раздел, ожидая только отвязки товаров? | `iblocks` / `content-data` | Нет; сначала оценить каскад и сохранить нужные связи/данные. | Обещать, что все элементы останутся без изменений |

| B188 | Как добавить второй раздел, не потеряв первый и основной? | `iblocks` / `content-data` | Прочитать текущие связи, сформировать полный набор и вызвать Update с основным разделом. | SetElementSection([$newId]) как безусловное добавление |

| B189 | Почему чтение разделов вернуло раздел из свойства RELATED_SECTION? | `iblocks` / `content-data` | По умолчанию включены связи свойств; для принадлежности нужен true. | Записать все найденные разделы обратно как принадлежность |
