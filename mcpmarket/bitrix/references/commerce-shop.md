# Commerce Shop
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `catalog.md`

# Торговый каталог — `catalog` 25.550.0

> Truth layer: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core`, модуль `catalog` версии `25.550.0` (`install/version.php`, дата `2026-02-17`). В этом core `catalog`, `sale`, `currency`, `bitrix.eshop`, `pull`, `bizproc`, `storeassist` реально присутствуют. Этот файл больше не deferred для shop-core-аудита, но в каждом клиентском проекте всё равно сначала проверяй `www/bitrix/modules/catalog`.

## 0. Обязательная проверка перед catalog-задачей

```bash
test -d www/bitrix/modules/catalog && sed -n '1,40p' www/bitrix/modules/catalog/install/version.php
find www/bitrix/modules/catalog/install/components/bitrix -maxdepth 1 -type d | sort
find local/components bitrix/templates local/templates -maxdepth 4 -type d 2>/dev/null | rg 'catalog|sale'
```

```php
use Bitrix\Main\Loader;

foreach (['iblock', 'currency', 'catalog'] as $module) {
    if (!Loader::includeModule($module)) {
        throw new \RuntimeException("Module {$module} is not installed");
    }
}
```

Проверенный shop-core содержит стандартные catalog-компоненты: `catalog.import.1c`, `catalog.export.1c`, `catalog.product.grid`, `catalog.productcard.*`, `catalog.store.*`, `catalog.store.document.*`, `catalog.report.store_*`, `catalog.product.subscribe*`, `catalog.viewed.products`, `currency.field.money`, `currency.money.input`, `currency.rates`.

## 1. Модель данных catalog

Catalog живёт поверх `iblock`, но коммерческие данные лежат в собственных таблицах:

| Слой | Таблицы / файлы | Что проверять |
|---|---|---|
| Привязка catalog к ИБ | `b_catalog_iblock`, `Bitrix\Catalog\CatalogIblockTable`, `CCatalogSKU` | `PRODUCT_IBLOCK_ID`, offers iblock, `SKU_PROPERTY_ID`, `YANDEX_EXPORT` |
| Товар | `b_catalog_product`, `Bitrix\Catalog\ProductTable`, `Bitrix\Catalog\Model\Product` | тип товара, количество, резерв, вес, VAT, quantity trace |
| Цена | `b_catalog_price`, `Bitrix\Catalog\PriceTable`, `Bitrix\Catalog\Model\Price` | тип цены, валюта, quantity range, base price |
| Тип цены | `b_catalog_group`, `b_catalog_group_lang`, `Bitrix\Catalog\GroupTable` | базовая цена, права групп, язык/название |
| SKU/offers | `CCatalogSKU`, `Bitrix\Catalog\Product\Sku`, свойство `CML2_LINK` | связь offer → product, отдельные цены/остатки offer |
| Остатки | `b_catalog_store`, `b_catalog_store_product`, `StoreTable`, `StoreProductTable` | складской остаток vs общий `QUANTITY` |
| Складские документы | `b_catalog_store_docs`, `b_catalog_docs_element`, `Storedocument*Table` | приход/расход/перемещение, batch, barcode |
| Единицы | `b_catalog_measure`, `b_catalog_measure_ratio`, `MeasureTable`, `MeasureRatioTable` | базовая единица, коэффициент продажи |
| НДС | `b_catalog_vat`, `VatTable` | ставка, включённость в цену |
| Скидки catalog | `b_catalog_discount*`, `Discount*` | legacy/catalog discounts, связь с sale discounts |
| Доступ | `b_catalog_role`, `b_catalog_permission` | catalog RBAC отдельно от iblock rights |

Не путай `iblock`-активность (`ACTIVE`, `ACTIVE_FROM/TO`, права разделов) с коммерческой доступностью (`QUANTITY`, `CAN_BUY_ZERO`, `AVAILABLE`, `SUBSCRIBE`, складские остатки).

## 2. Товар, offer и тип продукта

В этом core есть D7-слой `Bitrix\Catalog\ProductTable`, `Bitrix\Catalog\Model\Product`, `Bitrix\Catalog\Product\Sku`, но стандартные компоненты и старые обмены всё ещё часто идут через legacy `CCatalogProduct`, `CCatalogSKU`, `CIBlockElement`.

```php
use Bitrix\Catalog\ProductTable;

$product = ProductTable::getRow([
    'select' => ['ID', 'TYPE', 'QUANTITY', 'QUANTITY_RESERVED', 'AVAILABLE', 'CAN_BUY_ZERO', 'WEIGHT'],
    'filter' => ['=ID' => $productId],
]);
```

Типы не хардкодь по памяти: проверяй константы в `ProductTable` текущего ядра. Для диагностики SKU сначала найди offers-ИБ:

```php
$skuInfo = \CCatalogSKU::GetInfoByProductIBlock($productIblockId);
if ($skuInfo) {
    $offersIblockId = (int)$skuInfo['IBLOCK_ID'];
    $skuPropertyId = (int)$skuInfo['SKU_PROPERTY_ID'];
}
```

Для 1С-связки критичны `XML_ID`, external IDs и свойство offer → product. В шаблонах sale встречается фильтрация свойства `CML2_LINK`, поэтому не удаляй/не переименовывай это свойство без аудита обмена.

## 3. Цены и типы цен

Цены требуют модуля `currency`; валюта лежит в `b_catalog_currency*`, сами цены — в `b_catalog_price`.

```php
use Bitrix\Catalog\PriceTable;
use Bitrix\Catalog\GroupTable;

$prices = PriceTable::getList([
    'select' => ['ID', 'PRODUCT_ID', 'CATALOG_GROUP_ID', 'PRICE', 'CURRENCY', 'QUANTITY_FROM', 'QUANTITY_TO'],
    'filter' => ['=PRODUCT_ID' => $productId],
    'order' => ['CATALOG_GROUP_ID' => 'ASC', 'QUANTITY_FROM' => 'ASC'],
]);

$priceTypes = GroupTable::getList([
    'select' => ['ID', 'NAME', 'BASE', 'SORT'],
    'order' => ['SORT' => 'ASC'],
]);
```

Для витрины не показывай “первую попавшуюся” цену. Проверяй:

1. какие `CATALOG_GROUP_ID` переданы в компонент;
2. права группы пользователя на тип цены (`b_catalog_group2group`, `b_catalog_product2group`);
3. quantity range;
4. валюту и форматирование;
5. скидки `sale`/`catalog`, если цена выводится через компонент.

Для записи цены предпочитай D7 `PriceTable::add/update`, но перед боевым изменением проговаривай обратимость и чисть зависимые кеши.

## 4. Остатки, склады и availability

Общий остаток товара: `ProductTable::QUANTITY`. Складские остатки: `StoreProductTable` / `b_catalog_store_product`.

```php
use Bitrix\Catalog\StoreProductTable;

