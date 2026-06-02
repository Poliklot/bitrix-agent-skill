# Core Routing
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `core-audit-matrix.md`

# Core Audit Matrix — active core, shop-core и deferred zones

> Reference для Bitrix-скилла. Загружай, когда нужно понять, что реально установлено в текущем core, какие домены активны, какие условны и куда вести задачу. Матрица теперь поддерживает две подтверждённые фазы: non-commerce core и отдельный shop-core для интернет-магазина/1С.

## 0. Фазовый принцип

Bitrix skill остаётся **core-first**, а не “версией по памяти”. Есть два подтверждённых truth layer:

1. **Non-commerce checkout** — активны контентные/системные модули, commerce был deferred.
2. **Shop-core checkout** `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core` — подтверждены `catalog`, `sale`, `currency`, `bitrix.eshop`, `pull`, `bizproc`, `sender`, `storeassist`, 1С/CommerceML components.

В каждом новом пользовательском проекте сначала проверяй локальный `www/bitrix/modules`. Нельзя переносить активность `sale/catalog` из shop-core на другой проект без проверки.

## 1. Быстрые проверки

```bash
find www/bitrix/modules -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | sort

for m in main iblock currency catalog sale bizproc pull socialnet; do
  if test -f "www/bitrix/modules/$m/install/version.php"; then
    echo "--- $m ---" && sed -n '1,40p' "www/bitrix/modules/$m/install/version.php"
  elif test -f "www/bitrix/modules/$m/classes/general/version.php"; then
    echo "--- $m ---" && sed -n '1,20p' "www/bitrix/modules/$m/classes/general/version.php"
  else
    echo "MISS $m"
  fi
done
```

Для `main` не требуй обычный `install/version.php`: в проверенном shop-core версия лежит в `www/bitrix/modules/main/classes/general/version.php` (`SM_VERSION 26.150.0`).

## 2. Подтверждённый shop-core

Shop-core facts:

| Модуль | Версия | Статус | Reference |
|---|---:|---|---|
| `main` | `26.150.0` | active | `modules-loader.md`, `session-auth.md`, `database-layer.md`, `pagination.md` |
| `iblock` | `25.300.0` | active | `iblocks.md`, `entities-migrations.md` |
| `currency` | `26.0.0` | active shop | `currency.md` |
| `catalog` | `25.550.0` | active shop | `catalog.md` |
| `sale` | `26.0.0` | active shop | `sale.md` |
| `bitrix.eshop` | `25.0.0` | active shop solution | `commerce-workflows.md`, `shop-task-matrix.md` |
| `storeassist` | `24.0.0` | active shop assistant | `commerce-1c-integration.md`, `commerce-workflows.md` |
| `pull` | `25.300.0` | active in shop-core | `push-pull.md` after local confirmation |
| `bizproc` | `26.200.0` | active in shop-core | `workflow.md` after local confirmation |
| `sender` | `26.0.0` | active in shop-core | `mail-notifications.md`, `sale.md` side effects |

Shop-core содержит exchange components:

- `catalog.import.1c`
- `catalog.export.1c`
- `sale.export.1c`

Admin entrypoints:

- `/bitrix/admin/1c_import.php`
- `/bitrix/admin/1c_exchange.php`
- `/bitrix/admin/1c_admin.php`
- `/bitrix/admin/sale_exchange_log.php`

## 3. Активные non-commerce модули

