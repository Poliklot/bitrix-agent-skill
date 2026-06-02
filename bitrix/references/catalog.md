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

Проверенный shop-core содержит стандартные catalog-компоненты: `catalog.import.1c`, `catalog.export.1c`, `catalog.product.grid`, `catalog.productcard.*`, `catalog.store.*`, `catalog.store.document.*`, `catalog.report.store_*`, `catalog.product.subscribe*`, `catalog.viewed.products`, `currency.field.money`, `currency.money.input`, `currency.rates`. Для public `bitrix:catalog`, `catalog.section`, `catalog.element`, `catalog.smart.filter`, compare и eShop wizard/templates дополнительно открывай `shop-standard-components.md`, потому что эти витринные `catalog.*` лежат в `iblock`.

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

Для component-by-component карты public/admin магазина сначала открывай `shop-standard-components.md`. Здесь оставлен API-oriented catalog слой.

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

Если проблема в page 2, “Показать ещё”, infinite scroll или `PAGEN_<NavNum>` у `catalog.section`, открывай `shop-standard-components.md` и `pagination.md`: stock templates текущего shop-core отправляют следующую страницу через `PAGEN_` + `NavNum` и зависят от актуальных `navParams`, cache key, filter и sort.

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