$rows = StoreProductTable::getList([
    'select' => ['STORE_ID', 'PRODUCT_ID', 'AMOUNT', 'STORE_TITLE' => 'STORE.TITLE'],
    'filter' => ['=PRODUCT_ID' => $productId],
]);
```

После ручной правки складского остатка не забывай пересчёт товара:

```php
\CCatalogProduct::recalcQuantityProduct($productId);
```

Для задач “товар виден, но не покупается” проверяй вместе:

- `ACTIVE` элемента и раздела;
- `TYPE` товара: простой/parent SKU/offer;
- цена доступна текущей группе;
- `QUANTITY`, `QUANTITY_RESERVED`, `CAN_BUY_ZERO`, `QUANTITY_TRACE`;
- есть ли активный offer с ценой и остатком;
- не ломает ли `CatalogProvider` добавление в basket;
- кеш catalog-компонента и managed/tagged cache.

## 5. Складские документы, batch, barcode

В shop-core есть `catalog.store.document.*` компоненты и таблицы `b_catalog_store_docs`, `b_catalog_docs_element`, `b_catalog_store_batch`, `b_catalog_store_barcode`, `b_catalog_docs_barcode`. Для задач по складам не своди всё к `QUANTITY`.

Проверяй:

- включён ли складской учёт в настройках catalog;
- тип документа: приход, расход, перемещение, списание;
- contractor (`b_catalog_contractor`);
- batch/barcode, если используются партии или маркировка;
- пересчёт общего остатка и reserved quantity.

## 6. Standard components и admin UI

Подтверждённые component families в shop-core:

- импорт/экспорт: `catalog.import.1c`, `catalog.export.1c`, `catalog.import.hl`;
- карточка/грид товара: `catalog.product.grid`, `catalog.productcard.details`, `catalog.productcard.variation.grid`, `catalog.productcard.variation.details`, `catalog.grid.product.field`;
- склады: `catalog.store.*`, `catalog.store.document.*`, `catalog.productcard.store.amount*`;
- отчёты: `catalog.report.store_*`;
- подписки/viewed/recommended: `catalog.product.subscribe*`, `catalog.viewed.products`, `catalog.bigdata.products`.

Для стандартного компонента всегда читай:

1. `.description.php`;
2. `.parameters.php`;
3. `component.php` / `class.php`;
4. `templates/*`;
5. project override в `local/templates/.../components/bitrix/...`.

Если проблема в page 2, “Показать ещё”, infinite scroll или `PAGEN_<NavNum>` у `catalog.section`, дополнительно открывай `pagination.md`: stock templates текущего shop-core отправляют следующую страницу через `PAGEN_` + `NavNum` и зависят от актуальных `navParams`, cache key, filter и sort.

## 7. CommerceML и 1С

Catalog-часть обмена подтверждена через `catalog.import.1c` и `catalog.export.1c`. Детали маршрутизируй в `commerce-1c-integration.md`.

Ключевые режимы `catalog.import.1c/component.php`: `mode=checkauth`, `mode=init`, `mode=file`, `mode=import`; сессия `$_SESSION['BX_CML2_IMPORT']`; `sessid` и проверка источника. Для экспорта каталога аналогично смотри `catalog.export.1c`.

## 8. Диагностика типовых catalog-багов

### 1С выгрузила товар, но его нет на сайте

1. Найди элемент по `XML_ID`/external ID в iblock.
2. Проверь `ACTIVE`, section binding, site binding, права.
3. Проверь `b_catalog_product` для element ID.
4. Если это offer — проверь связь `CML2_LINK` / `SKU_PROPERTY_ID`.
5. Проверь цену в нужном `CATALOG_GROUP_ID` и валюту.
6. Проверь остатки и `AVAILABLE`.
7. Пересобери search/facet index и очисти component/tagged cache.

### Цена не обновилась

1. Убедись, что обновлялся product ID нужного offer, а не parent product.
2. Проверь `CATALOG_GROUP_ID`, quantity range и `CURRENCY`.
3. Проверь права текущей группы на тип цены.
4. Проверь, не применена ли скидка sale/catalog.
5. Проверь кеш компонента и managed cache.

### Остаток не совпадает

1. Разведи общий `b_catalog_product.QUANTITY` и складской `b_catalog_store_product.AMOUNT`.
2. Проверь reserved quantity через sale/basket/order.
3. Проверь складские документы, если включён складской учёт.
4. Запусти безопасный пересчёт, а не прямую SQL-правку.

## 9. Что не делать

- Не считать наличие `catalog.*` компонента внутри `iblock` доказательством установленного `catalog` в чужом проекте.
- Не писать цены/остатки прямым SQL, если можно использовать table/model/API и пересчёт.
- Не смешивать parent product и offer: цена/остаток часто живут на offer.
- Не чистить весь `/bitrix/cache` как первый шаг; сначала определи component/tagged/managed/facet/search слой.
- Не подключать production 1С или реальные платежи для smoke без явного подтверждения пользователя.

---

## Source: `sale.md`

# Sale — корзина, заказ, оплата, доставка (`sale` 26.0.0)

> Truth layer: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core`, модуль `sale` версии `26.0.0` (`install/version.php`, дата `2026-01-12`). В этом core `sale`, `catalog`, `currency`, `pull`, `bizproc`, `sender` присутствуют. В каждом проекте сначала проверяй наличие `www/bitrix/modules/sale` и конкретных компонентов.

## 0. Обязательная проверка перед sale-задачей

```bash
test -d www/bitrix/modules/sale && sed -n '1,40p' www/bitrix/modules/sale/install/version.php
find www/bitrix/modules/sale/install/components/bitrix -maxdepth 1 -type d | sort | rg '^.*/sale\.'
find www/bitrix/modules/sale/lib -maxdepth 2 -type f | sort | sed -n '1,120p'
```

```php
use Bitrix\Main\Loader;

