# Core Routing
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `core-audit-matrix.md`

# Core Audit Matrix без магазина — справочник

> Reference для Bitrix-скилла. Загружай, когда нужно понять, что реально установлено в текущем core, какие домены активны, какие условны, и куда вести задачу без `catalog`/`sale`.
>
> Матрица основана на текущем checkout `www/bitrix` и должна обновляться после установки новых модулей.

## Содержание
- Быстрые проверки
- Активные модули текущего core
- Условные и отложенные домены
- Ловушки текущего core
- Покрытие reference-файлами
- Как обновлять матрицу

## Быстрые проверки

```bash
find www/bitrix/modules -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | sort

find www/bitrix/modules -maxdepth 3 -path '*/install/version.php' -print | sort

find www/bitrix/modules -path '*/install/components/bitrix/*/.parameters.php' -print \
  | sed 's#.*/install/components/bitrix/##; s#/.parameters.php##' \
  | sort
```

Для `main` не требуй `www/bitrix/modules/main/install/version.php`: в текущем core у него есть `classes/general/version.php`, а не обычный `install/version.php`.

## Активные модули текущего core

| Модуль | Статус | Основной reference | Что проверять первым |
|---|---|---|---|
| `main` | active | `modules-loader.md`, `orm.md`, `session-auth.md`, `database-layer.md`, `access-rbac.md` | `lib/`, `classes/general`, компоненты `main.*`, user/session/cache/ORM |
| `iblock` | active | `iblocks.md`, `iblock-hl-relations.md`, `entities-migrations.md` | `install/components/bitrix`, properties, sections, UF, legacy + D7 |
| `highloadblock` | active | `highloadblock.md` | dynamic ORM, rights, UI selector, relation to iblock directory |
| `form` | active | `webforms.md`, `standard-components-noncommerce.md` | form/result/status/validators/handlers/CRM link, stock templates |
| `blog` | active | `blog-socialnet.md`, `standard-components-noncommerce.md` | `CBlog*` write path, D7 read-only tables, templates, search reindex |
| `forum` | active | `forum.md`, `standard-components-noncommerce.md` | `CForum*`, forum components, permissions, topic/message flow |
| `vote` | active | `vote.md`, `standard-components-noncommerce.md` | `CVote*`, channels/questions/answers, `voting.*` components |
| `subscribe` | active | `subscribe.md`, `mail-notifications.md` | rubrics, subscriptions, postings, templates |
| `search` | active | `search.md`, `index-cache-diagnostics.md` | `CSearch`, title search, `BeforeIndex`, URL generation, rights |
| `seo` | active | `seo-cache-access.md`, `index-cache-diagnostics.md` | sitemap, robots/noindex, canonical, OpenGraph, SEO admin tools |
| `landing` | active | `landing.md`, `standard-components-noncommerce.md` | Site/Landing/Block/Hook/Rights, mutator mode, templates |
| `bitrix.sitecorporate` | active | `sitecorporate.md`, `standard-components-noncommerce.md` | wizard shell, `corp_furniture`, public skeleton, stock `furniture.*` |
| `fileman` | active | `fileman.md`, `templates.md` | editor, address/map/video fields, visual assets |
| `location` | active | `location.md`, `fileman.md` | address/location services, formats, widgets |
| `messageservice` | active | `messageservice.md`, `mail-notifications.md` | SMS providers, limits, callbacks, REST |
| `socialservices` | active | `socialservices.md`, `users.md` | OAuth providers, user links, auth flow |
| `rest` | active | `rest.md`, `events-routing.md` | REST methods/events/webhooks/OAuth |
| `security` | active | `security.md`, `diagnostic-visibility.md` | WAF, OTP/MFA, redirect/IP rules, scanner/checker |
| `perfmon` | active | `perfmon.md`, `operations-runbook.md` | SQL/hit/cache diagnostics, schema/index insights |
| `clouds` | active | `clouds.md`, `file-upload-modern.md` | external storage, `HANDLER_ID`, resize/src/MakeFileArray |
| `bitrixcloud` | active | `bitrixcloud.md`, `operations-runbook.md` | backup policy, monitoring, mobile inspector |
| `mobileapp` | active | `mobileapp.md`, `standard-components-noncommerce.md` | admin mobile, JN/native components, push settings |
| `b24connector` | active | `b24connector.md` | remote portal binding, buttons, openline info, site restrictions |
| `translate` | active | `translate.md` | lang files, phrase index, CSV import/export, UI |
| `photogallery` | active | `photogallery.md`, `blog-socialnet.md`, `forum.md` | gallery root section, albums, upload, comments |
| `ui` | active | `grid-admin-modern.md`, `file-upload-modern.md` | grid/filter/uploader/entity selector |

