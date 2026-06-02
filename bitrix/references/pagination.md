# Bitrix Pagination — справочник

> Reference для Bitrix-скилла. Загружай, когда задача связана с пагинацией списков, `PAGEN_N`, `NavStart()`, `GetNavPrint()`, `PageNavigation`, `main.pagenavigation`, `system.pagenavigation`, ajax/lazy load, admin list/grid или симптомами “вторая страница пустая/дублируется/не листается”.

## Audit note

Проверено по shop-core:
- `www/bitrix/modules/main/classes/general/version.php` — `main` 26.150.0
- `www/bitrix/modules/main/classes/general/dbresult.php`
- `www/bitrix/modules/main/lib/ui/pagenavigation.php`
- `www/bitrix/modules/main/lib/ui/adminpagenavigation.php`
- `www/bitrix/modules/main/lib/ui/reversepagenavigation.php`
- `www/bitrix/modules/main/install/components/bitrix/system.pagenavigation/component.php`
- `www/bitrix/modules/main/install/components/bitrix/main.pagenavigation/class.php`
- `www/bitrix/modules/main/interface/navigation.php`
- `www/bitrix/modules/main/interface/admin_list.php`
- `www/bitrix/modules/main/interface/admin_ui_list.php`
- `www/bitrix/modules/main/interface/admin_lib.php`
- `www/bitrix/modules/main/install/components/bitrix/main.ui.grid/class.php`
- `www/bitrix/modules/iblock/classes/*/iblockelement.php`
- `www/bitrix/modules/iblock/lib/component/elementlist.php`
- stock templates `catalog.section` с ajax/lazy pagination через `PAGEN_<NavNum>`

Ниже только контракт, подтверждённый этим core. Если в проекте есть оверрайды в `local/components`, `local/templates` или `bitrix/templates`, сначала сравни их со stock-компонентом.

## Слои пагинации

### 1. Legacy DB result: `CDBResult` / `CAllDBResult`

Основной контракт находится в `main/classes/general/dbresult.php`.

Ключевые поля результата:
- `NavNum` — порядковый номер навигации на странице; формирует `PAGEN_<NavNum>`, `SIZEN_<NavNum>`, `SHOWALL_<NavNum>`.
- `NavPageCount` — количество страниц.
- `NavPageNomer` — текущая страница.
- `NavPageSize` — размер страницы.
- `NavShowAll` — режим “показать всё”.
- `NavRecordCount` — всего записей.
- `bDescPageNumbering` — обратная нумерация страниц.
- `add_anchor` — суффикс якоря для нескольких навигаций на одной странице.

Публичные методы:
- `NavStart($nPageSize = 0, $bShowAll = true, $iNumPage = false)`
- `GetNavPrint($title, $show_allways = false, $StyleText = "text", $template_path = false, $arDeleteParam = false)`
- `NavPrint(...)`
- `GetPageNavString(...)`
- `GetPageNavStringEx(...)`
- `NavStringForCache(...)`
- `GetNavParams(...)`

`GetNavParams()` читает текущий номер по глобальному `PAGEN_<NavNum+1>`, режим “всё” по `SHOWALL_<NavNum+1>`, при включённой опции `main/nav_page_in_session` использует session-ключи `SESS_PAGEN_*` и `SESS_ALL_*`. Если размер страницы не задан или меньше 1, core нормализует его в `10`.

`GetNavPrint()` и `system.pagenavigation` при сборке ссылок удаляют текущие nav-параметры и `PHPSESSID`, чтобы не смешивать старую страницу/размер с новой ссылкой.

### 2. Legacy visual component: `bitrix:system.pagenavigation`

Компонент принимает `NAV_RESULT`, который должен быть объектом-наследником `CAllDBResult`.

Подтверждённые входы и result-поля:
- `NAV_RESULT`
- `SHOW_ALWAYS`
- `NAV_TITLE`
- `BASE_LINK`
- `NavRecordCount`
- `NavPageCount`
- `NavPageNomer`
- `NavPageSize`
- `bShowAll`
- `NavShowAll`
- `NavNum`
- `bDescPageNumbering`
- `add_anchor`
- `nPageWindow`
- `bSavePage`
- `sUrlPath`
- `NavQueryString`
- `NavFirstRecordShow`
- `NavLastRecordShow`