foreach (['sale', 'catalog', 'currency'] as $module) {
    if (!Loader::includeModule($module)) {
        throw new \RuntimeException("Module {$module} is not installed");
    }
}
```

## 1. D7 object graph

```text
Order
├── Basket / BasketItem
├── PropertyCollection / PropertyValue
├── ShipmentCollection / Shipment / ShipmentItemCollection
├── PaymentCollection / Payment
├── Discount / OrderDiscount
├── Tax / Location / PersonType
└── Status lifecycle + history/change log
```

Подтверждённые классы/файлы:

- `Bitrix\Sale\Order` — `sale/lib/order.php`;
- `Bitrix\Sale\Basket`, `BasketItem`, `Fuser` — `sale/lib/basket*.php`, `sale/lib/fuser.php`;
- `Shipment`, `ShipmentCollection`, `ShipmentItemCollection` — `sale/lib/shipment*.php`;
- `Payment`, `PaymentCollection` — `sale/lib/payment*.php`;
- `Discount`, `OrderDiscount`, `OrderDiscountManager` — `sale/lib/discount.php`, `orderdiscount*.php`;
- `OrderStatus`, `DeliveryStatus`, `StatusBase` — `sale/lib/*status*.php`;
- `Location\*` — `sale/lib/location/*`;
- `Cashbox\*` — `sale/lib/cashbox/*`;
- exchange/1C — `sale/lib/exchange/*`, `sale/lib/exchange/onec/*`.

## 2. Главные таблицы

| Слой | Таблицы |
|---|---|
| Посетитель/корзина | `b_sale_fuser`, `b_sale_basket`, `b_sale_basket_props`, `b_sale_basket_reservation`, `b_sale_basket_reservation_history` |
| Заказ | `b_sale_order`, `b_sale_order_props*`, `b_sale_order_history`, `b_sale_order_change`, `b_sale_order_entities_custom_fields` |
| Отгрузки | `b_sale_order_delivery`, `b_sale_order_dlv_basket`, `b_sale_order_delivery_req*` |
| Оплаты | `b_sale_order_payment`, `b_sale_order_payment_item`, `b_sale_pay_system_action`, `b_sale_pay_system_err_log` |
| Скидки | `b_sale_discount*`, `b_sale_order_discount`, `b_sale_order_coupons`, `b_sale_order_rules*` |
| Статусы | `b_sale_status`, `b_sale_status_lang`, `b_sale_status_group_task` |
| Локации | `b_sale_location*`, `b_sale_loc_*`, `b_sale_location_group*` |
| Профили | `b_sale_user_props`, `b_sale_user_props_value`, `b_sale_person_type*` |
| 1С/exchange | `b_sale_export`, `b_sale_exchange_log`, `b_sale_synchronizer_log`, `b_sale_bizval_code_1c` |
| Кассы | `b_sale_cashbox*`, `b_sale_check*`, `b_sale_check_related_entities` |

## 3. Корзина

```php
use Bitrix\Sale\Basket;
use Bitrix\Sale\Fuser;

$basket = Basket::loadItemsForFUser(Fuser::getId(), SITE_ID);
$item = $basket->createItem('catalog', $productId);
$item->setFields([
    'QUANTITY' => 1,
    'CURRENCY' => \Bitrix\Currency\CurrencyManager::getBaseCurrency(),
    'LID' => SITE_ID,
    'PRODUCT_PROVIDER_CLASS' => \CCatalogProductProvider::class,
]);

$result = $basket->save();
if (!$result->isSuccess()) {
    throw new \RuntimeException(implode('; ', $result->getErrorMessages()));
}
```

Для production-кода не заполняй `PRICE` вручную без причины: provider/catalog должен пересчитать цену, доступность, вес и скидки. Если создаёшь service-layer, отдели:

- получение/создание `Fuser`;
- добавление item;
- refresh/recalculate;
- сохранение;
- обработку `Result/Error`.

## 4. Создание заказа

```php
use Bitrix\Sale\Order;
use Bitrix\Sale\Basket;
use Bitrix\Sale\Delivery;
use Bitrix\Sale\PaySystem;

$order = Order::create(SITE_ID, $userId);
$order->setPersonTypeId($personTypeId);
$order->setBasket(Basket::loadItemsForFUser(\Bitrix\Sale\Fuser::getId(), SITE_ID));

$propertyCollection = $order->getPropertyCollection();
$email = $propertyCollection->getUserEmail();
if ($email) {
    $email->setValue($userEmail);
}

$shipmentCollection = $order->getShipmentCollection();
$shipment = $shipmentCollection->createItem();
$delivery = Delivery\Services\Manager::getById($deliveryId);
$shipment->setFields([
    'DELIVERY_ID' => $delivery['ID'],
    'DELIVERY_NAME' => $delivery['NAME'],
    'CURRENCY' => $order->getCurrency(),
]);

foreach ($order->getBasket() as $basketItem) {
    $shipmentItem = $shipment->getShipmentItemCollection()->createItem($basketItem);
    $shipmentItem->setQuantity($basketItem->getQuantity());
}

$payment = $order->getPaymentCollection()->createItem();
$paySystem = PaySystem\Manager::getObjectById($paySystemId);
$payment->setFields([
    'PAY_SYSTEM_ID' => $paySystem->getField('ID'),
    'PAY_SYSTEM_NAME' => $paySystem->getField('NAME'),
    'SUM' => $order->getPrice(),
    'CURRENCY' => $order->getCurrency(),
]);

$result = $order->save();
```

Перед сохранением заказа проверь совместимость:

- `PERSON_TYPE_ID` ↔ свойства заказа;
- служба доставки ↔ location/person type/состав корзины;
- платёжная система ↔ person type/site/currency/sum;
- final basket refresh;
- обработчики `sale` events.

## 5. Статусы, оплата, отгрузка

```php
$order = \Bitrix\Sale\Order::load($orderId);
$order->setField('STATUS_ID', 'P');

foreach ($order->getPaymentCollection() as $payment) {
    $payment->setPaid('Y');
}

foreach ($order->getShipmentCollection() as $shipment) {
    if (!$shipment->isSystem()) {
        $shipment->setField('DEDUCTED', 'Y');
    }
}

$result = $order->save();
```

Не меняй `b_sale_order.STATUS_ID`, `PAYED`, `DEDUCTED` прямым SQL: потеряешь events, history, exchange flags, reservation/cashbox side effects.

## 6. Standard components

Подтверждённые storefront/account components:

- корзина: `sale.basket.basket`, `sale.basket.basket.line`, `sale.basket.basket.small`, `sale.basket.order.ajax`;
- оформление: `sale.order.ajax`, `sale.order.checkout`, `sale.order.full`;
- оплата: `sale.order.payment`, `sale.order.payment.change`, `sale.order.payment.receive`, `sale.account.pay`;
- личный кабинет: `sale.personal.order*`, `sale.personal.profile*`, `sale.personal.account`, `sale.personal.section`, `sale.personal.subscribe*`;
- доставка/локации: `sale.ajax.delivery.calculator`, `sale.location.*`, `sale.store.choose`, `sale.delivery.request*`;
- подарки/рекомендации: `sale.gift.*`, `sale.products.gift*`, `sale.recommended.products`;
- 1С: `sale.export.1c`.

Для checkout-багов всегда читай `.parameters.php`, `class.php/component.php`, `templates/*`, затем project template override.

## 7. Events и side effects

Sale-задачи почти всегда имеют побочные эффекты:

- reservation и доступный остаток catalog;
- скидки и купоны;
- почтовые события и sender triggers;
- payment callbacks;
- delivery requests;
- cashbox/check generation;
- exchange log и 1С-синхронизация;
- order history/change log;
- managed cache, personal account pages, basket line AJAX.

При изменении order lifecycle проговаривай, какие side effects нужны, а какие нельзя запускать.

## 8. 1С exchange для заказов

Маршрутизируй в `commerce-1c-integration.md`. В shop-core подтверждены:

- компонент `sale.export.1c`;
- admin entrypoint `/bitrix/admin/1c_exchange.php`;
- `/bitrix/admin/sale_exchange_log.php`;
- `sale/lib/exchange/*`, `sale/lib/exchange/onec/*`;
- таблицы `b_sale_exchange_log`, `b_sale_synchronizer_log`, `b_sale_bizval_code_1c`.

Ключевые режимы `sale.export.1c/component.php`: `mode=checkauth`, `mode=init`, `mode=file`, `mode=import`; сессия `$_SESSION['BX_CML2_EXPORT']`; `secure_1c_exchange`; `sessid`; zip/unzip; `last_xml_entry` для продолжения импорта.

## 9. Диагностика sale-багов

### Товар не добавляется в корзину

1. Проверь catalog product/offer, цену, остаток, provider.
2. Проверь `Fuser::getId()` и site ID.
3. Проверь `PRODUCT_PROVIDER_CLASS` и `MODULE` item.
4. Проверь sale basket component AJAX и CSRF/session.
5. Проверь event handlers, которые валидируют basket item.

### Checkout не создаёт заказ

1. Проверь `PERSON_TYPE_ID` и обязательные свойства.
2. Проверь location и delivery restrictions.
3. Проверь payment system restrictions.
4. Проверь basket refresh и coupons.
5. Проверь ошибки `$result->getErrorMessages()` от `Order::save()`.
6. Проверь component template и AJAX response.

### Заказ создан, но не уходит в 1С

1. Проверь настройки компонента `sale.export.1c` и группы доступа.
2. Проверь `b_sale_exchange_log` / `/bitrix/admin/sale_exchange_log.php`.
3. Проверь `DATE_UPDATE`, статус, оплату/отгрузку и критерии выгрузки.
4. Проверь `secure_1c_exchange`, `sessid`, cookies/session.
5. Проверь временные файлы `upload/1c_exchange` или temp-dir.

## 10. Что не делать

- Не писать заказ/оплату/отгрузку прямым SQL.
- Не создавать заказ без финального refresh basket/order.
- Не считать, что `sale.order.ajax` и `sale.order.checkout` имеют одинаковый контракт: проверяй конкретный component.
- Не подключать real pay systems/delivery/1С для smoke без явного подтверждения.
- Не игнорировать user/person type/site restrictions.

---

## Source: `currency.md`

# Currency — валюты, курсы и денежные поля (`currency` 26.0.0)

> Truth layer: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core`, модуль `currency` версии `26.0.0` (`install/version.php`, дата `2026-02-24`). Используй этот файл для цен catalog, сумм sale, форматирования денег, курсов и UF/property money fields.

## 1. Проверка модуля

```bash
test -d www/bitrix/modules/currency && sed -n '1,60p' www/bitrix/modules/currency/install/version.php
find www/bitrix/modules/currency -maxdepth 3 -type f | sort
```

```php
use Bitrix\Main\Loader;

if (!Loader::includeModule('currency')) {
    throw new \RuntimeException('Module currency is not installed');
}
```

## 2. Подтверждённые классы

`currency/autoload.php` регистрирует:

- legacy: `CCurrency`, `CCurrencyLang`, `CCurrencyRates`;
- D7: `Bitrix\Currency\CurrencyManager`, `CurrencyTable`, `CurrencyLangTable`, `CurrencyRateTable`, `CurrencyClassifier`;
- UI/fields: `Bitrix\Currency\UserField\Money`, components `currency.field.money`, `currency.money.input`, `currency.rates`;
- iblock integration: `lib/integration/iblockmoneyproperty.php`.

## 3. Таблицы

- `b_catalog_currency` — валюта, базовые настройки;
- `b_catalog_currency_lang` — форматирование и названия по языкам;
- `b_catalog_currency_rate` — курсы.

Исторически таблицы имеют префикс `b_catalog_*`, но модуль отдельный: `currency`.

## 4. Читать и форматировать валюты

```php
use Bitrix\Currency\CurrencyManager;
use Bitrix\Currency\CurrencyTable;
use Bitrix\Currency\CurrencyLangTable;

$base = CurrencyManager::getBaseCurrency();

$currencies = CurrencyTable::getList([
    'select' => ['CURRENCY', 'AMOUNT_CNT', 'AMOUNT', 'SORT', 'BASE'],
    'order' => ['SORT' => 'ASC'],
]);

$formats = CurrencyLangTable::getList([
    'select' => ['CURRENCY', 'LID', 'FORMAT_STRING', 'DEC_POINT', 'THOUSANDS_SEP'],
    'filter' => ['=LID' => LANGUAGE_ID],
]);
```

Для вывода суммы используй Bitrix formatting helpers текущего проекта, а не `number_format` руками: формат валюты зависит от языка и настроек `b_catalog_currency_lang`.

## 5. Курсы

```php
use Bitrix\Currency\CurrencyRateTable;

$rate = CurrencyRateTable::getList([
    'select' => ['CURRENCY', 'DATE_RATE', 'RATE_CNT', 'RATE'],
    'filter' => ['=CURRENCY' => 'USD'],
    'order' => ['DATE_RATE' => 'DESC'],
    'limit' => 1,
])->fetch();
```

Legacy `CCurrencyRates` всё ещё используется в старом коде и админке (`currency/general/currency_rate.php`). Если проект уже завязан на legacy API, не переписывай ради переписывания; сначала проверь surrounding code.

## 6. Связка с catalog и sale

Catalog:

- `b_catalog_price.CURRENCY` хранит код валюты цены;
- типы цен не равны валютам;
- quantity range цены может иметь разные суммы в одной валюте;
- при отображении учитываются права на тип цены и формат currency.

Sale:

- order, basket item, payment, shipment имеют currency fields;
- нельзя смешивать currency order и payment без проверки pay system restrictions;
- изменение базовой валюты влияет на расчёты, отчёты и обмены.

## 7. Диагностика

### Цена есть, но отображается странно

1. Проверь `CURRENCY` в `b_catalog_price`.
2. Проверь формат в `b_catalog_currency_lang` для языка сайта.
3. Проверь, не конвертирует ли компонент цену.
4. Проверь скидки sale/catalog и final price.
5. Проверь кеш компонента.

### Курс не применяется

1. Проверь базовую валюту через `CurrencyManager::getBaseCurrency()`.
2. Проверь `b_catalog_currency_rate` на дату.
3. Проверь, кто делает conversion: компонент, кастомный код или импорт.
4. Проверь timezone/date и округление.

## 8. Что не делать

- Не считать валюту равной типу цены.
- Не форматировать деньги руками в шаблоне, если есть currency format.
- Не менять базовую валюту на production без плана миграции цен, заказов, оплат и отчётов.
- Не игнорировать `currency` при catalog/sale задачах: цены и суммы без currency-контекста неполные.

---

## Source: `commerce-workflows.md`

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

---

## Source: `commerce-1c-integration.md`

# Commerce + 1С / CommerceML integration

> Truth layer: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core`. Подтверждены модули `catalog` 25.550.0, `sale` 26.0.0, `currency` 26.0.0, компоненты `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`, admin entrypoints `/bitrix/admin/1c_import.php`, `/bitrix/admin/1c_exchange.php`, `/bitrix/admin/1c_admin.php`, `/bitrix/admin/sale_exchange_log.php`.

Используй этот файл для задач обмена с 1С, CommerceML, выгрузки каталога, импорта товаров/цен/остатков, экспорта/импорта заказов, диагностики `mode=checkauth/init/file/import`.

## 1. Проверка наличия exchange слоя

```bash
for p in \
  www/bitrix/modules/catalog/install/components/bitrix/catalog.import.1c/component.php \
  www/bitrix/modules/catalog/install/components/bitrix/catalog.export.1c/component.php \
  www/bitrix/modules/sale/install/components/bitrix/sale.export.1c/component.php \
  www/bitrix/admin/1c_import.php \
  www/bitrix/admin/1c_exchange.php \
  www/bitrix/admin/sale_exchange_log.php
  do test -f "$p" && echo "OK $p" || echo "MISS $p"; done
```

```bash
find www/bitrix/modules/sale/lib/exchange -maxdepth 3 -type f | sort
rg "BX_CML2_IMPORT|BX_CML2_EXPORT|mode.*checkauth|mode.*init|mode.*file|mode.*import|secure_1c_exchange" www/bitrix/modules/{catalog,sale}
```

## 2. Entry points

| Поток | Entry point / component | Назначение |
|---|---|---|
| Импорт каталога из 1С | `catalog.import.1c` / `/bitrix/admin/1c_import.php` | товары, разделы, свойства, картинки, SKU, цены, остатки по CommerceML |
| Экспорт каталога | `catalog.export.1c` | выгрузка catalog data наружу |
| Обмен заказами | `sale.export.1c` / `/bitrix/admin/1c_exchange.php` | экспорт заказов в 1С и импорт обратных документов/статусов |
| Админка обмена | `/bitrix/admin/1c_admin.php` | настройки/страницы 1С exchange |
| Логи заказов | `/bitrix/admin/sale_exchange_log.php`, `b_sale_exchange_log` | диагностика обмена sale |

`/bitrix/admin/1c_import.php` просто требует `catalog/admin/1c_import.php`; `/bitrix/admin/1c_exchange.php` требует `sale/admin/1c_exchange.php`. Всегда переходи в модульный файл, а не анализируй wrapper как контракт.

## 3. Протокол режимов

Catalog import (`catalog.import.1c/component.php`) подтверждает режимы:

- `mode=checkauth` — авторизация, выдача cookie/session и `sessid`;
- `mode=init` — инициализация, ответ `zip=yes/no`, file limits, подготовка `$_SESSION['BX_CML2_IMPORT']`;
- `mode=file` — приём файла/chunk, запись во временный каталог;
- `mode=import` — распаковка zip или пошаговая обработка XML;
- session state: `BX_CML2_IMPORT`, `TEMP_DIR`, `zip`, `last_zip_entry`, `NS`, maps.

Sale exchange (`sale.export.1c/component.php`) подтверждает режимы:

- `mode=checkauth` — авторизация и `sessid`;
- `mode=init` — `zip=yes/no`, версия, `cmlVersion`, `BX_CML2_EXPORT`;
- `mode=file` — старый и новый формат загрузки;
- `mode=import` — unzip и обработка XML обратных документов;
- session state: `BX_CML2_EXPORT`, `last_zip_entry`, `last_xml_entry`, order prefix;
- option: `sale.secure_1c_exchange` и `check_bitrix_sessid()`.

## 4. Security и access

Проверяй:

1. группа пользователя, под которым ходит 1С;
2. права на catalog/sale exchange;
3. `secure_1c_exchange` и передачу `sessid`;
4. cookies/session: 1С должна сохранять cookie между `checkauth`, `init`, `file`, `import`;
5. `BX_SESSION_ID_CHANGE`, если компонент ругается на смену session ID;
6. `SKIP_SOURCE_CHECK` / source check в catalog import;
7. HTTPS/basic auth/proxy, если exchange идёт через внешний контур.

Никогда не советуй отключить security навсегда. Для диагностики можно временно подтвердить изменение с пользователем, но фиксируй rollback.

## 5. Временные файлы и zip/chunks

Типовые места:

- `upload/1c_exchange/` для sale export/import files;
- temp dir через `CTempFile::GetDirectoryName(...)`;
- `$_SESSION['BX_CML2_IMPORT']['TEMP_DIR']` / `BX_CML2_EXPORT['TEMP_DIR']`;
- zip state: `zip`, `last_zip_entry`;
- XML continuation: `last_xml_entry`.

Для больших файлов проверяй:

- `upload_max_filesize`, `post_max_size`, `max_execution_time`, `max_input_time`, memory;
- права на `upload/`, temp, `bitrix/tmp`;
- повторный chunk и идемпотентность;
- cleanup старых временных файлов;
- zip support (`zip_open`).

## 6. Catalog import: товары, SKU, цены, остатки

Диагностический порядок:

1. Найди XML/CommerceML файл и убедись, что 1С реально отправила нужный узел.
2. Проверь mapping по `XML_ID`: раздел, товар, offer, цена, склад.
3. Для товара проверь `CIBlockElement`, `b_catalog_product`.
4. Для SKU проверь offers-ИБ через `CCatalogSKU::GetInfoByProductIBlock()` и связь `CML2_LINK`/`SKU_PROPERTY_ID`.
5. Для цены проверь `b_catalog_price`, `CATALOG_GROUP_ID`, `CURRENCY`, quantity range.
6. Для остатков проверь `b_catalog_product.QUANTITY` и `b_catalog_store_product.AMOUNT`.
7. Проверь post-import side effects: facet/search index, managed/tagged/component cache.

## 7. Sale exchange: заказы и обратные документы

В shop-core есть `sale/lib/exchange/*`, `sale/lib/exchange/onec/*`, autoload для `Bitrix\Sale\Exchange\OneC\*` и `Bitrix\Sale\Exchange\Entity\*` loaders.

Проверяй:

- `b_sale_order.DATE_UPDATE`, status, paid/deducted/canceled;
- критерии выгрузки и order prefix в `BX_CML2_EXPORT`;
- `b_sale_exchange_log` и `sale_exchange_log.php`;
- `b_sale_synchronizer_log`, если участвует synchronizer;
- business values / `b_sale_bizval_code_1c`;
- import collision classes: order/shipment/payment/profile;
- обратные документы: payment/shipment/status updates.

## 8. Типовые проблемы

### `failure\nSession ID change is active`

Проверь файл включения компонента и рекомендацию компонента: `BX_SESSION_ID_CHANGE` должен быть определён до prolog, если это требуется конкретным exchange route. Не меняй глобально без понимания security impact.

### `checkauth` проходит, `file` или `import` падает

1. 1С не сохраняет cookie/session.
2. Потерян `sessid` при `secure_1c_exchange=Y`.
3. Temp/upload dir недоступен на запись.
4. File size/time limits.
5. Source check/CSRF/proxy режет запрос.

### Товар загружен, но не виден на витрине

1. `ACTIVE`, даты, section/site binding, права.
2. Товар vs offer: цена/остаток могут быть на offer.
3. `b_catalog_product` отсутствует или неверный `TYPE`.
4. Нет доступной цены для группы пользователя.
5. Остаток/availability запрещает покупку.
6. Не обновлён facet/search index или component cache.

### Цена/остаток не обновились

1. Неверный external ID / XML_ID.
2. Обновлён parent product вместо offer.
3. Неверный price type / currency.
4. Складской остаток обновился, общий quantity не пересчитан.
5. Сработал кастомный event handler и откатил/перезаписал значения.

### Заказы не уходят в 1С

1. Неверный exchange user или права.
2. Заказ не попадает в критерии выгрузки.
3. `DATE_UPDATE`/status не меняются ожидаемо.
4. Ошибка в `b_sale_exchange_log`.
5. `secure_1c_exchange` / `sessid` / cookies.
6. Кастомизация `sale.export.1c` или local override.

## 9. Safe verification flow

Перед любым тестом с обменом:

1. Используй sandbox, не production 1С.
2. Сохрани исходные options и настройки компонента.
3. Подготовь маленький CommerceML fixture: один раздел, один товар, один offer, одна цена, один остаток, один заказ.
4. Включи диагностические логи только на время теста.
5. После теста проверь таблицы, файлы, кеши, индексы.
6. Зафиксируй rollback: удалить тестовый товар/заказ/файлы, вернуть options.

## 10. Что не делать

- Не подключать реальную production 1С без подтверждения.
- Не отключать `secure_1c_exchange` как постоянное решение.
- Не удалять `CML2_LINK` и XML_ID-связи.
- Не чистить все товары перед импортом без backup и подтверждения.
- Не считать XML успешным только потому, что `file` вернул success: проверяй `import` и таблицы.

---

## Source: `workflow.md`

# Bitrix Бизнес-процессы (Bizproc / Workflow) — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с бизнес-процессами, CBPRuntime, кастомными активностями, запуском BP из кода или управлением статусами.
>
> Audit note: в shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core` модуль `bizproc` подтверждён, версия `26.200.0`. В каждом проекте всё равно сначала проверяй `www/bitrix/modules/bizproc`; без модуля этот файл остаётся условным reference.

## Содержание
- Архитектура: CBPRuntime, IBPActivity, Document
- Запуск БП из кода
- CBPDocument::GetDocumentType()
- Создание кастомного действия (IBPActivity)
- Кастомное условие (IBPCondition)
- Статусы БП
- Получить запущенные БП для документа
- Завершить/остановить БП
- Автозапуск через событие инфоблока
- Gotchas

---

## Архитектура

**CBPRuntime** — движок выполнения бизнес-процессов. Управляет жизненным циклом: запуск, приостановка (при ожидании задачи), возобновление, завершение.

**IBPActivity** — интерфейс активности (действия). Каждый шаг процесса — это активность. Базовый класс — `CBPActivity`.

**IBPWorkflowDocument** — интерфейс документа. Каждая сущность, с которой работает BP, должна реализовывать этот интерфейс через класс-документ.

**$documentType** — тройка `[MODULE_ID, DOCUMENT_CLASS, DOCUMENT_ID_PREFIX]`:
```php
// Для элементов инфоблока
$documentType = ['iblock', 'Bitrix\\Iblock\\Integration\\Bizproc\\Document\\Element', 'iblock_5'];
//                MODULE_ID   DOCUMENT_CLASS                                            DOCUMENT_ID_PREFIX
// iblock_5 = инфоблок с ID=5
// DocumentId (конкретный элемент) = 'iblock_5|' . $elementId
```

---

## Запуск БП из кода

```php
use Bitrix\Main\Loader;

Loader::includeModule('bizproc');
Loader::includeModule('iblock');

// ID шаблона БП (b_bp_workflow_template.ID)
$templateId = 10;

// Тип документа — инфоблок 5
$documentType = [
    'iblock',
    'Bitrix\\Iblock\\Integration\\Bizproc\\Document\\Element',
    'iblock_5',
];

// ID документа — конкретный элемент
$documentId = 'iblock_5|' . $elementId;

// Параметры запуска (соответствуют параметрам шаблона)
$startParams = [
    'TargetUser'    => 'user_' . $userId,  // ID пользователя с префиксом
    'Comment'       => 'Запущено из кода',
    'ApproveStatus' => 'waiting',
];

$errors = [];
$runtime = CBPRuntime::GetRuntime(true); // true = инициализировать если не запущен
$runtime->StartWorkflow(
    $templateId,
    $documentType,
    $documentId,
    $startParams,
    $errors,
    []  // дополнительные параметры (eventData)
);

if (!empty($errors)) {
    foreach ($errors as $error) {
        // ['code' => ..., 'message' => '...', 'file' => '...']
        error_log('BP error: ' . $error['message']);
    }
}

// Получить все шаблоны для типа документа
$templates = CBPWorkflowTemplateLoader::GetList(
    ['ID' => 'ASC'],
    ['DOCUMENT_TYPE' => $documentType],
    false, false,
    ['ID', 'NAME', 'AUTO_EXECUTE']
);
while ($tmpl = $templates->Fetch()) {
    // AUTO_EXECUTE: 0=вручную, 1=при добавлении, 2=при редактировании, 3=оба
}
```

---

## CBPDocument::GetDocumentType()

```php
Loader::includeModule('bizproc');
Loader::includeModule('iblock');

// Получить documentType для конкретного элемента инфоблока
$iblockId = 5;
$elementId = 100;

$documentType = CBPDocument::GetDocumentType(
    'iblock',                                                           // module_id
    'Bitrix\\Iblock\\Integration\\Bizproc\\Document\\Element',         // documentClass
    'iblock_' . $iblockId . '|' . $elementId                          // documentId
);
// вернёт: ['iblock', 'Bitrix\\Iblock\\...', 'iblock_5']

// Получить список типов документов модуля
$types = CBPDocument::GetDocumentTypes('iblock');
// array типов для всех инфоблоков: [['MODULE_ID', 'CLASS', 'PREFIX', 'NAME'], ...]

// Получить данные документа через Document API
$docData = CBPDocument::GetDocument(
    'iblock',
    'Bitrix\\Iblock\\Integration\\Bizproc\\Document\\Element',
    'iblock_5|100'
);
// ассоциативный массив полей элемента с типами документа
```

---

## Создание кастомного действия (IBPActivity)

```php
// Файл: local/modules/vendor.mymodule/lib/activity/sendnotification.php
// Namespace: Vendor\Mymodule\Activity\SendNotification
// Регистрация: в install/index.php через CBPActivity::RegisterActivity()

namespace Vendor\Mymodule\Activity;

use CBPActivity;
use CBPActivityExecutionStatus;
use CBPActivityExecutionResult;
use CBPRuntime;

class SendNotification extends CBPActivity
{
    public function __construct(string $name)
    {
        parent::__construct($name);
        $this->arProperties = [
            'Title'   => '',       // обязательное свойство — название в конструкторе
            'UserId'  => null,     // ID получателя
            'Message' => '',       // текст уведомления
        ];
    }

    // Основной метод выполнения — вызывается движком
    public function Execute(): int
    {
        // Получить значение свойства (может содержать placeholder типа {=Variable:varName})
        $userId = (int)CBPRuntime::GetRuntime()->ResolveProperty(
            $this,
            $this->UserId
        );
        $message = $this->ResolveValue($this->Message);

        if ($userId > 0) {
            // Отправить внутреннее уведомление Bitrix
            \CIMNotify::Add([
                'FROM_USER_ID' => 0,
                'TO_USER_ID'   => $userId,
                'NOTIFY_TYPE'  => IM_NOTIFY_SYSTEM,
                'NOTIFY_MODULE'=> 'vendor.mymodule',
                'NOTIFY_EVENT' => 'bp_notification',
                'NOTIFY_MESSAGE' => htmlspecialchars($message),
            ]);
        }

        // Завершить активность — перейти к следующему шагу
        $this->SetStatus(CBPActivityExecutionStatus::Closed);
        return CBPActivityExecutionResult::Succeed;
    }

    // Описание свойств для UI конструктора БП
    public static function GetPropertiesDialogValues(
        string $documentType,
        string $activityName,
        array  &$workflowTemplate,
        array  &$workflowParameters,
        array  &$workflowVariables,
        array  $currentValues,
        array  &$errors
    ): bool {
        $errors = [];

        // Получить значения из формы конструктора
        $userId  = trim($currentValues['UserId'] ?? '');
        $message = trim($currentValues['Message'] ?? '');

        if (empty($userId)) {
            $errors[] = [
                'code'    => 0,
                'parameter' => 'UserId',
                'message' => 'Не указан получатель',
            ];
        }

        if (!empty($errors)) {
            return false;
        }

        // Сохранить значения в шаблон
        $props = ['UserId' => $userId, 'Message' => $message];
        static::SetActivityPropertiesInTemplate($activityName, $props, $workflowTemplate);

        return true;
    }

    // HTML диалог настройки в конструкторе
    public static function GetPropertiesDialog(
        string $documentType,
        string $activityName,
        array  $workflowTemplate,
        array  $workflowParameters,
        array  $workflowVariables,
        array  $currentValues = []
    ): string {
        $currentActivity = null;
        static::GetCurrentActivityPropertiesFromTemplate(
            $activityName, $workflowTemplate, $currentActivity
        );

        $userId  = $currentActivity['UserId']  ?? '';
        $message = $currentActivity['Message'] ?? '';

        return '<table>
            <tr>
                <td>Получатель:</td>
                <td><input type="text" name="UserId" value="' . htmlspecialchars($userId) . '"></td>
            </tr>
            <tr>
                <td>Сообщение:</td>
                <td><textarea name="Message">' . htmlspecialchars($message) . '</textarea></td>
            </tr>
        </table>';
    }
}
```

### Регистрация кастомного действия

```php
// В install/index.php модуля в методе InstallDB()
\CBPActivity::RegisterActivity(
    'SendNotification',                         // уникальное имя
    \Vendor\Mymodule\Activity\SendNotification::class,  // полное имя класса
    'vendor.mymodule'                           // module_id
);

// Удаление при деинсталляции
\CBPActivity::UnregisterActivity('SendNotification');
```

---

## Кастомное условие (IBPCondition)

```php
// Кастомное условие для ветвления в конструкторе БП
namespace Vendor\Mymodule\Condition;

class OrderStatusCondition
{
    // Метод, который вычисляет условие — возвращает bool
    public static function Evaluate(
        string $documentType,
        string $operatorType,
        mixed  $leftValue,
        mixed  $rightValue
    ): bool {
        // $leftValue — поле документа (например, значение STATUS)
        // $operatorType — тип сравнения ('equal', 'not_equal', etc.)
        // $rightValue — значение для сравнения из настроек условия

        return match ($operatorType) {
            'equal'     => $leftValue === $rightValue,
            'not_equal' => $leftValue !== $rightValue,
            'in'        => in_array($leftValue, (array)$rightValue),
            default     => false,
        };
    }
}

// Регистрация типа условия (в install/index.php):
\CBPCondition::RegisterType(
    'OrderStatus',
    \Vendor\Mymodule\Condition\OrderStatusCondition::class,
    'Evaluate',
    'vendor.mymodule'
);
```

---

## Статусы БП

```php
Loader::includeModule('bizproc');

// Константы CBPWorkflowStatus:
// CBPWorkflowStatus::Created    = 0  — создан, не запущен
// CBPWorkflowStatus::Running    = 1  — выполняется
// CBPWorkflowStatus::Suspended  = 2  — приостановлен (ждёт задачу/таймер)
// CBPWorkflowStatus::Terminated = 3  — принудительно остановлен
// CBPWorkflowStatus::Completed  = 4  — завершён успешно
// CBPWorkflowStatus::Faulted    = 5  — завершён с ошибкой

// Получить статус конкретного экземпляра БП
$workflowId = 'abc123-...'; // GUID из b_bp_workflow_state

$state = CBPStateService::GetWorkflowState($workflowId);
// ['WORKFLOW_ID' => '...', 'STATE' => 1, 'TITLE' => '...', 'MODIFIED' => '...']

$statusCode = (int)$state['STATE'];
if ($statusCode === CBPWorkflowStatus::Running) {
    // BP в процессе выполнения
}
```

---

## Получить запущенные БП для документа

```php
Loader::includeModule('bizproc');

$documentType = [
    'iblock',
    'Bitrix\\Iblock\\Integration\\Bizproc\\Document\\Element',
    'iblock_5',
];
$documentId = 'iblock_5|100';

// Получить все БП для документа
$workflows = CBPStateService::GetWorkflows($documentType, $documentId);
// array: [['WORKFLOW_ID' => '...', 'STATE' => 1, 'TEMPLATE_ID' => 10, ...], ...]

foreach ($workflows as $wf) {
    echo $wf['WORKFLOW_ID'] . ': ' . $wf['STATE'];
}

// Получить только активные (Running или Suspended)
$activeWorkflows = CBPStateService::GetWorkflows(
    $documentType,
    $documentId,
    [CBPWorkflowStatus::Running, CBPWorkflowStatus::Suspended]
);

// Получить задачи (Tasks) активных БП для пользователя
$tasks = CBPTaskService::GetUserTasks($userId, $documentType);
while ($task = $tasks->Fetch()) {
    // ['ID' => ..., 'WORKFLOW_ID' => '...', 'NAME' => '...', 'STATUS' => 0, ...]
}
```

---

## Завершить/остановить БП

```php
Loader::includeModule('bizproc');

$workflowId = 'abc123-...'; // GUID экземпляра

$runtime = CBPRuntime::GetRuntime(true);

// Принудительно завершить (Terminate) — статус → Terminated
$errors = [];
$runtime->TerminateWorkflow($workflowId, null, $errors);

if (!empty($errors)) {
    foreach ($errors as $err) {
        error_log('Terminate error: ' . $err['message']);
    }
}

// Завершить с кастомным сообщением (причина завершения)
$runtime->TerminateWorkflow($workflowId, 'Отменён администратором', $errors);

// Приостановить (Suspend) — только если BP поддерживает
// CBPRuntime не имеет метода Suspend напрямую — управляется через активность CBPDelayActivity
// Для принудительной остановки используй TerminateWorkflow

// Очистить завершённые БП (обслуживание)
CBPStateService::DeleteWorkflows(['STATE' => CBPWorkflowStatus::Completed]);
```

---

## Автозапуск через событие инфоблока

```php
// Шаблон БП с AUTO_EXECUTE = 1 запускается автоматически при добавлении элемента.
// Под капотом ядро вешает обработчик на OnAfterIBlockElementAdd.

// Ручная имитация автозапуска (если нужен контроль):
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandler(
    'iblock',
    'OnAfterIBlockElementAdd',
    function(array &$fields) {
        if ((int)$fields['IBLOCK_ID'] !== 5) {
            return;
        }

        if (!\Bitrix\Main\Loader::includeModule('bizproc')) {
            return;
        }

        $documentType = [
            'iblock',
            'Bitrix\\Iblock\\Integration\\Bizproc\\Document\\Element',
            'iblock_5',
        ];
        $documentId = 'iblock_5|' . (int)$fields['ID'];

        // Запустить все шаблоны с AUTO_EXECUTE=1 для этого инфоблока
        CBPDocument::AutoStartWorkflows(
            $documentType,
            $documentId,
            CBPDocumentEventType::Create, // Create / Edit
            []
        );
    }
);
```

---

## Gotchas

- **`Loader::includeModule('bizproc')`** обязателен. Без него `CBPRuntime`, `CBPStateService`, `CBPDocument` и все активности не определены.
- **`$documentType` — тройка, не строка**: `['iblock', 'Bitrix\\Iblock\\...', 'iblock_5']`. Неправильный формат — тихая ошибка при запуске без исключения.
- **`$documentId` — строка `'iblock_5|100'`**, не число. Первая часть = `$documentType[2]`, вторая = ID элемента через `|`.
- **Документ должен реализовывать `IBPWorkflowDocument`**: для стандартных инфоблоков это `Bitrix\Iblock\Integration\Bizproc\Document\Element`. Для кастомных сущностей нужно реализовывать интерфейс самостоятельно.
- **`CBPRuntime::GetRuntime(true)`** — вызывай с `true` (инициализация). Без аргумента или с `false` вернёт runtime который может быть не готов, и `StartWorkflow` упадёт.
- **Ошибки не исключения**: `StartWorkflow()` и `TerminateWorkflow()` пишут ошибки в переданный по ссылке `$errors[]`. Всегда проверяй этот массив.
- **Шаблон БП привязан к типу документа**: шаблон для `iblock_5` не будет виден/работать для `iblock_6`. Это намеренное поведение — `DOCUMENT_TYPE[2]` должен совпадать.
- **`CBPActivity::RegisterActivity()`** нужно вызывать при каждой установке модуля — данные хранятся в `b_bp_activity`. При деинсталляции — `UnregisterActivity()`.
- **Задачи BP (`CBPTaskService`)** не удаляются автоматически при `TerminateWorkflow` — их нужно закрывать отдельно или они остаются "висящими" в `b_bp_task`.
- **`AUTO_EXECUTE`** в шаблоне: `0` = вручную, `1` = при добавлении, `2` = при редактировании, `3` = оба. Значение `3` = бинарный OR: `1|2`.
- **Производительность**: не запускай BP синхронно в массовых операциях — каждый `StartWorkflow()` делает несколько запросов к БД. Используй очереди или агенты.

---

## Source: `push-pull.md`

# Bitrix Push & Pull — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с real-time уведомлениями, Push&Pull, WebSocket, отправкой событий из PHP в браузер или настройкой каналов.
>
> Audit note: в shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core` модуль `pull` подтверждён, версия `25.300.0`. В каждом проекте всё равно сначала проверяй `www/bitrix/modules/pull`; без модуля этот файл остаётся условным reference.

## Содержание
- Архитектура Push&Pull
- Отправка события из PHP: Event::add()
- Отправка нескольким пользователям
- Broadcast на канал (CPullChannel)
- JS-сторона: BX.PULL.subscribe, getStatus, reconnect
- Регистрация канала и онлайн-статус
- Отладка
- Gotchas

---

## Архитектура Push & Pull

Bitrix Push&Pull — система доставки событий из PHP-кода в браузер в реальном времени.

**Транспорты** (выбираются автоматически по приоритету):
1. **WebSocket** — постоянное соединение, наименьшая задержка. Требует Push-сервер (nginx + модуль).
2. **SSE (Server-Sent Events)** — однонаправленный стриминг. Fallback при недоступности WS.
3. **Long Polling** — периодические HTTP-запросы. Работает всегда, самый надёжный fallback.

**Каналы** — именованные очереди событий. Каждый пользователь слушает свой персональный канал. Broadcast-каналы позволяют слать события группе пользователей.

**Поток данных:**
```
PHP: \Bitrix\Pull\Event::add($userId, $payload)
  → запись в b_pull_stack (MySQL) или Redis
  → Push-сервер / long-polling polling endpoint читает стек
  → доставляет в браузер через WS/SSE/LP
  → BX.PULL.subscribe callback вызывается в JS
```

---

## Отправка события из PHP

```php
use Bitrix\Main\Loader;

Loader::includeModule('pull');

// Отправить событие конкретному пользователю
\Bitrix\Pull\Event::add($userId, [
    'module_id' => 'vendor.mymodule',   // ваш модуль-отправитель
    'command'   => 'order_status_changed', // произвольная строка, обрабатывается на JS
    'params'    => [                    // данные события — только простой массив
        'order_id' => 123,
        'status'   => 'shipped',
        'message'  => 'Заказ отправлен',
    ],
    'extra'     => \CPullStack::AddByUser($userId), // необязательно, дополнительные мета
]);

// Минимальный вариант
\Bitrix\Pull\Event::add($userId, [
    'module_id' => 'vendor.mymodule',
    'command'   => 'ping',
    'params'    => ['ts' => time()],
]);
```

### Отправка нескольким пользователям

```php
Loader::includeModule('pull');

// Массив userId — разошлёт каждому в его персональный канал
$userIds = [1, 5, 12, 47];

\Bitrix\Pull\Event::add($userIds, [
    'module_id' => 'vendor.mymodule',
    'command'   => 'new_message',
    'params'    => [
        'from_user_id' => $senderId,
        'text'         => 'Привет всем!',
        'chat_id'      => $chatId,
    ],
]);

// Через CPullStack напрямую (legacy-способ, аналогичен Event::add)
CPullStack::AddByUsers($userIds, [
    'module_id' => 'vendor.mymodule',
    'command'   => 'new_message',
    'params'    => ['text' => 'Привет'],
]);
```

---

## Broadcast на канал (CPullChannel)

```php
Loader::includeModule('pull');

// Создать публичный канал (broadcast)
$channelId = 'my_custom_channel_' . $someEntityId;

// Подписать пользователя на канал
CPullChannel::AddUserToDemoChannel($userId, $channelId);

// Отправить событие в канал (получат все подписанные пользователи)
CPullStack::AddByChannel($channelId, [
    'module_id' => 'vendor.mymodule',
    'command'   => 'channel_event',
    'params'    => ['data' => 'payload'],
]);

// Получить ID канала пользователя (для передачи на клиент)
$channelToken = CPullChannel::GetChannelToken($userId);

// Зарегистрировать канал в системе (необходимо для публичных каналов)
CPullChannel::Register(
    $userId,        // владелец
    $channelId,     // уникальный ID
    3600,           // TTL в секундах
    false           // false = приватный, true = публичный
);
```

---

## JS-сторона

### Подписка на события

```javascript
// Убедись, что BX.PULL инициализирован (загружается с ядром Bitrix)
// В компоненте подключи расширение: \Bitrix\Main\UI\Extension::load('pull.client');

BX.PULL.subscribe({
    moduleId: 'vendor.mymodule',    // module_id из PHP Event::add
    callback: function(data) {
        // data.command   — строка команды
        // data.params    — объект с параметрами
        // data.extra     — дополнительные мета-данные

        if (data.command === 'order_status_changed') {
            console.log('Статус заказа:', data.params.status);
            // обновить UI
        }

        if (data.command === 'new_message') {
            BX.onCustomEvent('onNewMessage', [data.params]);
        }
    }
});

// Подписка с явным указанием типа события (D7 Pull Client)
BX.PULL.subscribe({
    type: BX.PullClient.SubscriptionType.Server, // Server | Shared | Online
    moduleId: 'vendor.mymodule',
    callback: function(data) { /* ... */ }
});
```

### Статус соединения и управление

```javascript
// Получить текущий статус соединения
const status = BX.PULL.getStatus();
// Возможные значения: 'online', 'offline', 'connecting', 'unknown'

