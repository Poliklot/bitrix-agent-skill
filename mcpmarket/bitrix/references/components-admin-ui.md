# Components Admin Ui
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `components.md`

# Bitrix Компоненты — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с компонентами, CBitrixComponent, шаблонами, кешированием в компонентах, CComponentEngine или Edit Area.
>
> Audit note: ниже сверено с текущим `main/classes/general/component.php`. В этой версии класс компонента действительно ищется через diff `get_declared_classes()` после `include_once(class.php)`, а `startResultCache()` сам открывает tag cache при `BX_COMP_MANAGED_CACHE`.

## Содержание
- Структура компонента: .parameters.php, .description.php, class.php, шаблоны
- CBitrixComponent: жизненный цикл, onPrepareComponentParams, executeComponent
- Кеширование: startResultCache/endResultCache/abortResultCache, тегированный кеш
- Шаблоны: переменные, setFrameMode, AddEditAction, GetEditAreaId
- CComponentEngine: URL-роутинг, #VAR#-шаблоны, addGreedyPart
- ~KEY в arParams

---

## Компоненты

### Архитектурный смысл

Компонент в Bitrix — это **MVC-юнит**: модель (логика в `class.php`), вид (шаблон в `templates/`), параметры (`.parameters.php`). Компонент изолирован, переиспользуем, кешируем.

**Два подхода:**
- **Современный (`class.php`)** — определяет класс, расширяющий `CBitrixComponent`. Переопределяемые методы, автозагрузка, тестируемость.
- **Legacy (`component.php`)** — процедурный файл. Используется если `class.php` отсутствует.

Если `class.php` существует и содержит подкласс `CBitrixComponent`, Bitrix создаёт его экземпляр. Поиск идёт через `get_declared_classes()` после `include_once`: ядро перебирает новые классы, берёт подходящий подкласс `CBitrixComponent`, а если позже встретит более специфический наследник, может заменить ранее выбранный.

### Имя и путь компонента

```
bitrix:news.list
├── namespace: bitrix
├── name: news.list
└── path: /bitrix/news.list → bitrix/components/bitrix/news.list/
```

Поиск компонента: `local/components/` → `bitrix/components/`. Правило:
```
namespace:name.subname → /namespace/name.subname/
```

### Структура компонента

```
bitrix/components/vendor/my.component/
├── .description.php         ← мета-информация, иконка, путь в дереве
├── .parameters.php          ← описание параметров (для визуального редактора)
├── class.php                ← D7-класс компонента (рекомендуется)
├── component.php            ← legacy-режим (если нет class.php)
├── lang/
│   ├── ru/
│   │   └── class.php        ← переводы
│   └── en/
└── templates/
    ├── .default/            ← шаблон по умолчанию
    │   ├── template.php     ← HTML-шаблон
    │   ├── script.js
    │   ├── style.css
    │   ├── .parameters.php  ← параметры специфичные для шаблона
    │   └── lang/
    └── my_template/         ← кастомный шаблон (переопределяется в local/)
```

### .description.php

```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

$arComponentDescription = [
    'NAME'        => GetMessage('MY_COMPONENT_NAME'),
    'DESCRIPTION' => GetMessage('MY_COMPONENT_DESC'),
    'ICON'        => '/images/icon.png',
    'SORT'        => 20,
    'CACHE_PATH'  => 'Y',  // компонент поддерживает кеш по пути
    'PATH'        => [
        'ID'    => 'content',
        'CHILD' => ['ID' => 'my_group'],
    ],
];
```

### .parameters.php

```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();
/** @var array $arCurrentValues */

$arComponentParameters = [
    'GROUPS' => [
        'SETTINGS' => ['NAME' => 'Настройки'],
    ],
    'PARAMETERS' => [
        'IBLOCK_ID' => [
            'PARENT'  => 'SETTINGS',
            'NAME'    => 'ID инфоблока',
            'TYPE'    => 'STRING',
            'DEFAULT' => '',
        ],
        'CACHE_TIME' => ['DEFAULT' => 3600],  // стандартный параметр кеша
    ],
];
```

### class.php — современный компонент

```php
<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

use Bitrix\Main\Loader;
use Bitrix\Main\Localization\Loc;

Loader::includeModule('iblock');

class MyVendorComponent extends CBitrixComponent
{
    /**
     * Вызывается ДО executeComponent(). Нормализует входные параметры.
     * ВАЖНО: параметры автоматически HTML-экранируются после этого метода.
     * Для raw-значений используй $this->arParams['~KEY'].
     */
    public function onPrepareComponentParams($arParams): array
    {
        $arParams['IBLOCK_ID'] = (int)($arParams['IBLOCK_ID'] ?? 0);
        $arParams['CACHE_TIME'] = (int)($arParams['CACHE_TIME'] ?? 3600);
        return $arParams;
    }

    /**
     * Основная точка входа. По умолчанию вызывает __includeComponent() → component.php.
     * При наличии class.php лучше переопределить этот метод.
     */
    public function executeComponent(): mixed
    {
        // Кеширование
        if ($this->startResultCache($this->arParams['CACHE_TIME'])) {
            $this->arResult = $this->getData();

            // Управление кешем через теги (BX_COMP_MANAGED_CACHE)
            global $CACHE_MANAGER;
            $CACHE_MANAGER->RegisterTag('iblock_id_' . $this->arParams['IBLOCK_ID']);
        }

        // includeComponentTemplate() вызывает endResultCache() автоматически
        $this->includeComponentTemplate();

        return $this->arResult;
    }

    private function getData(): array
    {
        // логика выборки...
        return ['ITEMS' => []];
    }

    /**
     * Ключи параметров, которые войдут в signedParameters.
     * Нужно для безопасной передачи ID инфоблока в AJAX-запросах.
     */
    protected function listKeysSignedParameters(): array
    {
        return ['IBLOCK_ID'];
    }
}
```

### Кеширование компонентов — детали

Кеш компонента управляется тремя параметрами, которые Bitrix обрабатывает автоматически:
- `CACHE_TYPE`: `Y` = всегда кешировать, `N` = никогда, `A` = по системной настройке
- `CACHE_TIME`: время жизни в секундах
- Ключ кеша = `SITE_ID + LANGUAGE_ID + TEMPLATE_ID + component_name + template_name + all_params + timezone_offset`

```php
// Паттерн кеширования
public function executeComponent(): mixed
{
    // startResultCache() возвращает true при CACHE MISS (нужно выполнить)
    // и false при CACHE HIT (arResult уже восстановлен из кеша)
    if ($this->startResultCache()) {
        // Тут выполняется только при cache miss
        $userId = $this->request->getQuery('user_id');
        if (!$userId) {
            // КРИТИЧНО: если выходим досрочно — обязателен abortResultCache()
            // иначе незакрытый кеш сохранится как пустой
            $this->abortResultCache();
            return null;
        }

        $this->arResult = $this->loadData();
    }

    // includeComponentTemplate() автоматически вызывает endResultCache()
    // Кешируются: arResult, CSS/JS, NavNum, дочерние компоненты
    $this->includeComponentTemplate();

    return $this->arResult;
}

// Инвалидация кеша конкретного компонента
CBitrixComponent::clearComponentCache('vendor:my.component', SITE_ID);

// Тегированный кеш (управляемый кеш):
// После изменения инфоблока с ID=5 инвалидирует все компоненты с тегом
BXClearCache(true, '/bitrix/cache/...'); // низкоуровнево
// Через CACHE_MANAGER (если BX_COMP_MANAGED_CACHE defined):
global $CACHE_MANAGER;
$CACHE_MANAGER->ClearByTag('iblock_id_5');
```

Если компонент строит список с `NavNum`, `PAGEN_N`, `NavStart()`, `main.pagenavigation` или ajax “Показать ещё”, подгружай `pagination.md` вместе с этим файлом.

**Gotcha: `arParams['~KEY']`** — после `onPrepareComponentParams()` и `__prepareComponentParams()` все строковые параметры HTML-экранируются. Raw-значение доступно через `$this->arParams['~IBLOCK_ID']`. Это сделано для безопасности шаблонов.

**Gotcha: `arResultCacheKeys`** — после шаблона Bitrix урежет `arResult` до перечисленных ключей и уже этот сокращённый набор сохранит в кеш. Сам шаблон при этом ещё видит полный `arResult`.

```php
// Кешируем только часть arResult
$this->arResultCacheKeys = ['ITEMS', 'TOTAL_COUNT'];
// CURRENT_USER и другие personalised-данные не кешируются
```

### Шаблон компонента

```php
<?php
// templates/.default/template.php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) die();

/**
 * @var CBitrixComponentTemplate $this
 * @var array $arParams       параметры компонента (HTML-экранированы)
 * @var array $arResult       результат компонента
 * @var CBitrixComponent $component  объект компонента
 * @var CMain $APPLICATION
 * @var CUser $USER
 */

// Включает composite caching (статические блоки)
$this->setFrameMode(true);
?>
<div class="my-list">
    <?php foreach ($arResult['ITEMS'] as $item): ?>
        <?php
        // Кнопки редактирования/удаления в режиме правки
        $this->AddEditAction($item['ID'], $item['EDIT_LINK'], 'Редактировать');
        $this->AddDeleteAction($item['ID'], $item['DELETE_LINK'], 'Удалить', ['CONFIRM' => 'Удалить?']);
        ?>
        <div id="<?= $this->GetEditAreaId($item['ID']) ?>">
            <?= htmlspecialcharsEx($item['NAME']) ?>
        </div>
    <?php endforeach ?>
</div>
```

### Подключение компонента на странице

```php
<?php
// В .php-файле страницы (внутри шаблона сайта)
$APPLICATION->IncludeComponent(
    'vendor:my.component',  // имя компонента
    '',                     // имя шаблона ('' = .default)
    [                       // параметры
        'IBLOCK_ID'  => 5,
        'CACHE_TIME' => 3600,
    ],
    false                   // родительский компонент или false
);

// Из другого компонента (class.php)
$this->includeComponent(
    'bitrix:news.list',
    '.default',
    ['IBLOCK_ID' => $this->arParams['IBLOCK_ID']],
    $this  // передаём себя как родителя для наследования CSS/JS
);
```

### CComponentEngine — URL-роутинг в компонентах

`CComponentEngine` используется внутри компонента для определения текущей "страницы" по URL. Это Legacy-механизм, альтернатива D7-роутингу для компонентов.