## Условные и отложенные домены

| Домен | Почему отложен | Что делать в ответе |
|---|---|---|
| `catalog` module | модуля `www/bitrix/modules/catalog` нет | не вести задачу в торговый каталог; если вопрос про `catalog.*` component, проверить владельца компонента |
| `sale` module | модуля `www/bitrix/modules/sale` нет | не обещать корзину/заказ/оплаты/доставку |
| `bizproc` | модуля нет | держать `workflow.md` как deferred |
| `pull` | модуля нет | не строить realtime/push route на `pull` |
| `socialnet` | модуля нет | использовать только условную часть `blog-socialnet.md` после подтверждения |

## Ловушки текущего core

- `catalog.*` стандартные компоненты физически лежат в `www/bitrix/modules/iblock/install/components/bitrix`, но это не доказывает наличие модуля `catalog`.
- `corp_furniture` wizard может ссылаться на `bitrix:catalog`, но это skeleton решения, а не подтверждение установленного магазинного core.
- Отсутствие `www/local` означает, что следующий слой истины — stock component templates, `bitrix/templates/*` и wizard assets.
- Vendor-файлы внутри `www/bitrix/modules/main/vendor/*` не являются project tooling.
- Наличие JS test directories в core не означает, что PHP test contour проекта настроен.

## Покрытие reference-файлами

| Зона | Статус покрытия | Файлы |
|---|---|---|
| Core/modules/components | full-route | `core-audit-matrix.md`, `standard-components-noncommerce.md` |
| Diagnostics | full-route | `diagnostic-visibility.md`, `index-cache-diagnostics.md`, `component-dataflow-debugging.md` |
| PHP architecture/testing/quality | full-route | `php-workflow.md`, `php-testing.md`, `php-quality.md`, `php-legacy-modernization.md` |
| Content modules | active | `iblocks.md`, `highloadblock.md`, `webforms.md`, `blog-socialnet.md`, `forum.md`, `vote.md`, `subscribe.md` |
| Search/SEO/cache | active | `search.md`, `seo-cache-access.md`, `cache-infra.md`, `index-cache-diagnostics.md` |
| Admin/ops | active | `admin-ui.md`, `operations-runbook.md`, `perfmon.md`, `update-stepper.md` |
| Commerce | deferred | `catalog.md`, `sale.md`, `commerce-workflows.md` |

## Как обновлять матрицу

После установки новых модулей:

1. повторно снять список `www/bitrix/modules`;
2. проверить `install/version.php` или модульный аналог версии;
3. найти компоненты и stock templates;
4. обновить эту матрицу и `SKILL.md`;
5. снять deferred-флаг только для реально появившегося модуля.

---

## Source: `noncommerce-task-matrix.md`

# Non-Commerce Task Matrix — справочник

> Reference для Bitrix-скилла. Загружай, когда нужно быстро сопоставить типовую или нетиповую задачу без интернет-магазина с правильными reference-файлами.

## Содержание
- Контент и структура
- Компоненты и фронт
- Поиск, SEO, кеш
- Пользователи и доступ
- Формы, уведомления, подписки
- Интеграции и эксплуатация
- PHP/project quality

## Контент и структура

| Задача | Читать |
|---|---|
| создать/изменить инфоблок | `iblocks.md`, `entities-migrations.md` |
| добавить свойства и UF | `iblocks.md`, `custom-uf-types.md` |
| связать iblock и HL | `iblock-hl-relations.md`, `highloadblock.md` |
| импортировать CSV/XML/JSON | `import-export.md`, `operations-runbook.md` |
| обновить файлы и картинки | `import-export.md`, `file-upload-modern.md`, `clouds.md` |
| сделать миграцию структуры | `entities-migrations.md`, `operations-runbook.md` |
| “в админке есть, на сайте нет” | `diagnostic-visibility.md`, `component-dataflow-debugging.md` |

## Компоненты и фронт

