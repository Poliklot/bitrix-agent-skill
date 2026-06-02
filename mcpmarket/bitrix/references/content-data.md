# Content Data
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `iblocks.md`

# Bitrix Инфоблоки и HL-блоки — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с инфоблоками (CIBlockElement, CIBlockSection), D7 ORM для инфоблоков (IblockTable::compileEntity, API_CODE), свойствами (PropertyTable), или высоконагруженными блоками (HighloadBlockTable).
>
> Audit note: ниже сверено с текущим `www/bitrix/modules/iblock`. Подтверждены `PROPERTY_*`, `CIBlockElement::GetByID()`, `IblockTable::compileEntity($apiCode)` и `Iblock::wakeUp($id)->getEntityDataClass()`. Формат множественных legacy-свойств в `GetNext()` считай нестабильным и проверяй по фактическому запросу.

## Содержание
- CIBlockElement::GetList — полная сигнатура, фильтры, select, пагинация
- CIBlockElement: Add/Update/Delete/GetByID
- CIBlockSection::GetList, Add
- D7 ORM инфоблоков: compileEntity, API_CODE, class naming
- Доступ к свойствам: одиночные (fetch+алиас), множественные (fetchObject+коллекция)
- PropertyTable: типы (S/N/F/E/G/L), USER_TYPE, PropertyEnumerationTable
- ElementPropertyTable: прямой доступ к значениям
- HL-блоки: compileEntity, UTM-таблицы, CRUD
- Инфоблок события: OnBefore/AfterIBlockElement*
- Gotchas

---

## Инфоблоки — Legacy API

### CIBlockElement::GetList

```php
\Bitrix\Main\Loader::includeModule('iblock');

// Сигнатура:
// GetList($arOrder, $arFilter, $arGroupBy, $arNavStartParams, $arSelectFields)

$res = CIBlockElement::GetList(
    ['SORT' => 'ASC', 'ID' => 'DESC'],    // order
    [
        'IBLOCK_ID'      => 5,             // обязательно
        'ACTIVE'         => 'Y',           // только активные
        '>=SORT'         => 100,           // операторы: =, !=, >, <, >=, <=, %
        'SECTION_ID'     => 10,            // прямые дети раздела (без вложенных)
        'INCLUDE_SUBSECTIONS' => 'Y',      // включить вложенные разделы
        'PROPERTY_COLOR' => 'red',         // значение свойства
        'PROPERTY_SIZE'  => [42, 44],      // массив значений (IN)
    ],
    false,                                 // groupBy: false = нет, [] = COUNT
    ['nPageSize' => 20, 'iNumPage' => 1],  // пагинация; nTopCount = LIMIT без NavString
    [
        'ID', 'NAME', 'CODE', 'SORT',
        'PREVIEW_TEXT', 'DETAIL_TEXT',
        'PREVIEW_PICTURE', 'DETAIL_PICTURE',
        'DATE_ACTIVE_FROM', 'DATE_ACTIVE_TO',
        'IBLOCK_SECTION_ID', 'XML_ID',
        'PROPERTY_COLOR',                  // конкретное свойство по CODE
        'PROPERTY_123',                    // или по ID
        'PROPERTY_*',                      // все свойства (дорого!)
    ]
);

while ($el = $res->GetNext()) {
    // Скалярное свойство
    echo $el['PROPERTY_COLOR_VALUE'];       // значение
    echo $el['PROPERTY_COLOR_ENUM_ID'];     // ID пункта списка (тип L)
    echo $el['PROPERTY_COLOR_VALUE_ID'];    // ID строки b_iblock_element_property

    // Файловое свойство (TYPE_FILE): VALUE = ID файла
    $fileId = $el['PROPERTY_PHOTO_VALUE'];
    $file = CFile::GetFileArray($fileId);

    // Привязка к элементу (TYPE_ELEMENT): VALUE = ID элемента
    $linkedId = $el['PROPERTY_RELATED_VALUE'];
}

// Только COUNT
$count = CIBlockElement::GetList([], ['IBLOCK_ID' => 5, 'ACTIVE' => 'Y'], false, false, []);
// При groupBy=[] (пустой массив) → возвращает CIBlockResult с полем CNT
$res2 = CIBlockElement::GetList([], ['IBLOCK_ID' => 5], []);
$row = $res2->Fetch();
echo $row['CNT'];
```

Для сложной пагинации, `PAGEN_N`, `NavNum`, lazy load и диагностики пустой второй страницы смотри `pagination.md`. Важно: `nTopCount` в core — это ограничение выборки, а не полноценная постраничная навигация.

### Множественные свойства в GetList

```php
// Для MULTIPLE='Y' надёжнее брать свойства через GetNextElement()->GetProperties(),
// а не полагаться на форму PROPERTY_CODE_VALUE в GetNext().
while ($obj = $res->GetNextElement()) {
    $arFields = $obj->GetFields();
    $arProps  = $obj->GetProperties(); // все свойства с полной структурой
    foreach ($arProps['TAGS']['VALUE'] as $val) {
        echo $val;
    }
}
```

### CIBlockElement — Add / Update / Delete / GetByID

```php
$el = new CIBlockElement();

// Add — возвращает int ID или false при ошибке
$id = $el->Add([
    'IBLOCK_ID'       => 5,
    'NAME'            => 'Заголовок',
    'ACTIVE'          => 'Y',
    'SORT'            => 500,
    'CODE'            => 'my-slug',               // символьный код
    'PREVIEW_TEXT'    => 'Краткое описание',
    'PREVIEW_TEXT_TYPE' => 'text',                 // 'text' | 'html'
    'DETAIL_TEXT'     => '<p>Полный текст</p>',
    'DETAIL_TEXT_TYPE' => 'html',
    'IBLOCK_SECTION_ID' => 10,                    // один раздел
    'IBLOCK_SECTION'  => [10, 15],                // несколько разделов
    'PROPERTY_VALUES' => [
        'COLOR'    => 'red',                      // по CODE свойства
        'TAGS'     => ['php', 'bitrix'],           // множественное
        'PHOTO'    => CFile::MakeFileArray('/path/to/file.jpg'), // файл
        'RELATED'  => 42,                         // привязка к элементу (ID)
    ],
]);
if (!$id) {
    echo $el->LAST_ERROR;
}

// Update — возвращает bool
$ok = $el->Update($id, ['NAME' => 'Новое имя', 'ACTIVE' => 'N']);

// Установить значения свойств после Add/Update
CIBlockElement::SetPropertyValuesEx($id, 5, [
    'COLOR' => 'blue',
    'TAGS'  => ['bitrix24', 'd7'],
]);

// GetByID — одиночный элемент
$res = CIBlockElement::GetByID($id);
$arEl = $res->GetNext();   // HTML-экранирование + обработка URL-шаблонов
// $rawEl = $res->Fetch();  // сырой массив без htmlspecialchars и без подстановки URL

// Delete
CIBlockElement::Delete($id); // удаляет элемент + все свойства + файлы
```

### CIBlockSection — GetList / Add

```php
// Сигнатура: GetList($arOrder, $arFilter, $bIncCnt, $arSelect, $arNavStartParams)
$res = CIBlockSection::GetList(
    ['SORT' => 'ASC', 'LEFT_MARGIN' => 'ASC'],
    [
        'IBLOCK_ID'   => 5,
        'ACTIVE'      => 'Y',
        'GLOBAL_ACTIVE' => 'Y',           // активна вся цепочка родителей
        'SECTION_ID'  => 0,               // корневые разделы (0 = корень)
        // DEPTH_LEVEL, LEFT_MARGIN, RIGHT_MARGIN, CNT
    ],
    true,                                 // bIncCnt — включить ELEMENT_CNT, SECTION_CNT
    ['ID', 'NAME', 'CODE', 'SORT', 'DEPTH_LEVEL',
     'SECTION_PAGE_URL', 'LEFT_MARGIN', 'RIGHT_MARGIN',
     'ELEMENT_CNT',                       // только если bIncCnt=true
    ]
);
while ($sec = $res->GetNext()) {
    echo $sec['NAME'], ' (', $sec['DEPTH_LEVEL'], ')';
}

// Add
$sec = new CIBlockSection();
$secId = $sec->Add([
    'IBLOCK_ID'        => 5,
    'IBLOCK_SECTION_ID' => 0,  // родитель (0 = корень)
    'NAME'             => 'Раздел',
    'CODE'             => 'section-slug',
    'ACTIVE'           => 'Y',
    'SORT'             => 100,
]);
```

---

## Инфоблоки — D7 ORM (`VERSION` 1 или 2)

### Почему D7 ORM для инфоблоков особенный

Bitrix компилирует **персональный класс DataManager** для каждого инфоблока с установленным `API_CODE`. Это происходит через `IblockTable::compileEntity()`. Класс наследует `ElementV1Table` (VERSION=1, общая таблица `b_iblock_element_property`) или `ElementV2Table` (VERSION=2, раздельные таблицы `b_iblock_element_prop_{ID}`).

### Требования и настройка

1. Инфоблок должен иметь заполненное поле **API_CODE** (в разделе настроек инфоблока)
2. Все свойства, доступные в ORM, должны иметь заполненный **CODE** (символьный код)
3. Модуль `iblock` должен быть подключён через `Loader::includeModule`

### Получение класса и базовый запрос

```php
use Bitrix\Main\Loader;
use Bitrix\Iblock\IblockTable;

Loader::includeModule('iblock');

// Вариант 1 — автозагрузка по namespace (если API_CODE = 'news')
// Класс: Bitrix\Iblock\Elements\ElementNewsTable
use Bitrix\Iblock\Elements\ElementNewsTable;

$result = ElementNewsTable::getList([
    'select' => ['ID', 'NAME', 'CODE', 'SORT', 'PREVIEW_TEXT', 'ACTIVE'],
    'filter' => ['=ACTIVE' => 'Y'],
    'order'  => ['SORT' => 'ASC'],
    'limit'  => 20,
]);
while ($row = $result->fetch()) {
    echo $row['ID'], ' — ', $row['NAME'];
}

// Вариант 2 — явная компиляция (если API_CODE неизвестен заранее)
$entity = IblockTable::compileEntity('news'); // 'news' = API_CODE (lowercase)
// IblockTable::compileEntity принимает строку (API_CODE) или объект Iblock
$dataClass = $entity->getDataClass(); // строка с FQN класса
$result = $dataClass::getList([...]);

// Вариант 3 — wakeUp по ID (наиболее правильный D7-способ когда знаешь ID, но не API_CODE)
use Bitrix\Iblock\Iblock;

$entityDataClass = Iblock::wakeUp($iblockId)->getEntityDataClass();
// getEntityDataClass() возвращает FQN класса (строка) или null если нет API_CODE
// Это эквивалент IblockTable::compileEntity(API_CODE)->getDataClass()
// но работает напрямую по ID без предварительного получения API_CODE

// Всегда проверяй результат — null если у инфоблока не задан API_CODE
if ($entityDataClass === null) {
    throw new \RuntimeException("Инфоблок #$iblockId не имеет API_CODE — D7 ORM недоступен");
}

$result = $entityDataClass::getList([
    'select' => ['ID', 'NAME', 'CODE'],
    'filter' => ['=ACTIVE' => 'Y', '=ID' => $productId],
    'limit'  => 1,
]);
$product = $result->fetch();
```

**Namespace и имя класса:**

| API_CODE | Namespace | Класс |
|----------|-----------|-------|
| `news` | `Bitrix\Iblock\Elements` | `ElementNewsTable` |
| `catalog` | `Bitrix\Iblock\Elements` | `ElementCatalogTable` |
| `my_products` | `Bitrix\Iblock\Elements` | `ElementMy_productsTable` |

Формула: `Element` + `ucfirst($apiCode)` + `Table`

### Доступ к свойствам элементов

**Одиночное свойство (MULTIPLE='N'):**

```php
// В select указываем алиас => 'КОД_СВОЙСТВА.VALUE'
$result = ElementNewsTable::getList([
    'select' => [
        'ID', 'NAME',
        'PRICE'        => 'PRICE.VALUE',        // обычное значение
        'PRICE_DESC'   => 'PRICE.DESCRIPTION',  // описание к свойству
        'COLOR_ENUM'   => 'COLOR.ITEM',         // текст пункта списка (тип L)
        'COLOR_ID'     => 'COLOR.ITEM_ID',      // ID пункта списка
    ],
    'filter' => ['=ACTIVE' => 'Y', '>PRICE.VALUE' => 1000],
    'order'  => ['PRICE.VALUE' => 'ASC'],
]);
while ($row = $result->fetch()) {
    echo $row['PRICE'];      // значение свойства PRICE
    echo $row['COLOR_ENUM']; // текст пункта COLOR
}
```

**Множественное свойство (MULTIPLE='Y') — через fetchObject():**

```php
// Для множественных — нельзя использовать fetch(), нужен fetchObject()
$result = ElementNewsTable::getList([
    'select' => ['ID', 'NAME', 'TAGS'],  // TAGS = CODE множественного свойства
    'filter' => ['=ACTIVE' => 'Y'],
]);
while ($obj = $result->fetchObject()) {
    echo $obj->getName();  // геттеры для полей
    $tagsCollection = $obj->getTags(); // коллекция PropertyValue объектов
    foreach ($tagsCollection as $tagValue) {
        echo $tagValue->getValue();
    }
}
```

**Фильтрация по свойству:**

