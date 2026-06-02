# StoreAssist — мастер интернет-магазина и 1С onboarding

> Reference для Bitrix-скилла. Загружай, когда задача связана с модулем `storeassist`, “Мастером магазина”, пунктами `storeassist_1c_*`, прогрессом настройки магазина, toolbar-задачами в админке или вопросом “это 1С интеграция или просто подсказка мастера?”.

## Audit note

Проверено по shop-core:
- `www/bitrix/modules/storeassist/install/version.php` — `storeassist` 24.0.0
- `www/bitrix/modules/storeassist/include.php`
- `www/bitrix/modules/storeassist/classes/general/storeassist.php`
- `www/bitrix/modules/storeassist/install/index.php`
- `www/bitrix/modules/storeassist/admin/storeassist.php`
- `www/bitrix/modules/storeassist/admin/storeassist_1c_catalog_fill.php`
- `www/bitrix/modules/storeassist/admin/storeassist_1c_unloading.php`
- `www/bitrix/modules/storeassist/admin/storeassist_1c_exchange_realtime.php`
- `www/bitrix/modules/storeassist/admin/storeassist_1c_small_firm.php`
- `www/bitrix/modules/storeassist/tools/storeassist.php`
- `www/bitrix/modules/storeassist/install/js/storeassist/storeassist.js`
- `www/bitrix/modules/storeassist/options.php`
- `www/bitrix/modules/storeassist/lang/ru/admin/storeassist.php`

Ниже только контракт, подтверждённый этим core.

## Главный вывод

`storeassist` — это **мастер/чеклист настройки интернет-магазина**, а не движок обмена с 1С.

Он:
- добавляет пункт “Мастер магазина” в sale settings menu;
- рисует toolbar-задачи на связанных admin-страницах;
- хранит выполненность задач в option `storeassist_settings`;
- показывает справочные/онбординг страницы `storeassist_1c_*`;
- ведёт пользователя в реальные admin pages `catalog`, `sale`, `seo`, `search`, `security`, `bitrixcloud`, `perfmon`;
- ежедневно считает paid finished/paid orders через agent для прогресса.

Он **не**:
- не принимает CommerceML files;
- не реализует `checkauth/init/file/import`;
- не обновляет товары, цены, остатки или заказы;
- не заменяет `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`.

Если пользователь жалуется на реальный обмен 1С — открывай `commerce-1c-integration.md`, `catalog.md`, `sale.md`. Если вопрос про мастер, чеклист, подсказку или task progress — открывай этот файл.

## Установка и hooks

`install/index.php`:

- `RegisterModule("storeassist")`;
- регистрирует dependency на `main` event `OnPrologAdminTitle` → `CStoreAssist::onPrologAdminTitle`;
- регистрирует dependency на `main` event `OnBuildGlobalMenu` → `CStoreAssist::onBuildGlobalMenu`;
- добавляет daily agent `CStoreAssist::AgentCountDayOrders();` с периодом `86400`;
- копирует:
  - `install/admin` → `/bitrix/admin`;
  - `install/js` → `/bitrix/js`;
  - `install/panel` → `/bitrix/panel`;
  - `install/tools` → `/bitrix/tools`.

`include.php`:

- autoload: `CStoreAssist` → `classes/general/storeassist.php`;
- JS extension `storeassist`:
  - JS `/bitrix/js/storeassist/storeassist.js`;
  - CSS `/bitrix/js/storeassist/css/storeassist.css`;
  - lang `modules/storeassist/lang/<LANG>/jsmessages.php`.

## Права и доступ

Все admin pages проверяют:

```php
$APPLICATION->GetGroupRight("storeassist") >= "R"
```

Для изменения статуса задачи нужен фактически write-доступ: toolbar кнопки рисуются только при `ST_RIGHT >= "W"`, а POST endpoint дополнительно требует `check_bitrix_sessid()`.

Модуль имеет `MODULE_GROUP_RIGHTS = "Y"`, значит права управляются как module rights.

## Основной класс `CStoreAssist`

Подтверждённые методы:

- `setSettingOption($pageId, $isDone)`
- `getSettingOption()`
- `getDocumentationLink($pageId)`
- `onPrologAdminTitle($pageUrl, $pageId = "")`
- `onBuildGlobalMenu(&$arGlobalMenu, &$arModuleMenu)`
- `getProgressPercent()`
- `AgentCountDayOrders()`

### Whitelist задач

`CStoreAssist::$arAllPageId` содержит whitelist допустимых `pageId`. `setSettingOption()` и `getDocumentationLink()` откажут, если `pageId` не в этом списке.

В whitelist есть ключевые shop/1С task ids:

- `currencies`
- `cat_group_admin`
- `cat_measure_list`
- `sale_person_type`
- `sale_buyers`
- `sale_status`
- `cat_store_list`
- `cat_product_list`
- `quantity`
- `cat_store_document_list`
- `order_setting`
- `reserve_setting`
- `storeassist_1c_catalog_fill`
- `1c_integration`
- `storeassist_1c_unloading`
- `1c_exchange`
- `storeassist_1c_exchange_realtime`
- `storeassist_1c_small_firm`
- `sale_pay_system`
- `sale_delivery`
- `sale_delivery_service_list`
- `storeassist_seo_settings`
- `search_reindex`
- `cat_discount_admin`
- `posting_admin`
- `cat_export_setup`
- `sale_order`
- `sale_report`
- `sale_account_admin`
- `sale_basket`
- `sale_personalization`
- `sale_crm`
- `storeassist_crm_client`
- `storeassist_crm_calls`
- `composite`
- `perfmon_panel`
- `security_filter`
- `dump_auto`
- `bitrixcloud_monitoring_admin`
- `security_scanner`
- `security_otp`

## Options

Подтверждённые options:

| Option | Где используется | Смысл |
|---|---|---|
| `storeassist_settings` | `setSettingOption()`, `getSettingOption()` | comma-separated список выполненных `pageId` |
| `partner_name` | `options.php`, lang/support task | партнёр-разработчик проекта |
| `partner_url` | `options.php`, `onPrologAdminTitle()`, support link | URL поддержки партнёра |
| `progress_percent` | `getProgressPercent()`, `AgentCountDayOrders()` | прогресс заказов от 0 до 10 |
| `num_orders` | `AgentCountDayOrders()` | serialized `newDay`/`prevDay` для динамики заказов |

`options.php` валидирует `partner_url` regex-ом на `http/https` URL и сохраняет через `COption::SetOptionString()`.

## AJAX endpoint

`/bitrix/tools/storeassist.php`:

- подключает `prolog_before.php`;
- подключает lang;
- требует `Loader::includeModule('storeassist')`;
- принимает только POST;
- требует `action` и `check_bitrix_sessid()`;
- поддерживает действие `setOption`;
- ждёт `pageId` и `status`;
- вызывает `CStoreAssist::setSettingOption($_POST["pageId"], $_POST["status"])`;
- отвечает JSON через `Bitrix\Main\Web\Json::encode()`.

JS `BX.Storeassist.Admin.setOption(pageId, status)` отправляет:

```js
{
  pageId: pageId,
  status: status,
  action: "setOption",
  sessid: BX.bitrix_sessid()
}
```

## Admin toolbar

`onPrologAdminTitle($pageUrl, $pageId = "")`:

- работает только для `LANGUAGE_ID` `ru` или `ua`;
- требует права `storeassist >= R`;
- если `pageId` не передан, вытаскивает его из имени текущего `.php`;
- проверяет whitelist `$arAllPageId`;
- читает выполненные задачи из `storeassist_settings`;
- подключает JSCore `storeassist`, `fx` и CSS `/bitrix/panel/storeassist/storeassist.css`;
- рисует toolbar с кнопкой назад в `/bitrix/admin/storeassist.php`, статусом done/not done и кнопкой документации;
- при `storeassist >= W` даёт кнопку отметить задачу выполненной/невыполненной.

Диагностика: если toolbar не появился на admin page, проверяй язык, права, event registration, whitelist `pageId`, наличие copied CSS/JS и query `pageid` там, где страница не совпадает с task id.

## Admin menu

`onBuildGlobalMenu()`:

- работает только для `ru` / `ua`;
- требует права `storeassist >= R`;
- добавляет пункт `storeassist.php?lang=<LANGUAGE_ID>` в menu item с `items_id === "menu_sale_settings"`.

Если пункта “Мастер магазина” нет, проверяй:
1. модуль `storeassist` установлен;
2. dependency `main:OnBuildGlobalMenu` зарегистрирован;
3. права группы на модуль;
4. присутствует sale settings menu;
5. язык `ru` или `ua`.

## Структура мастера `storeassist.php`

Главная admin page строит `$arAssistSteps` из трёх секций.

### `MAIN` — настройки, без которых магазин не сможет работать

`BLOCK_1` — основные настройки:
- валюты → `/bitrix/admin/currencies.php`, requires `currency`;
- варианты цен → `cat_group_admin.php`, requires `catalog`;
- единицы измерений → `cat_measure_list.php`, requires `catalog`;
- реквизиты магазина → `sale_report_edit.php`, requires `sale`;
- типы плательщиков → `sale_person_type.php`, requires `sale`;
- покупатели/profile → `sale_buyers.php`, requires `sale`;
- статусы заказов → `sale_status.php`, requires `sale`;
- склады → `cat_store_list.php`, requires `catalog`;
- social/phone replacement → `storeassist_social.php`.

`BLOCK_2` — товары, остатки, цены:
- product list: если найден active catalog iblock типа `catalog`, ведёт в `cat_product_list.php?IBLOCK_ID=...`; иначе в `storeassist_new_items.php`;
- quantity settings → `settings.php?mid=catalog&pageid=quantity`;
- store documents → `cat_store_document_list.php`;
- order behavior → `settings.php?mid=sale&pageid=order_setting`;
- reserve settings → `settings.php?mid=catalog&pageid=reserve_setting`.

`BLOCK_3` — интеграция с 1С:
- `storeassist_1c_catalog_fill.php` — справочная страница первичного заполнения каталога из 1С;
- `1c_admin.php?pageid=1c_integration` — реальная настройка интеграции, requires `sale` in this wizard;
- `storeassist_1c_unloading.php` — справочная страница выгрузки товаров из магазина в 1С;
- `1c_admin.php?pageid=1c_exchange` — настройка обмена заказами, requires `sale`;
- `storeassist_1c_exchange_realtime.php` — справочная страница realtime exchange;
- `storeassist_1c_small_firm.php` — справочная страница “Управление небольшой фирмой”.

Важно: `storeassist_1c_*` pages сами не выполняют exchange. Они показывают текст и ссылку на документацию. Реальная настройка/обмен идут через `sale`/`catalog` admin pages и exchange components.

`BLOCK_4` — payments/delivery:
- `sale_pay_system.php`;
- `sale_delivery_service_list.php` или legacy `sale_delivery.php` в зависимости от option `main/~sale_converted_15`.

`BLOCK_5` — SEO/search:
- `storeassist_seo_settings.php`;
- `seo_robots.php`;
- `seo_sitemap.php`;
- `seo_search_yandex.php`;
- `seo_search_google.php`;
- `search_reindex.php`.

### `WORK` — повседневная работа магазина

- opening/adaptive/checklist;
- discounts and mailings: `cat_discount_admin.php`, `posting_admin.php`;
- marketplaces/export: `cat_export_setup.php`, `sale_ymarket.php`, eBay-related task id;
- orders: `sale_order.php`, `sale_report.php`, `sale_buyers.php`, `sale_account_admin.php`, `sale_basket.php`;
- personalization: `sale_personalization.php`;
- support: `blog_comment.php`, `ticket_desktop.php`;
- CRM: `sale_crm.php`, `storeassist_crm_client.php`, `storeassist_crm_calls.php`.

### `HEALTH` — здоровье магазина

- performance: `site_speed.php`, `bitrixcloud_cdn.php`, `composite.php`, `perfmon_panel.php`;
- security/backups: `security_filter.php`, `dump_auto.php`, `security_scanner.php`, `bitrixcloud_monitoring_admin.php`, `security_otp.php`;
- scale/infra: `scale_graph.php`, `cluster_index.php`, `storeassist_virtual.php`;
- support/info links.