```php
// В component.php или executeComponent()
$arUrlTemplates = [
    'list'   => 'catalog/',
    'section'=> 'catalog/#SECTION_CODE#/',
    'detail' => 'catalog/#SECTION_CODE#/#ELEMENT_CODE#/',
];

$arVariables = [];
$componentPage = CComponentEngine::parseComponentPath(
    $arParams['SEF_FOLDER'],  // базовый путь, например '/catalog/'
    $arUrlTemplates,
    $arVariables              // сюда запишутся SECTION_CODE и ELEMENT_CODE
    // 4й аргумент = requestURL, если false — берётся текущий
);

// $componentPage = 'detail' если URL = /catalog/phones/iphone-15/
// $arVariables['SECTION_CODE'] = 'phones'
// $arVariables['ELEMENT_CODE'] = 'iphone-15'

// Для URL с несколькими сегментами (путь категорий) пометить переменную "жадной"
$engine = new CComponentEngine($this);
$engine->addGreedyPart('SECTION_CODE');  // SECTION_CODE может содержать /
$componentPage = $engine->guessComponentPath($folder, $arUrlTemplates, $arVariables);
```

---

---

## Source: `templates.md`

# Шаблоны сайта

## Audit note

Проверено по текущему core:
- `www/bitrix/modules/main/classes/general/main.php`
- `www/bitrix/modules/main/lib/page/assetlocation.php`
- `www/bitrix/modules/main/classes/general/component_template.php`
- `www/bitrix/modules/main/tools.php`

## Структура шаблона

```
/local/templates/<template_name>/        (или /bitrix/templates/)
├── header.php          ← верхняя часть страницы (до <body> / начало тела)
├── footer.php          ← нижняя часть страницы
├── styles.css          ← основные стили шаблона
├── script.js           ← основные скрипты шаблона
├── .parameters.php     ← настройки шаблона (области, стили)
├── images/             ← картинки шаблона
├── components/         ← кастомизированные шаблоны компонентов
│   └── bitrix/         ← пространство имён компонента
│       └── news.list/  ← имя компонента
│           └── my_tpl/ ← имя шаблона компонента
│               ├── template.php
│               └── style.css
└── areas/              ← динамические области (необязательно)
```

---

## header.php и footer.php

### Типичный `header.php`

```php
<?php
// Получить данные страницы, задать мета-теги до ShowHead()
$APPLICATION->SetTitle('Главная');
?><!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <?php $APPLICATION->ShowHead(); ?>      <!-- robots, keywords, description, canonical, CSS, JS -->
    <title><?php $APPLICATION->ShowTitle(); ?></title>
</head>
<body class="<?php echo SITE_TEMPLATE_ID; ?>">
<?php $APPLICATION->ShowPanel(); ?>         <!-- панель редактирования (для авторизованных) -->
```

### Типичный `footer.php`

```php
<?php $APPLICATION->ShowBodyScripts(); ?>   <!-- JS в конце body -->
</body>
</html>
```

---

## $APPLICATION — работа с шаблоном

### Заголовок и мета

```php
// В PHP-файле страницы или component.php — до вывода
global $APPLICATION;

$APPLICATION->SetTitle('Название страницы');

// Мета-теги (выводятся через ShowHead() в header.php)
$APPLICATION->SetPageProperty('keywords',    'ключевые, слова');
$APPLICATION->SetPageProperty('description', 'Описание страницы');
$APPLICATION->SetPageProperty('robots',      'noindex, nofollow');
$APPLICATION->SetPageProperty('canonical',   'https://example.com/page/');

// Прочитать
$title = $APPLICATION->GetTitle();                  // текущий заголовок
$desc  = $APPLICATION->GetPageProperty('description');
```

### Хлебные крошки

```php
// Добавить элемент в цепочку (в component.php или .php страницы)
$APPLICATION->AddChainItem('Каталог', '/catalog/');
$APPLICATION->AddChainItem('Категория', '/catalog/chairs/');
$APPLICATION->AddChainItem('Товар');  // без URL = текущая страница

// Стандартный способ вывода — компонент bitrix:breadcrumb.
// Важно: GetNavChain() в текущем core возвращает готовую HTML-строку, а не массив элементов.
echo $APPLICATION->GetNavChain();
```

---

## Подключение JS и CSS

### D7 Asset (правильный способ)

```php
use Bitrix\Main\Page\Asset;
use Bitrix\Main\Page\AssetLocation;

$asset = Asset::getInstance();

// Добавить CSS
$asset->addCss('/local/templates/my_tpl/styles/custom.css');

// Добавить JS-файл
$asset->addJs('/local/templates/my_tpl/js/custom.js');

// Инлайн-строка в head (после JS-ядра, по умолчанию)
$asset->addString('<script>var myVar = "value";</script>');

// Указать место вывода
$asset->addString(
    '<script>console.log("after js");</script>',
    false,                           // $unique — не дублировать
    AssetLocation::AFTER_JS          // константа места
);
```

### Константы AssetLocation

| Константа | Где выводится |
|-----------|--------------|
| `BEFORE_CSS` | перед CSS |
| `AFTER_CSS` | после CSS, до JS |
| `AFTER_JS_KERNEL` | после JS-ядра Bitrix (по умолчанию) |
| `AFTER_JS` | в самом конце `<head>` |
| `BODY_END` | перед `</body>` |

### Legacy-способы (встречаются в старом коде)

```php
// В шаблоне или .php файле
$APPLICATION->AddHeadString('<link rel="stylesheet" href="/css/style.css">');
$APPLICATION->AddHeadScript('/js/script.js');

// Из шаблона компонента — через $this
$this->addExternalCss($this->GetFolder() . '/style.css');
$this->addExternalJs($this->GetFolder() . '/script.js');
```

---

## .parameters.php — настройки шаблона

Определяет доступные CSS-стили и области для сайта:

```php
<?php
// /local/templates/my_tpl/.parameters.php

$arTemplateParameters = [];      // параметры, доступные в $arParams шаблона

// Области шаблона (можно включать компоненты программно)
$arAreas = [
    'sidebar' => [
        'name'        => 'Боковая панель',
        'type'        => 'component',
        'component'   => 'bitrix:menu',
        'template'    => 'sidebar',
        'params'      => ['MAX_LEVEL' => 2],
        'separator'   => 'delim',
    ],
];
```

---

## Шаблон компонента

### Расположение

```
/local/templates/<site_tpl>/components/<namespace>/<component>/<template_name>/
/local/components/<namespace>/<component>/templates/<template_name>/   ← приоритет выше
/bitrix/components/<namespace>/<component>/templates/<template_name>/
```

### Доступные переменные в `template.php`

```php
// Переменные, доступные без объявления:
$arResult       // данные из компонента (заполнены в component.php)
$arParams       // параметры компонента (переданы при вызове)
$this           // объект шаблона CBitrixComponentTemplate

// Путь к шаблону компонента
$this->GetFolder()                      // /local/templates/my_tpl/components/...

// Путь к файлам site-template через $APPLICATION
global $APPLICATION;
$APPLICATION->GetTemplatePath('/images/logo.svg');

// Добавить CSS/JS из шаблона компонента
$this->addExternalCss($this->GetFolder() . '/style.css');
$this->addExternalJs($this->GetFolder() . '/script.js');
```

### Переменные окружения в любом шаблоне

```php
SITE_ID           // 's1' — идентификатор сайта
SITE_DIR          // '/' — корень сайта (для мультисайтов может быть '/ru/')
SITE_TEMPLATE_ID  // 'my_tpl' — имя шаблона
SITE_TEMPLATE_PATH // '/local/templates/my_tpl' — путь к шаблону
LANGUAGE_ID       // 'ru' — язык сайта
LANG              // 'ru' — то же самое
```

---

## component_epilog.php и component_prolog.php

Выполняются до/после шаблона компонента, но **вне кешируемого блока**:

```php
// /local/templates/my_tpl/components/bitrix/news.list/my_tpl/component_prolog.php
// Выполняется ВСЕГДА, даже при выдаче из кеша
// Используется для: AddChainItem, SetTitle, SetPageProperty

global $APPLICATION;
if (!empty($arResult['META_TITLE'])) {
    $APPLICATION->SetTitle($arResult['META_TITLE']);
}
```

```php
// component_epilog.php — выполняется после шаблона
// Используется для: SEO-данных, финальных изменений
```

---

## Работа с HTTP-статусом и редиректами

```php
global $APPLICATION;

// Установить HTTP-статус страницы
$APPLICATION->SetStatus('404 Not Found');
$APPLICATION->SetStatus('403 Forbidden');

// Редирект
LocalRedirect('/new-url/');                                   // 302 Found
LocalRedirect('/new-url/', false, '301 Moved Permanently');   // 301
LocalRedirect('/new-url/', true, '302 Found');                // true = skip_security_check

// D7-способ
use Bitrix\Main\Application;
$response = Application::getInstance()->getContext()->getResponse()->redirectTo('/new-url/');
$response->flush('');
```

---

## Composite cache и шаблоны

Composite (статический HTML-кеш) кеширует **весь HTML страницы**. Части, которые не должны кешироваться (корзина, имя пользователя), выносятся в динамические блоки:

```php
// В шаблоне компонента или template.php:
if ($this->__component->StartResultCache()) {
    // кешируемая часть
    ...
    $this->__component->EndResultCache();
} else {
    // при выдаче из composite-кеша эта часть НЕ выполняется
}
```

Компонент в **Frame-режиме** (динамический блок, не кешируется composite):

```php
// В component.php
$this->setFrameMode(true);   // этот компонент всегда рендерится динамически
```

### Что НЕ кешировать composite:
- Корзина, сумма заказов
- Имя авторизованного пользователя
- Персональные данные
- CSRF-токены

---

## Gotchas

- `SetTitle`, `SetPageProperty` надо вызывать **до** того как `ShowHead()` сработает в header.php — т.е. в component_prolog.php, не в template.php
- У `CBitrixComponentTemplate` в текущем core нет подтверждённого `$this->GetTemplatePath(...)`: для URL ресурса шаблона компонента используй `$this->GetFolder() . '/img.png'`
- Если нужен серверный путь к ресурсу шаблона компонента, собирай его явно: `$_SERVER['DOCUMENT_ROOT'] . $this->GetFolder() . '/img.png'`
- `Asset::addCss/addJs` дедублирует по пути — можно вызывать несколько раз без дублей
- В `component_epilog.php` переменная `$arResult` доступна, в `component_prolog.php` — нет (компонент ещё не выполнен)
- `SITE_TEMPLATE_PATH` — URL-путь к шаблону (без хоста), удобен для построения URL ресурсов