// Принудительное переподключение (например, после восстановления сети)
BX.PULL.reconnect();

// Проверить, подключён ли Pull
if (BX.PULL.isConnected()) {
    console.log('Pull подключён');
}

// Событие смены статуса
BX.PULL.subscribe({
    type: BX.PullClient.SubscriptionType.Status,
    callback: function(data) {
        // data.status: 'online' | 'offline' | 'connecting'
        if (data.status === 'offline') {
            // показать индикатор отсутствия соединения
        }
    }
});

// Событие онлайн-статуса других пользователей
BX.PULL.subscribe({
    type: BX.PullClient.SubscriptionType.Online,
    callback: function(data) {
        // data.userId   — ID пользователя
        // data.online   — true/false
        console.log('User', data.userId, 'is', data.online ? 'online' : 'offline');
    }
});
```

---

## Регистрация канала и управление онлайн-статусом

```php
Loader::includeModule('pull');

// Онлайн-статус: обновить время последней активности пользователя
CPullOnline::SetOnline($userId, SITE_ID);

// Получить онлайн-пользователей сайта
$onlineUsers = CPullOnline::GetOnlineUsers(SITE_ID);
// array: [['USER_ID' => 1, 'LAST_SEEN' => timestamp], ...]

// Проверить онлайн-статус конкретного пользователя
$isOnline = CPullOnline::IsOnline($userId, SITE_ID);
// bool — онлайн если активен в последние ~60 секунд

