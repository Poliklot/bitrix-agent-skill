# Магазин, витрина и кросс-доменные workflow

> Truth layer: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core`. Подтверждены `catalog` 25.550.0, `sale` 26.0.0, `currency` 26.0.0, `bitrix.eshop` 25.0.0, `pull`, `bizproc`, `sender`, `storeassist`, компоненты `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`, storefront components `sale.*`, admin catalog/store/productcard components. Этот файл больше не deferred для shop-core-аудита, но в каждом проекте сначала проверяй наличие модулей.

## 1. Порядок чтения проекта

Для магазинных задач сначала смотри живой код проекта:

1. `www/bitrix/modules/main/classes/general/version.php` или `www/bitrix/modules/<module>/install/version.php`
2. `www/bitrix/modules/catalog/lib/`, `www/bitrix/modules/sale/lib/`, `www/bitrix/modules/currency/lib/`
3. `www/bitrix/modules/<module>/install/components/bitrix/<component>/`
4. `www/bitrix/admin/1c_import.php`, `1c_exchange.php`, `sale_exchange_log.php` и реальные module-admin файлы
5. `local/components/<vendor>/<component>/`
6. `local/templates/<site>/components/bitrix/<component>/`
7. `local/php_interface/`, `local/modules/`, `urlrewrite.php`

Минимальный модульный gate:

```bash
for m in iblock currency catalog sale; do
  test -d "www/bitrix/modules/$m" && echo "OK $m" || echo "MISS $m"