---

## Source: `admin-ui.md`

# Bitrix Admin UI — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с созданием или изменением страниц в битриксовой админке: списки, формы редактирования, фильтры, групповые действия, меню, права, кастомные типы пользовательских полей.

## Audit note

Проверено по текущему core:
- `www/bitrix/modules/main/interface/admin_list.php`
- `www/bitrix/modules/main/interface/admin_form.php`
- `www/bitrix/modules/main/interface/admin_filter.php`
- `www/bitrix/modules/main/interface/admin_tabcontrol.php`
- `www/bitrix/modules/main/interface/admin_lib.php`
- `www/bitrix/modules/main/include/prolog_admin_*.php`

Главный вывод: админский UI в этом core по-прежнему опирается прежде всего на legacy-слой из `main/interface/*`, а не на какой-то единый новый D7 admin framework.

## Содержание
- Анатомия admin-страницы: prolog/epilog
- CAdminList — список с сортировкой, фильтром, пагинацией
- CAdminSorting, CAdminResult, CAdminFilter
- CAdminListRow — поля строки, действия
- Групповые действия (GroupAction)
- CAdminContextMenu — кнопки контекстного меню
- Форма редактирования: CAdminTabControl vs CAdminForm
- Admin-меню модуля (menu.php)
- Права доступа модуля
- Кастомные типы пользовательских полей (OnUserTypeBuildList)
- Gotchas

---

## Анатомия admin-страницы

Каждая страница в `/bitrix/admin/` состоит из двух частей:

```
prolog_admin_before.php  ← инициализация: сессия, авторизация, константы
  [ваш PHP: данные, actions, объекты CAdminList / CAdminTabControl]
prolog_admin_after.php   ← вывод шапки, JS, CSS
  [ваш PHP+HTML: форма, фильтр, таблица]
epilog_admin.php         ← вывод подвала
```

```php
<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_before.php';

// Проверка прав
$right = $APPLICATION->GetGroupRight('my.module'); // 'D','R','W','X' или ''
if ($right === 'D') {
    $APPLICATION->AuthForm('Доступ запрещён');
}

// ... ваша логика (объекты, actions, фильтр) ...

require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_after.php';

// ... HTML/PHP разметка ...

require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/epilog_admin.php';
?>
```

---

## Страница-список: полный шаблон

```php
<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_before.php';

use Vendor\MyModule\MyTable;
use Bitrix\Main\Loader;

Loader::requireModule('my.module');
IncludeModuleLangFile(__FILE__);

$right = $APPLICATION->GetGroupRight('my.module');
if ($right === 'D') $APPLICATION->AuthForm(GetMessage('ACCESS_DENIED'));

// ── 1. Сортировка ──────────────────────────────────────────────────────────
$tableId = 'tbl_mymodule_items';
$oSort   = new CAdminSorting($tableId, 'ID', 'desc');
// new CAdminSorting($tableId, $defaultBy, $defaultOrder, $byParamName='by', $orderParamName='order')
// Читает GET-параметры by/order, кеширует в сессии

$lAdmin = new CAdminList($tableId, $oSort);

// ── 2. Фильтр ──────────────────────────────────────────────────────────────
// ВАЖНО: имена переменных фильтра — глобальные (global $$f внутри InitFilter)
$arFilterFields = ['find_id', 'find_name', 'find_active', 'find_date_from', 'find_date_to'];
$lAdmin->InitFilter($arFilterFields);
// После вызова доступны глобальные переменные: $find_id, $find_name и т.д.
foreach ($arFilterFields as $f) global $$f;

// ── 3. Групповые действия ──────────────────────────────────────────────────
if (($arIDs = $lAdmin->GroupAction()) && $right >= 'W' && check_bitrix_sessid()) {
    if ($_REQUEST['action_target'] === 'selected') {
        // "применить ко всем отфильтрованным"
        $arIDs = MyTable::getList(['select' => ['ID'], 'filter' => $arFilter])->fetchColumn();
    }
    foreach ($arIDs as $id) {
        $id = (int)$id;
        if (!$id) continue;
        switch ($_REQUEST['action']) {
            case 'delete':
                $r = MyTable::delete($id);
                if (!$r->isSuccess()) {
                    $lAdmin->AddGroupError(implode(', ', $r->getErrorMessages()), $id);
                }
                break;
            case 'activate':
                MyTable::update($id, ['ACTIVE' => 'Y']);
                break;
        }
    }
}

// ── 4. Инлайн-редактирование одной строки ─────────────────────────────────
if ($lAdmin->EditAction() && $right >= 'W' && check_bitrix_sessid()) {
    foreach ($lAdmin->GetEditFields() as $id => $arFields) {
        $id = (int)$id;
        $r = MyTable::update($id, [
            'NAME'   => trim($arFields['NAME'] ?? ''),
            'ACTIVE' => $arFields['ACTIVE'] ?? 'N',
        ]);
        if (!$r->isSuccess()) {
            $lAdmin->AddUpdateError(implode(', ', $r->getErrorMessages()), $id);
        }
    }
}

// ── 5. Составить фильтр для запроса ───────────────────────────────────────
$arFilter = [];
if ($find_id)         $arFilter['=ID']    = (int)$find_id;
if ($find_name)       $arFilter['%NAME']  = $find_name;
if ($find_active)     $arFilter['=ACTIVE'] = $find_active;
if ($find_date_from)  $arFilter['>=DATE_CREATE'] = $find_date_from;
if ($find_date_to)    $arFilter['<=DATE_CREATE']  = $find_date_to;

// ── 6. Запрос к БД ────────────────────────────────────────────────────────
global $by, $order; // установлены CAdminSorting
$dbResult = MyTable::getList([
    'select' => ['ID', 'NAME', 'ACTIVE', 'DATE_CREATE', 'PRICE'],
    'filter' => $arFilter,
    'order'  => [$by ?: 'ID' => strtoupper($order ?: 'DESC')],
]);

// Обернуть в CAdminResult для пагинации
$rsData = new CAdminResult($dbResult, $tableId);
$rsData->NavStart(20); // 20 записей на страницу

$lAdmin->NavText($rsData->GetNavPrint(GetMessage('MY_MODULE_PAGES')));

// ── 7. Заголовки колонок ───────────────────────────────────────────────────
$lAdmin->AddHeaders([
    ['id' => 'ID',          'content' => 'ID',           'sort' => 'ID',          'default' => true],
    ['id' => 'NAME',        'content' => 'Название',     'sort' => 'NAME',        'default' => true],
    ['id' => 'ACTIVE',      'content' => 'Активность',   'sort' => 'ACTIVE',      'default' => true],
    ['id' => 'DATE_CREATE', 'content' => 'Дата',         'sort' => 'DATE_CREATE', 'default' => true],
    ['id' => 'PRICE',       'content' => 'Цена',         'sort' => 'PRICE',       'default' => true, 'align' => 'right'],
    ['id' => 'ACTIONS',     'content' => '',             'default' => true],
]);

// ── 8. Строки ──────────────────────────────────────────────────────────────
$editUrl = '/bitrix/admin/mymodule_item_edit.php?lang=' . LANGUAGE_ID;

while ($res = $rsData->getNext()) {
    $id = (int)$res['ID'];

    // AddRow($id, $arRes, $editLink, $editTitle)
    $row = &$lAdmin->AddRow($id, $res, $editUrl . '&ID=' . $id, 'Редактировать');

    // Простое HTML-поле (view only)
    $row->AddViewField('NAME', '<a href="' . $editUrl . '&ID=' . $id . '">' . htmlspecialcharsEx($res['NAME']) . '</a>');

    // Текстовое поле + inline edit
    $row->AddField('ACTIVE', ($res['ACTIVE'] === 'Y' ? 'Да' : 'Нет'));
    $row->AddSelectField('ACTIVE', ['Y' => 'Да', 'N' => 'Нет']);

    $row->AddField('DATE_CREATE', htmlspecialcharsEx($res['DATE_CREATE']));
    $row->AddField('PRICE', htmlspecialcharsEx($res['PRICE']));

    // Действия строки (выпадающее меню)
    if ($right >= 'W') {
        $row->AddActions([
            [
                'ICON'   => 'edit',
                'TEXT'   => 'Редактировать',
                'ACTION' => "window.location='" . $editUrl . '&ID=' . $id . "'",
                'DEFAULT' => true, // двойной клик по строке
            ],
            [
                'ICON'   => 'delete',
                'TEXT'   => 'Удалить',
                'ACTION' => "if(confirm('Удалить запись?')) window.location='/bitrix/admin/mymodule_item_list.php?action=delete&ID={$id}&" . bitrix_sessid_get() . "'",
            ],
        ]);
    }
}

// ── 9. Подвал, групповые действия, контекстное меню ───────────────────────
$lAdmin->AddFooter([
    ['title' => 'Всего выбрано', 'value' => $rsData->SelectedRowsCount()],
    ['counter' => true, 'title' => 'Отмечено', 'value' => '0'],
]);

if ($right >= 'W') {
    $lAdmin->AddGroupActionTable([
        'delete'   => 'Удалить',
        'activate' => 'Активировать',
    ]);
}

$lAdmin->AddAdminContextMenu([
    [
        'TEXT'  => 'Добавить',
        'TITLE' => 'Новая запись',
        'LINK'  => $editUrl,
        'ICON'  => 'btn_new',
    ],
]);

$lAdmin->CheckListMode(); // обрабатывает экспорт в Excel и настройку колонок

// ── 10. Вывод ──────────────────────────────────────────────────────────────
$APPLICATION->SetTitle('Список записей');
require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_after.php';
?>

<form name="form1" method="GET" action="<?= $APPLICATION->GetCurPage() ?>">
<?php
// Фильтр
$oFilter = new CAdminFilter($tableId . '_filter', [
    'ID',
    'Название',
    'Активность',
    'Дата создания',
]);
$oFilter->Begin();
?>
<tr>
    <td>ID:</td>
    <td><input type="text" name="find_id" size="20" value="<?= htmlspecialcharsbx($find_id) ?>"></td>
</tr>
<tr>
    <td>Название:</td>
    <td><input type="text" name="find_name" size="40" value="<?= htmlspecialcharsbx($find_name) ?>"></td>
</tr>
<tr>
    <td>Активность:</td>
    <td><?= SelectBoxFromArray('find_active', ['Y' => 'Да', 'N' => 'Нет'], $find_active, 'Все') ?></td>
</tr>
<tr>
    <td>Дата создания:</td>
    <td><?= CalendarPeriod('find_date_from', htmlspecialcharsbx($find_date_from), 'find_date_to', htmlspecialcharsbx($find_date_to), 'form1', 'Y') ?></td>
</tr>
<?php
$oFilter->Buttons(['table_id' => $tableId, 'url' => $APPLICATION->GetCurPage(), 'form' => 'form1']);
$oFilter->End();
?>
</form>

<?php
$lAdmin->DisplayList();

require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/epilog_admin.php';
?>
```

