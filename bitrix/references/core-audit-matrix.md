# Core Audit Matrix — active core, shop-core и deferred zones

> Reference для Bitrix-скилла. Загружай, когда нужно понять, что реально установлено в текущем core, какие домены активны, какие условны и куда вести задачу. Матрица теперь поддерживает две подтверждённые фазы: non-commerce core и отдельный shop-core для интернет-магазина/1С. Для полного списка 49 модулей shop-core, версий, coverage status и очереди доаудита смотри `shop-core-module-inventory.md`.

## 0. Фазовый принцип

Bitrix skill остаётся **core-first**, а не “версией по памяти”. Есть два подтверждённых truth layer:

1. **Non-commerce checkout** — активны контентные/системные модули, commerce был deferred.
2. **Shop-core checkout** `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core` — подтверждены 49 модулей; deep baseline готов для `catalog`, `sale`, `currency`, standard shop components, shop marketing/analytics, shop automation/bizproc, `bitrix.eshop`, pagination и 1С/CommerceML components, а полный coverage status вынесен в `shop-core-module-inventory.md`.

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

Полный inventory всех 49 модулей, counts по components/admin/lib/classes и очередность uncovered зон хранится в `shop-core-module-inventory.md`. Ниже — краткий shop-critical срез.

Shop-core facts:

| Модуль | Версия | Статус | Reference |
|---|---:|---|---|
| `main` | `26.150.0` | active | `modules-loader.md`, `session-auth.md`, `database-layer.md`, `pagination.md` |
| `iblock` | `25.300.0` | active | `iblocks.md`, `entities-migrations.md`, `shop-standard-components.md` для `catalog.*` |
| `currency` | `26.0.0` | active shop | `currency.md` |
| `catalog` | `25.550.0` | active shop | `catalog.md`, `shop-standard-components.md` |
| `sale` | `26.0.0` | active shop | `sale.md`, `shop-standard-components.md` |
| `bitrix.eshop` | `25.0.0` | active shop solution | `shop-standard-components.md`, `commerce-workflows.md`, `shop-task-matrix.md` |
| `storeassist` | `24.0.0` | active shop assistant | `commerce-1c-integration.md`, `commerce-workflows.md` |
| `pull` | `25.300.0` | active realtime/transport in shop-core | `shop-automation-bizproc.md`, `push-pull.md` after local confirmation |
| `bizproc` | `26.200.0` | active workflow/automation in shop-core | `shop-automation-bizproc.md`, `workflow.md` after local confirmation |
| `bizprocdesigner`/`workflow`/`lists` | confirmed | active automation/list-process layer | `shop-automation-bizproc.md`, `workflow.md` |
| `sender` | `26.0.0` | active shop marketing | `shop-marketing-analytics.md`, `mail-notifications.md`, `messageservice.md` |
| `mail` | `26.100.200` | active shop marketing channel | `shop-marketing-analytics.md`, `mail-notifications.md` |
| `messageservice` | `25.200.100` | active shop SMS/provider channel | `shop-marketing-analytics.md`, `messageservice.md` |
| `subscribe` | `25.0.0` | active legacy subscriptions | `shop-marketing-analytics.md`, `subscribe.md` |
| `advertising`/`abtest`/`conversion`/`report`/`statistic` | confirmed | active analytics/ads layer | `shop-marketing-analytics.md` |
| `webservice` | `26.0.0` | active SOAP/WSDL integration extras | `shop-integrations-webservice.md`, `http.md` |
| `rest` sale/catalog hooks | `26.0.0` + module handlers | active apps/webhooks/events/placements | `shop-integrations-webservice.md`, `rest.md` |

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
| Товары/SKU/цены/остатки | `catalog` + `currency` есть | `catalog.md`, `shop-standard-components.md`, `currency.md`, `shop-task-matrix.md` |
| Корзина/order/checkout | `sale` + `catalog` + `currency` есть | `sale.md`, `shop-standard-components.md`, `commerce-workflows.md` |
| 1С/CommerceML | `catalog.import.1c` или `sale.export.1c` есть | `commerce-1c-integration.md` |
| Store documents | `catalog.store.document.*` есть | `catalog.md`, `commerce-workflows.md` |
| Bizproc/order automation | `bizproc` есть | `shop-automation-bizproc.md`, `workflow.md`, `sale.md` |
| Lists/process automation | `lists` + `bizproc` есть | `shop-automation-bizproc.md`, `iblocks.md` |
| Pull/realtime shop UI | `pull` есть | `shop-automation-bizproc.md`, `push-pull.md`, конкретный component |
| Eshop wizard/template | `bitrix.eshop` есть | `shop-standard-components.md`, `commerce-workflows.md`, `templates.md` |
| Маркетинг/аналитика магазина | `sender`, `messageservice`, `subscribe`, `advertising`, `abtest`, `conversion`, `report` или `statistic` есть | `shop-marketing-analytics.md`, `mail-notifications.md`, `messageservice.md`, `subscribe.md` |
| Webservice/REST integrations | `webservice`, `rest`, `webservice.sale`, `webservice.statistic`, sale/catalog REST есть | `shop-integrations-webservice.md`, `rest.md`, `http.md` |

