# Commerce Deferred
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `catalog.md`

# Торговый каталог (модуль Catalog)

```php
use Bitrix\Main\Loader;
Loader::includeModule('catalog');
Loader::includeModule('iblock');
```

> Audit note: в текущем проверенном core модуль `catalog` в `www/bitrix/modules` не найден. Этот файл сейчас отложен до установки магазинного core и не должен быть активным маршрутом в текущей фазе проекта.

## Архитектура

Модуль `catalog` работает поверх инфоблоков:
- **Товар** — элемент инфоблока с типом `D7_PRODUCT_TYPE = 1` (простой) или `6` (с ТП)
- **Торговое предложение (SKU/offer)** — элемент дочернего инфоблока типа `2`
- **Цена** — таблица `b_catalog_price`, связана с товаром по `PRODUCT_ID`
- **Склад** — таблица `b_catalog_store`, остатки в `b_catalog_store_product`

---

## Цены

### Прочитать цену товара

```php
use Bitrix\Catalog\PriceTable;

// Получить все цены товара
$result = PriceTable::getList([
    'select' => ['ID', 'PRODUCT_ID', 'CATALOG_GROUP_ID', 'PRICE', 'CURRENCY', 'QUANTITY_FROM', 'QUANTITY_TO'],
    'filter' => ['=PRODUCT_ID' => $productId],
    'order'  => ['CATALOG_GROUP_ID' => 'ASC'],
]);
while ($row = $result->fetch()) {
    // $row['CATALOG_GROUP_ID'] — ID типа цены (прайс-листа)
    // $row['PRICE'] — цена
    // $row['CURRENCY'] — валюта
}
```

### Получить цену для текущего пользователя (с учётом группы/скидок)

```php
// Массив цен по всем типам для одного товара
$prices = \CCatalogProduct::GetOptimalPrice(
    $productId,
    1,                         // количество
    $USER->GetUserGroupArray(), // группы пользователя
    'N',                       // 'N' — без повторного расчёта
    [],                        // дополнительные параметры
    SITE_ID,
    []
);
// $prices['PRICE']['PRICE'] — итоговая цена
// $prices['PRICE']['DISCOUNT_PRICE'] — цена до скидки
// $prices['PRICE']['PERCENT'] — % скидки
```

### Установить / обновить цену

```php
use Bitrix\Catalog\PriceTable;

// Найти существующую цену
$existing = PriceTable::getList([
    'filter' => ['=PRODUCT_ID' => $productId, '=CATALOG_GROUP_ID' => 1],
])->fetch();

if ($existing) {
    // Обновить
    $result = PriceTable::update($existing['ID'], [
        'PRICE'    => 1500.00,
        'CURRENCY' => 'RUB',
    ]);
} else {
    // Создать
    $result = PriceTable::add([
        'PRODUCT_ID'       => $productId,
        'CATALOG_GROUP_ID' => 1,    // ID прайс-листа
        'PRICE'            => 1500.00,
        'CURRENCY'         => 'RUB',
        'QUANTITY_FROM'    => null, // нет ограничения по количеству
        'QUANTITY_TO'      => null,
    ]);
}

if (!$result->isSuccess()) {
    // обработка ошибок
}
```

### Типы цен (прайс-листы)

```php
use Bitrix\Catalog\GroupTable;

$result = GroupTable::getList([
    'select' => ['ID', 'NAME', 'BASE'],
    'order'  => ['SORT' => 'ASC'],
]);
while ($row = $result->fetch()) {
    // $row['BASE'] == 'Y' — базовый прайс-лист
}
```

---

## Торговые предложения (SKU / Offers)

Торговые предложения — это элементы **дочернего инфоблока** с типом продукта `2`. Связь с родительским товаром через свойство типа `E` (привязка к элементу).

### Получить список ТП для товара