Stock templates в core:
- `.default`
- `modern`
- `bootstrap_v4`
- `grid`
- `arrows`
- `arrows_adm`
- `js`
- `orange`
- `round`
- `visual`

Используется через `CDBResult::GetPageNavStringEx(...)` и многими legacy-компонентами.

### 3. D7 navigation object: `Bitrix\Main\UI\PageNavigation`

Контракт в `main/lib/ui/pagenavigation.php`.

Поддержанные URL-форматы:
- query: `?nav-products=page-5`
- query с размером: `?nav-products=page-5-size-20`
- query “всё”: `?nav-products=page-all`
- SEF: `/page/nav-products/page-2/size-20/...`
- несколько независимых навигаций: `nav-cars`, `nav-books` и так далее.

Методы, которые реально есть в core:
- `__construct(string $id)`
- `initFromUri()`
- `setPageSize($n)`
- `setCurrentPage($n)`
- `allowAllRecords($mode)`
- `setRecordCount($n)`
- `setPageSizes(array $sizes)`
- `getRecordCount()`
- `getPageCount()`
- `getCurrentPage()`
- `getPageSize()`
- `getPageSizes()`
- `getId()`
- `getOffset()`
- `getLimit()`
- `allRecordsShown()`
- `allRecordsAllowed()`
- `addParams(Web\Uri $uri, $sef, $page, $size = null)`
- `clearParams(Web\Uri $uri, $sef)`

Важная деталь: `initFromUri()` ограничивает `currentPage` верхней границей только если `recordCount` уже задан. Если count узнаётся после чтения URI, отдельно подумай о нормализации страницы, иначе после сильного фильтра можно получить пустой offset.

### 4. `AdminPageNavigation` и `ReversePageNavigation`

`Bitrix\Main\UI\AdminPageNavigation`:
- наследует `PageNavigation`;
- разрешает “показать всё”;
- допустимые размеры: `10`, `20`, `50`, `100`, `200`, `500`;
- вызывает `initFromUri()` прямо в конструкторе.

`Bitrix\Main\UI\ReversePageNavigation`:
- принимает record count в конструкторе;
- по умолчанию текущая страница — последняя;
- считает offset/limit так, что последняя страница отображается первой;
- нужен для reverse paging, где порядок страниц инвертирован.

### 5. D7 visual component: `bitrix:main.pagenavigation`

Компонент в `main/install/components/bitrix/main.pagenavigation/class.php`.

Обязательный вход:
- `~NAV_OBJECT` / `NAV_OBJECT` должен быть `Bitrix\Main\UI\PageNavigation`.

Параметры:
- `PAGE_WINDOW`, default `5`
- `SHOW_ALWAYS`
- `SEF_MODE`
- `SHOW_COUNT`
- `~BASE_LINK`

Result-поля:
- `RECORD_COUNT`
- `PAGE_COUNT`
- `CURRENT_PAGE`
- `ALL_RECORDS`
- `PAGE_SIZE`
- `PAGE_SIZES`
- `SHOW_ALL`
- `ID`
- `REVERSED_PAGES`
- `URL`
- `URL_TEMPLATE`
- `START_PAGE`
- `END_PAGE`
- `FIRST_RECORD`
- `LAST_RECORD`

Если `SHOW_ALWAYS` выключен, компонент не рисует навигацию при одной странице и выключенном `allRecords`.

Stock templates:
- `.default`
- `modern`
- `admin`
- `grid`

## Базовые паттерны

### D7 ORM + `PageNavigation`