// Зарегистрировать обработчик Pull-команд в модуле (в install/index.php)
// Bitrix вызовет OnPullEvent когда придёт событие для модуля
EventManager::getInstance()->registerEventHandler(
    'pull', 'OnPullEvent',
    'vendor.mymodule',
    \Vendor\Mymodule\PullHandler::class,
    'onPullEvent'
);
```

```php
// Пример обработчика OnPullEvent
namespace Vendor\Mymodule;

class PullHandler
{
    public static function onPullEvent(string $moduleId, string $command, array $params): void
    {
        if ($moduleId !== 'vendor.mymodule') {
            return;
        }
        // обработать команду от клиента (если используется двусторонняя связь)
    }
}
```

---

## Подключение расширения в PHP-компоненте

```php
// В component.php или template/template.php — подключить Pull JS-клиент
\Bitrix\Main\UI\Extension::load('pull.client');

// Или через Asset Manager (legacy)
\CJSCore::Init(['pull', 'pull_status', 'pull_client']);

// Передать токен канала в JS через CUtil::InitJSCore()
// (токен генерируется автоматически для авторизованных пользователей)
```

---

## Отладка

### Параметр `?LISTEN_JS_REVISION` в URL

Добавь `?LISTEN_JS_REVISION=1` к любому URL Bitrix-страницы чтобы увидеть в консоли браузера:
- текущую JS-ревизию Pull-клиента
- параметры соединения (транспорт, канал, сервер)

### Chrome DevTools — что смотреть

**Network → WS (WebSocket)**:
- ищи соединение с путём `/bitrix/tools/pull/?CHANNEL=...`
- в Frames вкладке видны все входящие и исходящие frames в реальном времени

**Network → EventStream (SSE)**:
- при SSE-транспорте ищи `GET /bitrix/tools/pull/?type=sse&...`
- в EventStream вкладке — поток событий

**Network → XHR (Long Polling)**:
- запросы к `/bitrix/tools/pull/?type=json&...`
- каждый запрос держится открытым, пока не придут данные или таймаут

**Консоль**:
```javascript
// Получить диагностику Pull-соединения
BX.PULL.getDebugInfo();