---

## Страница редактирования: CAdminTabControl (raw HTML)

Используй `CAdminTabControl` когда нужен полный контроль над HTML полей.

```php
<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_before.php';

use Vendor\MyModule\MyTable;
use Bitrix\Main\Loader;

Loader::requireModule('my.module');
IncludeModuleLangFile(__FILE__);

$right = $APPLICATION->GetGroupRight('my.module');
if ($right === 'D') $APPLICATION->AuthForm('Доступ запрещён');

// ── Определить табы ────────────────────────────────────────────────────────
$aTabs = [
    ['DIV' => 'edit1', 'TAB' => 'Основное', 'ICON' => 'main_user_edit', 'TITLE' => 'Основные поля'],
    ['DIV' => 'edit2', 'TAB' => 'Дополнительно', 'ICON' => 'main_user_edit', 'TITLE' => 'Доп. настройки'],
];
$tabControl = new CAdminTabControl('tabControl', $aTabs);
$message = null;

// ── Сохранение ────────────────────────────────────────────────────────────
$ID = (int)($_REQUEST['ID'] ?? 0);

if (
    (!empty($_REQUEST['save']) || !empty($_REQUEST['apply']))
    && $_SERVER['REQUEST_METHOD'] === 'POST'
    && $right >= 'W'
    && check_bitrix_sessid()
) {
    $arFields = [
        'NAME'    => trim($_POST['NAME'] ?? ''),
        'PRICE'   => (float)($_POST['PRICE'] ?? 0),
        'ACTIVE'  => isset($_POST['ACTIVE']) ? 'Y' : 'N',
        'SORT'    => (int)($_POST['SORT'] ?? 500),
        'SECTION_ID' => (int)($_POST['SECTION_ID'] ?? 0),
    ];

    if (empty($arFields['NAME'])) {
        $message = new CAdminMessage('Название обязательно');
    } else {
        $r = $ID > 0
            ? MyTable::update($ID, $arFields)
            : MyTable::add($arFields);

        if ($r->isSuccess()) {
            $newId = $ID > 0 ? $ID : $r->getId();
            if (!empty($_REQUEST['save'])) {
                LocalRedirect('/bitrix/admin/mymodule_item_list.php?lang=' . LANGUAGE_ID);
            }
            LocalRedirect('/bitrix/admin/mymodule_item_edit.php?lang=' . LANGUAGE_ID . '&ID=' . $newId . '&' . $tabControl->ActiveTabParam());
        } else {
            $message = new CAdminMessage(implode(', ', $r->getErrorMessages()));
        }
    }
}

// ── Загрузить запись ───────────────────────────────────────────────────────
if ($ID > 0) {
    $res = MyTable::getById($ID)->fetch();
    if (!$res) {
        $message = new CAdminMessage("Запись #$ID не найдена");
        $ID = 0;
    }
    $APPLICATION->SetTitle("Редактирование записи #$ID");
} else {
    $res = ['NAME' => '', 'PRICE' => 0, 'ACTIVE' => 'Y', 'SORT' => 500, 'SECTION_ID' => 0];
    $APPLICATION->SetTitle('Новая запись');
}

// Если была ошибка POST — восстановить из формы
if (isset($bVarsFromForm) && $bVarsFromForm) {
    $res = array_intersect_key($_POST, $res);
}

require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_after.php';

// ── Контекстное меню ──────────────────────────────────────────────────────
$aMenu = [
    ['TEXT' => 'К списку', 'LINK' => '/bitrix/admin/mymodule_item_list.php?lang=' . LANGUAGE_ID, 'ICON' => 'btn_list'],
];
if ($ID > 0 && $right >= 'W') {
    $aMenu[] = [
        'TEXT'   => 'Удалить',
        'LINK'   => "javascript:if(confirm('Удалить?')) window.location='/bitrix/admin/mymodule_item_list.php?action=delete&ID={$ID}&" . bitrix_sessid_get() . "'",
        'ICON'   => 'btn_delete',
    ];
}
(new CAdminContextMenu($aMenu))->Show();

if ($message) echo $message->Show();
?>

<form method="POST" action="<?= $APPLICATION->GetCurPage() ?>" name="post_form">
<?= bitrix_sessid_post() ?>
<input type="hidden" name="ID" value="<?= $ID ?>">
<input type="hidden" name="lang" value="<?= LANGUAGE_ID ?>">

<?php $tabControl->Begin(); ?>

<?php
// ── Таб 1: Основное ────────────────────────────────────────────────────────
$tabControl->BeginNextTab();
?>
<tr class="adm-detail-required-field">
    <td width="40%">Название:</td>
    <td><input type="text" name="NAME" size="50" maxlength="255" value="<?= htmlspecialcharsbx($res['NAME']) ?>"></td>
</tr>
<tr>
    <td>Цена:</td>
    <td><input type="text" name="PRICE" size="15" value="<?= htmlspecialcharsbx($res['PRICE']) ?>"></td>
</tr>
<tr>
    <td>Активность:</td>
    <td><input type="checkbox" name="ACTIVE" value="Y" <?= $res['ACTIVE'] === 'Y' ? 'checked' : '' ?>></td>
</tr>
<tr>
    <td>Сортировка:</td>
    <td><input type="text" name="SORT" size="5" value="<?= (int)$res['SORT'] ?>"></td>
</tr>

<?php
// ── Таб 2: Дополнительно ───────────────────────────────────────────────────
$tabControl->BeginNextTab();
?>
<tr>
    <td>Раздел ID:</td>
    <td><input type="text" name="SECTION_ID" size="10" value="<?= (int)$res['SECTION_ID'] ?>"></td>
</tr>

<?php
$tabControl->EndTab();
$tabControl->Buttons([
    'disabled' => $right < 'W',
    'back_url' => '/bitrix/admin/mymodule_item_list.php?lang=' . LANGUAGE_ID,
]);
$tabControl->End();
?>
</form>
<?php $tabControl->ShowWarnings('post_form', $message); ?>

<?php require_once $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/epilog_admin.php'; ?>
```

---

## Страница редактирования: CAdminForm (высокоуровневый API)

`CAdminForm extends CAdminTabControl` добавляет удобные методы для стандартных полей. Используй вместо raw HTML когда структура полей стандартная.

```php
$aTabs = [['DIV' => 'edit1', 'TAB' => 'Основное', 'ICON' => 'main_user_edit', 'TITLE' => 'Поля']];
$tabControl = new CAdminForm('myform', $aTabs);

$tabControl->Begin(['FORM_ATTRIBUTES' => 'enctype="multipart/form-data"']);
$tabControl->BeginNextFormTab();

// Текстовое поле
// AddEditField($id, $label, $required, $arParams, $value)
$tabControl->AddEditField('NAME', 'Название', true, ['size' => 50, 'maxlength' => 255], $res['NAME']);

// Выпадающий список
// AddDropDownField($id, $label, $required, $arSelect, $value, $arParams)
$tabControl->AddDropDownField('ACTIVE', 'Активность', false, ['Y' => 'Да', 'N' => 'Нет'], $res['ACTIVE']);

// Текстовая область
// AddTextField($id, $label, $value, $arParams, $required)
$tabControl->AddTextField('DESCRIPTION', 'Описание', $res['DESCRIPTION'], ['rows' => 5, 'cols' => 60]);

// Чекбокс
// AddCheckBoxField($id, $label, $required, $value, $checked, $arParams)
$tabControl->AddCheckBoxField('IS_FEATURED', 'Рекомендуемый', false, 'Y', $res['IS_FEATURED'] === 'Y');

// Поле даты с календарём
// AddCalendarField($id, $label, $value, $required)
$tabControl->AddCalendarField('DATE_ACTIVE_FROM', 'Активен с', $res['DATE_ACTIVE_FROM']);

// Файл
// AddFileField($id, $label, $value, $arParams, $required)
$tabControl->AddFileField('PREVIEW_PICTURE', 'Превью', $res['PREVIEW_PICTURE']);

// Только просмотр (нет input)
// AddViewField($id, $label, $html, $required)
$tabControl->AddViewField('DATE_CREATE', 'Дата создания', htmlspecialcharsEx($res['DATE_CREATE']));

// Разделитель / заголовок секции
$tabControl->AddSection('sec1', 'Дополнительные поля');

$tabControl->Buttons([
    'disabled' => $right < 'W',
    'back_url'  => '/bitrix/admin/mymodule_item_list.php?lang=' . LANGUAGE_ID,
]);
$tabControl->End();
```

---

## Методы CAdminTabControl — быстрая таблица

| Метод | Описание |
|-------|----------|
| `Begin($arParams)` | Открывает `<form>` (для CAdminForm); у CAdminTabControl — нет формы, пиши HTML сам |
| `BeginNextTab()` | Переключиться на следующий таб (raw HTML) |
| `BeginNextFormTab()` | Переключиться на следующий таб (CAdminForm) |
| `EndTab()` | Закрыть текущий таб |
| `Buttons($arParams)` | Кнопки Сохранить/Применить/Отмена. `disabled` — отключить; `back_url` — куда после отмены |
| `End()` | Закрыть вкладочный блок |
| `ShowWarnings($formName, $message)` | Показать сообщения об ошибках (передать объект CAdminMessage) |
| `ActiveTabParam()` | URL-параметр для сохранения активного таба после redirect |

---

## Admin-меню модуля

Файл `local/modules/vendor.mymodule/admin/menu.php` — возвращает `$aMenu`.