```php
// Точное совпадение значения
ElementNewsTable::getList([
    'filter' => ['=COLOR.VALUE' => 'red'],
]);

// Множественное — через exists (если есть хоть одно такое значение)
ElementNewsTable::getList([
    'filter' => ['=TAGS.VALUE' => 'php'],
]);

// Диапазон числового свойства
ElementNewsTable::getList([
    'filter' => ['>=PRICE.VALUE' => 100, '<=PRICE.VALUE' => 500],
]);

// Привязка к разделу
ElementNewsTable::getList([
    'filter' => ['=IBLOCK_SECTION.CODE' => 'news-section'],
]);
```

### PropertyTable — работа со свойствами инфоблока

```php
use Bitrix\Iblock\PropertyTable;

// Типы свойств:
// PropertyTable::TYPE_STRING  = 'S'  — строка, HTML, дата (через USER_TYPE)
// PropertyTable::TYPE_NUMBER  = 'N'  — число
// PropertyTable::TYPE_FILE    = 'F'  — файл
// PropertyTable::TYPE_ELEMENT = 'E'  — привязка к элементу ИБ
// PropertyTable::TYPE_SECTION = 'G'  — привязка к разделу ИБ
// PropertyTable::TYPE_LIST    = 'L'  — список (enum)

// USER_TYPE для TYPE_STRING:
// PropertyTable::USER_TYPE_DATE     = 'Date'
// PropertyTable::USER_TYPE_DATETIME = 'DateTime'
// PropertyTable::USER_TYPE_HTML     = 'HTML'

// Получить все свойства инфоблока
$res = PropertyTable::getList([
    'select' => ['ID', 'NAME', 'CODE', 'PROPERTY_TYPE', 'MULTIPLE',
                 'USER_TYPE', 'LINK_IBLOCK_ID', 'SORT', 'IS_REQUIRED'],
    'filter' => ['=IBLOCK_ID' => 5, '=ACTIVE' => 'Y'],
    'order'  => ['SORT' => 'ASC'],
]);
while ($prop = $res->fetch()) {
    echo $prop['CODE'], ': ', $prop['PROPERTY_TYPE'];
    if ($prop['PROPERTY_TYPE'] === PropertyTable::TYPE_LIST) {
        // получить пункты списка
        $enums = \Bitrix\Iblock\PropertyEnumerationTable::getList([
            'filter' => ['=PROPERTY_ID' => $prop['ID']],
            'order'  => ['SORT' => 'ASC'],
        ]);
    }
}
```

### ElementPropertyTable — прямой доступ к значениям

```php
use Bitrix\Iblock\ElementPropertyTable;

// b_iblock_element_property — таблица значений VERSION=1 и множественных VERSION=2
$res = ElementPropertyTable::getList([
    'select' => ['IBLOCK_ELEMENT_ID', 'VALUE', 'VALUE_NUM', 'VALUE_ENUM', 'DESCRIPTION'],
    'filter' => [
        '=IBLOCK_PROPERTY_ID' => 42,   // ID свойства
        '=IBLOCK_ELEMENT_ID'  => 100,  // ID элемента
    ],
]);
// VALUE — текстовое значение
// VALUE_NUM — числовое значение (для TYPE_NUMBER, TYPE_FILE, TYPE_ELEMENT, TYPE_SECTION)
// VALUE_ENUM — ID пункта списка (для TYPE_LIST)
```

---

## HL-блоки (Highloadblock)

### Создание и использование HL-блока

```php
use Bitrix\Main\Loader;
use Bitrix\Highloadblock\HighloadBlockTable;

Loader::includeModule('highloadblock');

// Получить класс HL-блока по ID
$hlblock = HighloadBlockTable::getById($hlId)->fetch();
$entity  = HighloadBlockTable::compileEntity($hlblock);
// compileEntity($hlblock) — принимает массив (fetch) или объект, не int!
// Чтобы по ID:
$entity = HighloadBlockTable::compileEntity(
    HighloadBlockTable::getById($hlId)->fetch()
);
$entityClass = $entity->getDataClass(); // строка FQN

// По имени — если NAME='Colors', namespace Bitrix\Highloadblock
// Можно и через: HighloadBlockTable::getList(['filter' => ['=NAME' => 'Colors']])

// CRUD
$result = $entityClass::getList([
    'select' => ['*'],           // UF_* поля
    'filter' => ['=UF_ACTIVE' => 'Y'],
    'order'  => ['UF_SORT' => 'ASC'],
]);
while ($row = $result->fetch()) {
    echo $row['UF_NAME'];
}

// Add
$entityClass::add(['UF_NAME' => 'Красный', 'UF_CODE' => 'red', 'UF_ACTIVE' => 1]);

// Update
$entityClass::update($id, ['UF_ACTIVE' => 0]);

// Delete
$entityClass::delete($id);
```

### Множественные поля HL-блока (UTM-таблицы)

Поле типа "список" с `MULTIPLE='Y'` хранится в отдельной таблице `{TABLE_NAME}_{FIELD_CODE}` (не в основной). Первичный ключ — `ID`, внешний ключ — `OBJECT_ID` (ID записи HL-блока), `VALUE` — значение.

```php
// Если TABLE_NAME='b_hl_colors', поле UF_TAGS (множественное)
// → таблица: b_hl_colors_uf_tags
// Получить через relation (добавляется автоматически):
$obj = $entityClass::getByPrimary($id, [
    'select' => ['ID', 'UF_TAGS'],
])->fetchObject();
foreach ($obj->getUfTags() as $tagItem) {
    echo $tagItem->getValue();
}
```

### Получение класса HL-блока по символьному коду (по NAME)

```php
$hlblocks = HighloadBlockTable::getList([
    'filter' => ['=NAME' => 'Colors'],
])->fetch();
if ($hlblocks) {
    $entity = HighloadBlockTable::compileEntity($hlblocks);
    $entityClass = $entity->getDataClass();
}
```

---

## Инфоблоки — события

Все события инфоблоков (`OnBeforeIBlockElementAdd` и пр.) — **legacy**: параметры передаются по ссылке. Для корректной модификации полей и отмены операции используй `addEventHandlerCompatible`, а не `addEventHandler`.

> `addEventHandler` (version=2) оборачивает параметры в объект `Event` — ссылка теряется, изменения не применяются. `addEventHandlerCompatible` (version=1) передаёт `$arFields` напрямую по ссылке.

```php
use Bitrix\Main\EventManager;

$em = EventManager::getInstance();

// Изменение полей ДО добавления — addEventHandlerCompatible + by-ref
$em->addEventHandlerCompatible(
    'iblock',
    'OnBeforeIBlockElementAdd',
    ['\MyVendor\MyModule\IblockHandler', 'onBeforeAdd']
);

// Действия ПОСЛЕ добавления (кеш, уведомления)
$em->addEventHandlerCompatible(
    'iblock',
    'OnAfterIBlockElementAdd',
    ['\MyVendor\MyModule\IblockHandler', 'onAfterAdd']
);

// Аналогично: OnBeforeIBlockElementUpdate, OnAfterIBlockElementUpdate,
//             OnBeforeIBlockElementDelete, OnAfterIBlockElementDelete
```

```php
namespace MyVendor\MyModule;

use Bitrix\Main\Application;

class IblockHandler
{
    /**
     * OnBefore* — $arFields по ссылке.
     * Отмена операции: global $APPLICATION; $APPLICATION->ThrowException('Ошибка');
     * После ThrowException ядро прочитает GetException() и вернёт false из Add/Update.
     */
    public static function onBeforeAdd(array &$arFields): void
    {
        // Фильтровать только нужный инфоблок
        if ((int)($arFields['IBLOCK_ID'] ?? 0) !== MY_IBLOCK_ID) {
            return;
        }

        // Нормализация полей — работает через ссылку
        $arFields['NAME'] = trim($arFields['NAME'] ?? '');
        $arFields['PREVIEW_TEXT'] = strip_tags($arFields['PREVIEW_TEXT'] ?? '');

        // Отменить добавление
        if (empty($arFields['NAME'])) {
            global $APPLICATION;
            $APPLICATION->ThrowException('Название обязательно');
            return;
        }
    }

    /**
     * OnAfter* — $arFields по ссылке; содержит ['ID'] = ID только что добавленного элемента.
     */
    public static function onAfterAdd(array &$arFields): void
    {
        if ((int)($arFields['IBLOCK_ID'] ?? 0) !== MY_IBLOCK_ID) {
            return;
        }

        $id = (int)($arFields['ID'] ?? 0);
        if (!$id) {
            return;
        }

        // Очистить тегированный кеш инфоблока
        Application::getInstance()->getTaggedCache()
            ->clearByTag('iblock_id_' . MY_IBLOCK_ID);
    }

    /**
     * OnBeforeIBlockElementDelete — $id (int) по ссылке, не массив!
     */
    public static function onBeforeDelete(int &$id): void
    {
        // Проверка перед удалением
        // Отмена: $APPLICATION->ThrowException('...')
    }
}
```

---

## Инфоблоки — Gotchas

- **`compileEntity()` не принимает int** — только строку API_CODE или объект `Iblock`. Для компиляции по ID: сначала `getById()->fetchObject()`, потом передай объект.
- **Без API_CODE — нет D7 ORM**. Поле `API_CODE` обязательно. Если не установлено, `getEntityDataClass()` вернёт null и триггернёт `E_USER_WARNING`.
- **VERSION=1 vs VERSION=2**: v1 — все значения в `b_iblock_element_property`; v2 — одиночные в `b_iblock_element_prop_{ID}`, множественные в `b_iblock_element_prop_m_{ID}`. ORM абстрагирует разницу, но важно для прямых SQL.
- **Множественные свойства в D7 ORM**: нельзя использовать `fetch()` если в select есть множественное свойство — получишь дубли строк. Используй `fetchObject()` + коллекцию.
- **Свойство без CODE** — не попадёт в скомпилированную сущность (цикл по `$property->getCode()` пропускает пустые).
- **`GetNext()` vs `Fetch()` в legacy**: `GetNext()` заменяет спецсимволы HTML, применяет шаблоны URL (`LIST_PAGE_URL`, `DETAIL_PAGE_URL`). `Fetch()` — сырые данные без замен.
- **`SetPropertyValues` vs `SetPropertyValuesEx`**: `SetPropertyValues` устанавливает по массиву `[PROP_ID => value]`; `SetPropertyValuesEx` — по `[PROP_CODE => value]` — предпочтителен.
- **HL-блок: `compileEntity` кеширует класс** в памяти — повторный вызов возвращает уже созданный класс, не пересоздаёт. Безопасно вызывать несколько раз.
- **HL UTM-таблицы**: при переименовании поля физическая таблица не переименовывается — остаётся со старым именем. При удалении поля — таблица удаляется.
- **`SECTION_ID` vs `IBLOCK_SECTION_ID` в GetList**: `SECTION_ID` — фильтрует по разделу (с учётом `INCLUDE_SUBSECTIONS`); в поле результата — `IBLOCK_SECTION_ID`.

---

---

## Source: `highloadblock.md`

# Highload-блоки, права и UI (модуль highloadblock)

> Audit note: ниже сверено с текущим `www/bitrix/modules/highloadblock` версии `24.100.0`. Подтверждены `\Bitrix\Highloadblock\HighloadBlockTable`, `DataManager`, `HighloadBlockRightsTable`, компоненты `bitrix:highloadblock.list`, `bitrix:highloadblock.view`, `bitrix:highloadblock.field.element`, а также `\Bitrix\Highloadblock\Integration\UI\EntitySelector\ElementProvider`.

## Для чего использовать

`highloadblock` в этом core нужен не только как “справочник для directory-свойств”. Это отдельный рабочий контур для:

- CRUD и миграций HL-блоков;
- динамической ORM через `compileEntity`;
- пользовательских полей и UTM-таблиц для множественных UF;
- прав доступа к элементам HL;
- стандартного UI-вывода списка и карточки;
- selector-интеграции через `ui.entity-selector`.

Если задача звучит как:

- “создать/обновить highload-блок”
- “получить data class HL-блока”
- “почему HL-поле не сохранилось”
- “как показать HL-элементы в selector”

то первым маршрутом должен быть именно `highloadblock`, а не общие заметки про инфоблоки.

## `HighloadBlockTable`

Подтверждены ключевые методы:

- `add(array $data)`
- `update($primary, array $data)`
- `delete($primary)`
- `resolveHighloadblock($hlblock)`
- `compileEntity($hlblock, bool $force = false)`
- `compileEntityId($id)`
- `OnBeforeUserTypeAdd($field)`
- `onAfterUserTypeAdd($field)`
- `OnBeforeUserTypeDelete($field)`
- `getUtmEntityClassName(...)`
- `getMultipleValueTableName(...)`
- `cleanCache()`

Что важно:

- `add()` реально создаёт физическую таблицу HL-блока в БД;
- `update()` умеет переименовывать таблицу и UTM-таблицы множественных полей;
- `delete()` удаляет права, файлы file-UF и саму HL-таблицу;
- `cleanCache()` дополнительно чистит кеш `CIBlockPropertyDirectory`.

### `resolveHighloadblock` и `compileEntity`

`resolveHighloadblock(...)` принимает:

- массив описания HL-блока;
- ID;
- `NAME`.

`compileEntity(...)` принимает тот же набор и строит динамическую ORM-сущность поверх таблицы HL-блока.

```php
use Bitrix\Highloadblock\HighloadBlockTable;
use Bitrix\Main\Loader;

Loader::includeModule('highloadblock');

$hlblock = HighloadBlockTable::getRow([
    'filter' => ['=TABLE_NAME' => 'b_hlbd_brand'],
]);

$entity = HighloadBlockTable::compileEntity($hlblock);
$dataClass = $entity->getDataClass();

$rows = $dataClass::getList([
    'select' => ['ID', 'UF_NAME', 'UF_XML_ID'],
    'order' => ['UF_SORT' => 'ASC', 'ID' => 'ASC'],
]);
```