| Задача | Читать |
|---|---|
| доработать стандартный компонент | `standard-components-noncommerce.md`, `component-dataflow-debugging.md` |
| изменить шаблон без правки ядра | `components.md`, `templates.md` |
| вынести логику из шаблона | `php-workflow.md`, `php-legacy-modernization.md` |
| настроить `result_modifier.php` | `component-dataflow-debugging.md` |
| добавить breadcrumbs/meta | `component-dataflow-debugging.md`, `seo-cache-access.md` |
| сделать AJAX endpoint | `events-routing.md`, `security.md` |
| проверить отсутствие `local/*` | `core-audit-matrix.md`, `standard-components-noncommerce.md` |

## Поиск, SEO, кеш

| Задача | Читать |
|---|---|
| товар/страница не в поиске | `search.md`, `index-cache-diagnostics.md` |
| настроить быстрый поиск | `search.md`, `events-routing.md` |
| canonical/noindex/robots | `seo-cache-access.md` |
| sitemap | `seo-cache-access.md`, `operations-runbook.md` |
| очистка кеша после изменений | `cache-infra.md`, `index-cache-diagnostics.md` |
| диагностика дублей URL | `sef-urls.md`, `seo-cache-access.md` |

## Пользователи и доступ

| Задача | Читать |
|---|---|
| регистрация/авторизация | `users.md`, `session-auth.md` |
| восстановление пароля | `users.md`, `mail-notifications.md` |
| группы и права | `access-rbac.md`, `users.md` |
| социальная авторизация | `socialservices.md`, `users.md` |
| GDPR-согласие | `userconsent.md` |
| ограничение контента по правам | `access-rbac.md`, `diagnostic-visibility.md` |

## Формы, уведомления, подписки

| Задача | Читать |
|---|---|
| веб-форма | `webforms.md`, `standard-components-noncommerce.md` |
| custom validator | `webforms.md`, `validation.md` |
| форма отправляется, письма нет | `webforms.md`, `mail-notifications.md` |
| SMS/Telegram-like route | `messageservice.md`, `rest.md` |
| подписки и рассылки | `subscribe.md`, `mail-notifications.md` |
| secure file access in form | `webforms.md`, `file-upload-modern.md` |

## Интеграции и эксплуатация

| Задача | Читать |
|---|---|
| REST webhook/method | `rest.md`, `events-routing.md` |
| Bitrix24 connector | `b24connector.md`, `socialservices.md` |
| external file storage | `clouds.md` |
| backup/monitoring | `bitrixcloud.md`, `operations-runbook.md` |
| performance diagnostics | `perfmon.md`, `operations-runbook.md` |
| перенос стендов | `operations-runbook.md`, `entities-migrations.md` |
| agents/cron/stepper | `update-stepper.md`, `operations-runbook.md` |

## PHP/project quality

| Задача | Читать |
|---|---|
| разложить PHP-код по слоям | `php-workflow.md`, `modules-loader.md` |
| покрыть проверками | `php-testing.md` |
| настроить/использовать phpstan/psalm/fixer | `php-quality.md` |
| модернизировать legacy | `php-legacy-modernization.md` |
| не сломать Bitrix-boundary | `php-workflow.md`, `component-dataflow-debugging.md` |
| проверить vendor noise | `php-testing.md`, `php-quality.md` |

## Что остаётся deferred

Интернет-магазин, цены, остатки, SKU, корзина, заказ, оплата, доставка, скидки и checkout остаются deferred до установки `catalog` и `sale`.

---

## Source: `diagnostic-visibility.md`

# Visibility Diagnostics: “в админке есть, на сайте нет” — справочник

> Reference для Bitrix-скилла. Загружай для задач “не видно на сайте”, “в админке есть”, “компонент ничего не выводит”, “у одного пользователя видно, у другого нет”.

## Содержание
- Диагностическая цепочка
- Быстрые команды
- Типовые причины
- Модульные маршруты
- Что нельзя делать
- С чем читать вместе

## Диагностическая цепочка

Иди от источника данных к браузеру:

1. Модуль и компонент реально установлены.
2. Данные существуют и активны.
3. Сайт, язык, права и группы пользователя совпадают.
4. Компонент получает правильные параметры.
5. Выборка не отфильтровала данные.
6. `result_modifier.php` не выкинул нужные поля.
7. `template.php` реально выводит эти данные.
8. Кеш компонента/тегированный кеш не отдаёт старое состояние.
9. Страница не скрыта SEO/robots/noindex/canonical logic.
10. Клиентский JS/AJAX не перерисовывает пустое состояние.

## Быстрые команды