```php
use Bitrix\Main\Loader;
use Bitrix\Main\UI\PageNavigation;
use Vendor\Module\ItemTable;

Loader::includeModule('vendor.module');

$filter = ['=ACTIVE' => 'Y'];
$nav = new PageNavigation('nav-items');
$nav
    ->setPageSize(20)
    ->setPageSizes([20, 50, 100])
    ->allowAllRecords(false);

$count = ItemTable::getCount($filter);
$nav->setRecordCount($count);
$nav->initFromUri();

$rows = ItemTable::getList([
    'select' => ['ID', 'NAME', 'ACTIVE'],
    'filter' => $filter,
    'order' => ['SORT' => 'ASC', 'ID' => 'ASC'],
    'limit' => $nav->getLimit(),
    'offset' => $nav->getOffset(),
]);

$APPLICATION->IncludeComponent(
    'bitrix:main.pagenavigation',
    '',
    [
        'NAV_OBJECT' => $nav,
        'SEF_MODE' => 'N',
        'SHOW_COUNT' => 'Y',
    ],
    false
);
```

Правило: count и список должны использовать один и тот же filter. Для стабильности страниц всегда добавляй детерминированный secondary sort по `ID`.

### Legacy `CIBlockElement::GetList`

```php
$navParams = CDBResult::GetNavParams([
    'nPageSize' => 20,
    'bShowAll' => false,
]);

$res = CIBlockElement::GetList(
    ['SORT' => 'ASC', 'ID' => 'ASC'],
    [
        'IBLOCK_ID' => $iblockId,
        'ACTIVE' => 'Y',
    ],
    false,
    [
        'nPageSize' => 20,
        'iNumPage' => $navParams['PAGEN'],
        'bShowAll' => false,
    ],
    ['ID', 'IBLOCK_ID', 'NAME', 'DETAIL_PAGE_URL']
);

while ($item = $res->GetNext())
{
    // ...
}

echo $res->GetPageNavString('Страницы', 'modern');
```

`nTopCount` — это ограничение количества строк, а не полноценная пагинация. Не используй `nTopCount` вместо `nPageSize/iNumPage`, если нужны страницы, `PAGEN_N`, NavString, lazy load или корректный count.

### Legacy `CDBResult::NavStart`

```php
$rsData = SomeLegacyApi::GetList($sort, $filter);
$rsData->NavStart(20, false);

while ($row = $rsData->GetNext())
{
    // ...
}

echo $rsData->GetNavPrint('Элементы');
```

`NavStart()` должен быть вызван до цикла. Для `CAdminResult` — до вывода headers/rows.

### Admin list

```php
$tableId = 'vendor_items';
$sorting = new CAdminSorting($tableId, 'ID', 'DESC');
$adminList = new CAdminList($tableId, $sorting);

$result = ItemTable::getList([
    'select' => ['ID', 'NAME'],
    'filter' => $filter,
    'order' => [$by ?: 'ID' => strtoupper($order ?: 'DESC')],
]);

$adminResult = new CAdminResult($result, $tableId);
$adminResult->NavStart(20);

$adminList->NavText($adminResult->GetNavPrint('Элементы'));
```

В `CAdminResult::GetNavSize()` размер берётся из `SIZEN_<NavNum+1>`, session navigation storage или user option `list/<table_id>/page_size`.

### Modern grid

Если используется `Bitrix\Main\Grid\Grid`, сначала бери `getOrmParams()`: в этом core он уже включает `limit`/`offset`, когда у grid есть `PageNavigation`.

```php
$grid->processRequest();

$filter = $grid->getOrmFilter() ?? [];
$params = $grid->getOrmParams();

if ($grid->getPagination() !== null)
{
    $grid->getPagination()->setRecordCount(ItemTable::getCount($filter));
}

$grid->setRawRows(ItemTable::getList(array_merge(
    ['select' => ['ID', 'NAME']],
    $params
)));
```

Для прямого `main.ui.grid` можно передавать `NAV_OBJECT` с `PageNavigation`; компонент сам построит `NAV_STRING` через `main.pagenavigation`.

## AJAX, lazy load и catalog templates

Stock `catalog.section` templates в shop-core передают следующую страницу через:

```js
data['PAGEN_' + this.navParams.NavNum] = this.navParams.NavPageNomer + 1;
```