Практическое правило:

- если у тебя есть `TABLE_NAME`, сначала ищи HL через `getRow(...)`, потом компилируй entity;
- не пытайся руками строить DataManager для HL-таблиц.

### `compileEntityId`

Подтверждено:

- `HighloadBlockTable::compileEntityId(42)` возвращает строку `HLBLOCK_42`.

Это `ENTITY_ID` для UF-полей самого HL-блока, а не ID записи внутри него.

## Динамический `DataManager`

Подтверждён базовый класс `\Bitrix\Highloadblock\DataManager`.

Ключевые методы:

- `getHighloadBlock()`
- `checkFields(...)`
- `add(array $data)`
- `update($primary, array $data)`
- `delete($primary)`

Что это значит practically:

- add/update/delete HL-элементов идут не через обычный generic ORM, а через слой, который дополнительно прогоняет данные через `USER_FIELD_MANAGER`;
- file-UF, multiple-UF и save modifiers реально обрабатываются внутри этого класса;
- для HL-элементов не нужно руками повторять логику UTM и file cleanup.

```php
use Bitrix\Highloadblock\HighloadBlockTable;
use Bitrix\Main\Loader;

Loader::includeModule('highloadblock');

$entity = HighloadBlockTable::compileEntity('BrandReference');
$dataClass = $entity->getDataClass();

$result = $dataClass::add([
    'UF_NAME' => 'Acme',
    'UF_XML_ID' => 'acme',
    'UF_SORT' => 100,
]);

if (!$result->isSuccess())
{
    throw new \RuntimeException(implode('; ', $result->getErrorMessages()));
}
```

## Пользовательские поля и storage

Инсталлятор модуля подтверждает зависимости:

- `main:OnBeforeUserTypeAdd`
- `main:OnAfterUserTypeAdd`
- `main:OnBeforeUserTypeDelete`
- `main:OnUserTypeBuildList`
- `iblock:OnIBlockPropertyBuildList`

Отсюда следуют важные факты:

- HL сам управляет storage для своих UF;
- для множественных полей создаются отдельные UTM-таблицы;
- postfix `_REF` зарезервирован для ссылок на другие HL-блоки;
- `directory`-свойства инфоблоков тоже завязаны на модуль `highloadblock`.

Подтверждённые правила из ядра:

- при `OnBeforeUserTypeAdd` имя поля с суффиксом `_REF` запрещено;
- при удалении file-UF модуль сам удаляет привязанные файлы;
- при удалении multiple-UF модуль удаляет UTM-таблицу.

## Права доступа

В инсталляторе подтверждены модульные задачи:

- `hblock_denied`
- `hblock_read`
- `hblock_write`

И операции:

- `hl_element_read`
- `hl_element_write`
- `hl_element_delete`

Подтверждён `\Bitrix\Highloadblock\HighloadBlockRightsTable` и метод:

- `getOperationsName($hlId)`

Практически это значит:

- стандартные HL-компоненты реально проверяют права через `HighloadBlockRightsTable::getOperationsName(...)`;
- если пользователь не админ и операций нет, типовой UI не покажет блок.

## Стандартные компоненты

Подтверждены:

- `bitrix:highloadblock.list`
- `bitrix:highloadblock.view`
- `bitrix:highloadblock.field.element`

### `highloadblock.list`

Компонент:

- принимает `BLOCK_ID`;
- при `CHECK_PERMISSIONS='Y'` проверяет права;
- строит запрос через `Entity\Query`;
- поддерживает фильтр через `FILTER_NAME`;
- пагинацию через `\Bitrix\Main\UI\PageNavigation` (детальный контракт см. `pagination.md`);
- рендерит list values через `getadminlistviewhtml`.

### `highloadblock.view`

Компонент:

- принимает `BLOCK_ID`, `ROW_KEY`, `ROW_ID`;
- получает данные через `Entity\Query`;
- готовит UF через `getUserFieldsWithReadyData(...)`.

### `highloadblock.field.element`

Это штатный UF-компонент для поля типа HL-элемент. Он наследуется от `BaseUfComponent` и использует:

- `\CUserTypeHlblock::USER_TYPE_ID`
- `\CUserTypeHlblock::getDefaultSettings(...)`

## UI Entity Selector

Подтверждён `\Bitrix\Highloadblock\Integration\UI\EntitySelector\ElementProvider`.

Подтверждены:

- `ENTITY_ID = 'highloadblock-element'`
- опции `highloadblockId`, `valueField`, `titleField`, `orderField`, `direction`, `queryMethod`
- методы `getItems`, `getPreselectedItems`, `fillDialog`, `doSearch`

По умолчанию используются поля:

- `UF_XML_ID` как value;
- `UF_NAME` как title;
- `UF_SORT` как order.

Это важный маршрут, если задача про selector/dialog вместо старого select в админке или форме.

## Gotchas

- `compileEntityId()` нужен для UF-схемы HL-блока, а не для выборки его строк.
- `compileEntity(...)` принимает ID, NAME или массив блока; если вход кривой, ядро бросает `SystemException`.
- `_REF` в имени UF-поля HL-блока зарезервирован, не используй его произвольно.
- Множественные HL-поля создают отдельные UTM-таблицы, так что “поле есть, а колонки нет” для `MULTIPLE=Y` — нормальное поведение.
- Если в HL-компоненте у не-админа внезапно 404/пусто, сначала смотри `HighloadBlockRightsTable::getOperationsName(...)`, а не фильтр компонента.

---

## Source: `iblock-hl-relations.md`

# Связь инфоблок ↔ HL-блок

> Этот reference держи как слой именно про связи ИБ ↔ HL и `_REF`/`directory`-механику. Если задача уже про сам highload-блок как сущность, его CRUD, права, `compileEntity`, стандартные `highloadblock.*` компоненты или selector, дополнительно загружай `highloadblock.md`.

Два совершенно разных механизма. Путают часто. Важно понять какой именно используется в проекте.

---

## Механизм 1 — Свойство инфоблока типа `directory` (USER_TYPE='directory')

**Класс:** `CIBlockPropertyDirectory` (модуль `highloadblock`)

**Что хранит:** строку `UF_XML_ID` HL-записи — **не числовой ID**, а XML-код.

**Настройки свойства:** `USER_TYPE_SETTINGS['TABLE_NAME']` = имя таблицы HL-блока (напр. `b_hlbd_color`).

**Для чего используют:** HL-блок как справочник (цвет, размер, страна и т.п.). HL-блок должен иметь стандартные поля: `UF_XML_ID` (обязательно), `UF_NAME`, `UF_SORT`, `UF_FILE`, `UF_DEF`.

### Чтение через legacy

```php
use Bitrix\Main\Loader;
Loader::includeModule('iblock');
Loader::includeModule('highloadblock');

// $el['PROPERTY_COLOR_VALUE'] = 'red' — это UF_XML_ID HL-записи!
$res = CIBlockElement::GetList(
    ['SORT' => 'ASC'],
    ['IBLOCK_ID' => PRODUCTS_IBLOCK_ID, 'ACTIVE' => 'Y'],
    false, false,
    ['ID', 'NAME', 'PROPERTY_COLOR']
);
while ($el = $res->GetNext()) {
    $xmlId = $el['PROPERTY_COLOR_VALUE'];  // строка 'red', не int!

    // Получить полную HL-запись по UF_XML_ID
    if ($xmlId) {
        $colorRecord = self::getHlRecordByXmlId('b_hlbd_color', $xmlId);
        echo $colorRecord['UF_NAME'];      // 'Красный'
    }
}

// Вспомогательный метод — получить HL-запись по UF_XML_ID
function getHlRecordByXmlId(string $tableName, string $xmlId): ?array
{
    $hlblock = \Bitrix\Highloadblock\HighloadBlockTable::getRow([
        'filter' => ['=TABLE_NAME' => $tableName],
    ]);
    if (!$hlblock) return null;

    $entity = \Bitrix\Highloadblock\HighloadBlockTable::compileEntity($hlblock);
    $dataClass = $entity->getDataClass();

    return $dataClass::getRow([
        'filter' => ['=UF_XML_ID' => $xmlId],
        'select' => ['ID', 'UF_XML_ID', 'UF_NAME', 'UF_FILE', 'UF_SORT'],
    ]);
}
```

### Чтение через D7 ORM (ElementV2Table)

```php
use Bitrix\Iblock\Elements\ElementProductsTable; // API_CODE='products'

$result = ElementProductsTable::getList([
    'select' => ['ID', 'NAME', 'COLOR_XML_ID' => 'COLOR.VALUE'],
    'filter' => ['=ACTIVE' => 'Y'],
]);
while ($row = $result->fetch()) {
    $xmlId = $row['COLOR_XML_ID'];  // UF_XML_ID из b_iblock_element_property.VALUE
    // Отдельный запрос к HL-блоку (join в D7 ORM инфоблоков для directory не автоматический)
}
```

### Фильтрация элементов ИБ по значению directory-свойства

```php
// Legacy — фильтр по UF_XML_ID значению
CIBlockElement::GetList([], [
    'IBLOCK_ID'       => PRODUCTS_IBLOCK_ID,
    'PROPERTY_COLOR'  => 'red',            // значение = UF_XML_ID
], false, false, ['ID', 'NAME']);

// D7 ORM
ElementProductsTable::getList([
    'filter' => ['=COLOR.VALUE' => 'red'],  // VALUE = UF_XML_ID
    'select' => ['ID', 'NAME'],
]);
```

### Массовая загрузка: весь справочник в кеш

```php
// Загрузить весь HL-справочник в память — эффективнее чем N запросов в цикле
function loadDirectoryIndex(string $tableName): array
{
    $hlblock = \Bitrix\Highloadblock\HighloadBlockTable::getRow([
        'filter' => ['=TABLE_NAME' => $tableName],
    ]);
    if (!$hlblock) return [];

    $entity = \Bitrix\Highloadblock\HighloadBlockTable::compileEntity($hlblock);
    $dataClass = $entity->getDataClass();

    $index = [];
    $iterator = $dataClass::getList([
        'select' => ['ID', 'UF_XML_ID', 'UF_NAME', 'UF_FILE', 'UF_SORT'],
        'order'  => ['UF_SORT' => 'ASC'],
    ]);
    while ($row = $iterator->fetch()) {
        $index[$row['UF_XML_ID']] = $row;
    }
    return $index;
}

// Использование
$colors = loadDirectoryIndex('b_hlbd_color');

$res = CIBlockElement::GetList([], ['IBLOCK_ID' => PRODUCTS_IBLOCK_ID], false, false,
    ['ID', 'NAME', 'PROPERTY_COLOR']);
while ($el = $res->GetNext()) {
    $xmlId = $el['PROPERTY_COLOR_VALUE'];
    $color = $colors[$xmlId] ?? null;
    echo $color ? $color['UF_NAME'] : '—';
}
```

---

## Механизм 2 — UF-поле типа `hlblock` (USER_TYPE_ID='hlblock')

**Класс:** `CUserTypeHlblock` (модуль `highloadblock`)

**Что хранит:** числовой `ID` HL-записи (int).

**Где хранится:** зависит от сущности и кратности поля. В текущем core `CUserTypeHlblock` даёт `BASE_TYPE_INT`, а точные таблицы надо смотреть по конкретной сущности: single-value может лежать в основной/UTS-структуре, multiple — в UTM-таблице.

**Настройки:** `SETTINGS['HLBLOCK_ID']` = ID HL-блока, `SETTINGS['HLFIELD_ID']` = ID поля HL для отображения в списке.

**Для чего используют:** произвольные связи сущность → HL-запись, когда нужен `int` ID и/или автоматический `_REF`.

**Регистрация UF:** `ENTITY_ID` зависит от сущности. Не предполагай `'IBLOCK_ELEMENT'` вслепую. Для разделов в текущем core типичный паттерн — `IBLOCK_<IBLOCK_ID>_SECTION`, для HL-сущностей — `HLBLOCK_<ID>`.

> Поле называется `UF_BRAND`, `UF_PRODUCER` и т.д. — с префиксом `UF_`.

### Чтение через legacy

```php
global $USER_FIELD_MANAGER;

// Получить UF-значения элемента ИБ
$ufValues = $USER_FIELD_MANAGER->GetUserFields('IBLOCK_ELEMENT', $elementId, LANGUAGE_ID);
$hlRecordId = $ufValues['UF_BRAND']['VALUE'];  // int — ID HL-записи

// Получить HL-запись по ID
$hlblock = \Bitrix\Highloadblock\HighloadBlockTable::getById($hlblockId)->fetch();
$entity  = \Bitrix\Highloadblock\HighloadBlockTable::compileEntity($hlblock);
$dataClass = $entity->getDataClass();

$brandRecord = $dataClass::getById($hlRecordId)->fetch();
echo $brandRecord['UF_NAME'];
```

### Чтение через D7 ORM — автоматический Reference (_REF)

`CUserTypeHlblock::getEntityReferences()` автоматически добавляет relation `UF_BRAND_REF` в скомпилированную сущность инфоблока. Работает в `ElementV2Table`.

```php
use Bitrix\Iblock\Elements\ElementProductsTable; // VERSION=2, API_CODE='products'

$result = ElementProductsTable::getList([
    'select' => [
        'ID',
        'NAME',
        'UF_BRAND',                         // числовой ID HL-записи
        'BRAND_NAME'  => 'UF_BRAND_REF.UF_NAME',   // JOIN к HL-блоку!
        'BRAND_LOGO'  => 'UF_BRAND_REF.UF_LOGO',   // файл
        'BRAND_XML'   => 'UF_BRAND_REF.UF_XML_ID',
    ],
    'filter' => ['=ACTIVE' => 'Y'],
    'order'  => ['SORT' => 'ASC'],
]);
while ($row = $result->fetch()) {
    echo $row['NAME'] . ' — ' . $row['BRAND_NAME'];
}
```