```bash
find www/bitrix/modules -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | sort

find local/components bitrix/templates www/bitrix/templates -path '*result_modifier.php' -o -path '*component_epilog.php' -o -path '*template.php'

rg -n 'CACHE_TYPE|CACHE_TIME|CACHE_TAG|clearByTag|clearTaggedCache|StartTagCache|EndTagCache|setResultCacheKeys|AbortResultCache' local bitrix/templates www/bitrix/templates www/bitrix/modules

rg -n 'ACTIVE|ACTIVE_FROM|ACTIVE_TO|SITE_ID|LID|GROUP_ID|PERMISSION|RIGHT|CHECK_PERMISSIONS|noindex|canonical|robots' local bitrix/templates www/bitrix/templates www/bitrix/modules
```

Если `local/*` отсутствует, сразу переходи к `bitrix/templates`, `www/bitrix/templates` и stock templates в `www/bitrix/modules/*/install/components/bitrix`.

## Типовые причины

| Симптом | Проверить |
|---|---|
| В админке есть, на публичке пусто | `ACTIVE`, даты активности, site binding, section active chain, права |
| У админа видно, у гостя нет | группы пользователя, `CHECK_PERMISSIONS`, inherited rights, component params |
| После правки не меняется | component cache, tagged cache, managed cache, composite/static cache |
| В списке нет, детальная открывается | фильтр списка, section filter, pagination, sort, `INCLUDE_SUBSECTIONS` |
| В поиске нет | search index, module `search`, `BeforeIndex`, rights, site, URL function |
| SEO/URL странный | `urlrewrite.php`, SEF params, canonical, redirects, robots/noindex |
| Файл не открывается | `clouds`, `HANDLER_ID`, secure file access, `CFile` path, rights |
| Форма отправляется, но результата нет | form status, validators, handlers, permissions, CRM link |

## Модульные маршруты

- IBlock/HL: сначала `iblocks.md`, `highloadblock.md`, потом кеш и права.
- Forms: `webforms.md`, затем status/validator/handler/secure files.
- Blog/forum/vote: legacy API и standard component template layer.
- Search/SEO: `search.md`, `seo-cache-access.md`, `index-cache-diagnostics.md`.
- File/address/media: `fileman.md`, `location.md`, `clouds.md`.
- Security: WAF/MFA/redirect/IP restrictions can affect visibility and access.

## Что нельзя делать

- Не говорить “почистите весь кеш” как единственный ответ.
- Не менять шаблон, пока не проверен входной `$arResult`.
- Не считать отсутствие `local/*` отсутствием кастомизации: stock templates и wizard templates всё ещё влияют на вывод.
- Не путать физическое наличие `catalog.*` компонента в `iblock` с установленным модулем `catalog`.
- Не отключать права/кеш/SEO без понимания побочных эффектов.

## С чем читать вместе

- Component/data flow — [component-dataflow-debugging.md](component-dataflow-debugging.md)
- Cache/index — [index-cache-diagnostics.md](index-cache-diagnostics.md)
- Components/templates — [components.md](components.md), [templates.md](templates.md)
- Search/SEO — [search.md](search.md), [seo-cache-access.md](seo-cache-access.md)
- Security/access — [security.md](security.md), [access-rbac.md](access-rbac.md)

---

## Source: `index-cache-diagnostics.md`

# Cache и Index Diagnostics — справочник

> Reference для Bitrix-скилла. Загружай, когда задача связана с устаревшим выводом, поиском, SEO, тегированным кешем, индексами, импортом или “после изменения данные не обновились”.

## Содержание
- Карта кешей и индексов
- Порядок диагностики
- Что проверять по доменам
- Verification после правки
- Common mistakes

## Карта кешей и индексов

| Слой | Где проявляется | Reference |
|---|---|---|
| Component cache | стандартные компоненты, `$arParams['CACHE_*']` | `components.md` |
| Tagged cache | инфоблоки, HL, связанные данные | `cache-infra.md`, `iblocks.md` |
| Managed cache | options, ORM metadata, module state | `cache-infra.md`, `modules-loader.md` |
| Composite/static HTML | публичные страницы, персональные блоки | `templates.md` |
| Search index | `CSearch`, `search.page`, `search.title` | `search.md` |
| SEO artifacts | sitemap, robots, canonical, OpenGraph | `seo-cache-access.md` |
| Landing cache | landing blocks/pages/hooks | `landing.md` |

## Порядок диагностики