```php
// Найти инфоблок ТП
$offersIblockId = \CCatalogSKU::GetInfoByProductIBlock($productIblockId);
// $offersIblockId['IBLOCK_ID'] — ID инфоблока ТП
// $offersIblockId['SKU_PROPERTY_ID'] — ID свойства-связки

// Получить ТП для конкретного товара
$res = CIBlockElement::GetList(
    ['SORT' => 'ASC'],
    [
        'IBLOCK_ID'                              => $offersIblockId['IBLOCK_ID'],
        'ACTIVE'                                 => 'Y',
        'PROPERTY_' . $offersIblockId['SKU_PROPERTY_ID'] => $productId,
    ],
    false,
    false,
    ['ID', 'NAME', 'PROPERTY_COLOR', 'PROPERTY_SIZE']
);
while ($offer = $res->GetNext()) {
    $offerId = $offer['ID'];
    // Получить цену ТП
    $prices = PriceTable::getList(['filter' => ['=PRODUCT_ID' => $offerId]])->fetch();
}
```

### D7 для инфоблока с API_CODE

```php
// Если инфоблок ТП имеет API_CODE='catalog_offers':
use Bitrix\Iblock\Elements\ElementCatalogOffersTable;

$result = ElementCatalogOffersTable::getList([
    'select' => ['ID', 'NAME', 'COLOR' => 'COLOR.VALUE', 'SIZE' => 'SIZE.VALUE'],
    'filter' => [
        '=ACTIVE' => 'Y',
        '=PARENT_PRODUCT.ID' => $productId, // через reference
    ],
]);
```

---

## Склады и остатки

### Получить остатки на всех складах

```php
use Bitrix\Catalog\StoreProductTable;

$result = StoreProductTable::getList([
    'select' => ['STORE_ID', 'AMOUNT', 'STORE_TITLE' => 'STORE.TITLE'],
    'filter' => ['=PRODUCT_ID' => $productId],
]);
while ($row = $result->fetch()) {
    // $row['STORE_TITLE'] — название склада
    // $row['AMOUNT'] — количество
}
```

### Суммарный остаток

```php
use Bitrix\Catalog\ProductTable;

$product = ProductTable::getRow([
    'select' => ['ID', 'QUANTITY', 'QUANTITY_RESERVED'],
    'filter' => ['=ID' => $productId],
]);
// $product['QUANTITY'] — общий остаток
// $product['QUANTITY'] - $product['QUANTITY_RESERVED'] — доступный
```

### Обновить остаток на складе

```php
use Bitrix\Catalog\StoreProductTable;

$existing = StoreProductTable::getList([
    'filter' => ['=PRODUCT_ID' => $productId, '=STORE_ID' => $storeId],
])->fetch();

if ($existing) {
    StoreProductTable::update($existing['ID'], ['AMOUNT' => $newQuantity]);
} else {
    StoreProductTable::add([
        'PRODUCT_ID' => $productId,
        'STORE_ID'   => $storeId,
        'AMOUNT'     => $newQuantity,
    ]);
}

// Пересчитать общий остаток в b_catalog_product
\CCatalogProduct::recalcQuantityProduct($productId);
```

---

## Типы продуктов

```php
use Bitrix\Catalog\ProductTable;

// Константы типа продукта
ProductTable::TYPE_PRODUCT      // 1 — простой товар
ProductTable::TYPE_SET          // 2 — комплект (устарело)
ProductTable::TYPE_SKU          // 3 — товар с ТП (родительский)
ProductTable::TYPE_OFFER        // 4 — торговое предложение
ProductTable::TYPE_FREE_OFFER   // 5 — свободное ТП
ProductTable::TYPE_EMPTY_SKU    // 6 — товар без ТП (новый тип)
```

### Получить тип товара

```php
use Bitrix\Catalog\ProductTable;

$product = ProductTable::getRow([
    'select' => ['TYPE', 'AVAILABLE'],
    'filter' => ['=ID' => $productId],
]);
// $product['TYPE'] — тип
// $product['AVAILABLE'] == 'Y' — в наличии (по остаткам)
```

---

## Скидки каталога

### Список скидок

```php
use Bitrix\Catalog\DiscountTable;

$result = DiscountTable::getList([
    'select' => ['ID', 'NAME', 'ACTIVE', 'DISCOUNT_TYPE', 'DISCOUNT_VALUE'],
    'filter' => ['=ACTIVE' => 'Y', '=SITE_ID' => SITE_ID],
    'order'  => ['SORT' => 'ASC'],
]);
```