> **Gotcha:** `UF_BRAND_REF` работает только в `ElementV2Table` (VERSION=2). В legacy ORM (`ElementV1Table`) автоматический reference не добавляется.

### Фильтр по UF_hlblock в D7 ORM

```php
ElementProductsTable::getList([
    'filter' => ['=UF_BRAND' => 5],           // по ID HL-записи
    'select' => ['ID', 'NAME', 'UF_BRAND'],
]);

// Фильтр по полю HL-записи (через _REF)
ElementProductsTable::getList([
    'filter' => ['=UF_BRAND_REF.UF_XML_ID' => 'nike'],
    'select' => ['ID', 'NAME', 'BRAND_NAME' => 'UF_BRAND_REF.UF_NAME'],
]);
```

### Множественное UF-поле типа hlblock

Если `MULTIPLE='Y'` — значения хранятся в UTM-таблице `b_utm_iblock_element.UF_BRAND[]`.

```php
// Через fetchObject + коллекцию
$obj = ElementProductsTable::query()
    ->setSelect(['ID', 'NAME', 'UF_BRANDS'])
    ->setFilter(['=ACTIVE' => 'Y'])
    ->fetchObject();

foreach ($obj->getUfBrands() as $brandId) {
    // каждый $brandId — int ID HL-записи
}

// Через runtime Reference + множественную связь
// Сложнее — проще два запроса
```

---

## Механизм 3 — Числовое/строковое свойство (ручная связь)

Встречается в старых проектах: обычное свойство `TYPE_NUMBER` или `TYPE_STRING`, в котором вручную хранится ID HL-записи. Никакого автоматического join-а нет.

```php
// Чтение
$el = CIBlockElement::GetByID($id)->GetNext();
$hlId = (int)$el['PROPERTY_HL_REF_VALUE'];

// Затем отдельный запрос к HL
$hlblock = \Bitrix\Highloadblock\HighloadBlockTable::getById($hlblockId)->fetch();
$entity  = \Bitrix\Highloadblock\HighloadBlockTable::compileEntity($hlblock);
$dataClass = $entity->getDataClass();
$row = $dataClass::getById($hlId)->fetch();
```

---

## Паттерн AbstractOrmRepository и связь с HL

`AbstractOrmRepository` — кастомный базовый класс, типичный в D7-проектах. Он оборачивает `DataManager::getList()` и предоставляет репозиторный интерфейс.

### Типичная реализация

```php
abstract class AbstractOrmRepository
{
    abstract protected function getDataClass(): string; // вернуть FQN DataManager

    public function findById(int $id): ?array
    {
        return $this->getDataClass()::getById($id)->fetch() ?: null;
    }

    public function findAll(array $filter = [], array $select = ['*'], array $order = ['ID' => 'ASC']): array
    {
        return $this->getDataClass()::getList([
            'filter' => $filter,
            'select' => $select,
            'order'  => $order,
        ])->fetchAll();
    }

    public function findOne(array $filter, array $select = ['*']): ?array
    {
        return $this->getDataClass()::getRow([
            'filter' => $filter,
            'select' => $select,
        ]);
    }
}
```

### Репозиторий инфоблока с HL-связью

Если базовый класс наследует `AbstractOrmRepository` и обёртывает `ElementProductsTable`, подключить HL-поля через `_REF`:

```php
use Bitrix\Iblock\Elements\ElementProductsTable;

class ProductRepository extends AbstractOrmRepository
{
    protected function getDataClass(): string
    {
        return ElementProductsTable::class;
    }

    // Список продуктов с данными HL-бренда (VERSION=2, UF_BRAND поле hlblock-типа)
    public function findActiveWithBrand(array $filter = []): array
    {
        return ElementProductsTable::getList([
            'select' => [
                'ID', 'NAME', 'CODE', 'SORT',
                'PREVIEW_TEXT',
                'UF_BRAND',
                'BRAND_NAME' => 'UF_BRAND_REF.UF_NAME',
                'BRAND_LOGO' => 'UF_BRAND_REF.UF_LOGO',
            ],
            'filter' => array_merge(['=ACTIVE' => 'Y'], $filter),
            'order'  => ['SORT' => 'ASC'],
        ])->fetchAll();
    }

    // Альтернатива: отдельный запрос к HL (если VERSION=1 или нет _REF)
    public function findActiveWithBrandSeparate(): array
    {
        // Шаг 1: элементы
        $elements = ElementProductsTable::getList([
            'select' => ['ID', 'NAME', 'UF_BRAND'],
            'filter' => ['=ACTIVE' => 'Y'],
        ])->fetchAll();

        // Шаг 2: собрать уникальные ID брендов
        $brandIds = array_unique(array_filter(array_column($elements, 'UF_BRAND')));

        if (empty($brandIds)) {
            return $elements;
        }

        // Шаг 3: один запрос к HL
        $hlblock  = \Bitrix\Highloadblock\HighloadBlockTable::getRow(
            ['filter' => ['=NAME' => 'Brands']]
        );
        $entity   = \Bitrix\Highloadblock\HighloadBlockTable::compileEntity($hlblock);
        $dataClass = $entity->getDataClass();

        $brandsIndex = [];
        $iterator = $dataClass::getList([
            'filter' => ['=ID' => $brandIds],
            'select' => ['ID', 'UF_NAME', 'UF_LOGO'],
        ]);
        while ($row = $iterator->fetch()) {
            $brandsIndex[(int)$row['ID']] = $row;
        }

        // Шаг 4: смержить
        foreach ($elements as &$el) {
            $el['BRAND'] = $brandsIndex[(int)($el['UF_BRAND'] ?? 0)] ?? null;
        }
        unset($el);

        return $elements;
    }
}
```

### Репозиторий со связью через directory-свойство

```php
class ProductRepository extends AbstractOrmRepository
{
    protected function getDataClass(): string
    {
        return ElementProductsTable::class;
    }

    // COLOR — свойство типа directory, хранит UF_XML_ID
    public function findActiveWithColor(): array
    {
        // Шаг 1: загрузить весь справочник цветов
        $colorsHlblock = \Bitrix\Highloadblock\HighloadBlockTable::getRow([
            'filter' => ['=TABLE_NAME' => 'b_hlbd_color'],
        ]);
        $colorsEntity = \Bitrix\Highloadblock\HighloadBlockTable::compileEntity($colorsHlblock);
        $colorsClass  = $colorsEntity->getDataClass();

        $colorsIndex = [];
        $iterator = $colorsClass::getList([
            'select' => ['ID', 'UF_XML_ID', 'UF_NAME', 'UF_FILE'],
        ]);
        while ($row = $iterator->fetch()) {
            $colorsIndex[$row['UF_XML_ID']] = $row;
        }

        // Шаг 2: элементы с property COLOR
        $elements = ElementProductsTable::getList([
            'select' => ['ID', 'NAME', 'COLOR_XML_ID' => 'COLOR.VALUE'],
            'filter' => ['=ACTIVE' => 'Y'],
        ])->fetchAll();

        // Шаг 3: смержить
        foreach ($elements as &$el) {
            $xmlId = $el['COLOR_XML_ID'] ?? '';
            $el['COLOR'] = $colorsIndex[$xmlId] ?? null;
        }
        unset($el);

        return $elements;
    }
}
```

---

## ORM Runtime Reference: join HL к ИБ в одном запросе

Когда нет автоматического `_REF` (VERSION=1 или directory-свойство), можно добавить runtime Reference.

### Для UF_BRAND (хранит int ID)

```php
use Bitrix\Main\ORM\Fields\Relations\Reference;
use Bitrix\Main\ORM\Query\Join;
use Bitrix\Highloadblock\HighloadBlockTable;
use Bitrix\Iblock\Elements\ElementProductsTable;

// Компилируем сущность HL
$hlblock   = HighloadBlockTable::getRow(['filter' => ['=NAME' => 'Brands']]);
$hlEntity  = HighloadBlockTable::compileEntity($hlblock);

$result = ElementProductsTable::getList([
    'select' => [
        'ID', 'NAME',
        'BRAND_NAME' => 'BRAND_HL.UF_NAME',
        'BRAND_LOGO' => 'BRAND_HL.UF_LOGO',
    ],
    'runtime' => [
        new Reference(
            'BRAND_HL',
            $hlEntity,
            Join::on('this.UF_BRAND', 'ref.ID'),
            ['join_type' => 'LEFT']
        ),
    ],
    'filter' => ['=ACTIVE' => 'Y'],
]);
```

### Для directory-свойства (хранит UF_XML_ID строку)

```php
$colorsHlblock = HighloadBlockTable::getRow(['filter' => ['=TABLE_NAME' => 'b_hlbd_color']]);
$colorsEntity  = HighloadBlockTable::compileEntity($colorsHlblock);

$result = ElementProductsTable::getList([
    'select' => [
        'ID', 'NAME',
        'COLOR_XML_ID' => 'COLOR.VALUE',
        'COLOR_NAME'   => 'COLOR_HL.UF_NAME',
    ],
    'runtime' => [
        new Reference(
            'COLOR_HL',
            $colorsEntity,
            Join::on('this.COLOR.VALUE', 'ref.UF_XML_ID'),  // string = string
            ['join_type' => 'LEFT']
        ),
    ],
    'filter' => ['=ACTIVE' => 'Y'],
]);
```

> **Gotcha:** runtime Reference на свойство `COLOR.VALUE` работает только если `COLOR` уже является ORM-relation в скомпилированной сущности. Если нет — придётся делать два запроса.

---

## Как определить какой механизм используется в проекте

```php
use Bitrix\Iblock\PropertyTable;

// Проверить тип свойства в ИБ
$prop = PropertyTable::getRow([
    'filter' => ['=IBLOCK_ID' => PRODUCTS_IBLOCK_ID, '=CODE' => 'COLOR'],
    'select' => ['PROPERTY_TYPE', 'USER_TYPE', 'USER_TYPE_SETTINGS', 'LINK_IBLOCK_ID'],
]);

if ($prop) {
    // PROPERTY_TYPE='S', USER_TYPE='directory' → механизм 1
    //   $prop['USER_TYPE_SETTINGS']['TABLE_NAME'] = 'b_hlbd_color'
    //   VALUE хранит UF_XML_ID (строку)

    // PROPERTY_TYPE='E' → это не HL, это привязка к другому ЭЛЕМЕНТУ ИБ
    //   $prop['LINK_IBLOCK_ID'] = ID связанного ИБ
}

// Проверить UF-поля на конкретной UF-enabled сущности
global $USER_FIELD_MANAGER;
$entityId = 'IBLOCK_' . PRODUCTS_IBLOCK_ID . '_SECTION';
$ufs = $USER_FIELD_MANAGER->GetUserFields($entityId, 0, LANGUAGE_ID);
foreach ($ufs as $uf) {
    if ($uf['USER_TYPE_ID'] === 'hlblock') {
        // Механизм 2: UF_* поле
        // $uf['SETTINGS']['HLBLOCK_ID'] — ID HL-блока
        // $uf['FIELD_NAME'] = 'UF_BRAND'
        // VALUE хранит int ID HL-записи
    }
}
```

---

## Краткая таблица сравнения

| | directory (USER_TYPE) | hlblock (UF тип) | ручная (число/строка) |
|---|---|---|---|
| Где определяется | Свойство ИБ | UF-поле сущности | Свойство ИБ |
| Хранит | `UF_XML_ID` (строка) | `ID` (int) | ID или код (любой) |
| ORM-join | только runtime | `_REF` авто (v2) | только runtime |
| Фильтр по значению | `=PROPERTY_CODE => 'xml_id'` | `=UF_FIELD => 42` | `=PROPERTY_CODE => 42` |
| Доступ в legacy | `GetNext()['PROPERTY_CODE_VALUE']` | `USER_FIELD_MANAGER->GetUserFields` | `GetNext()['PROPERTY_CODE_VALUE']` |
| Доступ в D7 ORM | `CODE.VALUE` | `UF_FIELD` + `UF_FIELD_REF.*` | `CODE.VALUE` |

---

## Gotchas

- **directory хранит UF_XML_ID, не ID** — частая ошибка: ищут HL-запись по `ID = $value` вместо `UF_XML_ID = $value`
- **`_REF` добавляется через `CUserTypeHlblock::getEntityReferences()`** — не угадывай имя join-а, смотри реальную compiled entity
- **ENTITY_ID зависит от сущности** — сначала выясни, где живёт UF-поле в конкретном проекте, потом уже читай/пиши его
- **`compileEntity` по TABLE_NAME** — всегда ищи HL-блок через `HighloadBlockTable::getRow(['filter'=>['=TABLE_NAME'=>...]])`, затем `compileEntity` с полученным массивом
- **Runtime Reference на `CODE.VALUE`** — работает только если `CODE` — объявленный relations в скомпилированной сущности; если CODE ещё не в select — join не встроится
- **N+1 в цикле** — никогда не делай запрос к HL внутри foreach элементов. Загружай весь индекс один раз (загрузка всех записей HL), потом смерживай в памяти
- **`HighloadBlockTable::compileEntityId($id)`** возвращает строку `'HLBLOCK_42'` — это ENTITY_ID для UF-полей самого HL-блока, не элементов ИБ

---

## Source: `entities-migrations.md`

# Bitrix Сущности и миграции — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с программным созданием инфоблоков, типов инфоблоков, свойств, групп пользователей, назначением прав или написанием миграций.

## ⚠️ ПРАВИЛО ПОДТВЕРЖДЕНИЯ