1. Определи, какие данные менялись: element, section, UF, form result, blog post, file, landing block, user, option.
2. Найди компонент или endpoint, который отдаёт публичный результат.
3. Проверь, кешируется ли результат и какие cache keys/tag-и используются.
4. Проверь, нужно ли переиндексировать поиск или SEO artifacts.
5. Проверь права и site binding, чтобы не перепутать кеш с access problem.
6. После исправления обнови только нужный слой, а не весь сайт без причины.

## Что проверять по доменам

| Домен | После изменения думать о |
|---|---|
| IBlock elements/sections | component cache, tagged cache, search index, sitemap/URL |
| HL blocks | ORM cache, component cache, dependent iblock/UF references |
| Web forms | result permissions, form cache, status handlers, mail events |
| Blog/forum/vote | legacy write API side effects, search index, template cache |
| Search | `CSearch::Index`, `CSearch::DeleteIndex`, `CSearch::ReIndexAll`, `BeforeIndex` |
| SEO | sitemap rebuild, robots/noindex, canonical duplicates |
| Landing | block hooks, mutator mode, page publication, landing cache |
| Files/clouds | `HANDLER_ID`, delayed resize, external `SRC`, file access |
| Users/access | group membership, session cache, permission cache |

## Verification после правки

Минимальный набор:

1. проверить изменённый runtime path без кеша или с точечной инвалидацией;
2. проверить повторный запрос с включённым кешем;
3. проверить гостя и авторизованного пользователя, если данные персональные;
4. проверить search/SEO только если задача меняла индексируемые данные;
5. зафиксировать, какой кеш или индекс был причиной.

## Common mistakes

- Сбрасывать весь кеш вместо определения слоя.
- Обновлять данные через D7 ORM, когда конкретный legacy-модуль ожидает `C*` write API side effects.
- Забывать search reindex после массового импорта.
- Кешировать персональные данные в общем component cache.
- Считать SEO-дубль проблемой шаблона, когда причина в SEF/canonical/urlrewrite.

## С чем читать вместе

- Cache primitives — [cache-infra.md](cache-infra.md)
- Components/templates — [components.md](components.md), [templates.md](templates.md)
- Search — [search.md](search.md)
- SEO — [seo-cache-access.md](seo-cache-access.md)
- Operations — [operations-runbook.md](operations-runbook.md)

---

## Source: `component-dataflow-debugging.md`

# Component и Data Flow Debugging — справочник

> Reference для Bitrix-скилла. Загружай для задач по стандартным компонентам, шаблонам, `result_modifier.php`, `component_epilog.php`, AJAX и трассировке данных от API до HTML.

## Содержание
- Truth layers
- Путь данных
- Где менять код
- Диагностические команды
- Red flags
- С чем читать вместе

## Truth layers

Порядок проверки:

1. `www/bitrix/modules/<module>/install/components/bitrix/<component>/`
2. `local/components/<vendor>/<component>/`, если есть
3. `local/templates/<template>/components/bitrix/<component>/<template>/`, если есть
4. `bitrix/templates/<template>/components/bitrix/<component>/<template>/`
5. `www/bitrix/templates/*/components/bitrix/...`
6. wizard public/template assets

Если `local/*` отсутствует, не останавливайся: stock templates и `bitrix/templates/*` становятся следующим живым слоем.

## Путь данных

1. `.parameters.php` задаёт контракт параметров.
2. `component.php` / `class.php` собирает данные и управляет кешем.
3. `result_modifier.php` изменяет `$arResult` до шаблона.
4. `template.php` отвечает за вывод и минимальную view-логику.
5. `component_epilog.php` делает поздние эффекты: meta, breadcrumbs, assets, deferred work.
6. JS/AJAX может заменить HTML после загрузки.

## Где менять код

| Что нужно | Слой |
|---|---|
| Изменить внешний вид | copied template |
| Подготовить поля для view | `result_modifier.php` или service до него |
| Добавить meta/breadcrumbs/canonical | `component_epilog.php` или page layer |
| Изменить бизнес-правило | service/module layer |
| Поменять выборку | component params, service, repository/ORM/legacy API |
| Добавить AJAX endpoint | controller/action route, не inline chaos в шаблоне |
| Починить кеш | component cache keys, tagged cache, `setResultCacheKeys` |

## Диагностические команды

```bash
find www/bitrix/modules -path '*/install/components/bitrix/<component>' -type d

find local/components bitrix/templates www/bitrix/templates -path '*<component>*' -type f

rg -n 'result_modifier|component_epilog|setResultCacheKeys|AbortResultCache|StartResultCache|includeComponentTemplate|ajax|BX.ajax' local bitrix/templates www/bitrix/templates www/bitrix/modules
```