// Включить verbose-логирование
BX.PULL.setLogLevel(BX.PullClient.LogLevel.DEBUG);
```

### Отладка стека событий в PHP

```php
Loader::includeModule('pull');

// Посмотреть что лежит в стеке для пользователя (не потреблять)
$stack = CPullStack::GetStack($userId);
// array необработанных событий

// Очистить стек пользователя (осторожно в production!)
CPullStack::ClearStack($userId);

// Проверить активные каналы
$channels = CPullChannel::GetUserChannels($userId);
var_dump($channels);
```

---

## Gotchas

- **`Loader::includeModule('pull')`** обязателен перед любым использованием `\Bitrix\Pull\Event`, `CPullStack`, `CPullChannel`, `CPullOnline`. Без него классы не определены.
- **`EVENT_ID` vs `command`**: в PHP-вызове `Event::add()` поле называется `command`, не `event_id`. В JS-подписке `BX.PULL.subscribe` тоже `callback` получает `data.command`. Не путай с `EVENT_ID` из `CSocNetLog`.
- **Данные `params` должны быть простым массивом**: без объектов PHP, без вложенных классов, только скалярные значения и массивы. Данные сериализуются через `json_encode` — PHP-объекты потеряют тип.
- **Ограничение размера события**: максимальный размер `params` — около 64 КБ. При превышении событие молча отбрасывается. Для больших данных передавай только ID и загружай данные отдельным AJAX.
- **Long Polling включён всегда** как fallback — даже без Push-сервера Push&Pull работает. Push-сервер только ускоряет доставку.
- **`BX.PULL.subscribe()` без `type`** по умолчанию подписывается на `SubscriptionType.Server` — серверные события. Для онлайн-статуса используй явно `SubscriptionType.Online`.
- **Авторизованные vs анонимные**: Push&Pull работает только для авторизованных пользователей. Для анонимных нужны отдельные публичные каналы через `CPullChannel::Register()` с `$public = true`.
- **Токен канала не статичный**: он ротируется. Не кешируй токен на клиенте — получай через JS-инициализацию Bitrix.
- **В `\Bitrix\Pull\Event::add()` первый параметр** может быть `int` (один userId) или `int[]` (массив). Строки не принимаются — только целые числа.
- **SSE и Long Polling держат соединение** — не вызывай `Event::add()` в цикле с тысячами пользователей синхронно. Используй фоновые задачи (агенты, очереди) для массовой рассылки.