**Любое действие, изменяющее данные в БД, требует явного подтверждения пользователя.**

Перед выполнением каждой операции показывай:
```
Собираюсь выполнить:
  [тип операции]: [краткое описание]
  Что изменится: [таблицы/данные]
  Обратимость: [обратимо / необратимо]

Продолжить? (да/нет)
```

Примеры обязательного подтверждения:
- Создание инфоблока/типа/свойства
- Удаление инфоблока, группы, пользователя
- Установка прав доступа (перезаписывает старые)
- Запуск SQL-миграции
- Удаление таблицы или ALTER TABLE

---

## Содержание
- Инфоблок-тип (CIBlockType)
- Создание инфоблока (CIBlock::Add)
- Свойства инфоблока (CIBlockProperty)
- Права на инфоблок (CIBlock::SetPermission)
- Группы пользователей (CGroup)
- Управление пользователями (CUser)
- Права модулей (SetGroupRight)
- Миграции в Bitrix
- Gotchas

---

## Типы инфоблоков (CIBlockType)

Тип — контейнер для группировки инфоблоков (например `catalog`, `content`, `news`).

```php
// Проверяем: тип уже существует?
$existing = CIBlockType::GetByID('catalog');
if ($existing->Fetch()) {
    // тип уже есть — не создавать
}

// Создать тип
$ibt = new CIBlockType();
$id = $ibt->Add([
    'ID'       => 'catalog',     // уникальный строковый ID, только латиница+цифры+_
    'SECTIONS' => 'Y',           // 'Y' = инфоблоки этого типа имеют разделы
    'IN_RSS'   => 'N',
    'SORT'     => 100,
    'LANG'     => [
        'ru' => ['NAME' => 'Каталог', 'ELEMENT_NAME' => 'Товар', 'SECTION_NAME' => 'Раздел'],
        'en' => ['NAME' => 'Catalog', 'ELEMENT_NAME' => 'Product', 'SECTION_NAME' => 'Section'],
    ],
]);
if (!$id) {
    throw new \RuntimeException('CIBlockType::Add error: ' . $ibt->LAST_ERROR);
}
```

---

## Создание инфоблока (CIBlock::Add)

```php
use Bitrix\Main\Loader;
Loader::requireModule('iblock');

// Всегда проверяй существование перед созданием
$existing = \Bitrix\Iblock\IblockTable::getList([
    'filter' => ['=CODE' => 'products'],
    'select' => ['ID'],
])->fetch();
if ($existing) {
    return $existing['ID']; // уже создан
}

$ib = new CIBlock();
$iblockId = $ib->Add([
    // --- Обязательные ---
    'IBLOCK_TYPE_ID' => 'catalog',  // ID типа инфоблока
    'LID'            => ['s1'],     // массив ID сайтов (или строка 's1')
    'NAME'           => 'Товары',
    'CODE'           => 'products', // символьный код (латиница, уникальный)

    // --- Настройки ---
    'ACTIVE'         => 'Y',
    'SORT'           => 100,
    'VERSION'        => 2,          // 1 = старая схема, 2 = раздельные таблицы (рекомендуется)
    'INDEX_ELEMENT'  => 'Y',        // индексировать элементы для поиска
    'INDEX_SECTION'  => 'N',

    // --- API_CODE ---
    // Нужен не всегда, но обязателен для ряда generated DataClass / REST-сценариев.
    // Формат в текущем core: первая буква латинская, далее только буквы и цифры.
    'API_CODE'       => 'products',

    // --- Опционально ---
    'DESCRIPTION'          => '',
    'DESCRIPTION_TYPE'     => 'text', // 'text' | 'html'
    'LIST_PAGE_URL'        => '#SITE_DIR#/catalog/',
    'DETAIL_PAGE_URL'      => '#SITE_DIR#/catalog/#CODE#/',
    'SECTION_PAGE_URL'     => '#SITE_DIR#/catalog/#SECTION_CODE#/',
    'RIGHTS_MODE'          => 'S',  // 'S' = простые права, 'E' = расширенные
    'WORKFLOW'             => 'N',  // устаревший режим документооборота
]);

if (!$iblockId) {
    throw new \RuntimeException('CIBlock::Add error: ' . $ib->LAST_ERROR);
}
```

---

## Свойства инфоблока (CIBlockProperty::Add)

```php
$prop = new CIBlockProperty();

// Строковое свойство
$prop->Add([
    'IBLOCK_ID'     => $iblockId,
    'NAME'          => 'Артикул',
    'CODE'          => 'ARTICLE',        // символьный код, уникальный в рамках ИБ
    'PROPERTY_TYPE' => 'S',             // S=строка, N=число, F=файл, E=элемент, G=раздел, L=список
    'ACTIVE'        => 'Y',
    'SORT'          => 100,
    'MULTIPLE'      => 'N',
    'IS_REQUIRED'   => 'N',
    'SEARCHABLE'    => 'Y',
    'FILTRABLE'     => 'Y',
    'USER_TYPE'     => '',              // '' | 'HTML' | 'DateTime' | 'Date' | 'video' | кастомный
]);

// Числовое свойство
$prop->Add([
    'IBLOCK_ID'     => $iblockId,
    'NAME'          => 'Цена',
    'CODE'          => 'PRICE',
    'PROPERTY_TYPE' => 'N',
    'SORT'          => 200,
]);

// Свойство-список (перечисление)
$listPropId = $prop->Add([
    'IBLOCK_ID'     => $iblockId,
    'NAME'          => 'Цвет',
    'CODE'          => 'COLOR',
    'PROPERTY_TYPE' => 'L',
    'LIST_TYPE'     => 'L',  // 'L'=выпадающий список, 'C'=чекбоксы
    'SORT'          => 300,
]);
// Добавить варианты списка
if ($listPropId) {
    $enum = new CIBlockPropertyEnum();
    foreach (['Красный', 'Синий', 'Зелёный'] as $i => $val) {
        $enum->Add([
            'PROPERTY_ID' => $listPropId,
            'VALUE'       => $val,
            'SORT'        => ($i + 1) * 10,
            'XML_ID'      => mb_strtolower($val),
        ]);
    }
}

// Привязка к элементу другого ИБ
$prop->Add([
    'IBLOCK_ID'       => $iblockId,
    'NAME'            => 'Бренд',
    'CODE'            => 'BRAND',
    'PROPERTY_TYPE'   => 'E',
    'LINK_IBLOCK_ID'  => $brandIblockId,  // ID ИБ, к которому привязка
    'SORT'            => 400,
]);

// Множественное файловое свойство
$prop->Add([
    'IBLOCK_ID'     => $iblockId,
    'NAME'          => 'Галерея',
    'CODE'          => 'GALLERY',
    'PROPERTY_TYPE' => 'F',
    'MULTIPLE'      => 'Y',
    'SORT'          => 500,
]);

if (!$prop->LAST_ERROR) {
    // успех
} else {
    throw new \RuntimeException('CIBlockProperty::Add error: ' . $prop->LAST_ERROR);
}
```

---

## Права на инфоблок (CIBlock::SetPermission)

`SetPermission` **перезаписывает** все права инфоблока. Передавай полный список групп.

```php
// Уровни прав:
// 'R' = чтение
// 'S' = чтение + просмотр детального
// 'E' = чтение + запись элементов
// 'T' = чтение + ограниченная модификация
// 'U' = workflow/документооборотный уровень
// 'W' = запись (редактирование, добавление)
// 'X' = полные права
// Важно: в текущем core "нет доступа" достигается не буквой 'D', а отсутствием записи для группы.

CIBlock::SetPermission($iblockId, [
    1  => 'X',  // группа 1 = Администраторы
    2  => 'R',  // группа 2 = Все (Everyone) — публичное чтение
    // другие группы — просто не указывать
]);

// Получить ID групп по коду:
$rs = CGroup::GetList('', '', ['STRING_ID' => 'MY_EDITORS']);
$editorGroup = $rs->Fetch();
// $editorGroup['ID'] — ID группы

CIBlock::SetPermission($iblockId, [
    1                    => 'X',   // Администраторы
    2                    => 'R',   // Все
    $editorGroup['ID']   => 'W',   // Редакторы
]);
```

---

## Группы пользователей (CGroup)

```php
// Найти группу по строковому коду перед созданием
$existing = CGroup::GetList('', '', ['STRING_ID' => 'CATALOG_EDITORS'])->Fetch();
if ($existing) {
    $groupId = $existing['ID'];
} else {
    // Создать группу
    $group = new CGroup();
    $groupId = $group->Add([
        'NAME'        => 'Редакторы каталога',
        'DESCRIPTION' => 'Могут редактировать товары в каталоге',
        'STRING_ID'   => 'CATALOG_EDITORS',  // уникальный строковый код — удобен для поиска
        'ACTIVE'      => 'Y',
        'C_SORT'      => 100,
    ]);
    if (!$groupId) {
        throw new \RuntimeException('CGroup::Add error: ' . $group->LAST_ERROR);
    }
}

// Изменить группу
$group = new CGroup();
$group->Update($groupId, [
    'NAME' => 'Редакторы каталога и новостей',
]);
```

---

## Управление пользователями (CUser)

```php
// Найти пользователя
$res = CUser::GetList('', '', ['LOGIN' => 'editor@example.ru']);
$user = $res->Fetch();

// Создать пользователя
$user = new CUser();
$userId = $user->Add([
    'LOGIN'          => 'editor',
    'PASSWORD'       => 'SecurePass123!',
    'CONFIRM_PASSWORD' => 'SecurePass123!',
    'EMAIL'          => 'editor@example.ru',
    'NAME'           => 'Иван',
    'LAST_NAME'      => 'Иванов',
    'ACTIVE'         => 'Y',
    'GROUP_ID'       => [$groupId], // сразу назначить группы
]);
if (!$userId) {
    throw new \RuntimeException('CUser::Add error: ' . $user->LAST_ERROR);
}

// Назначить группы пользователю
// ВАЖНО: SetUserGroup ЗАМЕНЯЕТ все группы пользователя (кроме группы 2 = Все)
CUser::SetUserGroup($userId, [
    ['GROUP_ID' => $groupId],
    ['GROUP_ID' => 5],              // ещё одна группа
]);

// Получить группы пользователя
$groups = CUser::GetUserGroup($userId); // возвращает массив ID групп

// Обновить пользователя
$user = new CUser();
$user->Update($userId, [
    'EMAIL' => 'new-email@example.ru',
]);
```

---

## Права модулей для групп (SetGroupRight)

```php
// Установить права модуля для группы пользователей
// $right не универсален для всех модулей.
// В b_module_group хранится строка G_ACCESS, а допустимые значения зависят от модуля.
// Для iblock часто используют R/W/X, но не прошивай это как общий закон Bitrix.

// Глобально для всех сайтов
$APPLICATION->SetGroupRight('iblock', $groupId, 'W');

// Или напрямую:
CMain::SetGroupRight('iblock', $groupId, 'W');

// Для конкретного сайта
CMain::SetGroupRight('iblock', $groupId, 'W', 's1');

// Получить текущий уровень для конкретной группы:
$right = CMain::GetGroupRight('iblock', [$groupId]);

// Или для текущего пользователя:
$right = $APPLICATION->GetGroupRight('iblock');
```

---

## Миграции в Bitrix

### Реальность: в Bitrix нет встроенной системы миграций

Bitrix не имеет встроенного инструмента типа Laravel Artisan Migrate. Используются три подхода:

### Подход 1 — Установщик модуля как миграция (стандартный)

Для создания таблиц и начальных данных при установке модуля:

```php
// install/index.php → InstallDB() + UnInstallDB()
public function InstallDB(): bool
{
    $connection = \Bitrix\Main\Application::getConnection();

    // Создать таблицу через SQL
    if (!$connection->isTableExists('my_module_items')) {
        $connection->queryExecute("
            CREATE TABLE IF NOT EXISTS `my_module_items` (
                `ID` int(11) NOT NULL AUTO_INCREMENT,
                `NAME` varchar(255) NOT NULL DEFAULT '',
                `ACTIVE` char(1) NOT NULL DEFAULT 'Y',
                `SORT` int(11) NOT NULL DEFAULT 500,
                `DATE_CREATE` datetime NOT NULL,
                PRIMARY KEY (`ID`),
                KEY `IDX_ACTIVE` (`ACTIVE`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ");
    }

    // Или через ORM Entity
    MyItemTable::getEntity()->createDbTable();

    \Bitrix\Main\ModuleManager::registerModule($this->MODULE_ID);
    return true;
}
```

### Подход 2 — Скрипты обновления (update/)

Для изменения схемы при обновлении версии модуля:

```
local/modules/vendor.mymodule/
└── install/
    └── db/
        ├── mysql/
        │   ├── install.sql     ← полная схема (для новых установок)
        │   └── uninstall.sql
        └── updates/
            └── v1_1_0.sql      ← только изменения (для обновлений)
```

```php
// В методе DoUpdate() или в событии OnBeforeProlog (через агент)
// Проверяем версию и применяем нужные изменения:

$connection = \Bitrix\Main\Application::getConnection();

// Добавить колонку если не существует
$columns = $connection->query("SHOW COLUMNS FROM `my_module_items` LIKE 'DESCRIPTION'")->fetch();
if (!$columns) {
    $connection->queryExecute("
        ALTER TABLE `my_module_items`
        ADD COLUMN `DESCRIPTION` text NULL AFTER `NAME`
    ");
}

// Добавить индекс если не существует
if (!$connection->isIndexExists('my_module_items', ['SORT'])) {
    $connection->queryExecute("
        CREATE INDEX `IDX_SORT` ON `my_module_items` (`SORT`)
    ");
}

// Удалить колонку
$connection->queryExecute("
    ALTER TABLE `my_module_items` DROP COLUMN IF EXISTS `OLD_FIELD`
");
```