```
local/modules/vendor.mymodule/
└── admin/
    └── menu.php    ← регистрируется автоматически при установке модуля
```

```php
<?php
// local/modules/vendor.mymodule/admin/menu.php
IncludeModuleLangFile(__FILE__);

$right = $APPLICATION->GetGroupRight('vendor.mymodule');
if ($right === 'D') return false; // скрыть меню если нет прав

$aMenu = [
    'parent_menu' => 'global_menu_services', // куда прицепить: global_menu_services | global_menu_store | ...
    'section'     => 'vendor_mymodule',       // уникальный ID секции
    'sort'        => 100,
    'module_id'   => 'vendor.mymodule',
    'text'        => GetMessage('MY_MODULE_MENU'),
    'title'       => GetMessage('MY_MODULE_MENU_TITLE'),
    'icon'        => 'main_menu_icon',          // CSS-класс иконки
    'page_icon'   => 'main_page_icon',
    'items_id'    => 'menu_vendor_mymodule',
    'items' => [
        [
            'text'     => GetMessage('MY_MODULE_ITEMS_LIST'),
            'url'      => 'mymodule_item_list.php?lang=' . LANGUAGE_ID,
            'title'    => GetMessage('MY_MODULE_ITEMS_LIST_TITLE'),
            'items_id' => 'menu_mymodule_items',
            'more_url' => ['mymodule_item_edit.php'], // страницы, при которых пункт остаётся активным
        ],
    ],
];

// Пункт настроек — только для W и выше
if ($right >= 'W') {
    $aMenu['items'][] = [
        'text'  => 'Настройки',
        'url'   => 'mymodule_settings.php?lang=' . LANGUAGE_ID,
        'title' => 'Настройки модуля',
    ];
}

return $aMenu;
?>
```

### Доступные `parent_menu` (куда вставлять)

| Значение | Раздел |
|----------|--------|
| `global_menu_content` | Контент |
| `global_menu_services` | Сервисы |
| `global_menu_store` | Интернет-магазин |
| `global_menu_crm` | CRM |
| `global_menu_marketing` | Маркетинг |
| `global_menu_settings` | Настройки |

---

## Права доступа модуля

```php
// install/index.php — регистрация прав в InstallDB
ModuleManager::registerModule($this->MODULE_ID);

// Получение уровня прав для текущего пользователя:
$right = $APPLICATION->GetGroupRight('my.module');
// Возможные значения: 'D' (нет доступа), 'R' (чтение), 'W' (запись), 'X' (полный)
// Сравнение: $right >= 'W' — есть права на запись
// 'D' < 'R' < 'W' < 'X' — ASCII-сравнение работает корректно

// Проверка в admin-странице:
if ($right === 'D') {
    $APPLICATION->AuthForm('Доступ запрещён'); // редирект на форму входа
}

// Разграничение в коде:
if ($right >= 'W') { /* редактирование */ }
if ($right === 'X') { /* полный доступ, например настройки */ }
```

---

## Кастомные типы пользовательских полей

Пользовательские поля (UF_*) для HL-блоков, профилей пользователей, инфоблоков.

### Новый D7 способ (BaseType)

```php
// local/modules/vendor.mymodule/lib/UserField/ColorType.php
namespace Vendor\MyModule\UserField;

use Bitrix\Main\UserField\Types\BaseType;

class ColorType extends BaseType
{
    // USER_TYPE_ID — уникальный идентификатор типа
    protected const USER_TYPE_ID = 'vendor_color';

    // Тип колонки в БД: varchar(255) | int | double | text | datetime | date | char
    public static function getDbColumnType(): string
    {
        return 'varchar(255)';
    }

    // Метаданные типа — что показывается в списке типов при создании поля
    protected static function getDescription(): array
    {
        return [
            'DESCRIPTION'     => 'Цвет (HEX)',
            'BASE_TYPE'       => 'string', // string | int | double | datetime | date | file | enum
        ];
    }

    // HTML для просмотра значения в публичной части и в списке
    public static function renderAdminListView(array $userField, ?array $additionalParameters): string
    {
        $value = $userField['VALUE'] ?? '';
        if (!$value) return '';
        $safe = htmlspecialcharsEx($value);
        return '<span style="display:inline-block;width:16px;height:16px;background:' . $safe . ';border:1px solid #ccc;vertical-align:middle;"></span> ' . $safe;
    }

    // HTML input для редактирования в форме (edit form)
    public static function renderEditForm(array $userField, ?array $additionalParameters): string
    {
        $fieldName  = htmlspecialcharsbx($userField['FIELD_NAME']);
        $value      = htmlspecialcharsbx($userField['VALUE'] ?? '');
        $attributes = $userField['MULTIPLE'] === 'Y' ? ' multiple' : '';

        return '<input type="text" name="' . $fieldName . '" value="' . $value . '" placeholder="#RRGGBB"' . $attributes . ' pattern="^#[0-9A-Fa-f]{6}$">';
    }

    // HTML input для инлайн-редактирования в списке
    public static function renderAdminListEdit(array $userField, ?array $additionalParameters)
    {
        return self::renderEditForm($userField, $additionalParameters);
    }

    // HTML для фильтра в списке
    public static function renderFilter(array $userField, ?array $additionalParameters): string
    {
        $fieldName = 'find_' . htmlspecialcharsbx($userField['FIELD_NAME']);
        $value     = htmlspecialcharsbx($additionalParameters['VALUE'] ?? '');
        return '<input type="text" name="' . $fieldName . '" value="' . $value . '" placeholder="#RRGGBB" size="15">';
    }

    // HTML настроек типа (в форме создания поля)
    public static function renderSettings($userField, ?array $additionalParameters, $varsFromForm): string
    {
        // Можно добавить специфичные настройки — например, палитра цветов
        return '';
    }

    // Валидация значения при сохранении
    public static function checkFields(array $userField, $value): array
    {
        $errors = [];
        if (!empty($value) && !preg_match('/^#[0-9A-Fa-f]{6}$/', $value)) {
            $errors[] = ['id' => $userField['FIELD_NAME'], 'text' => 'Некорректный формат HEX-цвета'];
        }
        return $errors; // пустой массив = нет ошибок
    }

    // Подготовка настроек (нормализация) при сохранении типа
    public static function prepareSettings($userField): array
    {
        return $userField['SETTINGS'] ?? [];
    }
}
```

### Регистрация через событие

```php
// local/modules/vendor.mymodule/include.php
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandler(
    'main',
    'OnUserTypeBuildList',
    ['\\Vendor\\MyModule\\UserField\\ColorType', 'getUserTypeDescription']
);
```

`getUserTypeDescription()` унаследован из `BaseType` и возвращает корректный массив. Движок вызывает это событие при первом обращении к типам — метод должен быть дёшевым.

### Легаси-способ (CUserTypeString-стиль, совместимость)

Если нужно поддерживать старые версии Bitrix или не использовать BaseType:

```php
class CUserTypeMyColor
{
    const USER_TYPE_ID = 'my_color';

    public static function getUserTypeDescription(): array
    {
        return [
            'USER_TYPE_ID' => self::USER_TYPE_ID,
            'CLASS_NAME'   => __CLASS__,
            'DESCRIPTION'  => 'Мой цвет',
            'BASE_TYPE'    => 'string',
        ];
    }

    public static function getDbColumnType(): string { return 'varchar(255)'; }

    // Метод вызывается CUserTypeManager
    public function getEditFormHtml(array $userField, array $additionalParameters): string
    {
        return '<input type="text" name="' . htmlspecialcharsbx($userField['FIELD_NAME']) . '" value="' . htmlspecialcharsbx($userField['VALUE'] ?? '') . '">';
    }

    public function getAdminListViewHtml(array $userField, array $additionalParameters): string
    {
        return htmlspecialcharsEx($userField['VALUE'] ?? '');
    }

    public function getAdminListEditHtml(array $userField, array $additionalParameters): string
    {
        return $this->getEditFormHtml($userField, $additionalParameters);
    }

    public function getFilterHtml(array $userField, array $additionalParameters): string
    {
        return '<input type="text" name="find_' . htmlspecialcharsbx($userField['FIELD_NAME']) . '" value="' . htmlspecialcharsbx($additionalParameters['VALUE'] ?? '') . '">';
    }

    public function getSettingsHtml(array $userField, array $additionalParameters, $varsFromForm): string { return ''; }
    public function prepareSettings(array $userField): array { return []; }
    public function checkFields(array $userField, $value): array { return []; }
}
```

### Создание поля UF_* программно

```php
// В InstallDB инсталлятора или миграции
global $USER_FIELD_MANAGER;

$hlId = /* ID вашего HL-блока */;

$userTypeManager = new CUserTypeEntity();
$userTypeManager->Add([
    'ENTITY_ID'          => 'HLBLOCK_' . $hlId,  // или 'USER', 'IBLOCK_ELEMENT_{ID}'
    'FIELD_NAME'         => 'UF_COLOR',
    'USER_TYPE_ID'       => 'vendor_color',        // ваш кастомный тип
    'SORT'               => 100,
    'MULTIPLE'           => 'N',
    'MANDATORY'          => 'N',
    'SHOW_FILTER'        => 'Y',
    'SHOW_IN_LIST'       => 'Y',
    'EDIT_IN_LIST'       => 'Y',
    'IS_SEARCHABLE'      => 'N',
    'SETTINGS'           => [],
    'EDIT_FORM_LABEL'    => ['ru' => 'Цвет', 'en' => 'Color'],
    'LIST_COLUMN_LABEL'  => ['ru' => 'Цвет', 'en' => 'Color'],
    'LIST_FILTER_LABEL'  => ['ru' => 'Цвет', 'en' => 'Color'],
]);
```

### Стандартные USER_TYPE_ID

| ID | Тип | DB column |
|----|-----|-----------|
| `string` | Строка | varchar(255) |
| `integer` | Целое | int |
| `double` | Число с дробью | double |
| `boolean` | Да/Нет | char(1) |
| `datetime` | Дата и время | datetime |
| `date` | Дата | date |
| `string_formatted` | Форматированный текст | text |
| `url` | Ссылка | varchar(2000) |
| `file` | Файл | int (FK → b_file) |
| `enumeration` | Список (enum) | int (FK → b_user_field_enum) |
| `iblock_element` | Элемент ИБ | int |
| `iblock_section` | Раздел ИБ | int |

---

## CAdminMessage — сообщения

