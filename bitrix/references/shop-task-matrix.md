# Shop task matrix — routing интернет-магазина

> Используй этот файл как быстрый роутер для задач по интернет-магазину. Truth layer для нового этапа: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core` с 49 подтверждёнными модулями. Полный inventory и coverage status смотри в `shop-core-module-inventory.md`.

## 1. Быстрый routing

| Запрос пользователя | Сначала читать | Затем |
|---|---|---|
| “Все ли модули магазина/1С покрыты?” | `shop-core-module-inventory.md`, `runtime-smoke-verification.md` | `core-audit-matrix.md`, затем нужный deep-reference; code-first coverage ≠ runtime pass |
| Товары, свойства, разделы, SKU | `catalog.md`, `shop-standard-components.md`, `iblocks.md` | `commerce-1c-integration.md`, если есть 1С/XML_ID |
| Цена не та / не показывается | `catalog.md`, `currency.md` | `sale.md`, `search-seo-ops` bundles для кеша |
| Остатки, склады, доступность | `catalog.md`, `shop-standard-components.md` | `sale.md` для reservation/order effects |
| Корзина не работает | `shop-standard-components.md`, `sale.md`, `catalog.md` | `components.md`, `events-routing.md` |
| Checkout / оформление заказа | `shop-standard-components.md`, `sale.md` | `users.md`, `validation.md`, `templates.md` |
| Оплата / callback | `sale.md` | `http.md`, `events-routing.md`, cashbox section в `sale.md` |
| Доставка / locations | `shop-standard-components.md`, `sale.md`, `location.md` | `components.md`, `validation.md` |
| Скидки / купоны | `sale.md`, `catalog.md` | `currency.md` |
| 1С выгрузка товаров | `commerce-1c-integration.md`, `catalog.md` | `currency.md`, `cache-infra.md` |
| Заказы в 1С | `commerce-1c-integration.md`, `sale.md` | `http.md`, `operations-runbook.md` |
| StoreAssist / мастер настройки 1С | `storeassist.md`, `shop-standard-components.md`, `shop-core-module-inventory.md` | `commerce-1c-integration.md` для реального exchange |
| Рассылки, follow-up, маркетинг | `shop-marketing-analytics.md` | `mail-notifications.md`, `messageservice.md`, `sale.md` |
| Форма подписки / отписка | `shop-marketing-analytics.md`, `subscribe.md` | `userconsent.md`, `mail-notifications.md` |
| SMS / message provider / лимиты | `shop-marketing-analytics.md`, `messageservice.md` | REST/provider config, `mail-notifications.md` |
| Баннеры, A/B, conversion, reports, statistic | `shop-marketing-analytics.md` | `templates.md`, `seo-cache-access.md`, `perfmon.md` |
| Автоматизация заказа / роботы | `shop-automation-bizproc.md`, `sale.md` | проверить локальный order provider/CRM/custom module перед обещанием sale robots |
| Бизнес-процесс / задание / шаблон не стартует | `shop-automation-bizproc.md`, `workflow.md` | `iblocks.md`, `lists` section, permissions |
| Процессы в списках | `shop-automation-bizproc.md`, `workflow.md`, `iblocks.md` | list rights, `BIZPROC=Y`, `CLists::isBpFeatureEnabled` |
| Realtime / pull / push в автоматизации | `shop-automation-bizproc.md`, `push-pull.md` | pull server config, channels/watches |
| `webservice.sale` / SOAP order stats | `shop-integrations-webservice.md`, `sale.md` | это не 1С и не order CRUD; проверить WSDL, sale rights, date/status filters |
| `webservice.statistic` / SOAP traffic stats | `shop-integrations-webservice.md`, `shop-marketing-analytics.md` | `statistic` rights, traffic tables, `STAT_LIST_TOP_SIZE` |
| REST sale/catalog app hooks, webhooks, placements | `shop-integrations-webservice.md`, `rest.md` | `methods`/`method.get`, scopes, `b_rest_event`, `b_rest_placement` |
| “В админке есть, на сайте нет” для товара | `shop-standard-components.md`, `catalog.md`, `diagnostic-visibility.md` | `index-cache-diagnostics.md`, `component-dataflow-debugging.md` |
| Вторая страница каталога пустая, lazy load сломан | `pagination.md`, `shop-standard-components.md`, `catalog.md`, `component-dataflow-debugging.md` | `sef-urls.md`, `cache-infra.md` |
| Производительность каталога | `catalog.md`, `perfmon.md`, `cache-infra.md` | `search.md`, `seo-cache-access.md` |
| Production-safe план доработки магазина | `production-best-practices.md`, `shop-task-matrix.md` | конкретные `catalog.md`/`sale.md`/`commerce-1c-integration.md`/`shop-integrations-webservice.md` |
| Подводные камни checkout/order/1С/REST | `pitfalls-matrix.md` | затем профильный shop reference |
| Runtime smoke магазина | `runtime-smoke-verification.md` | `catalog.md`, `sale.md`, `commerce-1c-integration.md`, `shop-integrations-webservice.md` |

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
3. `component`: open `shop-standard-components.md`, then params, filter, selected price types, offers props.
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
7. Component AJAX template and JS (`shop-standard-components.md` → stock template/project override).

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

Полный формат runtime verification смотри в `runtime-smoke-verification.md`; ниже только короткий shop-набор.

Первым запускать **пакет 1** из `runtime-smoke-verification.md`: каталог → SKU/цены/остатки → корзина/заказ. Минимальная матрица пакета:

| ID | Проверка |
|---|---|
| P1-01 | preflight modules/PHP/DB/site/template |
| P1-02 | public catalog list/detail |
| P1-03 | price/currency/stock |
| P1-04 | SKU/offer selection |
| P1-05 | guest basket |
| P1-06 | auth basket |
| P1-07 | checkout/order save в test mode |
| P1-08 | second request/cache pass |

Дальше по очереди:

- `P2 CommerceML`: `checkauth`, `init`, `file`, catalog `import`, repeated import, broken XML, order export;
- `P3 REST/webservice`: method discovery, missing scope, sale/catalog events, `webservice.sale`, `webservice.statistic`;
- `P4 marketing/automation/realtime`: sender/subscription, mail/SMS stubs, banner/conversion/report/statistic, bizproc/list task, pull/realtime.

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