### Подход 3 — Sprint.Migration (популярный пакет)

**Sprint.Migration** (`andreyryabin/sprint.migration`) — де-факто стандарт для миграций в Bitrix. Устанавливается через Composer.

```
local/
└── php_interface/
    └── migrations/
        └── 20240315_120000_CreateCatalogIblock.php
```

```php
// Структура файла миграции
<?php
namespace Sprint\Migration;

class CreateCatalogIblock extends Version
{
    protected $description = 'Создать инфоблок Каталог';

    // Выполнить миграцию
    public function up(): bool
    {
        Loader::includeModule('iblock');

        $ib = new \CIBlock();
        $id = $ib->Add([
            'IBLOCK_TYPE_ID' => 'catalog',
            'LID'            => ['s1'],
            'NAME'           => 'Каталог',
            'CODE'           => 'products',
            'API_CODE'       => 'products',
            'VERSION'        => 2,
            'ACTIVE'         => 'Y',
        ]);

        if (!$id) {
            $this->log('Ошибка: ' . $ib->LAST_ERROR);
            return false;
        }

        $this->log('Инфоблок создан: ID=' . $id);
        return true;
    }

    // Откатить миграцию
    public function down(): bool
    {
        // Найти и удалить
        $res = \Bitrix\Iblock\IblockTable::getList([
            'filter' => ['=CODE' => 'products'],
            'select' => ['ID'],
        ])->fetch();

        if ($res) {
            \CIBlock::Delete($res['ID']);
            $this->log('Инфоблок удалён: ID=' . $res['ID']);
        }
        return true;
    }
}
```

Запуск миграций через консоль (если установлен bitrix-cli):
```bash
php bitrix-cli sprint:migration up
php bitrix-cli sprint:migration down
php bitrix-cli sprint:migration list
```

Или через admin-интерфейс `/bitrix/admin/sprint_migration.php`.

### Проверка схемы через D7 Connection API

```php
$connection = \Bitrix\Main\Application::getConnection();

// Существует ли таблица?
$connection->isTableExists('my_table');       // bool

// Существует ли индекс?
$connection->isIndexExists('my_table', ['SORT', 'ACTIVE']); // bool

// Список полей таблицы: ['NAME' => ['type'=>'varchar', 'length'=>255, ...], ...]
$fields = $connection->getTableFields('my_table');
array_key_exists('DESCRIPTION', $fields);     // проверить наличие колонки

// Выполнить произвольный SQL
$connection->queryExecute("ALTER TABLE `my_table` ADD ...");

// Транзакция
$connection->startTransaction();
try {
    $connection->queryExecute("UPDATE ...");
    $connection->queryExecute("INSERT ...");
    $connection->commitTransaction();
} catch (\Exception $e) {
    $connection->rollbackTransaction();
    throw $e;
}
```

### ORM Entity.createDbTable()

```php
// Создать таблицу из DataManager-класса (полностью по Map)
MyItemTable::getEntity()->createDbTable();

// НЕ поддерживает ALTER — только CREATE.
// Для изменения существующей схемы используй прямой SQL.
```

---

## Полный пример: инфоблок + свойства + права (в InstallDB)

```php
public function InstallDB(): bool
{
    \Bitrix\Main\Loader::requireModule('iblock');

    // 1. Тип инфоблока
    if (!\CIBlockType::GetByID('catalog')->Fetch()) {
        $ibt = new \CIBlockType();
        $ibt->Add([
            'ID'       => 'catalog',
            'SECTIONS' => 'Y',
            'SORT'     => 10,
            'LANG'     => ['ru' => ['NAME' => 'Каталог', 'ELEMENT_NAME' => 'Товар', 'SECTION_NAME' => 'Категория']],
        ]);
    }

    // 2. Инфоблок
    $iblockId = null;
    $existIb = \Bitrix\Iblock\IblockTable::getList(['filter' => ['=CODE' => 'products'], 'select' => ['ID']])->fetch();
    if ($existIb) {
        $iblockId = $existIb['ID'];
    } else {
        $ib = new \CIBlock();
        $iblockId = $ib->Add([
            'IBLOCK_TYPE_ID' => 'catalog',
            'LID'            => ['s1'],
            'NAME'           => 'Товары',
            'CODE'           => 'products',
            'API_CODE'       => 'products',
            'ACTIVE'         => 'Y',
            'VERSION'        => 2,
            'SORT'           => 100,
        ]);
        if (!$iblockId) {
            throw new \RuntimeException($ib->LAST_ERROR);
        }
    }

    // 3. Свойства (только если не созданы)
    $propMap = [
        'ARTICLE'  => ['NAME' => 'Артикул',  'PROPERTY_TYPE' => 'S', 'SORT' => 100],
        'PRICE'    => ['NAME' => 'Цена',     'PROPERTY_TYPE' => 'N', 'SORT' => 200],
        'ACTIVE_FROM' => ['NAME' => 'Активен с', 'PROPERTY_TYPE' => 'S', 'USER_TYPE' => 'DateTime', 'SORT' => 300],
    ];
    foreach ($propMap as $code => $fields) {
        $exists = \Bitrix\Iblock\PropertyTable::getList([
            'filter' => ['=IBLOCK_ID' => $iblockId, '=CODE' => $code],
            'select' => ['ID'],
        ])->fetch();
        if (!$exists) {
            $prop = new \CIBlockProperty();
            $prop->Add(array_merge($fields, ['IBLOCK_ID' => $iblockId, 'CODE' => $code, 'ACTIVE' => 'Y']));
        }
    }

    // 4. Права
    $adminGroup  = 1;
    $allGroup    = 2;
    $editGroupId = \CGroup::GetList('', '', ['STRING_ID' => 'CATALOG_EDITORS'])->Fetch()['ID'] ?? null;

    $perms = [$adminGroup => 'X', $allGroup => 'R'];
    if ($editGroupId) $perms[$editGroupId] = 'W';
    \CIBlock::SetPermission($iblockId, $perms);

    // 5. Права модуля iblock для группы редакторов
    if ($editGroupId) {
        \CMain::SetGroupRight('iblock', $editGroupId, 'W');
    }

    \Bitrix\Main\ModuleManager::registerModule($this->MODULE_ID);
    return true;
}
```

---

## Gotchas

- **`CIBlock::SetPermission` перезаписывает все права** — не "добавляет" к существующим. Всегда передавай полный список групп. Если передать пустой массив — права удалятся у всех.
- **`CUser::SetUserGroup` заменяет все группы** — пользователь выйдет из всех предыдущих групп (кроме группы 2 = Все). Сначала получи текущие группы и объедини: `array_merge(CUser::GetUserGroup($id), [$newGroup])`.
- **`API_CODE` не обязателен для любого ИБ** — но если проект опирается на generated iblock DataClass или REST-связки, лучше задавать его сразу. В текущем core формат проверяется regex `^[a-z][a-z0-9]{0,49}$`, underscore не допускается.
- **`VERSION=2` несовместим с VERSION=1** — при создании нового инфоблока всегда используй `VERSION=2`. Менять версию существующего инфоблока с данными — опасно.
- **`CIBlockPropertyEnum::Add`** — добавлять варианты списка нужно только для `PROPERTY_TYPE='L'`. Получить существующие варианты: `CIBlockPropertyEnum::GetList([], ['PROPERTY_ID' => $propId])`.
- **`createDbTable()` не делает ALTER** — если таблица уже существует, метод бросит SQL-ошибку. Всегда проверяй `isTableExists()` перед вызовом.
- **Sprint.Migration** — при использовании храни конфиг в `local/php_interface/sprint_migration_options.php`. Миграции в git, накатывать на deploy через CI.
- **`isIndexExists`** — принимает точный набор колонок в том же порядке. Составной индекс `['A', 'B']` не найдёт индекс `['B', 'A']`.
- **`GetGroupRight` vs `SetGroupRight`**: первая — для получения прав текущего пользователя, вторая — для установки прав конкретной группы. Разные методы, разные аргументы.
- **Группа `STRING_ID`** — не обязательное поле при создании, но позволяет находить группу без хранения числового ID в коде. Используй осмысленные строковые коды в модулях.

---

## Source: `custom-uf-types.md`

# Кастомные UF-типы — core-first справочник

> Reference для Bitrix-скилла. Загружай, когда задача связана с `OnUserTypeBuildList`, кастомными UF-типами, `Bitrix\Main\UserField\Types\BaseType`, HL-backed UF-типами или рендером пользовательских полей через системные компоненты.

## Что подтверждено в текущем core

- D7-базовый класс — `Bitrix\Main\UserField\Types\BaseType`.
- Базовые D7-типы (`string`, `integer`, `double`, `date`, `datetime`, `boolean`, `enum`, `file`) уже построены поверх `BaseType`.
- Legacy-обёртки (`CUserTypeString`, `CUserTypeFile` и т.д.) делегируют в D7-типы.
- UF-тип регистрируется через событие `main:OnUserTypeBuildList`.

---

## Минимальный паттерн кастомного типа

```php
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandler(
    'main',
    'OnUserTypeBuildList',
    ['\\MyVendor\\MyModule\\UserField\\MyCustomType', 'getUserTypeDescription']
);
```

```php
namespace MyVendor\MyModule\UserField;

use Bitrix\Main\Application;
use Bitrix\Main\ORM\Fields\StringField;
use Bitrix\Main\UserField\Types\BaseType;
use CUserTypeManager;

class MyCustomType extends BaseType
{
    public const USER_TYPE_ID = 'my_custom_type';
    public const RENDER_COMPONENT = 'bitrix:system.field.edit';

    protected static function getDescription(): array
    {
        return [
            'DESCRIPTION' => 'Мой UF-тип',
            'BASE_TYPE' => CUserTypeManager::BASE_TYPE_STRING,
        ];
    }

    public static function getDbColumnType(): string
    {
        $connection = Application::getConnection();
        return $connection->getSqlHelper()->getColumnTypeByField(new StringField('x'));
    }

    public static function prepareSettings(array $userField): array
    {
        return [
            'DEFAULT_VALUE' => is_array($userField['SETTINGS'])
                ? ($userField['SETTINGS']['DEFAULT_VALUE'] ?? '')
                : '',
        ];
    }

    public static function checkFields(array $userField, $value): array
    {
        return [];
    }

    public static function onBeforeSave(array $userField, $value)
    {
        return is_scalar($value) ? (string)$value : '';
    }
}
```

### Почему именно так

- `getUserTypeDescription()` уже приходит из `BaseType`, если заданы `USER_TYPE_ID`, `RENDER_COMPONENT` и `getDescription()`.
- `BASE_TYPE` в текущем core задаётся в `getDescription()`, а не как обязательная константа класса.
- Единственный действительно абстрактный метод `BaseType` — `getDbColumnType()`.

---

## Что у `BaseType` делает сам core

`BaseType` уже предоставляет:

- `renderView()`
- `renderEdit()`
- `renderEditForm()`
- `renderAdminListView()`
- `renderAdminListEdit()`
- `renderFilter()`
- `renderText()`
- `getDefaultValue()`

Все они работают через `APPLICATION->IncludeComponent(...)` и системные field-компоненты.

Это значит, что переопределять `renderEditForm()` и `renderAdminListView()` нужно только когда реально нужен кастомный HTML.

---

## Какие хуки реально стоит считать опциональными

В текущем core для D7 UF-типа полезны, но не обязательны:

- `prepareSettings(array $userField): array`
- `checkFields(array $userField, $value): array`
- `onBeforeSave(array $userField, $value)`
- `renderEditForm(...)`
- `renderAdminListView(...)`
- `getFilterData(...)`
- `getEntityField(...)`
- `getEntityReferences(...)`
- `onSearchIndex(array $userField)`

Не нужно объявлять их как "обязательные" по умолчанию.

---

## HL-backed тип `hlblock`

В текущем core тип `hlblock` реализован классом `CUserTypeHlblock`:

- `USER_TYPE_ID = 'hlblock'`
- `BASE_TYPE = int`
- `RENDER_COMPONENT = bitrix:highloadblock.field.element`
- `getEntityReferences()` автоматически добавляет `<FIELD_NAME>_REF`

Это важный ориентир, если нужно реализовать свой тип со ссылочной логикой: смотри на `highloadblock/classes/general/cusertypehlblock.php`, а не придумывай свою семантику `_REF`.

---

## Про файлы

Для файлового UF-типа в текущем core опорный пример — `Bitrix\Main\UserField\Types\FileType`.

Что у него реально подтверждено:

- `BASE_TYPE = file` приходит через `getDescription()`;
- колонка хранит `int` (`b_file.ID`);
- `onBeforeSave()` поддерживает и старый механизм массива файла, и новые registries;
- `onSearchIndex()` уже реализован в core;
- логика удаления и валидации сложнее, чем "если пусто, просто вернуть false".

Если нужен свой файловый тип, безопаснее отталкиваться от `FileType`, а не писать упрощённую версию "по памяти".

---

## Gotchas

- В D7-паттерне не переопределяй `getUserTypeDescription()` без необходимости: у `BaseType` уже есть нормальная базовая реализация.
- Не объявляй `BASE_TYPE` как самостоятельную "обязательную" константу. Для текущего core надёжнее задавать `BASE_TYPE` через `getDescription()`.
- Не рассчитывай на универсальный `onDelete()` для кастомного UF-типа: в текущем core это не общий контракт `BaseType`.
- Если тип должен участвовать в ORM-связях, смотри на `getEntityField()` и `getEntityReferences()`.
- Для HL-ссылок ориентируйся на `CUserTypeHlblock`, для directory-свойств — на `CIBlockPropertyDirectory`: это два разных механизма.