```php
// Ошибка из строки
$message = new CAdminMessage('Произошла ошибка: неверный формат');

// Ошибка из исключения (GetException)
if ($e = $APPLICATION->GetException()) {
    $message = new CAdminMessage('Ошибка сохранения', $e);
}

// Вывод в HTML
echo $message->Show();

// Или через ShowWarnings (после tabControl->End())
$tabControl->ShowWarnings('post_form', $message);
```

---

## Структура admin-файлов в модуле

```
local/modules/vendor.mymodule/
├── admin/
│   └── menu.php                        ← пункт меню
├── install/
│   ├── admin/
│   │   ├── mymodule_item_list.php      ← симлинк/require к admin/
│   │   └── mymodule_item_edit.php      ← копируется в /bitrix/admin/ при установке
│   └── index.php                        ← InstallFiles() копирует файлы
└── lib/
    └── UserField/
        └── ColorType.php               ← кастомный UF-тип
```

Копирование admin-файлов при установке:

```php
// install/index.php
public function InstallFiles(): bool
{
    CopyDirFiles(
        __DIR__ . '/admin',
        $_SERVER['DOCUMENT_ROOT'] . '/bitrix/admin',
        true, // rewrite
        false // не рекурсивно
    );
    return true;
}

public function UnInstallFiles(): bool
{
    DeleteDirFiles(__DIR__ . '/admin', $_SERVER['DOCUMENT_ROOT'] . '/bitrix/admin');
    return true;
}
```

---

## Gotchas

- **Имена переменных фильтра глобальные** — `InitFilter(['find_id', 'find_name'])` создаёт `global $find_id, $find_name`. Без `global $$f` в своём коде они недоступны. Всегда делай `foreach ($arFilterFields as $f) global $$f;` после `InitFilter`.
- **`check_bitrix_sessid()` обязателен** перед любым изменением данных через POST. Без него — уязвимость CSRF. Всегда пиши `check_bitrix_sessid()` в условии сохранения.
- **`CAdminResult::NavStart()`** — вызывать до `AddHeaders` и цикла по строкам. Без вызова пагинация не работает. Для `PAGEN_N`/`SIZEN_N`, session page size и modern `PageNavigation` смотри `pagination.md`.
- **`global $by, $order`** — эти глобальные переменные устанавливает `CAdminSorting`. Используй их в ORM `order` параметре после инициализации `CAdminSorting`.
- **`$row->AddField()` vs `$row->AddViewField()`** — `AddField(id, viewText, editValue)` добавляет и view, и edit (inline); `AddViewField(id, html)` — только view, не участвует в инлайн-редактировании.
- **`AddSelectField` / `AddInputField`** — добавляют только edit-вариант поля, без view. Нужен `AddField` или `AddViewField` для отображения.
- **Inline edit** — чтобы строка была редактируемой, вызови хотя бы один `Add*Field` с edit-вариантом и обработай `$lAdmin->EditAction()` и `$lAdmin->GetEditFields()`.
- **`CAdminForm` vs `CAdminTabControl`** — `CAdminForm` сам открывает буферизацию в конструкторе (`ob_start()`) и рендерит форму в `Show()`. Если используешь `CAdminTabControl` — пиши `<form>` сам.
- **`OnUserTypeBuildList`** вызывается при каждом обращении к типам через `CUserTypeManager::GetUserType()`. Handler должен только возвращать описание, без запросов в БД.
- **`CUserTypeEntity::Add`** vs `CUserTypeManager`** — создание поля через `CUserTypeEntity`, чтение значений через `CUserTypeManager`. Это разные классы.
- **Файлы в `/bitrix/admin/`** — именно туда копируются страницы при установке модуля. Без копирования `menu.php` будет ссылаться на несуществующие URL. `InstallFiles()` / `UnInstallFiles()` обязательны.
- **`htmlspecialcharsbx` vs `htmlspecialcharsEx`** — первая для атрибутов (value="..."), вторая для HTML-контента. Обе защищают от XSS. Не используй прямой вывод данных из БД без экранирования.

---

## Source: `grid-admin-modern.md`

# Bitrix Modern Grid UI — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с `Bitrix\Main\Grid\Grid`, `Settings`, `Options`, `Component\ComponentParams` и компонентом `bitrix:main.ui.grid`.

## Audit note

Проверено по текущему core:
- `www/bitrix/modules/main/lib/grid/grid.php`
- `www/bitrix/modules/main/lib/grid/settings.php`
- `www/bitrix/modules/main/lib/grid/options.php`
- `www/bitrix/modules/main/lib/grid/component/componentparams.php`
- `www/bitrix/modules/main/lib/grid/column/*`
- `www/bitrix/modules/main/lib/grid/panel/*`

Ниже только тот контракт, который реально подтверждён этим core.

## Главное отличие от старого reference

В текущем core:
- `Grid` абстрактный, его нельзя инстанцировать напрямую;
- `createColumns()` должен вернуть `Bitrix\Main\Grid\Column\Columns`, а не массив;
- `Columns` собирается из `Column\DataProvider`, а не из произвольного списка `Column::create(...)`;
- `Panel` не настраивается через `setActions()`: он работает через `DataProvider`;
- `Filter\Field` нельзя создать как `new Field('TITLE', [...])`: конструктору нужен `DataProvider`.

## Базовый паттерн

```php
use Bitrix\Main\Grid\Column\Columns;
use Bitrix\Main\Grid\Grid;
use Bitrix\Main\Grid\Settings;
use Bitrix\Main\Grid\Component\ComponentParams;

$settings = new Settings([
    'ID' => 'my_module_items',
]);

$grid = new ItemGrid($settings);
$grid->processRequest();

$ormFilter = $grid->getOrmFilter() ?? [];
$ormParams = $grid->getOrmParams();

if ($grid->getPagination() !== null)
{
    $grid->getPagination()->setRecordCount(
        ItemTable::getCount($ormFilter)
    );
}

$grid->setRawRows(
    ItemTable::getList(array_merge(
        ['select' => ['ID', 'TITLE', 'ACTIVE']],
        $ormParams
    ))
);

$APPLICATION->IncludeComponent(
    'bitrix:main.ui.grid',
    '',
    ComponentParams::get($grid, [
        'AJAX_MODE' => 'Y',
    ])
);
```

## Как правильно определить колонки

В текущем API `Grid::createColumns()` должен вернуть `Columns`. `Columns` принимает `Column\DataProvider`.

```php
namespace Vendor\Module\Grid;

use Bitrix\Main\Grid\Column\Column;
use Bitrix\Main\Grid\Column\Columns;
use Bitrix\Main\Grid\Column\DataProvider;
use Bitrix\Main\Grid\Grid;

final class ItemColumnsProvider extends DataProvider
{
    public function prepareColumns(): array
    {
        return $this->createColumns([
            'ID' => [
                'name' => 'ID',
                'sort' => 'ID',
                'default' => true,
                'width' => 80,
            ],
            'TITLE' => [
                'name' => 'Название',
                'sort' => 'TITLE',
                'default' => true,
            ],
            'ACTIVE' => [
                'name' => 'Активность',
                'sort' => 'ACTIVE',
                'default' => true,
                'necessary' => true,
            ],
        ]);
    }
}

final class ItemGrid extends Grid
{
    protected function createColumns(): Columns
    {
        return new Columns(
            new ItemColumnsProvider($this->getSettings())
        );
    }
}
```

Если нужен прямой `Column`, в этом core он создаётся через `new Column($id, $params)`. Не обещай chain-конструктор `Column::create(...)`, пока не подтвердил его локально.

## Что делает `getOrmParams()`

Подтверждённый состав:
- `select` из видимых и necessary-колонок;
- `order` из `Options::getSorting(...)`;
- `filter`, если есть `Filter`;
- `limit`/`offset`, если есть `PageNavigation`.

То есть `getOrmParams()` уже включает ORM-friendly параметры для `DataManager::getList(...)`.

## Pagination и Options

Подробный core-first слой по `PageNavigation`, `main.pagenavigation`, admin/grid navigation, `PAGEN_N` и lazy load вынесен в `pagination.md`.

`Options` в текущем core наследуется от `CGridOptions` и даёт, среди прочего:
- `getSorting(...)`
- `GetVisibleColumns()`
- `getNavParams()`
- `setPageSize(...)`
- `getExpandedRows()`
- `setExpandedRows(...)`

`Settings` подтверждает:
- `MODE_HTML`
- `MODE_EXCEL`
- `getID()`
- `isHtmlMode()`
- `isExcelMode()`

## Filter

`Grid` сам фильтр не строит. `getOrmFilter()` работает только если `createFilter()` вернул объект `Bitrix\Main\Filter\Filter`.

В текущем core `Bitrix\Main\Filter\Field` требует `DataProvider` первым аргументом, поэтому универсальный “короткий” пример вида

```php
new Field('TITLE', [...])
```

для этого ядра неверен.

Практическое правило:
- если фильтр уже есть в модуле или проекте, ориентируйся на его `DataProvider`;
- если фильтра нет, не придумывай shortcut API, которого нет в этом core.

## Panel

`Bitrix\Main\Grid\Panel\Panel` в текущем core строится через `Panel\Action\DataProvider`, а не через `setActions(...)`.

Подтверждённый контракт:
- `new Panel(DataProvider ...$providers)`
- `getControls()`
- `processRequest(...)`

Если тебе нужна массовая action-panel, ищи или пиши provider, а не вызывай несуществующий fluent API.

## Gotchas

- Не инстанцируй `new Grid(...)`: класс абстрактный.
- Не возвращай из `createColumns()` массив: нужен объект `Columns`.
- Не обещай `Column::create(...)` и `Panel::setActions(...)`, пока не подтвердил их локально.
- `setRawRows()` действительно принимает `iterable`, но сохраняет строки во внутренний массив, так что это не “ленивая” обёртка.
- `getOrmFilter()` может вернуть `null` и это штатный сценарий.

---

## Source: `pagination.md`

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

---

## Source: `file-upload-modern.md`

# Bitrix File Uploader — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с загрузкой файлов через `Bitrix\Main\FileUploader\FieldFileUploaderController`, `Bitrix\UI\FileUploader\UploaderController`, `Configuration`, `UploadedFilesRegistry` и `UploaderFileSigner`.

## Audit note