| Модуль | Статус | Основной reference | Что проверять первым |
|---|---|---|---|
| `main` | active | `modules-loader.md`, `orm.md`, `session-auth.md`, `database-layer.md`, `access-rbac.md`, `pagination.md` | `lib/`, `classes/general`, компоненты `main.*`, user/session/cache/ORM/navigation |
| `iblock` | active | `iblocks.md`, `iblock-hl-relations.md`, `entities-migrations.md` | components, properties, sections, UF, legacy + D7 |
| `highloadblock` | active | `highloadblock.md` | dynamic ORM, rights, UI selector |
| `form` | active | `webforms.md` | form/result/status/validators/handlers/CRM link |
| `blog` | active | `blog-socialnet.md` | `CBlog*` write path, D7 read-only tables |
| `forum` | active | `forum.md` | `CForum*`, forum components, permissions |
| `vote` | active | `vote.md` | `CVote*`, channels/questions/answers |
| `subscribe` | active | `subscribe.md`, `mail-notifications.md` | rubrics, subscriptions, postings |
| `search` | active | `search.md`, `index-cache-diagnostics.md` | `CSearch`, title search, `BeforeIndex`, rights |
| `seo` | active | `seo-cache-access.md` | sitemap, robots/noindex, canonical, OpenGraph |
| `landing` | active | `landing.md` | Site/Landing/Block/Hook/Rights, mutator mode |
| `bitrix.sitecorporate` | active | `sitecorporate.md` | wizard shell, public skeleton, stock components |
| `fileman` | active | `fileman.md` | editor, address/map/video fields |
| `location` | active | `location.md` | address/location services, formats, widgets |
| `messageservice` | active | `messageservice.md` | SMS providers, limits, callbacks |
| `socialservices` | active | `socialservices.md` | OAuth providers, user links |
| `rest` | active | `rest.md` | REST methods/events/webhooks/OAuth |
| `security` | active | `security.md` | WAF, OTP/MFA, redirect/IP rules |
| `perfmon` | active | `perfmon.md` | SQL/hit/cache diagnostics |
| `clouds` | active | `clouds.md` | external storage, `HANDLER_ID`, resize/src |
| `bitrixcloud` | active | `bitrixcloud.md` | backup policy, monitoring |
| `mobileapp` | active | `mobileapp.md` | admin mobile, JN/native components |
| `b24connector` | active | `b24connector.md` | portal binding, buttons, site restrictions |
| `translate` | active | `translate.md` | lang files, phrase index, import/export |
| `photogallery` | active | `photogallery.md` | gallery root, albums, upload, comments |
| `ui` | active | `grid-admin-modern.md`, `file-upload-modern.md` | grid/filter/uploader/entity selector |

## 4. Shop task routing

| Домен | Активируется когда | Читать |
|---|---|---|
| Товары/SKU/цены/остатки | `catalog` + `currency` есть | `catalog.md`, `currency.md`, `shop-task-matrix.md` |
| Корзина/order/checkout | `sale` + `catalog` + `currency` есть | `sale.md`, `commerce-workflows.md` |
| 1С/CommerceML | `catalog.import.1c` или `sale.export.1c` есть | `commerce-1c-integration.md` |
| Store documents | `catalog.store.document.*` есть | `catalog.md`, `commerce-workflows.md` |
| Bizproc/order automation | `bizproc` есть | `workflow.md`, `sale.md` |
| Pull/realtime shop UI | `pull` есть | `push-pull.md`, конкретный component |
| Eshop wizard/template | `bitrix.eshop` есть | `commerce-workflows.md`, `templates.md` |

## 5. Условные и отложенные домены

| Домен | Когда deferred | Что делать |
|---|---|---|
| `catalog` | нет `www/bitrix/modules/catalog` | не обещать цены/SKU/остатки; `catalog.*` из `iblock` считать только component-family без commerce API |
| `sale` | нет `www/bitrix/modules/sale` | не обещать basket/order/payment/delivery |
| `currency` | нет `www/bitrix/modules/currency` | не рассчитывать цены как полноценный commerce |
| `bizproc` | нет модуля | держать `workflow.md` как deferred |
| `pull` | нет модуля | не строить realtime/push route |
| `socialnet` | нет модуля | использовать только `blog`-часть `blog-socialnet.md` |
| 1С exchange | нет `catalog.import.1c`/`sale.export.1c` | описывать только generic import/export, не CommerceML route |

## 6. Ловушки