---

## Source: `import-export.md`

# Импорт / экспорт и работа с файлами

> Этот reference держи как общий маршрут по `CFile`, CSV/XML/URL и обычному файловому lifecycle. Если задача уже про `HANDLER_ID`, bucket-ы, внешний `SRC`, `OnMakeFileArray`, delayed resize или облачное хранилище, дополнительно загружай `clouds.md`: это отдельный модульный файловый контур.

## CFile — работа с файлами Bitrix

По умолчанию Bitrix хранит метаданные файлов в `b_file`, а физические файлы — в `upload/`. Но в текущем core есть события `OnFileSave` и `OnMakeFileArray`, поэтому внешнее хранилище тоже возможно. `CFile` остаётся корректной точкой входа для сохранения, получения и изменения файлов.

---

### CFile::SaveFile — сохранить файл в БД

```php
// $arFile — массив в формате $_FILES (или аналогичный)
$arFile = [
    'name'     => 'photo.jpg',      // оригинальное имя
    'tmp_name' => '/tmp/phpXXX',    // физический путь к временному файлу
    'type'     => 'image/jpeg',     // MIME-тип
    'size'     => 204800,           // размер в байтах
    'error'    => 0,
];

$fileId = CFile::SaveFile($arFile, 'my_module');   // обычно int ID, но при delete-only сценарии может вернуть строку "NULL"
if (!$fileId) {
    // ошибка сохранения
}
```

`$strSavePath` — поддиректория внутри `upload/`. Выбирай по смыслу: `'iblock'`, `'my.module'`, `'user'`.

#### Сохранить загруженный файл из $_FILES

```php
use Bitrix\Main\Application;

$request = Application::getInstance()->getContext()->getRequest();

// Получить через D7 (рекомендуется)
$uploadedFile = $request->getFile('image');  // эквивалент $_FILES['image']

if ($uploadedFile && $uploadedFile['error'] === UPLOAD_ERR_OK) {
    // Проверить тип — белый список
    $allowed = ['image/jpeg', 'image/png', 'image/webp'];
    if (!in_array($uploadedFile['type'], $allowed, true)) {
        throw new \RuntimeException('Недопустимый тип файла');
    }

    $fileId = CFile::SaveFile($uploadedFile, 'my_module');
}
```

> **Gotcha:** `$request->getFile('name')` возвращает тот же массив что и `$_FILES['name']`, но через D7-обёртку. Используй его вместо `$_FILES` напрямую.

---

### CFile::MakeFileArray — получить массив-дескриптор файла

Принимает ID, путь или URL. Возвращает массив в формате `$_FILES` или `false/null`.

```php
// По ID из b_file (например, из поля инфоблока)
$arFile = CFile::MakeFileArray(123);

// По локальному пути (относительно DOCUMENT_ROOT или абсолютный)
$arFile = CFile::MakeFileArray('/local/import/photo.jpg');

// По URL — скачивает через HttpClient во временный файл
$arFile = CFile::MakeFileArray('https://example.com/image.jpg');

if ($arFile) {
    $newFileId = CFile::SaveFile($arFile, 'my_module');
}
```

**Возвращаемый массив:**
```php
[
    'name'        => 'photo.jpg',      // оригинальное имя
    'tmp_name'    => '/path/to/file',  // физический путь
    'type'        => 'image/jpeg',
    'size'        => 204800,
    'description' => '',
]
```

> Для `http/https` ядро создаёт `HttpClient`, вызывает `setPrivateIp(false)` и блокирует приватные IP. Для `php://` и `phar://` действует отдельный запрет, кроме `php://input`.

---

### CFile::GetFileArray — получить данные файла из БД

```php
$arFile = CFile::GetFileArray($fileId);
// [
//   'ID'           => 123,
//   'FILE_NAME'    => 'abc123.jpg',
//   'ORIGINAL_NAME'=> 'photo.jpg',
//   'SUBDIR'       => 'iblock/abc',
//   'SRC'          => '/upload/iblock/abc/abc123.jpg',
//   'CONTENT_TYPE' => 'image/jpeg',
//   'FILE_SIZE'    => 204800,
//   'HEIGHT'       => 800,
//   'WIDTH'        => 600,
// ]
```

---

### CFile::ResizeImageGet — получить превью

Возвращает массив с данными уже отресайзенного изображения (берёт из кеша или создаёт):

```php
$arSize = ['width' => 300, 'height' => 200];

// BX_RESIZE_IMAGE_PROPORTIONAL — вписать пропорционально (по умолчанию)
// BX_RESIZE_IMAGE_EXACT         — точный crop
// BX_RESIZE_IMAGE_PROPORTIONAL_ALT — пропорционально по большей стороне

$arResized = CFile::ResizeImageGet(
    $fileId,                           // int или массив от GetFileArray
    $arSize,
    BX_RESIZE_IMAGE_PROPORTIONAL
);

if ($arResized) {
    // $arResized['src']    — '/upload/resize_cache/.../photo.jpg'
    // $arResized['width']  — реальная ширина
    // $arResized['height'] — реальная высота
    echo '<img src="' . htmlspecialchars($arResized['src']) . '"
               width="' . $arResized['width'] . '"
               height="' . $arResized['height'] . '">';
}
```

### CFile::ResizeImage — изменить размер перед сохранением

Модифицирует `$arFile['tmp_name']` на месте (временный файл):

```php
$arFile = CFile::MakeFileArray('/local/import/big.jpg');
if ($arFile) {
    $resized = CFile::ResizeImage($arFile, ['width' => 800, 'height' => 600], BX_RESIZE_IMAGE_PROPORTIONAL);
    if ($resized) {
        $fileId = CFile::SaveFile($arFile, 'my_module');
    }
}
```

### CFile::Delete — удалить файл

```php
CFile::Delete($fileId);  // удаляет из b_file и физически с диска
```

---

## Импорт из CSV

### Простой одношаговый импорт

```php
use Bitrix\Main\Application;
use Bitrix\Main\Loader;

Loader::includeModule('iblock');

$filePath = $_SERVER['DOCUMENT_ROOT'] . '/local/import/products.csv';

if (!file_exists($filePath)) {
    throw new \RuntimeException('Файл не найден');
}

$handle = fopen($filePath, 'r');
$header = fgetcsv($handle, 0, ';');  // первая строка — заголовки
// $header = ['NAME', 'PRICE', 'ARTICLE', 'SECTION_CODE']

// Белый список допустимых столбцов
$allowed = array_flip(['NAME', 'PRICE', 'ARTICLE', 'SECTION_CODE']);
$header = array_map(
    fn($col) => isset($allowed[$col]) ? $col : null,
    $header
);

while (($row = fgetcsv($handle, 0, ';')) !== false) {
    $data = array_combine($header, $row);
    $data = array_filter($data, fn($v, $k) => $k !== null, ARRAY_FILTER_USE_BOTH);

    $el = new \CIBlockElement();
    $result = $el->Add([
        'IBLOCK_ID'  => CATALOG_IBLOCK_ID,
        'NAME'       => trim($data['NAME']),
        'ACTIVE'     => 'Y',
        'PROPERTY_VALUES' => [
            'ARTICLE' => trim($data['ARTICLE'] ?? ''),
            'PRICE'   => (float)str_replace(',', '.', $data['PRICE'] ?? '0'),
        ],
    ]);

    if (!$result) {
        error_log('Ошибка импорта: ' . $el->LAST_ERROR . ' | строка: ' . implode(';', $row));
    }
}

fclose($handle);
```

---

### Многошаговый импорт (через сессию)

Для больших файлов — обрабатывать пачками по N строк, хранить позицию в сессии:

```php
// Шаг 1: загрузка файла (разовый POST)
// Шаг 2-N: обработка пачек (повторяющиеся AJAX-запросы)
// Шаг финал: очистка сессии

use Bitrix\Main\Application;

$request = Application::getInstance()->getContext()->getRequest();
$session = Application::getInstance()->getSession();

$BATCH_SIZE = 50;

// --- Загрузка файла (шаг 1) ---
if ($request->isPost() && $request->getPost('action') === 'upload') {
    $uploadedFile = $request->getFile('csv_file');

    if (!$uploadedFile || $uploadedFile['error'] !== UPLOAD_ERR_OK) {
        echo json_encode(['error' => 'Ошибка загрузки файла']);
        die();
    }

    // Сохранить во временную директорию (не в b_file — нужен физический путь)
    $tmpPath = sys_get_temp_dir() . '/import_' . md5(uniqid('', true)) . '.csv';
    move_uploaded_file($uploadedFile['tmp_name'], $tmpPath);

    // Подсчитать строк (для прогресса)
    $totalLines = max(0, (int)shell_exec('wc -l < ' . escapeshellarg($tmpPath)) - 1); // -1 заголовок

    $session->set('import_file',   $tmpPath);
    $session->set('import_offset', 0);
    $session->set('import_total',  $totalLines);

    echo json_encode(['total' => $totalLines, 'processed' => 0]);
    die();
}

// --- Обработка пачки (шаги 2-N) ---
if ($request->isPost() && $request->getPost('action') === 'process') {
    $tmpPath = $session->get('import_file');
    $offset  = (int)$session->get('import_offset');
    $total   = (int)$session->get('import_total');

    if (!$tmpPath || !file_exists($tmpPath)) {
        echo json_encode(['error' => 'Сессия импорта не найдена']);
        die();
    }

    $handle = fopen($tmpPath, 'r');
    $header = fgetcsv($handle, 0, ';');

    // Перемотать к нужной строке
    for ($i = 0; $i < $offset; $i++) {
        fgetcsv($handle, 0, ';');
    }

    $processed = 0;
    $errors    = [];

    for ($i = 0; $i < $BATCH_SIZE; $i++) {
        $row = fgetcsv($handle, 0, ';');
        if ($row === false) {
            break;
        }

        $data = array_combine($header, $row);

        // ... сохранить элемент (аналогично одношаговому) ...
        $processed++;
    }

    fclose($handle);

    $newOffset = $offset + $processed;
    $session->set('import_offset', $newOffset);

    $done = $newOffset >= $total;

    if ($done) {
        unlink($tmpPath);
        $session->remove('import_file');
        $session->remove('import_offset');
        $session->remove('import_total');
    }

    echo json_encode([
        'processed' => $newOffset,
        'total'     => $total,
        'done'      => $done,
        'errors'    => $errors,
    ]);
    die();
}
```

#### JS-клиент для многошагового импорта

```javascript
async function runImport(file) {
    // Шаг 1: загрузить файл
    const form = new FormData();
    form.append('sessid', BX.bitrix_sessid());
    form.append('action', 'upload');
    form.append('csv_file', file);

    let resp = await fetch('/local/import/handler.php', { method: 'POST', body: form });
    let data = await resp.json();

    // Шаги 2-N: пакетная обработка
    while (!data.done) {
        const body = new URLSearchParams({
            sessid: BX.bitrix_sessid(),
            action: 'process',
        });
        resp = await fetch('/local/import/handler.php', { method: 'POST', body });
        data = await resp.json();

        const progress = Math.round(data.processed / data.total * 100);
        document.getElementById('progress').textContent = progress + '%';
    }

    alert('Импорт завершён. Обработано: ' + data.processed);
}
```

---

## Импорт изображений из URL

Типичная задача при импорте товаров: загрузить картинку по URL и прикрепить к элементу.

```php
use Bitrix\Main\Loader;
Loader::includeModule('iblock');

foreach ($products as $product) {
    $picFileId = false;

    if (!empty($product['IMAGE_URL'])) {
        // MakeFileArray скачивает URL через HttpClient
        $arFile = CFile::MakeFileArray($product['IMAGE_URL']);
        if ($arFile) {
            // Опциональный ресайз перед сохранением
            CFile::ResizeImage($arFile, ['width' => 800, 'height' => 800], BX_RESIZE_IMAGE_PROPORTIONAL);

            $picFileId = CFile::SaveFile($arFile, 'iblock');
        }
    }

    $el = new \CIBlockElement();
    $el->Add([
        'IBLOCK_ID'        => CATALOG_IBLOCK_ID,
        'NAME'             => $product['NAME'],
        'PREVIEW_PICTURE'  => $picFileId ?: false,
        'DETAIL_PICTURE'   => $picFileId ?: false,
        'ACTIVE'           => 'Y',
    ]);
}
```

---

## Экспорт в CSV (потоковый)

Потоковый экспорт не накапливает данные в памяти — сразу пишет в вывод:

```php
use Bitrix\Main\Loader;
use Bitrix\Main\Application;

Loader::includeModule('iblock');

// Отключить буферизацию вывода
while (ob_get_level()) {
    ob_end_clean();
}

$response = Application::getInstance()->getContext()->getResponse();
$response->addHeader('Content-Type', 'text/csv; charset=utf-8');
$response->addHeader('Content-Disposition', 'attachment; filename="export_' . date('Y-m-d') . '.csv"');
$response->flush('');  // отправить заголовки

// BOM для корректного открытия в Excel
echo "\xEF\xBB\xBF";

$out = fopen('php://output', 'w');
fputcsv($out, ['ID', 'Название', 'Артикул', 'Цена'], ';');

$res = \CIBlockElement::GetList(
    ['ID' => 'ASC'],
    ['IBLOCK_ID' => CATALOG_IBLOCK_ID, 'ACTIVE' => 'Y'],
    false,
    false,
    ['ID', 'NAME', 'PROPERTY_ARTICLE', 'PROPERTY_PRICE']
);

while ($el = $res->GetNext()) {
    fputcsv($out, [
        $el['ID'],
        $el['NAME'],
        $el['PROPERTY_ARTICLE_VALUE'] ?? '',
        $el['PROPERTY_PRICE_VALUE'] ?? '',
    ], ';');

    if (connection_aborted()) {
        break;
    }
}

fclose($out);
die();
```