Проверено по текущему core:
- `www/bitrix/modules/main/lib/fileuploader/FieldFileUploaderController.php`
- `www/bitrix/modules/ui/lib/fileuploader/UploaderController.php`
- `www/bitrix/modules/ui/lib/fileuploader/Configuration.php`
- `www/bitrix/modules/main/lib/userfield/file/uploadedfilesregistry.php`
- `www/bitrix/modules/main/lib/userfield/file/uploaderfilesigner.php`
- `www/bitrix/modules/main/lib/userfield/file/uploadercontextgenerator.php`

В этой установке не найден стандартный компонент `bitrix:ui.file.input` внутри `modules/*/install/components`, поэтому не обещай его как гарантированную точку входа. Для фронта ориентируйся на реальный проектный код и на контекст, который собирает core вокруг userfield/file utilities.

## Что реально есть в core

### `FieldFileUploaderController`

Это готовый контроллер для UF-файлов. Он:
- наследует `Bitrix\UI\FileUploader\UploaderController`;
- валидирует `id`, `cid`, `entityId`, `fieldName`, `multiple`, `signedFileId`;
- берёт ограничения поля через `$USER_FIELD_MANAGER->GetUserFields(...)`;
- в `getConfiguration()` настраивает `Configuration`;
- в `onUploadComplete()` регистрирует файл во внутренних utility/registry механизмах.

Подтверждённые опции конструктора:

```php
[
    'id' => 0,
    'cid' => '',
    'entityId' => '',
    'fieldName' => '',
    'multiple' => false,
    'signedFileId' => '',
]
```

`cid` в текущем core проходит regex-проверку на 32 hex-символа.

### `UploaderController`

В `ui` это абстрактный базовый класс. Он требует реализовать:
- `isAvailable(): bool`
- `getConfiguration(): Configuration`
- `canUpload(): bool|CanUploadResult`
- `canView(): bool`
- `verifyFileOwner(FileOwnershipCollection $files): void`
- `canRemove(): bool`

Есть стандартные lifecycle hooks:
- `onUploadStart(...)`
- `onUploadComplete(...)`
- `onUploadError(...)`

### `UploadedFilesRegistry`

В текущем core это не сервис `confirm()`. Реально он умеет:
- `registerFile(int $fileId, string $controlId, string $cid, string $tempFileToken)`
- `getTokenByFileId(...)`
- `getCidByFileId(...)`
- `unregisterFile(...)`

То есть это session-backed registry временных связей `fileId <-> controlId/cid/token`, а не универсальный confirm-API.

### `UploaderFileSigner`

Сигнатура в текущем core:

```php
new UploaderFileSigner(string $entityId, string $fieldName)
```

Подтверждённые методы:
- `sign(int $fileId): string`
- `verify(string $signedString, int $fileId): bool`

Это важно: `verify()` требует и signed string, и реальный `fileId`.

## Конфигурация загрузчика

В `Bitrix\UI\FileUploader\Configuration` подтверждены методы:
- `setMaxFileSize(?int $bytes)`
- `setMinFileSize(int $bytes)`
- `setAcceptedFileTypes(array $extensions)`
- `setAcceptOnlyImages(bool $flag = true)`
- `acceptOnlyImages()`
- `setImageMinWidth(...)`
- `setImageMinHeight(...)`
- `setImageMaxWidth(...)`
- `setImageMaxHeight(...)`
- `setImageMaxFileSize(...)`
- `setImageMinFileSize(...)`
- `setTreatOversizeImageAsFile(bool)`
- `setIgnoreUnknownImageTypes(bool)`
- `toArray()`

В этом core нет подтверждения для методов вроде:
- `setAllowedFileExtensions(...)`
- `setMultiple(...)`
- `setMaxFileCount(...)`
- `setMaxTotalFileSize(...)`

Не используй их в reference как гарантированный API.

## Как выглядит безопасный базовый паттерн

```php
use Bitrix\Main\FileUploader\FieldFileUploaderController;

$controller = new FieldFileUploaderController([
    'entityId' => 'USER',
    'fieldName' => 'UF_PHOTO',
    'multiple' => false,
    'cid' => $cid,
    'id' => (int)$userId,
]);

if (!$controller->isAvailable())
{
    throw new \RuntimeException('Uploader is not available');
}

$config = $controller->getConfiguration()->toArray();
```

## View mode и edit mode

Внутренний контекст различается так:
- edit mode использует `cid`;
- view mode использует `signedFileId`.

Core-утилита `UploaderContextGenerator` подтверждает оба сценария:

```php
use Bitrix\Main\UserField\File\UploaderContextGenerator;
use Bitrix\Main\UI\FileInputUtility;

$generator = new UploaderContextGenerator(
    FileInputUtility::instance(),
    [
        'ID' => 0,
        'ENTITY_ID' => 'USER',
        'FIELD_NAME' => 'UF_PHOTO',
        'MULTIPLE' => 'N',
    ]
);

$editContext = $generator->getContextInEditMode($cid);
$viewContext = $generator->getContextForFileInViewMode($fileId);
```

## Кастомный контроллер

Если нужен свой upload controller, ориентируйся на реальный контракт `UploaderController`, а не на выдуманные методы вроде `getOwners()`.

```php
namespace Vendor\Module\FileUploader;

use Bitrix\UI\FileUploader\Configuration;
use Bitrix\UI\FileUploader\FileOwnershipCollection;
use Bitrix\UI\FileUploader\UploaderController;

final class ItemUploaderController extends UploaderController
{
    public function isAvailable(): bool
    {
        global $USER;

        return $USER instanceof \CUser && $USER->IsAuthorized();
    }

    public function getConfiguration(): Configuration
    {
        return (new Configuration())
            ->setMaxFileSize(10 * 1024 * 1024)
            ->setAcceptedFileTypes(['.jpg', '.png', '.pdf']);
    }

    public function canUpload(): bool
    {
        return true;
    }

    public function canView(): bool
    {
        return true;
    }

    public function verifyFileOwner(FileOwnershipCollection $files): void
    {
        foreach ($files as $file)
        {
            $file->markAsOwn();
        }
    }

    public function canRemove(): bool
    {
        return true;
    }
}
```

## Gotchas

- Не обещай `UploadedFilesRegistry::confirm()`: в текущем core такого метода нет.
- Не вызывай `new UploaderFileSigner()` без аргументов: ему нужны `entityId` и `fieldName`.
- Не подменяй `Configuration::setAcceptedFileTypes()` на `setAllowedFileExtensions()`: это не подтверждено текущим API.
- Не обещай стандартный `bitrix:ui.file.input`, пока не увидел его реально в установленном core или в проектном коде.
- Для `FieldFileUploaderController::canUpload()` мало одной авторизации: там ещё проверяется зарегистрированный `cid` через `FileInputUtility`.

---

## Source: `numerator.md`

# Bitrix Numerator — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с нумерацией документов через `Bitrix\Main\Numerator\Numerator`, `NumberGeneratorFactory`, `NumeratorTable` и `NumeratorSequenceTable`.

## Audit note

Проверено по текущему core:
- `www/bitrix/modules/main/lib/numerator/numerator.php`
- `www/bitrix/modules/main/lib/numerator/numbergeneratorfactory.php`
- `www/bitrix/modules/main/lib/numerator/model/numerator.php`
- `www/bitrix/modules/main/lib/numerator/model/numeratorsequence.php`
- `www/bitrix/modules/main/lib/numerator/generator/*`

Это реальный модульный слой текущего `main`, а не внешняя библиотека.

## Что есть в этом core

Основные классы:
- `Bitrix\Main\Numerator\Numerator`
- `Bitrix\Main\Numerator\NumberGeneratorFactory`
- `Bitrix\Main\Numerator\Model\NumeratorTable`
- `Bitrix\Main\Numerator\Model\NumeratorSequenceTable`

Встроенные генераторы:
- `SequentNumberGenerator`
- `DateNumberGenerator`
- `RandomNumberGenerator`
- `PrefixNumberGenerator`

В `NumberGeneratorFactory` генераторы собираются из core и могут расширяться событием `main:onNumberGeneratorsClassesCollect`.

## Важное отличие от старых описаний

В текущем core:
- следующий номер получают через `Numerator::getNext(...)`, а не `getNumber()`;
- preview идёт через `previewNextNumber(...)`;
- конфиг хранится в поле `SETTINGS`, а не `CONFIG`;
- таблица нумераторов называется `b_numerator`, а последовательностей `b_numerator_sequence`;
- есть `load($id, $source = null)` и `loadByCode($code, $source = null)`.

## Как создавать и сохранять

У `Numerator::create()` конструктор пустой. Публичных chain-методов `setName()/setType()/setTemplate()` в текущем core нет. Рабочий путь — подготовить конфиг и вызвать `setConfig(...)`, затем `save()`.

```php
use Bitrix\Main\Numerator\Generator\SequentNumberGenerator;
use Bitrix\Main\Numerator\Numerator;

$numerator = Numerator::create();

$result = $numerator->setConfig([
    Numerator::getType() => [
        'name' => 'Нумерация заказов',
        'type' => Numerator::NUMERATOR_DEFAULT_TYPE,
        'template' => '{PREFIX}-{YEAR}{MONTH}-{NUMBER}',
        'code' => 'orders',
    ],
    SequentNumberGenerator::getType() => [
        'start' => 1,
        'step' => 1,
        'length' => 6,
        'padString' => '0',
        'periodicBy' => SequentNumberGenerator::MONTH,
    ],
]);

if (!$result->isSuccess())
{
    throw new \RuntimeException(implode('; ', $result->getErrorMessages()));
}

$saveResult = $numerator->save();
if (!$saveResult->isSuccess())
{
    throw new \RuntimeException(implode('; ', $saveResult->getErrorMessages()));
}

$numeratorId = (int)$saveResult->getId();
```

## Загрузка

```php
use Bitrix\Main\Numerator\Numerator;

$numerator = Numerator::load($numeratorId);
$byCode = Numerator::loadByCode('orders');
```

Если нумератор не найден или конфиг невалиден, вернётся `null`.

Второй аргумент `load(..., $source)` можно использовать как:
- dynamic config для `DynamicConfigurable` генераторов;
- hash-source для последовательности, если объект реализует `Hashable`.

## Генерация номера

```php
if (!$numerator)
{
    throw new \RuntimeException('Numerator not found');
}

$next = $numerator->getNext();
$preview = $numerator->previewNextNumber();
```