### Применить скидки каталога к ценам (при отображении)

```php
// Инициализировать движок скидок для пользователя
\CCatalogDiscount::SetDiscountGroups($USER->GetUserGroupArray());

// Получить цену с учётом скидок каталога
$discountPrice = \CCatalogProduct::GetOptimalPrice(
    $productId,
    1,
    $USER->GetUserGroupArray(),
    'N',
    [],
    SITE_ID,
    []
);
```

---

## Товар и его свойства — полный набор данных

```php
// Получить элемент инфоблока + данные каталога
$element = CIBlockElement::GetByID($productId)->GetNextElement();
if ($element) {
    $fields     = $element->GetFields();        // стандартные поля
    $properties = $element->GetProperties();    // свойства

    // Данные из catalog
    $catalogData = \CCatalogProduct::GetByID($productId);
    // $catalogData['WEIGHT'], ['WIDTH'], ['HEIGHT'], ['LENGTH'], ['CAN_BUY_ZERO']

    // Цена
    $price = \CPrice::GetBasePrice($productId);
    // $price['PRICE'], $price['CURRENCY']
}
```

---

## Работа с группами покупателей и типами цен

```php
// Список групп покупателей для прайс-листа
use Bitrix\Catalog\GroupAccessTable;

$result = GroupAccessTable::getList([
    'select' => ['GROUP_ID', 'CATALOG_GROUP_ID', 'ACCESS'],
    'filter' => ['=CATALOG_GROUP_ID' => $priceTypeId],
]);
// ACCESS: 'D' — запрет, 'V' — просмотр, 'B' — покупка

// Назначить группу пользователей на тип цены
GroupAccessTable::add([
    'GROUP_ID'         => $userGroupId,     // ID группы пользователей Bitrix
    'CATALOG_GROUP_ID' => $priceTypeId,
    'ACCESS'           => 'B',              // покупка
]);
```

---

## Gotchas

- Функция `\CCatalogProduct::GetOptimalPrice` сама применяет все скидки каталога — не нужно применять их вручную
- `ProductTable::TYPE_SKU` (3) — товар с торговыми предложениями. У него **нет собственной цены** — цены у ТП (`TYPE_OFFER`)
- `QUANTITY` в `ProductTable` — суммарный по всем складам, обновляется через `recalcQuantityProduct`
- `StoreProductTable` работает только если включён складской учёт в настройках каталога
- При импорте товаров всегда вызывай `\CCatalogProduct::recalcQuantityProduct($id)` после обновления остатков на складах
- `CAN_BUY_ZERO = 'Y'` — позволяет добавлять в корзину товар с нулевым остатком

---

## Source: `sale.md`

# Модуль Sale — заказы, корзина, оплата, доставка

```php
use Bitrix\Main\Loader;
Loader::includeModule('sale');
Loader::includeModule('catalog'); // для работы с товарами
```

> Audit note: в текущем проверенном core модули `sale` и `catalog` в `www/bitrix/modules` не найдены. Этот файл сейчас отложен до установки магазинного core и не должен быть активным маршрутом в текущей фазе проекта.

## Архитектура Sale D7

```
Order (заказ)
├── Basket (корзина)
│   └── BasketItem[] (позиции)
├── PropertyCollection (свойства заказа — ФИО, адрес, телефон)
├── ShipmentCollection
│   └── Shipment[] (отправления)
│       └── ShipmentItemCollection → ShipmentItem[]
└── PaymentCollection
    └── Payment[] (оплаты)
```

---

## Корзина

### Добавить товар в корзину текущего пользователя

```php
use Bitrix\Sale\Basket;
use Bitrix\Sale\BasketItem;
use Bitrix\Main\Context;

$basket = Basket::loadItemsForFUser(
    \CSaleBasket::GetBasketUserID(), // fuser_id текущего посетителя
    SITE_ID
);

// Проверить, есть ли товар уже в корзине
$existingItem = null;
foreach ($basket as $item) {
    if ($item->getField('PRODUCT_ID') == $productId) {
        $existingItem = $item;
        break;
    }
}

if ($existingItem) {
    // Увеличить количество
    $existingItem->setField('QUANTITY', $existingItem->getQuantity() + $quantity);
} else {
    // Новая позиция
    $item = $basket->createItem('catalog', $productId);
    $item->setFields([
        'QUANTITY'   => $quantity,
        'CURRENCY'   => \Bitrix\Currency\CurrencyManager::getBaseCurrency(),
        'LID'        => SITE_ID,
        'PRODUCT_ID' => $productId,
        'NAME'       => $productName,
        'PRICE'      => $price,
        'PRODUCT_PROVIDER_CLASS' => '\CCatalogProductProvider',
    ]);
}

$result = $basket->save();
if (!$result->isSuccess()) {
    // обработка ошибок
}
```