## 1С pages: как трактовать

| Page | Что делает в core | Куда вести реальную диагностику |
|---|---|---|
| `storeassist_1c_catalog_fill.php` | static onboarding text + wizard/docs buttons | `catalog.import.1c`, `commerce-1c-integration.md` |
| `storeassist_1c_unloading.php` | static onboarding text + wizard/docs buttons | `catalog.export.1c`, `commerce-1c-integration.md` |
| `storeassist_1c_exchange_realtime.php` | static text about realtime exchange | сначала `commerce-1c-integration.md`, затем конкретный 1С-side setup |
| `storeassist_1c_small_firm.php` | static text about 1С:УНФ / CommerceML 2.0 | `commerce-1c-integration.md` |
| `1c_admin.php?pageid=1c_integration` | external sale/catalog admin route | `sale.md`, `catalog.md`, `commerce-1c-integration.md` |
| `1c_admin.php?pageid=1c_exchange` | external sale/catalog admin route | `sale.export.1c`, `sale_exchange_log` |

## Agent: progress by orders

`CStoreAssist::AgentCountDayOrders()`:

- runs only if `Loader::includeModule("sale")` succeeds;
- filters orders:
  - `STATUS_ID` in `F`, `P`;
  - `PAYED` = `Y`;
  - `DATE_STATUS` between calculated previous/current day boundaries;
- uses `CSaleOrder::GetList()` and `SelectedRowsCount()`;
- stores option `num_orders` as serialized array with `newDay` and `prevDay`;
- adjusts `progress_percent` between 0 and 10;
- returns its own agent string.

Если прогресс заказов не меняется, проверяй:
1. module agent exists for `storeassist`;
2. `sale` installed;
3. orders match statuses `F`/`P` and `PAYED=Y`;
4. `DATE_STATUS` falls into expected period;
5. options `num_orders` and `progress_percent`.

## Диагностика

### Task completion не сохраняется

Проверь:
1. POST идёт в `/bitrix/tools/storeassist.php`;
2. есть `sessid: BX.bitrix_sessid()`;
3. `check_bitrix_sessid()` проходит;
4. `pageId` есть в `CStoreAssist::$arAllPageId`;
5. `status` строго `Y` или `N`;
6. option `storeassist_settings` обновляется;
7. пользователь имеет право `storeassist >= W` для UI-кнопок.

### “Мастер магазина” не виден в меню

Проверь:
1. `storeassist` installed;
2. module rights `>= R`;
3. language `ru`/`ua`;
4. event `OnBuildGlobalMenu` registered;
5. sale settings menu item `menu_sale_settings` существует.

### Toolbar не появился на странице

Проверь:
1. language `ru`/`ua`;
2. права `storeassist >= R`;
3. `OnPrologAdminTitle` registered;
4. page id в whitelist;
5. если реальная admin page не совпадает с task id — передаётся `pageid` в URL;
6. copied `/bitrix/panel/storeassist/storeassist.css` и JS extension.

### Пользователь думает, что `storeassist_1c_*` выполняет обмен

Объясняй: это onboarding/static pages. Для реального exchange проверяются:
- `catalog.import.1c` / `catalog.export.1c`;
- `sale.export.1c`;
- `/bitrix/admin/1c_admin.php`;
- `/bitrix/admin/1c_exchange.php`;
- `b_sale_exchange_log`, temp files, sessions, `BX_CML2_IMPORT` / `BX_CML2_EXPORT`.

## Что нельзя делать

- Не чинить реальный 1С import/export в `storeassist_1c_*` страницах: там нет exchange engine.
- Не считать `storeassist_settings` бизнес-статусом магазина — это только чеклист мастера.
- Не использовать `AgentCountDayOrders()` как аналитический отчёт продаж: это грубый indicator для progress widget.
- Не открывать внешние doc/help URLs как source of truth, если есть локальный core. Для поведения модуля приоритет у files выше.
- Не активировать `storeassist` route в другом проекте без проверки `www/bitrix/modules/storeassist`.
