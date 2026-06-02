# Shop task matrix — routing интернет-магазина

> Используй этот файл как быстрый роутер для задач по интернет-магазину. Truth layer для нового этапа: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core` с 49 подтверждёнными модулями. Полный inventory и coverage status смотри в `shop-core-module-inventory.md`.

## 1. Быстрый routing

| Запрос пользователя | Сначала читать | Затем |
|---|---|---|
| “Все ли модули магазина/1С покрыты?” | `shop-core-module-inventory.md` | `core-audit-matrix.md`, затем нужный deep-reference |
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
| StoreAssist / мастер настройки 1С | `shop-core-module-inventory.md`, `commerce-1c-integration.md` | будущий `storeassist.md` |
| Рассылки, follow-up, маркетинг | `shop-core-module-inventory.md`, `mail-notifications.md`, `messageservice.md` | будущий `shop-marketing-analytics.md` |
| Автоматизация заказа / роботы | `shop-core-module-inventory.md`, `workflow.md`, `sale.md` | будущий `shop-automation-bizproc.md` |
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