### Получить корзину

```php
$fUserId = \CSaleBasket::GetBasketUserID();
$basket  = Basket::loadItemsForFUser($fUserId, SITE_ID);

$total   = $basket->getPrice();    // итоговая сумма с учётом скидок
$weight  = $basket->getWeight();   // вес

foreach ($basket as $item) {
    $productId = $item->getProductId();
    $name      = $item->getField('NAME');
    $quantity  = $item->getQuantity();
    $price     = $item->getPrice();       // цена за единицу
    $finalPrice = $item->getFinalPrice(); // с учётом скидок
}
```

### Удалить позицию из корзины

```php
foreach ($basket as $item) {
    if ($item->getProductId() == $productId) {
        $item->delete();
        break;
    }
}
$basket->save();
```

---

## Заказы

### Создать заказ из корзины

```php
use Bitrix\Sale\Order;
use Bitrix\Sale\Basket;
use Bitrix\Sale\Delivery;
use Bitrix\Sale\PaySystem;

$userId = (int)$GLOBALS['USER']->GetID();

// 1. Создать заказ
$order = Order::create(SITE_ID, $userId);
$order->setPersonTypeId(1); // 1 — физ.лицо, 2 — юр.лицо (зависит от настроек)

// 2. Привязать корзину
$basket = Basket::loadItemsForFUser(\CSaleBasket::GetBasketUserID(), SITE_ID);
$order->setBasket($basket);

// 3. Свойства заказа (ФИО, телефон, адрес и т.д.)
$propertyCollection = $order->getPropertyCollection();
foreach ($propertyCollection as $prop) {
    $code = $prop->getField('CODE');
    if ($code === 'NAME') {
        $prop->setValue('Иван Иванов');
    } elseif ($code === 'EMAIL') {
        $prop->setValue('ivan@example.com');
    } elseif ($code === 'PHONE') {
        $prop->setValue('+79991234567');
    }
}

// 4. Доставка
$shipmentCollection = $order->getShipmentCollection();
$shipment = $shipmentCollection->createItem();

$deliveryService = Delivery\Services\Manager::getById(1); // ID службы доставки
$shipment->setFields([
    'DELIVERY_ID'   => $deliveryService['ID'],
    'DELIVERY_NAME' => $deliveryService['NAME'],
    'CURRENCY'      => $order->getCurrency(),
    'PRICE_DELIVERY'=> 300.00,
]);

// Перенести позиции корзины в отправление
$shipmentItemCollection = $shipment->getShipmentItemCollection();
foreach ($basket as $basketItem) {
    $shipmentItem = $shipmentItemCollection->createItem($basketItem);
    $shipmentItem->setQuantity($basketItem->getQuantity());
}

// 5. Оплата
$paymentCollection = $order->getPaymentCollection();
$payment = $paymentCollection->createItem();

$paySystemService = PaySystem\Manager::getById(1); // ID платёжной системы
$payment->setFields([
    'PAY_SYSTEM_ID'   => $paySystemService['ID'],
    'PAY_SYSTEM_NAME' => $paySystemService['NAME'],
    'SUM'             => $order->getPrice(),
    'CURRENCY'        => $order->getCurrency(),
]);

// 6. Сохранить
$result = $order->save();
if ($result->isSuccess()) {
    $orderId = $order->getId();
} else {
    $errors = $result->getErrorMessages();
}
```

### Получить заказ