## 5. Условные и отложенные домены

| Домен | Когда deferred | Что делать |
|---|---|---|
| `catalog` | нет `www/bitrix/modules/catalog` | не обещать цены/SKU/остатки; `catalog.*` из `iblock` считать только component-family без commerce API |
| `sale` | нет `www/bitrix/modules/sale` | не обещать basket/order/payment/delivery |
| `currency` | нет `www/bitrix/modules/currency` | не рассчитывать цены как полноценный commerce |
| `bizproc` | нет модуля | держать `workflow.md` как deferred |
| `pull` | нет модуля | не строить realtime/push route |
| `socialnet` | нет модуля | использовать только `blog`-часть `blog-socialnet.md` |
| 1С exchange | нет `catalog.import.1c`/`sale.export.1c` | описывать только generic import/export, не CommerceML route; `webservice.sale` не считать 1С exchange |

## 6. Ловушки

- Наличие `catalog.*` components внутри `iblock` или шаблонов не доказывает установленный `catalog` module.
- Наличие shop-core в одном checkout не доказывает commerce-модули в другом проекте.
- Parent product и offer — разные product IDs; цена/остаток часто живут на offer.
- `currency` обязателен для корректного понимания catalog prices и sale sums.
- `sale` side effects нельзя заменить SQL-правкой: order history, reservation, payment, shipment, cashbox, exchange.
- 1С exchange success на `file` не означает успешный import: проверяй `mode=import`, session state, tables, logs.
- Vendor-файлы внутри `www/bitrix/modules/*/vendor` не являются project tooling.
- Пагинация не сводится к `PAGEN_1`: legacy `NavNum` может породить `PAGEN_2+`, D7 использует строковый id `PageNavigation`, а `nTopCount` — это limit без полноценного NavString.
- `sender.subscribe`, `subscribe.form/edit` и `catalog.product.subscribe*` — разные подсистемы подписок, не заменяй одну другой.
- `workflow` legacy и `bizproc` workflow engine — разные подсистемы; `iblock` не должен быть одновременно `WORKFLOW=Y` и `BIZPROC=Y`.
- `bizproc` в shop-core не доказывает наличие sale-order robots: для заказов проверяй provider/CRM/custom module.

## 7. Покрытие reference-файлами

| Зона | Статус покрытия | Файлы |
|---|---|---|
| Core/modules/components | full-route | `core-audit-matrix.md`, `standard-components-noncommerce.md` |
| Diagnostics | full-route | `diagnostic-visibility.md`, `pagination.md`, `index-cache-diagnostics.md`, `component-dataflow-debugging.md` |
| PHP architecture/testing/quality | full-route | `php-workflow.md`, `php-testing.md`, `php-quality.md`, `php-legacy-modernization.md` |
| Content modules | active | `iblocks.md`, `highloadblock.md`, `webforms.md`, `blog-socialnet.md`, `forum.md`, `vote.md`, `subscribe.md` |
| Search/SEO/cache | active | `search.md`, `seo-cache-access.md`, `cache-infra.md`, `index-cache-diagnostics.md` |
| Admin/ops | active | `admin-ui.md`, `grid-admin-modern.md`, `pagination.md`, `operations-runbook.md`, `perfmon.md`, `update-stepper.md` |
| Commerce/shop | active after local module confirmation | `shop-task-matrix.md`, `shop-standard-components.md`, `shop-marketing-analytics.md`, `shop-automation-bizproc.md`, `catalog.md`, `sale.md`, `currency.md`, `commerce-workflows.md` |
| 1С/CommerceML | active after component confirmation | `commerce-1c-integration.md` |
| Full shop-core inventory | routing map | `shop-core-module-inventory.md` |

## 8. Как обновлять матрицу

После установки новых модулей:

1. повторно снять список `www/bitrix/modules`;
2. проверить version files;
3. найти components and stock templates;
4. проверить admin entrypoints;
5. обновить эту матрицу, `SKILL.md`, `README.md`, `CHANGELOG.md`, `VERSION`;
6. снять deferred-флаг только для реально появившегося модуля.