При диагностике “Показать ещё”/infinite scroll проверяй:
- `navParams.NavNum`, `NavPageNomer`, `NavPageCount` в JS;
- что ajax-запрос уходит в правильный `componentPath/ajax.php`;
- что `parameters` не устарели после filter/sort;
- что ответ возвращает `items`, `pagination`, `epilogue` и при необходимости новые `navParams`;
- что selector `[data-pagination-num="<NavNum>"]` реально есть в DOM;
- что cache key компонента учитывает page/filter/sort или корректно использует стандартный component cache.

## Диагностика симптомов

### Вторая страница пустая

Проверь:
1. Count и data-query используют один filter.
2. Текущая страница не вышла за `PAGE_COUNT` после изменения фильтра.
3. Для D7 `PageNavigation` record count задан до `initFromUri()` или страница нормализована после count.
4. Offset считается через `getOffset()`, limit — через `getLimit()`.
5. Нет смешивания `nTopCount` с полноценной пагинацией.
6. Sort стабильный: добавлен `ID`.

### Страницы дублируют или пропускают элементы

Чаще всего причина в нестабильном order: `SORT` или `DATE_CREATE` не уникальны. Добавь `ID` вторым/последним ключом сортировки и убедись, что фильтр не меняется между запросами.

### Две пагинации конфликтуют

Legacy-слой использует глобальный счётчик `NavNum` и параметры `PAGEN_1`, `PAGEN_2`. D7-слой использует строковый id вроде `nav-products`. Не хардкодь `PAGEN_1`, если на странице несколько списков. Для D7 задавай уникальный id каждому `PageNavigation`.

### После фильтра остаётся старая страница

Проверь session-сохранение `main/nav_page_in_session`, `SESS_PAGEN_*`, `ADMIN_PAGINATION_DATA`, `clear_nav=Y` в admin UI и удаление старых nav-параметров из URL. В публичном списке обычно при изменении filter/sort нужно сбрасывать страницу на 1.

### Не работает SEF-пагинация

Проверь:
- `SEF_MODE` в `main.pagenavigation`;
- `PageNavigation::addParams()` / `clearParams()`;
- `urlrewrite.php` и component route;
- отсутствие ручной склейки URL, которая оставляет старый `/nav-id/page-N/size-M/`.

### Admin page size не сохраняется

Проверь:
- `table_id` стабилен и безопасно нормализован;
- в запросе есть `SIZEN_<NavNum>`;
- `main/nav_page_in_session` не отключён, если ожидается session-память;
- user option `list/<table_id>/page_size`;
- для modern grid — `Bitrix\Main\Grid\Options::getNavParams()` и `setPageSize(...)`.

### Lazy load подгружает не ту страницу

Проверь `NavNum` в JS и PHP, `PAGEN_<NavNum>` в ajax payload, актуальность `parameters`, component cache и то, что при `deferredLoad`/cyclic loading template не сбрасывает `NavPageNomer` неожиданно.

## Cache/SEO side effects

- `CDBResult::NavStringForCache()` включает page/show-all в cache string; не выкидывай nav-параметры из cache key вручную.
- Component cache должен учитывать page, filter, sort и page size.
- При `SHOWALL` на больших каталогах легко получить memory/time проблемы; не включай “показать всё” без лимитов.
- SEO-политика для page > 1 зависит от проекта: canonical/noindex/prev-next/sitemap не трогай шаблонно. Сначала проверь текущие требования сайта и `seo-cache-access.md`.
- Composite/static HTML cache может отдавать старую навигацию после изменения filter/sort/template; проверяй clear cache и tagged cache по data source.

## Что нельзя делать

- Не использовать `nTopCount` как замену страницам.
- Не хардкодить `PAGEN_1`, когда на странице может быть больше одной навигации.
- Не вызывать `GetNavPrint()`/`GetPageNavString()` без предварительного `NavStart()` или nav-aware `GetList(...)`.
- Не строить `LIMIT/OFFSET` вручную, если уже есть `PageNavigation`.
- Не забывать `setRecordCount()` перед render `main.pagenavigation`.
- Не включать `allowAllRecords(true)` на больших публичных списках без продуктового ограничения.
- Не менять страницу/размер напрямую из `$_GET` без нормализации.