```php
use Bitrix\Sale\Order;

$order = Order::load($orderId);

if ($order) {
    $userId   = $order->getUserId();
    $status   = $order->getField('STATUS_ID');   // N, P, F и т.д.
    $price    = $order->getPrice();              // сумма
    $currency = $order->getCurrency();
    $paid     = $order->isPaid();                // bool
    $canceled = $order->isCanceled();            // bool

    // Свойства
    $propCollection = $order->getPropertyCollection();
    $email = $propCollection->getUserEmail();    // специальный метод
    $name  = $propCollection->getPayerName();
    $phone = $propCollection->getPhone();
}
```

### Список заказов через ORM

```php
use Bitrix\Sale\Internals\OrderTable;

$result = OrderTable::getList([
    'select' => ['ID', 'USER_ID', 'PRICE', 'CURRENCY', 'STATUS_ID', 'DATE_INSERT'],
    'filter' => [
        '=USER_ID'   => $userId,
        '=STATUS_ID' => ['N', 'P'],   // новые и оплаченные
    ],
    'order'  => ['DATE_INSERT' => 'DESC'],
    'limit'  => 20,
]);
while ($row = $result->fetch()) { ... }
```

### Изменить статус заказа

```php
use Bitrix\Sale\Order;

$order = Order::load($orderId);
$order->setField('STATUS_ID', 'F'); // F = завершён
$result = $order->save();
```

### Отменить заказ

```php
$order = Order::load($orderId);
$order->setField('CANCELED', 'Y');
$order->setField('REASON_CANCELED', 'Отказ клиента');
$order->save();
```

---

## Оплата (Payment)

### Отметить платёж как оплаченный

```php
use Bitrix\Sale\Order;

$order = Order::load($orderId);
$paymentCollection = $order->getPaymentCollection();

foreach ($paymentCollection as $payment) {
    if (!$payment->isPaid()) {
        $result = $payment->setPaid('Y');
        if ($result->isSuccess()) {
            $order->save();
        }
    }
}
```

### Статусы Payment

| Метод | Описание |
|-------|---------|
| `$payment->isPaid()` | оплачен |
| `$payment->getSum()` | сумма платежа |
| `$payment->getField('PAY_SYSTEM_ID')` | ID платёжной системы |
| `$payment->getField('DATE_PAID')` | дата оплаты |

---

## Скидки и купоны

### Применить купон к заказу

```php
use Bitrix\Sale\DiscountCouponsManager;

// Добавить купон (привязывается к fuser)
$result = DiscountCouponsManager::add($couponCode);
if (!$result) {
    // неверный купон
}

// Применяется автоматически при расчёте заказа через Order::refreshData()
```

### Проверить купон вручную

```php
use Bitrix\Sale\Discount\Discount;

$couponInfo = \CSaleDiscount::GetCoupon($couponCode, SITE_ID);
// $couponInfo['ID'], ['DISCOUNT_ID'], ['TYPE'] (1=один раз, 2=многократно, 3=на одного)
```

---

## События Sale

Регистрация в `include.php` модуля:

```php
use Bitrix\Main\EventManager;

// Перед сохранением заказа
EventManager::getInstance()->addEventHandler('sale', 'OnSaleOrderBeforeSaved', [\My\Handler::class, 'onBeforeSave']);

// После сохранения заказа
EventManager::getInstance()->addEventHandler('sale', 'OnSaleOrderSaved', [\My\Handler::class, 'onSaved']);

// Смена статуса
EventManager::getInstance()->addEventHandler('sale', 'OnSaleStatusOrder', [\My\Handler::class, 'onStatus']);

// Оплата
EventManager::getInstance()->addEventHandler('sale', 'OnSalePaymentPaid', [\My\Handler::class, 'onPaid']);
```

```php
// Обработчик
class Handler
{
    public static function onSaved(\Bitrix\Main\Event $event): void
    {
        /** @var \Bitrix\Sale\Order $order */
        $order  = $event->getParameter('ENTITY');
        $isNew  = $event->getParameter('IS_NEW');   // bool — новый заказ?
        $values = $event->getParameter('VALUES');    // изменённые поля

        $orderId = $order->getId();
    }
}
```

### Ключевые события