done
```

Если `catalog`, `sale` или `currency` отсутствуют — не веди задачу как полноценный интернет-магазин.

## 2. Карта слоёв магазина

| Слой | Что лежит здесь | Reference |
|---|---|---|
| Контентный | ИБ, разделы, элементы, свойства, UF, файлы, XML_ID | `iblocks.md`, `entities-migrations.md`, `import-export.md` |
| Catalog | товар, offer, цена, тип цены, остаток, склад, measure, VAT | `catalog.md`, `currency.md` |
| Sale | basket, order, shipment, payment, discount, coupon, person type, locations | `sale.md`, `users.md`, `validation.md` |
| 1С / CommerceML | `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`, `BX_CML2_*` | `commerce-1c-integration.md` |
| Витрина | complex catalog, list/detail, smart filter, SKU JS, basket line, checkout | `components.md`, `templates.md`, `component-dataflow-debugging.md` |
| Индексы/кеш | component/tagged/managed/cache, facet, search, composite, SEO | `cache-infra.md`, `index-cache-diagnostics.md`, `search.md`, `seo-cache-access.md` |
| Ops | agents, cron, stepper, import queues, logs, perf, backup | `operations-runbook.md`, `update-stepper.md`, `perfmon.md` |

## 3. Как выбирать точку изменения

### Модель товара / SKU / свойства

1. Проверить iblock и offers iblock.
2. Проверить `CCatalogSKU::GetInfoByProductIBlock()`.
3. Проверить, где живёт цена/остаток: parent product или offer.
4. Для повторяемого изменения писать migration/install step/CLI, а не клик в админке.
5. Для 1С учитывать `XML_ID` и `CML2_LINK`.

### Цена / валюта / скидка

1. `currency.md`: базовая валюта, формат, курс.
2. `catalog.md`: `b_catalog_price`, `CATALOG_GROUP_ID`, права типа цены.
3. `sale.md`: скидки, купоны, финальный расчёт basket/order.
4. Кеш компонента и managed cache.

### Остатки / склады / доступность

1. Общий `b_catalog_product.QUANTITY`.
2. Складской `b_catalog_store_product.AMOUNT`.
3. Reservation из sale/order/basket.
4. Store documents/batches/barcodes, если включён складской учёт.
5. `CAN_BUY_ZERO`, `QUANTITY_TRACE`, availability.

### Корзина / checkout / заказ

1. `sale.md`: `Fuser`, `Basket`, provider, `Order` object graph.
2. Проверить component: `sale.basket.*`, `sale.order.ajax`, `sale.order.checkout`, `sale.order.full`.
3. Проверить person type, свойства заказа, delivery/payment restrictions.
4. Проверить order save result и event handlers.
5. Проверить side effects: stock reservation, mail, sender, cashbox, exchange.

### Обмен с 1С

1. Определить поток: catalog import, catalog export, sale exchange.
2. Проверить `checkauth → init → file → import`.
3. Проверить session/cookies/sessid/secure exchange.
4. Проверить temp files, zip, chunk upload, PHP limits.
5. Проверить mapping XML_ID/CML2_LINK/price type/store.
6. Проверить post-import indexes/cache.
7. Для orders проверить `b_sale_exchange_log`, критерии выгрузки, обратные документы.

## 4. Diagnostic routes

### “В админке товар есть, на сайте нет”

```text
iblock entity
→ section/site/activity/rights
→ catalog row/type/SKU
→ price/currency/price group rights
→ stock/availability
→ component params/filter/select
→ result_modifier/template/SKU JS
→ component/tagged/facet/search/composite cache
→ SEF/urlrewrite/SEO
```

### “Товар виден, но не покупается”

```text
product vs offer ID
→ catalog provider
→ accessible price
→ stock/reservation/can-buy-zero
→ basket item creation
→ sale events/validators
→ AJAX response/template
```

### “Checkout разваливается”

```text
basket refresh
→ person type
→ required order props
→ location/delivery restrictions
→ payment restrictions
→ discounts/coupons
→ order save errors
→ event handlers
→ mail/payment/cashbox/exchange side effects
```

### “1С выгрузила, но данные не обновились”

```text
checkauth/session
→ init limits/zip
→ file upload/temp dir
→ import XML step
→ XML_ID mapping
→ product/offer/price/store tables
→ custom event handlers
→ indexes/cache
```

## 5. Components map

Catalog/admin:

- `catalog.product.grid`, `catalog.productcard.details`, `catalog.productcard.variation.grid`, `catalog.productcard.store.amount*`;
- `catalog.store.*`, `catalog.store.document.*`;
- `catalog.report.store_*`;
- `catalog.import.1c`, `catalog.export.1c`.

Sale/storefront:

- `sale.basket.basket`, `sale.basket.basket.line`, `sale.basket.basket.small`, `sale.basket.order.ajax`;
- `sale.order.ajax`, `sale.order.checkout`, `sale.order.full`;
- `sale.personal.order*`, `sale.personal.profile*`, `sale.personal.account`, `sale.personal.section`;
- `sale.order.payment*`, `sale.account.pay`, `sale.delivery.request*`, `sale.location.*`;
- `sale.export.1c`.

Currency:

- `currency.field.money`, `currency.money.input`, `currency.rates`.

Всегда читай `.parameters.php`, `component.php/class.php`, `templates/*`, затем project override.

## 6. Что проговаривать в ответе

Для любой кросс-доменной shop-задачи явно укажи:

- какие модули и версии подтверждены;
- product vs offer ID;
- где цена, валюта, остаток и доступность;
- какой компонент и template участвуют;
- какие order/basket side effects есть;
- какие кеши/индексы надо обновить;
- есть ли 1С/CommerceML или внешний sync;
- что можно менять кодом, а что требует подтверждения как data mutation.

## 7. Safety

- Не меняй production catalog/sale данные без подтверждения.
- Не подключай реальную 1С, платежи, доставки, кассы без подтверждения.
- Не делай прямой SQL для order/basket/payment/shipment/product price/stock, если есть API и side effects.
- Не удаляй XML_ID/CML2_LINK без плана миграции обмена.
- Не чисти глобально все кеши первым действием; определи слой.
- Не используй один shop-core как универсальную истину для всех версий: всегда перепроверяй локальный проект.
