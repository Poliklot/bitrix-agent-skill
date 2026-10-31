# Sale — корзина, заказ, оплата, доставка (`sale` 26.0.0)

> Truth layer: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core`, модуль `sale` версии `26.0.0` (`install/version.php`, дата `2026-01-12`). Для sale REST controllers/events, external pay system/delivery/cashbox handlers and `webservice.sale` SOAP stats открывай `shop-integrations-webservice.md`. В этом core `sale`, `catalog`, `currency`, `pull`, `bizproc`, `sender` присутствуют. В каждом проекте сначала проверяй наличие `www/bitrix/modules/sale` и конкретных компонентов.

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


Для задач по стандартным компонентам sale (`sale.basket.*`, `sale.order.ajax`, `sale.order.checkout`, `sale.personal.*`, `sale.order.payment*`, delivery/location/gifts) сначала открывай `shop-standard-components.md`, а этот файл используй для D7 API, lifecycle и side effects корзины/заказа. Для sender-сегментов покупателей, `TargetSaleMailConnector`, follow-up рассылок и sale statistic events открывай `shop-marketing-analytics.md`. Для роботов/БП заказа открывай `shop-automation-bizproc.md`, но не обещай sale-order robots без локального provider-а/CRM/custom module.

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

Ниже — только свободная корзина посетителя. Если корзина уже принадлежит заказу, сохраняй через `Order::save()`, см. K11.

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

Статус заказа, подтверждение конкретной оплаты и отгрузка — три разные операции. Не связывай их одним универсальным циклом. Сначала проверяются права/внешнее подтверждение и целевая сущность; каждая операция имеет свои проверки и последствия (см. K14–K15).

Для оплаты: загрузить Order и конкретный Payment из его коллекции, сверить сумму/валюту/связь с подтверждённой транзакцией, обработать повтор. Только затем `Payment::setPaid('Y')`, проверка Result и `Order::save()` с проверкой Result. Это не инструкция пометить весь заказ оплаченным по browser redirect.

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

## K11 — Корзина заказа сохраняется через агрегат Order

Различай свободную корзину посетителя и `$order->getBasket()`. Для второй не вызывать `Basket::save()` отдельно: связанные оплаты/отгрузки могут измениться вместе с корзиной. Менять объекты в памяти, проверять Results, затем один раз сохранять владеющий Order вне его обработчиков. Свободная корзина сохраняется своим `save()`. ORM `Basket::getList` годится для чтения, но не заменяет объектный lifecycle мутации.

**Проверка на стенде:** Изменить количество в заказе с оплатой и отгрузкой; после reload проверить весь граф, а не одну строку basket.

[Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/sale/technique/basket.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K12 — FUSER и пользователь — разные идентификаторы

`Fuser::getId()` разрешает посетителя текущего контекста, а не возвращает `$USER->GetID()`. `getIdByUserId` — отдельный путь для пользователя. При фоновой задаче/импорте явно определить целевого владельца и сайт, не использовать случайную CLI-сессию как покупателя. В web endpoint FUSER не принимается на доверии из запроса. После login/слияния гостевой корзины заново разрешить актуальную корзину; не удерживать старый FUSER как глобальный ключ.

**Проверка на стенде:** Guest → login с уже существующей корзиной; два сайта и фоновой запуск не должны смешивать владельцев.

[Официальный контракт](https://docs.1c-bitrix.ru/api/classes/Bitrix-Sale-Fuser.html). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K13 — Идентичность строки корзины не равна PRODUCT_ID

Один товар может быть представлен разными строками с различными свойствами/условиями. Для изменения существующей строки использовать её ID внутри уже авторизованной корзины, не первый найденный `PRODUCT_ID`. У ещё не сохранённого item есть `getBasketCode()` — ключ объектной корзины, который нельзя автоматически трактовать как DB ID. Решение объединять строки принимать по контракту provider/свойств; после save обновить mapping созданных строк.

**Проверка на стенде:** Две строки одного SKU и новый item до save: меняется только выбранная строка, связи после save сохранены.

[Официальный контракт](https://docs.1c-bitrix.ru/api/classes/Bitrix-Sale-BasketItem.html). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K14 — Системная отгрузка и распределение количества

System shipment отражает нераспределённую часть корзины, а не реальную отправку покупателю. Для отправки создать/выбрать обычную Shipment и распределять её ShipmentItem quantities через объектный API с проверкой Result. Не ставить DEDUCTED системной отгрузке и не удалять её как мусор. При уменьшении корзины сначала согласовать уже распределённые/отгруженные количества. Отчёт доставки исключает system; бизнес-проверка сверяет распределение с корзиной.

**Проверка на стенде:** Разделить 5 единиц на две отправки и остаток; уменьшение ниже уже отгруженного количества должно быть обработано явно.

[Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/sale/technique/shipment.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K15 — Частичные оплаты и повтор подтверждения

Оплаченность относится к конкретному Payment. Callback/ручное подтверждение должны разрешить именно его внутри заказа, сверить сумму, валюту и внешний идентификатор; браузерная страница успеха не является подтверждением провайдера. Повтор одной транзакции не должен повторять зачисление или побочные эффекты. Состояния заказа и остальных оплат не проставлять вручную «за компанию». Ошибки `setPaid` и сохранения Order проверяются; фактический возврат у провайдера — отдельный процесс, не просто `setPaid(N)`.

**Проверка на стенде:** Две частичные оплаты: подтверждение и повтор первой не оплачивают вторую и не создают повторный эффект.

[Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/sale/classes/payment/setpaid.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.