---

## Gotchas

- `CFile::SaveFile` сохраняет файл физически в `upload/`, возвращает `false` при ошибке — всегда проверяй
- `CFile::MakeFileArray` при передаче URL скачивает файл во временную директорию — при ошибке сети возвращает `null`
- `CFile::ResizeImage` изменяет `$arFile['tmp_name']` на месте — оригинал теряется. Если нужен оригинал, скопируй сначала
- `BX_RESIZE_IMAGE_EXACT` = точный crop по центру; `BX_RESIZE_IMAGE_PROPORTIONAL` = вписать в рамку (поля пустые)
- В CSV-экспорте добавляй UTF-8 BOM `\xEF\xBB\xBF` — Excel иначе не откроет кириллицу корректно
- При многошаговом импорте храни файл вне `upload/` (в `sys_get_temp_dir()`), иначе он попадёт в БД
- `fgetcsv` зависит от локали — если возникают проблемы с кодировкой, используй `mb_convert_encoding`
- `connection_aborted()` в цикле экспорта позволяет корректно завершить если пользователь закрыл браузер

---

## Source: `sef-urls.md`

# SEF URLs / ЧПУ в Bitrix

## Audit note

Проверено по текущему core:
- `www/bitrix/modules/main/include/urlrewrite.php`
- `www/bitrix/modules/main/lib/urlrewriter.php`

## Как работает urlrewrite

При каждом запросе Bitrix подключает `/bitrix/modules/main/include/urlrewrite.php`, который:
1. Загружает массив `$arUrlRewrite` из корневого `urlrewrite.php` сайта
2. Итерирует правила (уже отсортированы по приоритету)
3. Для каждого правила: `preg_match(CONDITION, $requestUri)`
4. При совпадении:
   - Если `RULE` пуст — просто берёт `PATH` как исполняемый PHP-файл
   - Если RULE есть — `preg_replace(CONDITION, PATH.'?'.RULE, URI)` → `parse_str` → заполняет `$_GET`
5. Включает найденный PHP-файл и прекращает обработку

### Формат записи в `urlrewrite.php`

```php
// Корневой /urlrewrite.php сайта
$arUrlRewrite = [
    [
        'CONDITION' => '#^/travels/([^/]+?)/?(\?.*)?$#',  // регулярка для preg_match
        'RULE'      => 'type=$1&$2',                       // шаблон для preg_replace
        'ID'        => 'travels.type',                     // произвольный идентификатор
        'PATH'      => '/travels/index.php',               // файл-обработчик
        'SORT'      => 100,                                // меньше = выше приоритет
    ],
];
```

**Backreferences в RULE:** `$1`, `$2` … соответствуют скобочным группам в CONDITION.

**Итоговый URL:** `preg_replace(CONDITION, PATH.'?'.RULE, $requestUri)`
Пример: `/travels/russia/` → `/travels/index.php?type=russia&`

### Переменные в SEF_RULE

| Суффикс переменной | Regex в CONDITION | Пример |
|---------------------|-------------------|--------|
| обычная (`#TYPE#`) | `([^/]+?)` | совпадает с одним сегментом пути |
| `_PATH` (`#SECTION_PATH#`) | `(.+?)` | совпадает с несколькими сегментами |

---

## D7 API: `\Bitrix\Main\UrlRewriter`

```php
use Bitrix\Main\UrlRewriter;

// Добавить правило (не добавляет дубликат по CONDITION)
UrlRewriter::add('s1', [
    'CONDITION' => '#^/travels/([^/]+?)/?(\?.*)?$#',
    'RULE'      => 'type=$1&$2',
    'ID'        => 'travels.type',
    'PATH'      => '/travels/index.php',
    'SORT'      => 100,
]);

// Обновить существующее правило
UrlRewriter::update('s1', [
    'CONDITION' => '#^/travels/([^/]+?)/?(\?.*)?$#',  // ключ поиска
], [
    'RULE' => 'type=$1&$2',
    'SORT' => 50,
]);

// Удалить правило
UrlRewriter::delete('s1', ['CONDITION' => '#^/travels/([^/]+?)/?(\?.*)?$#']);

// Полная переиндексация активного сайта
UrlRewriter::reindexAll(0, ['SITE_ID' => 's1']);
```

Первый параметр для `add/update/delete` — `SITE_ID` (`s1`, `s2` и т.д.).

После `add/delete` правила автоматически пересортировываются: сначала по SORT, затем по убыванию длины CONDITION (более специфичные — выше).

Важно: `reindexFile()` в текущем core имеет сигнатуру

```php
UrlRewriter::reindexFile($siteId, $rootPath, $path, $maxFileSize = 0)
```

То есть это не shorthand с одним `siteId`.

---

## Компонент с SEF_MODE=Y

```php
// /travels/index.php
$APPLICATION->IncludeComponent(
    'bitrix:catalog.section',
    'travels',
    [
        'SEF_MODE'   => 'Y',
        'SEF_FOLDER' => '/travels/',           // базовый URL-путь
        'SEF_RULE'   => 'travels/#TYPE#/',     // шаблон → CONDITION+RULE в urlrewrite
        // остальные параметры компонента
        'IBLOCK_ID'  => 5,
    ]
);
```

**Как Bitrix генерирует urlrewrite-запись из SEF_RULE:**

`UrlRewriterRuleMaker::process('travels/#TYPE#/')` создаёт:
- `CONDITION` = `#^/travels/([^/]+?)\??(.*)#`
- `RULE` = `TYPE=$1&$2`
- `PATH` = `/travels/index.php`

Запись автоматически добавляется/обновляется в `urlrewrite.php` при первом вызове компонента в режиме SEF.

### Чтение SEF-параметров внутри компонента

```php
// В component.php или template.php
$sefFolder = $this->arParams['SEF_FOLDER']; // '/travels/'

// CComponentEngine разбирает текущий URL относительно SEF_FOLDER
$componentEngine = new CComponentEngine($this);
$variables = [];
$defaultPage = 'list';
$urlTemplates = [
    'list'   => '',
    'detail' => '#TYPE#/#CODE#/',
];
$page = $componentEngine->guessComponentPath(
    $sefFolder,
    $urlTemplates,
    $variables
);
// $variables['TYPE'], $variables['CODE'] — разобранные из URL
```

---

## Практика: перевод `travels/?type=russia` → `travels/russia/`

### 1. Добавляем новое SEF-правило

```php
use Bitrix\Main\UrlRewriter;

// Новый красивый URL
UrlRewriter::add('s1', [
    'CONDITION' => '#^/travels/([^/]+?)/?(\?.*)?$#',
    'RULE'      => 'type=$1&$2',
    'ID'        => 'travels.sef',
    'PATH'      => '/travels/index.php',
    'SORT'      => 100,
]);
```

### 2. Редирект со старых URL (301)

В `/travels/index.php` или в компоненте — до `IncludeComponent`:

```php
use Bitrix\Main\Application;

$request = Application::getInstance()->getContext()->getRequest();
$type = $request->getQuery('type');

// Если пришли по старому URL (?type=...) — редиректим на ЧПУ
if ($type !== null && !preg_match('#^/travels/[^/?]+/#', $request->getRequestUri())) {
    LocalRedirect('/travels/' . rawurlencode($type) . '/', false, '301 Moved Permanently');
    die();
}
```

### 3. Компонент принимает тип из URL

```php
$APPLICATION->IncludeComponent(
    'my:travels.list',
    '',
    [
        'SEF_MODE'   => 'Y',
        'SEF_FOLDER' => '/travels/',
        'SEF_RULE'   => 'travels/#TYPE#/',
        'IBLOCK_ID'  => 5,
    ]
);
```

Внутри `component.php` переменная `$arResult['TYPE']` = `russia` берётся из `$_GET['TYPE']`, который заполнил urlrewrite.

---

## Сортировка и фильтрация элементов инфоблока

Типовой паттерн: GET-параметры → arFilter/arOrder в компоненте. Фильтрация всегда на стороне сервера через `CIBlockElement::GetList` или ORM.

### Параметры фильтра из URL

```
/catalog/?PRICE_FROM=1000&PRICE_TO=5000&BRAND=nike&SORT=PRICE&ORDER=ASC
```

### Компонент: безопасная сборка фильтра

```php
// В component.php
use Bitrix\Main\Application;

$request = Application::getInstance()->getContext()->getRequest();

// Белый список допустимых GET-параметров фильтра
$allowedProps = ['BRAND', 'COLOR', 'SIZE'];
$arFilter = [
    'IBLOCK_ID' => $this->arParams['IBLOCK_ID'],
    'ACTIVE'    => 'Y',
];

// Числовой диапазон цены
$priceFrom = (int)$request->getQuery('PRICE_FROM');
$priceTo   = (int)$request->getQuery('PRICE_TO');
if ($priceFrom > 0) {
    $arFilter['>=CATALOG_PRICE_1'] = $priceFrom;
}
if ($priceTo > 0) {
    $arFilter['<=CATALOG_PRICE_1'] = $priceTo;
}

// Свойства из белого списка
foreach ($allowedProps as $propCode) {
    $val = $request->getQuery($propCode);
    if ($val !== null && $val !== '') {
        $arFilter['PROPERTY_' . $propCode] = $val;
    }
}

// Сортировка из белого списка
$allowedSort  = ['NAME', 'PRICE', 'SORT', 'DATE_CREATE'];
$allowedOrder = ['ASC', 'DESC'];
$sortField = strtoupper($request->getQuery('SORT') ?? 'SORT');
$sortOrder = strtoupper($request->getQuery('ORDER') ?? 'ASC');

if (!in_array($sortField, $allowedSort, true))  { $sortField = 'SORT'; }
if (!in_array($sortOrder, $allowedOrder, true)) { $sortOrder = 'ASC'; }

$arSort = [$sortField => $sortOrder, 'ID' => 'ASC'];

$navParams = CDBResult::GetNavParams([
    'nPageSize' => 20,
    'bShowAll' => false,
]);

// Запрос
$res = CIBlockElement::GetList(
    $arSort,
    $arFilter,
    false,
    ['nPageSize' => 20, 'iNumPage' => $navParams['PAGEN'], 'bShowAll' => false],
    ['ID', 'NAME', 'PROPERTY_BRAND', 'PROPERTY_COLOR']
);
```

**Gotchas:**
- Никогда не передавай `$_GET`/`$_POST` напрямую в arFilter — только через белый список
- `CATALOG_PRICE_1` — цена прайс-листа с ID=1; для других прайс-листов меняй цифру
- Пагинация Bitrix: не хардкодь `PAGEN_1`, если на странице может быть несколько списков; смотри `pagination.md` про `NavNum`, `CDBResult::GetNavParams()` и D7 `PageNavigation`

### SEF + фильтр вместе

Если нужны и ЧПУ-сегменты, и GET-фильтр:

```
/catalog/russia/?COLOR=red&SORT=PRICE
```

urlrewrite разбирает `/catalog/russia/` → `TYPE=russia`, затем Bitrix добавляет GET-параметры `COLOR` и `SORT` из строки запроса — они доступны одновременно.

---

## CComponentEngine: детальные страницы

```php
// Несколько шаблонов URL в одном компоненте
$urlTemplates = [
    'list'   => '',                    // /catalog/
    'section'=> '#SECTION_CODE#/',     // /catalog/chairs/
    'detail' => '#SECTION_CODE#/#CODE#/', // /catalog/chairs/item-slug/
];

$variables = [];
$page = $componentEngine->guessComponentPath(
    '/catalog/',
    $urlTemplates,
    $variables
);
// $page = 'detail', $variables = ['SECTION_CODE' => 'chairs', 'CODE' => 'item-slug']

// Генерация URL обратно
$detailUrl = $componentEngine->makePathFromTemplate(
    '/catalog/#SECTION_CODE#/#CODE#/',
    ['SECTION_CODE' => 'chairs', 'CODE' => 'item-slug']
);
// → '/catalog/chairs/item-slug/'
```

---

## Программная работа с urlrewrite.php напрямую

Когда нужно массово перезаписать правила (например, в миграции):

```php
use Bitrix\Main\IO\File;

$siteId = 's1';
$urlRewriteFile = Application::getInstance()->getDocumentRoot()
    . BX_PERSONAL_ROOT . '/urlrewrite.php'; // обычно /bitrix/urlrewrite.php

// Читаем текущие правила
$arUrlRewrite = [];
if (file_exists($urlRewriteFile)) {
    include $urlRewriteFile;
}

// Добавляем своё
$arUrlRewrite[] = [
    'CONDITION' => '#^/travels/([^/]+?)/?(\?.*)?$#',
    'RULE'      => 'type=$1&$2',
    'ID'        => 'travels.sef',
    'PATH'      => '/travels/index.php',
    'SORT'      => 100,
];

// Сортируем: сначала по SORT, потом по убыванию длины CONDITION
usort($arUrlRewrite, function($a, $b) {
    if ($a['SORT'] !== $b['SORT']) return $a['SORT'] <=> $b['SORT'];
    return strlen($b['CONDITION']) <=> strlen($a['CONDITION']);
});

// Записываем обратно (как это делает UrlRewriter::saveRules)
File::putFileContents(
    $urlRewriteFile,
    "<?php\n\$arUrlRewrite=" . var_export($arUrlRewrite, true) . ";\n"
);
```

> **Gotcha:** после ручной правки `urlrewrite.php` нужно сбросить кеш страниц или дождаться следующего запроса — файл читается при каждом хите, кеша нет.

---