| Событие | Когда |
|---------|-------|
| `OnSaleOrderBeforeSaved` | перед сохранением (можно отменить) |
| `OnSaleOrderSaved` | после сохранения |
| `OnSaleStatusOrder` | смена статуса заказа |
| `OnSalePaymentPaid` | заказ отмечен как оплаченный |
| `OnSaleBasketItemSaved` | сохранение позиции корзины |
| `OnSaleShipmentSaved` | сохранение отправления |

---

## Legacy API (встречается в старых проектах)

```php
// Получить список заказов пользователя
$res = CSaleOrder::GetList(
    ['ID' => 'DESC'],
    ['USER_ID' => $userId, 'STATUS_ID' => 'N'],
    false,
    ['nPageSize' => 20]
);
while ($order = $res->GetNext()) {
    echo $order['ID'] . ' — ' . $order['PRICE'];
}

// Изменить статус
CSaleOrder::StatusOrder($orderId, 'F');

// Отменить
CSaleOrder::CancelOrder($orderId, 'Y', 'Причина');
```

---

## Gotchas

- `Order::create` не сохраняет — нужен явный `$order->save()`
- При добавлении товара в корзину обязательно указывай `PRODUCT_PROVIDER_CLASS` — без него не будет проверки остатков и расчёта скидок
- `$basket->getPrice()` возвращает цену **с учётом скидок** — только после `$order->doFinalAction(true)` пересчитываются скидки заказа
- `isPaid()` на Order проверяет **все** платежи. Если один из нескольких платежей не оплачен — `isPaid()` = false
- `PersonType` (физ/юр. лицо) влияет на набор свойств заказа — всегда проверяй какие типы настроены на сайте

---

## Source: `commerce-workflows.md`

# Магазин, витрина и кросс-доменные workflow

> Загружай этот файл, когда задача затрагивает сразу несколько слоёв интернет-магазина: модель данных, витрину, поиск, фильтрацию, SEO, корзину, оформление заказа, обмены или эксплуатацию.
>
> Audit note: этот файл целиком отложен до установки магазинного core. В текущем проверенном ядре модули `catalog` и `sale` не подтверждены, поэтому магазинные workflow не должны быть активным маршрутом на этой фазе проекта.

## 1. Порядок чтения проекта

Для магазинных задач сначала смотри не API-справочник, а живой код проекта:

1. `www/bitrix/modules/<module>/install/version.php`
2. `www/bitrix/modules/<module>/lib/`
3. `www/bitrix/modules/<module>/install/components/bitrix/<component>/`
4. `local/components/<vendor>/<component>/`
5. `local/templates/<site>/components/bitrix/<component>/`
6. `local/php_interface/`, `local/modules/`, `urlrewrite.php`

Минимальный набор проверок:

- установлен ли модуль;
- есть ли нужный стандартный компонент;
- есть ли проектный оверрайд компонента или шаблона;
- не разъехались ли параметры компонента, данные и шаблон;
- какие кеши и индексы участвуют в цепочке.

## 2. Карта слоёв магазина

| Слой | Что обычно лежит здесь | Основные reference-файлы |
|------|-------------------------|---------------------------|
| Контентный | инфоблоки, разделы, элементы, свойства, UF разделов, файлы, символьные коды, XML ID | `iblocks.md`, `entities-migrations.md`, `import-export.md`, `sef-urls.md` |
| Коммерческий | тип товара, офферы, цены, типы цен, остатки, склады, доступность | `catalog.md`, `iblocks.md` |
| Транзакционный | корзина, свойства заказа, оплата, доставка, скидки, купоны, статусы | `sale.md`, `users.md`, `validation.md` |
| Поисковый | smart filter, facet, search index, URL фильтра, релевантность | `search.md`, `seo-cache-access.md`, `sef-urls.md`, `cache-infra.md` |
| Презентационный | стандартный компонент, `arResult`, `result_modifier.php`, шаблон, `component_epilog.php`, AJAX | `components.md`, `templates.md`, `cache-infra.md` |
| Операционный | обмены, агенты, stepper, cron, админка, миграции, логи | `update-stepper.md`, `admin-ui.md`, `entities-migrations.md`, `cache-infra.md` |

## 3. Как выбирать точку изменения

### Если меняется модель данных

Предпочитай:

- миграцию;
- установщик/обновлятор модуля;
- отдельный CLI-скрипт для разового переноса;
- stepper/агент для тяжёлой пакетной операции.

Не полагайся на разовые клики в админке, если изменение должно повторяться на других стендах.

### Если меняется поведение витрины

Порядок проверки обычно такой:

1. стандартный компонент и его параметры;
2. проектный шаблон компонента;
3. `result_modifier.php`;
4. `component_epilog.php`;
5. сервисный слой и отдельные репозитории;
6. кеш и AJAX-контур.

Тяжёлую выборку и бизнес-правила старайся держать вне `template.php`.

### Если меняется обмен или синхронизация

Процесс должен быть:

- идемпотентным;
- пакетным;
- логируемым;
- безопасным к повторному запуску;
- понятным по стратегии повторной обработки ошибок.

После синхронизации учитывай зависимые индексы и кеши.

## 4. Диагностические маршруты

### Расхождение между админкой и витриной

Проверь по цепочке:

1. активность сущности, сайт, раздел, даты активности, права;
2. фильтр и `select` в компоненте;
3. проектный `result_modifier.php` и шаблон;
4. кеш компонента, тегированный кеш, composite;
5. ЧПУ, `urlrewrite.php`, обработку 404 и canonical.

### Расхождение между данными товара и отображением

Проверь:

1. структуру модели: простой товар или родитель/оффер;
2. источник цены, доступности, картинок и свойств;
3. какой слой собирает итоговый `arResult`;
4. не фильтрует ли шаблон “пустые” поля;
5. не остался ли старый кеш после обновления данных.

### Расхождение в поиске и фильтрации

Проверь:

1. настройки свойств и их пригодность для фильтра/индекса;
2. актуальность facet/search индекса;
3. соответствие URL-правил и параметров компонента;
4. права и привязку к сайту;
5. кеш, который может отдавать старую форму фильтра или выдачу.

### Расхождение в цепочке оформления заказа

Проверь:

1. тип плательщика и коллекцию свойств заказа;
2. совместимость службы доставки и платёжной системы;
3. финальный пересчёт заказа перед сохранением;
4. обработчики `sale`, которые могут дозаполнять или ломать данные;
5. внешние callback и логи обмена, если проблема проявляется уже после создания заказа.

### Расхождение после обмена или импорта

Проверь:

1. стратегию сопоставления внутренних и внешних идентификаторов;
2. работу с файлами и множественными свойствами;
3. повторяемость апдейта и пропуск уже обработанных данных;
4. переиндексацию поиска/фасета и очистку кешей;
5. отложенные задачи, которые завершают обработку не в том же запросе.

## 5. Компоненты и реальные контракты

Когда задача касается стандартного компонента, читай его контракт из ядра:

- `.parameters.php` — доступные параметры;
- `component.php` или `class.php` — сборка данных;
- `templates/` — реальная структура шаблонов;
- `.description.php` — позиционирование компонента и назначение.

Для каталогоподобной витрины обычно критичны:

- корневой комплексный компонент;
- список раздела;
- детальная карточка;
- фильтр;
- поисковый компонент каталога.

Сначала подтверди их наличие в текущем ядре, потом проектные переопределения.

## 6. Что нужно проговаривать в ответе

Для кросс-доменных задач ответ должен явно содержать:

- какие модули и компоненты были проверены в ядре;
- какой слой является источником данных;
- где именно вносить изменение;
- какие кеши и индексы завязаны на это изменение;
- какие ограничения есть из-за отсутствующего модуля или проектной архитектуры.

---

## Source: `workflow.md`

# Bitrix Бизнес-процессы (Bizproc / Workflow) — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с бизнес-процессами, CBPRuntime, кастомными активностями, запуском BP из кода или управлением статусами.
>
> Audit note: в текущем проверенном core модуль `bizproc` в `www/bitrix/modules` не найден. Этот файл сейчас отложен и не должен использоваться как основной маршрут, пока модуль не установлен и не подтверждён в ядре.

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
> Audit note: в текущем проверенном core модуль `pull` в `www/bitrix/modules` не найден. Этот файл сейчас отложен и не должен быть основным маршрутом, пока модуль не установлен и не подтверждён в ядре.

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