Для последовательного генератора:
- `getNext()` реально увеличивает счётчик;
- `previewNextNumber()` только считает следующий видимый номер;
- `previewNextSequentialNumber()` возвращает только следующее числовое значение счётчика;
- `setNextSequentialNumber(...)` позволяет принудительно сдвинуть последовательность.

## Хеш и независимые последовательности

Последовательность в текущем core может вестись независимо по хешу.

```php
$nextForCompany42 = $numerator->getNext('COMPANY_42');
$nextForCompany64 = $numerator->getNext('COMPANY_64');
```

`NumeratorSequenceTable` хранит ключ как:
- `KEY = md5($numberHash)`
- `TEXT_KEY = mb_substr($numberHash, 0, 50)`

## Таблицы

### `NumeratorTable`

`Bitrix\Main\Numerator\Model\NumeratorTable` работает с таблицей `b_numerator`.

Реальные поля:
- `ID`
- `NAME`
- `TEMPLATE`
- `SETTINGS`
- `TYPE`
- `CREATED_AT`
- `CREATED_BY`
- `UPDATED_AT`
- `UPDATED_BY`
- `CODE`

`CODE`:
- nullable;
- должен быть уникальным;
- если передан, обязан быть непустой строкой.

Полезные методы:
- `getList(...)`
- `getById(...)`
- `getNumeratorList($type, $sort)`
- `loadSettings($numeratorId)`
- `saveNumerator($numeratorId, $fields)`
- `getIdByCode($code)`

### `NumeratorSequenceTable`

`Bitrix\Main\Numerator\Model\NumeratorSequenceTable` работает с таблицей `b_numerator_sequence`.

Реальные поля:
- `NUMERATOR_ID`
- `KEY`
- `TEXT_KEY`
- `NEXT_NUMBER`
- `LAST_INVOCATION_TIME`

Полезные методы:
- `getSettings($numeratorId, $numberHash)`
- `setSettings($numeratorId, $numberHash, $defaultNumber, $lastInvocationTime)`
- `updateSettings($numeratorId, $numberHash, $fields, $whereNextNumber = null)`
- `deleteByNumeratorId($id)`

## Периодичность последовательности

В `SequentNumberGenerator` подтверждены значения:
- `SequentNumberGenerator::DAY`
- `SequentNumberGenerator::MONTH`
- `SequentNumberGenerator::YEAR`
- пустое значение для режима без периодического сброса

Не подменяй их псевдо-значениями вроде `DAILY`, `MONTHLY`, `YEARLY`: в этом core используются именно `day`, `month`, `year`.

## Шаблон и встроенные слова

Конкретный набор слов зависит от подключённых генераторов, но в текущем core подтверждены:
- `{NUMBER}`
- `{DAY}`
- `{MONTH}`
- `{YEAR}`
- `{RANDOM}`
- `{PREFIX}`

Для получения доступных слов безопаснее использовать:

```php
use Bitrix\Main\Numerator\Numerator;

$words = Numerator::getTemplateWordsForType();
$settings = Numerator::getSettingsFields(Numerator::NUMERATOR_DEFAULT_TYPE);
```

## Обновление и удаление

```php
use Bitrix\Main\Numerator\Numerator;

$updateResult = Numerator::update($numeratorId, [
    Numerator::getType() => [
        'idFromDb' => $numeratorId,
        'name' => 'Обновлённый нумератор',
        'type' => Numerator::NUMERATOR_DEFAULT_TYPE,
        'template' => '{PREFIX}-{YEAR}-{NUMBER}',
        'code' => 'orders',
    ],
]);

$deleteResult = Numerator::delete($numeratorId);
```

`delete($id)` дополнительно чистит связанные записи последовательностей через `NumeratorSequenceTable::deleteByNumeratorId(...)`.

## Gotchas

- Не используй `getNumber()`: в текущем core рабочий метод называется `getNext()`.
- Не пиши в примерах поле `CONFIG`: в таблице хранится `SETTINGS`, причём через JSON.
- Не строй конфиг через несуществующие public chain-методы `setType()/setTemplate()/setName()`.
- Не подменяй периодичность значениями `YEARLY`/`MONTHLY`/`DAILY`: ядро использует `year`/`month`/`day`.
- Если нужен preview без инкремента, используй `previewNextNumber()`, а не `getNext()`.

---

## Source: `userconsent.md`

# Bitrix UserConsent — core-first справочник

> Reference для Bitrix-скилла. Загружай, когда задача связана с соглашениями пользователя, записью согласий, `Bitrix\Main\UserConsent\Agreement`, `Consent`, `AgreementLink`, `DataProvider` или REST-методами userconsent.

## Что подтверждено в текущем core

`UserConsent` лежит внутри `main`:

- `Bitrix\Main\UserConsent\Agreement`
- `Bitrix\Main\UserConsent\Consent`
- `Bitrix\Main\UserConsent\DataProvider`
- `Bitrix\Main\UserConsent\Policy`
- `Bitrix\Main\UserConsent\AgreementLink`
- `Bitrix\Main\UserConsent\Rest`
- `Bitrix\Main\UserConsent\Internals\AgreementTable`
- `Bitrix\Main\UserConsent\Internals\ConsentTable`

---

## Agreement

```php
use Bitrix\Main\UserConsent\Agreement;

$agreement = new Agreement($agreementId);

if ($agreement->isExist() && $agreement->isActive()) {
    $data = $agreement->getData();
    $text = $agreement->getText();
    $html = $agreement->getHtml();
    $label = $agreement->getLabel();
    $labelText = $agreement->getLabelText();
    $url = $agreement->getUrl();
}
```

Подтверждённые методы:

- `isExist()`
- `isActive()`
- `getData()`
- `getText()`
- `getHtml()`
- `getLabelText()`
- `getLabel()`
- `getUrl()`

### Что важно

- `getUrl()` возвращает URL только если у соглашения `USE_URL = 'Y'` и URL реально задан.
- `getLabel()` работает с `%...%`-разметкой текста ссылки.
- В текущем core у `Agreement` нет метода `getCheckBoxHtml()`.

---

## `Consent::addByContext()`

```php
use Bitrix\Main\UserConsent\Consent;

$consentId = Consent::addByContext(
    $agreementId,
    $originatorId,
    $originId,
    [
        'USER_ID' => $USER->GetID(),
        'IP' => '203.0.113.10',
        'URL' => 'https://example.test/form/',
        'ITEMS' => [
            ['VALUE' => 'analytics'],
            ['VALUE' => 'marketing'],
        ],
    ]
);
```

Что реально делает метод:

- проверяет, что соглашение существует и активно;
- берёт `USER_ID` из params или из глобального `$USER`;
- берёт `IP` из params или из `Context::getCurrent()->getRequest()->getRemoteAddress()`;
- берёт `URL` из params или собирает из текущего request;
- режет URL до 4000 символов;
- пишет запись в `Internals\ConsentTable`;
- если передан `ITEMS`, добавляет их в `Internals\UserConsentItemTable`.

`addByContext()` возвращает `int|null`.

---

## Проверка существующего согласия

```php
use Bitrix\Main\UserConsent\Internals\ConsentTable;

$row = ConsentTable::getList([
    'filter' => [
        '=AGREEMENT_ID' => $agreementId,
        '=USER_ID' => $userId,
    ],
    'limit' => 1,
])->fetch();

$hasConsent = $row !== false;
```

В текущем core `addByContext()` сам дубликаты не отсекает.

---

## `AgreementLink`

`AgreementLink` нужен, когда соглашение надо безопасно отдать наружу с подписанными replace-параметрами.

```php
use Bitrix\Main\UserConsent\AgreementLink;

$uri = AgreementLink::getUri($agreementId, ['COMPANY' => 'Acme'], '/consent/');
$agreement = AgreementLink::getAgreementFromUriParameters($_GET);
$errors = AgreementLink::getErrors();
```

Под капотом используется `Bitrix\Main\Security\Sign\Signer`.

---

## Два разных события provider-слоя

В текущем core здесь легко ошибиться, потому что событий два и они про разное.

### 1. `OnUserConsentProviderList`

Источник: `Consent::EVENT_NAME_LIST`.

Это список origin/provider-источников для `Consent::getOriginData()` и `Consent::getItems()`.

Форма элемента:

```php
use Bitrix\Main\EventResult;

return new EventResult(EventResult::SUCCESS, [
    [
        'CODE' => 'MY_PROVIDER',
        'NAME' => 'My Provider',
        'DATA' => function ($id) {
            return [
                'NAME' => 'Object name',
                'URL' => '/object/' . (int)$id . '/',
            ];
        },
        'ITEMS' => function ($value) {
            return (string)$value;
        },
    ],
], 'my.module');
```

Минимально обязательны:

- `CODE`
- `NAME`
- `DATA` callable

### 2. `OnUserConsentDataProviderList`

Источник: `DataProvider::EVENT_NAME_LIST`.

Это список data-provider'ов для подстановок в текст соглашения.

Форма элемента:

```php
use Bitrix\Main\EventResult;

return new EventResult(EventResult::SUCCESS, [
    [
        'CODE' => 'MY_DATA',
        'NAME' => 'My data provider',
        'DATA' => function () {
            return [
                'COMPANY_NAME' => 'Acme',
                'EMAIL' => 'legal@example.test',
            ];
        },
        'EDIT_URL' => '/bitrix/admin/my_module_settings.php',
    ],
], 'my.module');
```

Минимально обязательны:

- `CODE`
- `NAME`
- `DATA` как `array` или `callable`

---

## REST в текущем core

`main` сам публикует userconsent REST-методы через `Bitrix\Main\Rest\Handlers`:

- `userconsent.consent.add`
- `userconsent.agreement.list`
- `userconsent.agreement.text`

Реализация лежит в `Bitrix\Main\UserConsent\Rest`.

---

## Gotchas

- Не ищи `Loader::includeModule('userconsent')`: отдельного модуля нет, это часть `main`.
- Не используй `Agreement::getCheckBoxHtml()` — такого метода в текущем core нет.
- `OnUserConsentProviderList` и `OnUserConsentDataProviderList` нельзя смешивать: первый про origin/items, второй про подстановочные данные для текста.
- `Agreement::getUrl()` может вернуть `null`; всегда проверяй это перед рендером ссылки.
- Если нужно одноразовое согласие, сначала проверь `ConsentTable`, потом вызывай `addByContext()`.