Заменяй `<component>` на реальное имя, например `form.result.new`, `blog.post`, `search.page`.

## Red flags

- Толстая бизнес-логика в `template.php`.
- SQL или внешнее API прямо из шаблона.
- `result_modifier.php` меняет данные без учёта кеша.
- `component_epilog.php` используется для тяжёлых запросов вместо поздних page effects.
- Копия шаблона оторвана от stock variant и не сверена после обновления core.
- AJAX endpoint живёт в случайном PHP-файле без CSRF/access checks.

## С чем читать вместе

- Components — [components.md](components.md)
- Templates — [templates.md](templates.md)
- Standard non-commerce components — [standard-components-noncommerce.md](standard-components-noncommerce.md)
- Events/routing — [events-routing.md](events-routing.md)
- PHP workflow — [php-workflow.md](php-workflow.md)

---

## Source: `standard-components-noncommerce.md`

# Standard Components без магазина — справочник

> Reference для Bitrix-скилла. Загружай для задач по stock components и templates текущего core без `catalog`/`sale`.

## Содержание
- Принцип
- Активные component families
- Особая ловушка `catalog.*`
- Где искать template variants
- Что менять
- С чем читать вместе

## Принцип

Стандартный компонент — это контракт. Перед доработкой прочитай его из текущего core:

1. `.parameters.php`;
2. `component.php` или `class.php`;
3. stock `templates/*`;
4. вложенные components в комплексном шаблоне;
5. `result_modifier.php` и `component_epilog.php`, если есть.

## Активные component families

| Семейство | Модуль-владелец | Reference |
|---|---|---|
| `main.*` | `main` | `components.md`, `templates.md`, `users.md`, `grid-admin-modern.md` |
| `iblock.*` | `iblock` | `iblocks.md`, `entities-migrations.md` |
| `highloadblock.*` | `highloadblock` | `highloadblock.md` |
| `form`, `form.result.*` | `form` | `webforms.md` |
| `blog.*` | `blog` | `blog-socialnet.md` |
| `forum.*` | `forum` | `forum.md` |
| `voting.*`, `vote.*` | `vote` | `vote.md` |
| `search.*` | `search` | `search.md` |
| `landing.*` | `landing` | `landing.md` |
| `b24connector.*` | `b24connector` | `b24connector.md` |
| `bitrixcloud.mobile.*` | `bitrixcloud` | `bitrixcloud.md` |
| `messageservice.*` | `messageservice` | `messageservice.md` |
| `fileman.*`, maps/editor fields | `fileman` | `fileman.md`, `location.md` |

## Особая ловушка `catalog.*`

В текущем core `catalog.*` directories есть внутри:

```text
www/bitrix/modules/iblock/install/components/bitrix/catalog*
```

Это означает наличие iblock-based public components, но не наличие модуля `catalog`.

Правило:

- можно разбирать `catalog.section`/`catalog.element` как стандартный компонент из `iblock`;
- нельзя обещать торговый каталог, цены, SKU, остатки, корзину, заказ и checkout без модулей `catalog`/`sale`;
- если пользователь просит магазинную задачу, фиксируй deferred status.

## Где искать template variants

```bash
find www/bitrix/modules/<module>/install/components/bitrix/<component>/templates -maxdepth 2 -type f

find bitrix/templates www/bitrix/templates local/templates -path '*components/bitrix/<component>*' -type f
```

Если `local/templates` отсутствует, смотри `bitrix/templates/.default`, `bitrix/templates/furniture_gray`, `bitrix/templates/landing24` и wizard templates.

## Что менять

| Задача | Слой |
|---|---|
| внешний HTML | copy template |
| подготовка данных | `result_modifier.php` или service |
| meta/breadcrumbs/canonical | `component_epilog.php` |
| параметры выборки | component params и API-layer |
| бизнес-правило | service/module layer |
| кеш | component cache + tagged cache |
| AJAX | controller/action с CSRF/access checks |

## С чем читать вместе

- Components/data flow — [component-dataflow-debugging.md](component-dataflow-debugging.md)
- Templates — [templates.md](templates.md)
- Web forms — [webforms.md](webforms.md)
- Blog/forum/vote — [blog-socialnet.md](blog-socialnet.md), [forum.md](forum.md), [vote.md](vote.md)
- Search/SEO — [search.md](search.md), [seo-cache-access.md](seo-cache-access.md)
