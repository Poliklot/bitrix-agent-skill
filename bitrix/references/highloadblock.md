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
- пагинацию через `\Bitrix\Main\UI\PageNavigation`;
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