- Наличие `catalog.*` components внутри `iblock` или шаблонов не доказывает установленный `catalog` module.
- Наличие shop-core в одном checkout не доказывает commerce-модули в другом проекте.
- Parent product и offer — разные product IDs; цена/остаток часто живут на offer.
- `currency` обязателен для корректного понимания catalog prices и sale sums.
- `sale` side effects нельзя заменить SQL-правкой: order history, reservation, payment, shipment, cashbox, exchange.
- 1С exchange success на `file` не означает успешный import: проверяй `mode=import`, session state, tables, logs.
- Vendor-файлы внутри `www/bitrix/modules/*/vendor` не являются project tooling.
- Пагинация не сводится к `PAGEN_1`: legacy `NavNum` может породить `PAGEN_2+`, D7 использует строковый id `PageNavigation`, а `nTopCount` — это limit без полноценного NavString.

## 7. Покрытие reference-файлами

| Зона | Статус покрытия | Файлы |
|---|---|---|
| Core/modules/components | full-route | `core-audit-matrix.md`, `standard-components-noncommerce.md` |
| Diagnostics | full-route | `diagnostic-visibility.md`, `pagination.md`, `index-cache-diagnostics.md`, `component-dataflow-debugging.md` |
| PHP architecture/testing/quality | full-route | `php-workflow.md`, `php-testing.md`, `php-quality.md`, `php-legacy-modernization.md` |
| Content modules | active | `iblocks.md`, `highloadblock.md`, `webforms.md`, `blog-socialnet.md`, `forum.md`, `vote.md`, `subscribe.md` |
| Search/SEO/cache | active | `search.md`, `seo-cache-access.md`, `cache-infra.md`, `index-cache-diagnostics.md` |
| Admin/ops | active | `admin-ui.md`, `grid-admin-modern.md`, `pagination.md`, `operations-runbook.md`, `perfmon.md`, `update-stepper.md` |
| Commerce/shop | active after local module confirmation | `shop-task-matrix.md`, `catalog.md`, `sale.md`, `currency.md`, `commerce-workflows.md` |
| 1С/CommerceML | active after component confirmation | `commerce-1c-integration.md` |

## 8. Как обновлять матрицу

После установки новых модулей:

1. повторно снять список `www/bitrix/modules`;
2. проверить version files;
3. найти components and stock templates;
4. проверить admin entrypoints;
5. обновить эту матрицу, `SKILL.md`, `README.md`, `CHANGELOG.md`, `VERSION`;
6. снять deferred-флаг только для реально появившегося модуля.

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
| исправить пустую/дублирующую вторую страницу | `pagination.md`, `component-dataflow-debugging.md`, `iblocks.md` |
| настроить `PageNavigation`, `PAGEN_N` или “Показать ещё” | `pagination.md`, `components.md`, `grid-admin-modern.md` |
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

## Commerce boundary

Этот файл остаётся роутером именно для задач **без интернет-магазина**. Если в проекте подтверждены `catalog`, `sale` и `currency`, для магазинных задач переходи в `shop-task-matrix.md`, `catalog.md`, `sale.md`, `currency.md`, `commerce-workflows.md` и `commerce-1c-integration.md`. Если модулей нет — commerce остаётся deferred и не должен подменяться `iblock`-компонентами.

---

## Source: `shop-task-matrix.md`

# Shop task matrix — routing интернет-магазина

