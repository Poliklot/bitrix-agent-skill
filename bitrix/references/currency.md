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

// Диагностическая запись не позднее выбранной даты, не замена conversion API.
$rateDate = new \Bitrix\Main\Type\Date();
$rate = CurrencyRateTable::getList([
    'select' => ['CURRENCY', 'DATE_RATE', 'RATE_CNT', 'RATE'],
    'filter' => ['=CURRENCY' => 'USD', '<=DATE_RATE' => $rateDate],
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

## K151 — RATE_CNT задаёт номинал валютного курса

RATE относится к RATE_CNT единицам валюты. Для цены одной единицы нужен RATE/RATE_CNT, не RATE. При импорте сохраняй номинал источника вместе со стоимостью и отклоняй нулевой номинал; для перевода суммы используй штатный валютный API, а не вручную умножай на сырую колонку.

**Проверка на стенде:** Котировки за 1 и за 100 единиц дают одинаковый результат после нормализации.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencyrates/ccurrencyrates__add.a9ea23d5.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K152 — Историческая конвертация требует даты, а не последней строки курса

GetConvertFactorEx принимает явную дату YYYY-MM-DD; пустая дата означает текущий курс. Для исторического расчёта не заменяй API запросом ORDER BY DATE_RATE DESC без границы даты. Отдельно проверь наличие нужных курсов и политику проекта при их отсутствии; не объявляй случайный fallback подтверждённым историческим курсом.

**Проверка на стенде:** Будущий курс не влияет на расчёт выбранной прошлой даты.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencyrates/getconvertfactorex.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K153 — CurrencyFormat форматирует, но не переводит между валютами

CurrencyFormat/formatValue возвращают строку оформления, не выполняют перевод из одной валюты в другую. Сначала ConvertCurrency с исходной/целевой валютой и выбранной датой, затем форматирование в валюте результата. useTemplate=false убирает шаблон, но не превращает строку в числовое значение для хранения.

**Проверка на стенде:** Смена оформления не меняет исходное число; конвертация выполняется отдельным шагом.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencylang/currencyformat.php?print=Y). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K154 — Большие суммы форматируются десятичной строкой с учётом версии

С currency 24.0.0 formatValue поддерживает длинные десятичные строки без предварительного приведения к float. Передавай каноническую строку с точкой, не локализованные пробелы/запятую и не рассчитывай на произвольную экспоненциальную запись. На старой версии не обещай тот же контракт; форматирование не обеспечивает точную арифметику.

**Проверка на стенде:** Последние цифры длинной суммы сохраняются в поддерживаемой версии.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencylang/formatvalue.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K155 — HIDE_ZERO различает публичный и административный вывод

HIDE_ZERO управляет незначащими дробными нулями публичного вывода. Несовпадение вида 10 и 10.00 между витриной и админкой само по себе не означает разные суммы. Получай GetFormatDescription для текущего языка, сравнивай настройки и контекст; не исправляй отображение записью округлённого PRICE.

**Проверка на стенде:** Одинаковая сохранённая сумма имеет допустимое разное оформление без мутации.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/developer/ccurrencylang/getformatdescription.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K156 — Обработчик CurrencyFormat может заменить штатный результат

Непустая строка из обработчика CurrencyFormat становится результатом форматирования. Если настройки валюты верны, а вывод другой, проверь обработчики события до правки форматов в БД. Возвращай замену только для своей области; для остальных случаев не подменяй результат. Контекст вывода и безопасность HTML остаются ответственностью шаблона.

**Проверка на стенде:** Кастомный обработчик меняет только выбранную валюту, остальные используют штатный формат.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/currency/events/currencyformat.php?print=Y). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K157 — checkCurrencyID возвращает код, а существование проверяется отдельно

Успешный checkCurrencyID возвращает строку кода, ошибка — false: сравнение результата с true неверно. Не приравнивай проверку идентификатора к наличию валюты; для этого есть [isCurrencyExist](https://dev.1c-bitrix.ru/api_d7/bitrix/currency/currencymanager/iscurrencyexist.php) (с 17.0.0). После проверки используй возвращённый код, а разрешённый для операции набор валют проверяй отдельно.

**Проверка на стенде:** Неустановленный код не попадает в запись цены даже при допустимой форме идентификатора.

[Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/currency/currencymanager/checkcurrencyid.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.
