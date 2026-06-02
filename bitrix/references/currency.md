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