> Используй этот файл как быстрый роутер для задач по интернет-магазину. Truth layer для нового этапа: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core` с подтверждёнными `catalog` 25.550.0, `sale` 26.0.0, `currency` 26.0.0, `bitrix.eshop` 25.0.0, `pull`, `bizproc`, `sender`, `storeassist`.

## 1. Быстрый routing

| Запрос пользователя | Сначала читать | Затем |
|---|---|---|
| Товары, свойства, разделы, SKU | `catalog.md`, `iblocks.md` | `commerce-1c-integration.md`, если есть 1С/XML_ID |
| Цена не та / не показывается | `catalog.md`, `currency.md` | `sale.md`, `search-seo-ops` bundles для кеша |
| Остатки, склады, доступность | `catalog.md` | `sale.md` для reservation/order effects |
| Корзина не работает | `sale.md`, `catalog.md` | `components.md`, `events-routing.md` |
| Checkout / оформление заказа | `sale.md` | `users.md`, `validation.md`, `templates.md` |
| Оплата / callback | `sale.md` | `http.md`, `events-routing.md`, cashbox section в `sale.md` |
| Доставка / locations | `sale.md`, `location.md` | `components.md`, `validation.md` |
| Скидки / купоны | `sale.md`, `catalog.md` | `currency.md` |
| 1С выгрузка товаров | `commerce-1c-integration.md`, `catalog.md` | `currency.md`, `cache-infra.md` |
| Заказы в 1С | `commerce-1c-integration.md`, `sale.md` | `http.md`, `operations-runbook.md` |
| “В админке есть, на сайте нет” для товара | `catalog.md`, `diagnostic-visibility.md` | `index-cache-diagnostics.md`, `component-dataflow-debugging.md` |
| Вторая страница каталога пустая, lazy load сломан | `pagination.md`, `catalog.md`, `component-dataflow-debugging.md` | `sef-urls.md`, `cache-infra.md` |
| Производительность каталога | `catalog.md`, `perfmon.md`, `cache-infra.md` | `search.md`, `seo-cache-access.md` |

## 2. Минимальная проверка shop-core

```bash
for m in main iblock currency catalog sale; do
  if test -f "www/bitrix/modules/$m/install/version.php"; then
    sed -n '1,40p' "www/bitrix/modules/$m/install/version.php"
  elif test -f "www/bitrix/modules/$m/classes/general/version.php"; then
    sed -n '1,20p' "www/bitrix/modules/$m/classes/general/version.php"
  else
    echo "MISS $m"
  fi
done
```

Если `catalog`, `sale` или `currency` отсутствуют, возвращайся к non-commerce маршруту и не веди задачу как магазинную.

## 3. Диагностические цепочки

### Товар есть в админке, но не виден на сайте

1. `iblock`: element active, section active, site binding, dates, rights.
2. `catalog`: product row, type, offer relation, price, currency, availability.
3. `component`: params, filter, selected price types, offers props.
4. `template`: `result_modifier.php`, скрытие пустых props, JS SKU switcher.
5. `cache`: component/tagged/managed, facet/search index, composite.
6. `seo`: SEF/urlrewrite/canonical, 404 handling.

### Товар виден, но не покупается

1. Product/offer ID: добавляется parent или offer?
2. Price exists and accessible for user group.
3. Currency valid and formatted.
4. Quantity/availability/can buy zero/reservation.
5. Catalog provider returns item data for basket.
6. Sale basket event handlers and AJAX response.

### Checkout падает

1. Basket is not empty and refreshed.
2. Person type and mandatory order properties.
3. Delivery restrictions and location.
4. Payment restrictions and currency.
5. Discounts/coupons recalculation.
6. `Order::save()` errors.
7. Component AJAX template and JS.

### 1С обмен падает

1. Which flow: catalog import, catalog export, sale export/import.
2. `checkauth` response and cookie persistence.
3. `init` response: zip, file limit, sessid.
4. `file`: upload/chunk/temp dir permissions.
5. `import`: XML parsing, session state, last entry.
6. Mapping: XML_ID, CML2_LINK, price type, store.
7. Logs: `b_sale_exchange_log`, temp files, PHP/Apache errors.
8. Side effects: cache, indexes, order status/reservation.

## 4. Smoke fixtures для будущего теста

Минимальный sandbox-набор:

- один раздел каталога;
- один простой товар;
- один товар с двумя offers;
- базовая цена в `RUB`;
- один склад и остаток;
- один тестовый пользователь;
- одна корзина;
- один заказ с доставкой и оплатой;
- один CommerceML import fixture;
- один order export/import fixture.

## 5. Safety rules

- Production data changes require explicit confirmation.
- No real 1С, payments, delivery services, cashbox without confirmation.
- Prefer migrations/CLI/fixtures over admin clicks.
- Any exchange test must have cleanup and rollback.
- Never trust memory over `www/bitrix` code.

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
| В списке нет, детальная открывается | фильтр списка, section filter, `pagination.md`, sort, `INCLUDE_SUBSECTIONS` |
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
>
> Если симптом связан со второй страницей, `PAGEN_N`, `NavNum`, `PageNavigation`, lazy load или `main.pagenavigation`, дополнительно загружай `pagination.md`.

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
