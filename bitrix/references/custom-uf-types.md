# Кастомные UF-типы и ACF-паттерны через HL-блоки

## Архитектура

Пользовательские поля (UF) в Bitrix регистрируются через `OnUserTypeBuildList`. Каждый тип — это PHP-класс, унаследованный от `Bitrix\Main\UserField\Types\BaseType` (D7) или legacy-обёртка, делегирующая к D7-классу.

HL-блоки (`highloadblock`) — это способ реализовать ACF-подобные поля: repeater, group, flexible content — через связанные таблицы с UF-полями.

---

## Кастомный UF-тип: полный шаблон

### Регистрация в модуле

```php
// include.php модуля
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandler(
    'main',
    'OnUserTypeBuildList',
    ['\MyVendor\MyModule\UserField\MyCustomType', 'getUserTypeDescription']
);
```

### Класс типа (D7 BaseType)

```php
namespace MyVendor\MyModule\UserField;

use Bitrix\Main\UserField\Types\BaseType;
use Bitrix\Main\UserField\TypeBase;

class MyCustomType extends BaseType
{
    // Уникальный идентификатор типа (в b_user_field.USER_TYPE_ID)
    public const USER_TYPE_ID = 'my_custom_type';

    // BASE_TYPE определяет тип колонки и поведение при удалении:
    // 'string', 'int', 'double', 'datetime', 'file'
    // BASE_TYPE='file' → Bitrix автоматически вызывает CFile::Delete при удалении поля
    public const BASE_TYPE = TypeBase::BASE_TYPE_INT;

    public static function getUserTypeDescription(): array
    {
        return [
            'USER_TYPE_ID'  => static::USER_TYPE_ID,
            'CLASS_NAME'    => static::class,
            'DESCRIPTION'   => 'Мой тип поля',
            'BASE_TYPE'     => static::BASE_TYPE,
            // Опционально: рендерить через компонент
            // 'RENDER_COMPONENT' => 'my.module:uf.my_custom_type',
        ];
    }

    // ОБЯЗАТЕЛЬНЫЙ абстрактный метод — тип SQL-колонки
    public static function getDbColumnType(): string
    {
        return 'INT';  // или 'VARCHAR(255)', 'TEXT', 'DOUBLE', 'DATETIME'
    }

    // Хук: вызывается ДО сохранения значения в БД
    // Возвращает значение для записи, или false для отмены
    public static function onBeforeSave(array $userField, mixed $value): mixed
    {
        // $value — что пришло из формы (строка, массив $_FILES и т.д.)
        return $value;
    }

    // Хук: вызывается при удалении значения (не типа!)
    // Используй для очистки зависимых данных
    public static function onDelete(array $userField, mixed $value): void
    {
        // например, удалить файл если хранишь свои данные
    }

    // Хук: вызывается при индексации поля для поиска
    public static function onSearchIndex(array $userField, mixed $value): string
    {
        return (string)$value;
    }

    // Хук: валидация при сохранении
    // Возвращает массив ошибок или пустой массив
    public static function checkFields(array $userField, mixed $value): array
    {
        $errors = [];
        // if (empty($value)) {
        //     $errors[] = ['id' => 'FIELD_ID', 'text' => 'Поле обязательно'];
        // }
        return $errors;
    }

    // Метаданные о настройках типа
    public static function prepareSettings(array $userField): array
    {
        // Нормализует $userField['SETTINGS'] при сохранении типа
        return $userField['SETTINGS'] ?? [];
    }

    // Рендер поля редактирования
    public static function renderEditForm(array $userField, array $additionalParameters): string
    {
        $name  = htmlspecialchars($additionalParameters['NAME']);
        $value = htmlspecialchars((string)($additionalParameters['VALUE'] ?? ''));
        return '<input type="text" name="' . $name . '" value="' . $value . '">';
    }

    // Рендер в списке admin
    public static function renderAdminListView(array $userField, array $additionalParameters): string
    {
        return htmlspecialchars((string)($additionalParameters['VALUE'] ?? ''));
    }
}
```

---

## Кастомный UF-тип с загрузкой файла

Самый сложный случай — тип, который хранит файл через `CFile`.

```php
namespace MyVendor\MyModule\UserField;

use Bitrix\Main\UserField\Types\BaseType;
use Bitrix\Main\UserField\TypeBase;
use CFile;

class FileCustomType extends BaseType
{
    public const USER_TYPE_ID = 'my_file_type';

    // BASE_TYPE_FILE — Bitrix автоматически вызовет CFile::Delete
    // при удалении значения или самого UF-поля
    public const BASE_TYPE = TypeBase::BASE_TYPE_FILE;

    public static function getUserTypeDescription(): array
    {
        return [
            'USER_TYPE_ID' => static::USER_TYPE_ID,
            'CLASS_NAME'   => static::class,
            'DESCRIPTION'  => 'Файл (кастомный)',
            'BASE_TYPE'    => static::BASE_TYPE,
        ];
    }

    // Файл хранится как INT (ID из b_file)
    public static function getDbColumnType(): string
    {
        return 'INT';
    }

    /**
     * Вызывается ПЕРЕД записью в БД.
     * $value из формы — массив в формате $_FILES или int (уже сохранённый ID).
     */
    public static function onBeforeSave(array $userField, mixed $value): int|false
    {
        // Уже сохранённый файл (редактирование без замены)
        if (is_numeric($value) && (int)$value > 0) {
            return (int)$value;
        }

        // Удаление файла (пришло 0 или пустая строка)
        if (empty($value) || $value === '0') {
            return false;  // false → NULL в БД, Bitrix удалит через BASE_TYPE_FILE
        }

        // Новый файл из формы (массив $_FILES)
        if (is_array($value) && isset($value['tmp_name']) && $value['tmp_name'] !== '') {
            if ($value['error'] !== UPLOAD_ERR_OK) {
                return false;
            }

            // Проверка типа (белый список)
            $allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!in_array($value['type'], $allowed, true)) {
                return false;
            }

            $fileId = CFile::SaveFile($value, 'uf_my_file_type');
            return $fileId ?: false;
        }

        return false;
    }

    // Рендер поля редактирования с поддержкой замены/удаления
    public static function renderEditForm(array $userField, array $additionalParameters): string
    {
        $name    = htmlspecialchars($additionalParameters['NAME']);
        $value   = (int)($additionalParameters['VALUE'] ?? 0);
        $html    = '';

        if ($value > 0) {
            $arFile = CFile::GetFileArray($value);
            if ($arFile) {
                $src = htmlspecialchars($arFile['SRC']);
                $fn  = htmlspecialchars($arFile['ORIGINAL_NAME']);
                // Показать превью или имя файла
                $html .= '<div class="uf-file-current">';
                $html .= '<img src="' . $src . '" style="max-height:80px"> ' . $fn . '<br>';
                $html .= '<label><input type="checkbox" name="' . $name . '[del]" value="Y"> Удалить</label>';
                $html .= '<input type="hidden" name="' . $name . '[old_id]" value="' . $value . '">';
                $html .= '</div>';
            }
        }

        $html .= '<input type="file" name="' . $name . '[file]">';
        return $html;
    }

    /**
     * Это полная реализация onBeforeSave для multipart-формы выше.
     * В реальном классе ЗАМЕНИ упрощённый onBeforeSave выше на этот метод
     * (переименуй в onBeforeSave — Bitrix вызывает только этот хук).
     * Получает массив ['del'=>'Y','old_id'=>123,'file'=>[...]] из renderEditForm.
     */
    public static function onBeforeSave(array $userField, mixed $value): int|false
    {
        if (!is_array($value)) {
            return is_numeric($value) ? (int)$value : false;
        }

        $oldId = (int)($value['old_id'] ?? 0);
        $del   = ($value['del'] ?? '') === 'Y';
        $file  = $value['file'] ?? [];

        // Удаление
        if ($del) {
            if ($oldId > 0) {
                CFile::Delete($oldId);
            }
            return false;
        }

        // Новый файл
        if (is_array($file) && !empty($file['tmp_name'])) {
            if ($oldId > 0) {
                CFile::Delete($oldId);  // удалить старый
            }
            $newId = CFile::SaveFile($file, 'uf_my_file_type');
            return $newId ?: false;
        }

        // Без изменений — вернуть старый ID
        return $oldId ?: false;
    }
}
```

> **Gotcha:** Если `BASE_TYPE = BASE_TYPE_FILE`, Bitrix сам вызывает `CFile::Delete` для всех сохранённых значений при удалении UF-поля (через `CUserTypeManager::DeleteUserType`). Но при замене файла через редактирование — старый файл нужно удалять вручную в `onBeforeSave`.

---

## ACF-паттерны через HL-блоки

### Паттерн 1: Repeater (список дочерних записей)

HL-блок хранит набор записей, каждая привязана к элементу ИБ через `UF_ELEMENT_ID`.

**Структура HL-блока `my_repeater`:**
| Поле | Тип | Описание |
|------|-----|----------|
| UF_ELEMENT_ID | integer | ID элемента ИБ |
| UF_SORT | integer | Порядок сортировки |
| UF_TITLE | string | Заголовок строки |
| UF_TEXT | string | Текст |
| UF_IMAGE | file | Изображение (ID из b_file) |

```php
use Bitrix\Main\Loader;
use Bitrix\Highloadblock\HighloadBlockTable;

Loader::includeModule('highloadblock');

// Получить скомпилированный DataManager для HL
$hlblock = HighloadBlockTable::getRow(['filter' => ['=NAME' => 'MyRepeater']]);
$entity  = HighloadBlockTable::compileEntity($hlblock);
$dataClass = $entity->getDataClass();  // 'MyRepeaterTable' псевдокласс

// Получить все строки repeater для элемента ИБ
$rows = $dataClass::getList([
    'filter' => ['=UF_ELEMENT_ID' => $elementId],
    'order'  => ['UF_SORT' => 'ASC'],
    'select' => ['ID', 'UF_SORT', 'UF_TITLE', 'UF_TEXT', 'UF_IMAGE'],
])->fetchAll();

// Добавить строку
$addResult = $dataClass::add([
    'UF_ELEMENT_ID' => $elementId,
    'UF_SORT'       => 100,
    'UF_TITLE'      => 'Заголовок',
    'UF_TEXT'       => 'Текст',
    'UF_IMAGE'      => $fileId,  // int из b_file
]);
if (!$addResult->isSuccess()) {
    // обработать ошибки
}
```

#### Сохранение repeater через EditFormAddFields (UF-lifecycle)

Если строки HL содержат UF-поля (включая файлы), используй `EditFormAddFields` — он вызовет `onBeforeSave` для каждого UF:

```php
global $USER_FIELD_MANAGER;

$hlId     = $hlblock['ID'];
$entityId = 'HLBLOCK_' . $hlId;

// Данные из формы (включая $_FILES через $request->getFile(...))
$data = [
    'UF_ELEMENT_ID' => $elementId,
    'UF_SORT'       => 100,
    'UF_TITLE'      => $request->getPost('uf_title'),
];

// Обработать UF-поля (onBeforeSave, валидация и т.д.)
if (!$USER_FIELD_MANAGER->EditFormAddFields($entityId, $data)) {
    // ошибка валидации
    $errors = $USER_FIELD_MANAGER->GetErrorMessage();
}

$result = $dataClass::add($data);
```

---

### Паттерн 2: Group (расширение 1:1)

HL-блок хранит одну запись на элемент ИБ (дополнительные поля).

```php
// Получить/создать связанную запись
$row = $dataClass::getRow(['filter' => ['=UF_ELEMENT_ID' => $elementId]]);

if ($row) {
    // Обновить
    $dataClass::update($row['ID'], ['UF_EXTRA_FIELD' => $value]);
} else {
    // Создать
    $dataClass::add(['UF_ELEMENT_ID' => $elementId, 'UF_EXTRA_FIELD' => $value]);
}
```

**Рекомендация:** Создавай уникальный индекс на `UF_ELEMENT_ID` в HL-таблице:

```sql
ALTER TABLE hl_my_group ADD UNIQUE KEY ux_element_id (UF_ELEMENT_ID);
```

Или контролируй уникальность на уровне ORM событий:

```php
// В модуле — обработчик ORM события HL
$entity->addEventHandler('onBeforeAdd', function(\Bitrix\Main\ORM\Event $event) use ($dataClass) {
    $data = $event->getParameter('fields');
    $exists = $dataClass::getCount(['=UF_ELEMENT_ID' => $data['UF_ELEMENT_ID']]);
    if ($exists > 0) {
        $result = new \Bitrix\Main\ORM\EventResult();
        $result->addError(new \Bitrix\Main\ORM\FieldError(
            $event->getEntity()->getField('UF_ELEMENT_ID'),
            'Запись для этого элемента уже существует'
        ));
        return $result;
    }
});
```

---

### Паттерн 3: Flexible Content (дискриминатор типа)

HL-блок с полем `UF_TYPE` + разные контентные блоки:

**Структура HL-блока `my_flexible`:**
| Поле | Тип | Описание |
|------|-----|----------|
| UF_ELEMENT_ID | integer | ID элемента ИБ |
| UF_SORT | integer | Порядок |
| UF_TYPE | string(50) | 'text', 'image', 'video', 'quote' |
| UF_TEXT | string | Текст (для type=text,quote) |
| UF_IMAGE | file | Изображение (для type=image) |
| UF_AUTHOR | string | Автор (для type=quote) |
| UF_VIDEO_URL | string | URL видео (для type=video) |

```php
$blocks = $dataClass::getList([
    'filter' => ['=UF_ELEMENT_ID' => $elementId],
    'order'  => ['UF_SORT' => 'ASC'],
])->fetchAll();

foreach ($blocks as $block) {
    switch ($block['UF_TYPE']) {
        case 'text':
            echo '<p>' . htmlspecialchars($block['UF_TEXT']) . '</p>';
            break;
        case 'image':
            $img = CFile::ResizeImageGet($block['UF_IMAGE'], ['width' => 800, 'height' => 600]);
            if ($img) {
                echo '<img src="' . htmlspecialchars($img['src']) . '">';
            }
            break;
        case 'quote':
            echo '<blockquote>' . htmlspecialchars($block['UF_TEXT'])
               . '<cite>' . htmlspecialchars($block['UF_AUTHOR']) . '</cite></blockquote>';
            break;
        case 'video':
            echo '<div class="video" data-url="' . htmlspecialchars($block['UF_VIDEO_URL']) . '"></div>';
            break;
    }
}
```

---

### Паттерн 4: Глубокая вложенность (HL поле → другой HL-блок)

Через UF-тип `hlblock` можно создать HL-запись, которая ссылается на записи другого HL.

**Пример:** Товар → Характеристики (repeater HL) → каждая характеристика содержит UF поле типа `hlblock` → Единица измерения (другой HL).

```
ElementTable (iblock element, VERSION=2)
  └── UF_SPECS_REF (hlblock UF → HlSpecsTable)
        HlSpecsTable (HL: my_specs)
          ├── UF_ELEMENT_ID (int, ссылка на элемент ИБ)
          ├── UF_VALUE (string)
          └── UF_UNIT_REF (hlblock UF → HlUnitsTable)
                HlUnitsTable (HL: my_units)
                  ├── UF_NAME (string)
                  └── UF_SYMBOL (string)
```

```php
// Загрузить характеристики со связанными единицами измерения
use Bitrix\Main\ORM\Fields\Relations\Reference;
use Bitrix\Main\ORM\Query\Join;

$specsEntity = HighloadBlockTable::compileEntity($specsHlblock);
$specsClass  = $specsEntity->getDataClass();

$unitsEntity = HighloadBlockTable::compileEntity($unitsHlblock);
$unitsClass  = $unitsEntity->getDataClass();

// Runtime Reference для JOIN units к specs (через UF_UNIT поле)
$specsClass::getList([
    'filter' => ['=UF_ELEMENT_ID' => $elementId],
    'select' => [
        'ID', 'UF_VALUE',
        'UNIT_NAME'   => 'UNIT.UF_NAME',
        'UNIT_SYMBOL' => 'UNIT.UF_SYMBOL',
    ],
    'runtime' => [
        new Reference(
            'UNIT',
            $unitsClass,
            Join::on('this.UF_UNIT', 'ref.ID')  // UF_UNIT хранит int ID
        ),
    ],
]);
```

---

## Массовая загрузка HL-данных без N+1

Проблема: для 50 элементов ИБ делать 50 запросов к HL — антипаттерн.

```php
// Шаг 1: получить элементы ИБ
$elements = ElementProductsTable::getList([
    'filter' => ['=ACTIVE' => 'Y'],
    'select' => ['ID', 'NAME'],
    'limit'  => 50,
])->fetchAll();

$elementIds = array_column($elements, 'ID');

// Шаг 2: один запрос к HL — все repeater-строки для всех элементов
$repeaterRows = $dataClass::getList([
    'filter' => ['@UF_ELEMENT_ID' => $elementIds],  // IN
    'order'  => ['UF_ELEMENT_ID' => 'ASC', 'UF_SORT' => 'ASC'],
])->fetchAll();

// Шаг 3: сгруппировать по UF_ELEMENT_ID
$index = [];
foreach ($repeaterRows as $row) {
    $index[$row['UF_ELEMENT_ID']][] = $row;
}

// Шаг 4: смержить
foreach ($elements as &$el) {
    $el['SPECS'] = $index[$el['ID']] ?? [];
}
unset($el);
```

---

## Регистрация UF-поля через HL-тип на HL-сущности

Чтобы UF-поле на HL-блоке ссылалось на другой HL-блок (глубокая вложенность):

```php
use Bitrix\Main\UserField\Types\EnumType;

global $USER_FIELD_MANAGER;

// Добавить UF поле типа 'hlblock' на HL-блок my_specs
$USER_FIELD_MANAGER->Add([
    'ENTITY_ID'        => 'HLBLOCK_' . $specsHlblockId,  // не IBLOCK_ELEMENT!
    'FIELD_NAME'       => 'UF_UNIT',
    'USER_TYPE_ID'     => 'hlblock',
    'SORT'             => 200,
    'MULTIPLE'         => 'N',
    'MANDATORY'        => 'N',
    'SETTINGS'         => [
        'HLBLOCK_ID' => $unitsHlblockId,   // ID целевого HL-блока
        'HLFIELD_ID' => 0,                  // 0 = по ID записи
    ],
]);
```

> **Gotcha:** `ENTITY_ID` для HL-сущностей = `'HLBLOCK_' . $hlblock['ID']`. Для элементов ИБ = `'IBLOCK_ELEMENT'` (общая для всех ИБ!).

---

## Файл в UF-поле HL-записи

При сохранении HL-строки с UF-полем типа `file` через `EditFormAddFields`:

```php
// В контроллере / обработчике формы
use Bitrix\Main\Application;

$request = Application::getInstance()->getContext()->getRequest();

// Получить файл из запроса
$uploadedFile = $request->getFile('uf_image');  // эквивалент $_FILES['uf_image']

$data = [
    'UF_ELEMENT_ID' => $elementId,
    'UF_SORT'       => 100,
    'UF_TITLE'      => $request->getPost('uf_title'),
    'UF_IMAGE'      => $uploadedFile,  // передать массив $_FILES — onBeforeSave разберёт сам
];

// EditFormAddFields вызывает onBeforeSave для UF_IMAGE:
// FileType::onBeforeSave получит массив $_FILES и вызовет CFile::SaveFile
global $USER_FIELD_MANAGER;
$entityId = 'HLBLOCK_' . $hlId;

if (!$USER_FIELD_MANAGER->EditFormAddFields($entityId, $data)) {
    throw new \RuntimeException('UF validation failed: ' . $USER_FIELD_MANAGER->GetErrorMessage());
}

// После EditFormAddFields в $data['UF_IMAGE'] уже лежит int (ID из b_file)
$result = $dataClass::add($data);
if (!$result->isSuccess()) {
    // откатить файл если нужно
    if (!empty($data['UF_IMAGE'])) {
        CFile::Delete($data['UF_IMAGE']);
    }
}
```

---

## RENDER_COMPONENT — рендер через компонент

Если логика рендера сложная, выноси в компонент вместо методов класса:

```php
public static function getUserTypeDescription(): array
{
    return [
        'USER_TYPE_ID'     => static::USER_TYPE_ID,
        'CLASS_NAME'       => static::class,
        'DESCRIPTION'      => 'Цвет (кастомный)',
        'BASE_TYPE'        => TypeBase::BASE_TYPE_STRING,
        'RENDER_COMPONENT' => 'my.module:uf.color',  // bitrix/local/components/my.module/uf.color/
    ];
}
```

Компонент получает в `$arParams`:
- `MODE` — 'edit', 'view', 'admin_list_view', 'admin_list_edit', 'filter', 'settings'
- `VALUE` — текущее значение
- `FIELD_NAME` — имя input
- `USER_FIELD` — весь массив описания UF-поля
- `ADDITIONAL_PARAMETERS` — параметры из контекста

---

## Полный пример: ACF Repeater с изображением

**Модуль добавляет repeater к инфоблоку:** каждый элемент может иметь список «слайдов» (заголовок + изображение).

```php
// 1. Создать HL-блок (один раз, при установке модуля)
use Bitrix\Highloadblock\HighloadBlockTable;

$result = HighloadBlockTable::add([
    'NAME'       => 'ProductSliders',
    'TABLE_NAME' => 'hl_product_sliders',
]);
$hlId = $result->getId();

// 2. Добавить UF-поля к HL-блоку
global $USER_FIELD_MANAGER;

$fields = [
    ['FIELD_NAME' => 'UF_ELEMENT_ID', 'USER_TYPE_ID' => 'integer',   'SORT' => 10],
    ['FIELD_NAME' => 'UF_SORT',       'USER_TYPE_ID' => 'integer',   'SORT' => 20],
    ['FIELD_NAME' => 'UF_TITLE',      'USER_TYPE_ID' => 'string',    'SORT' => 30],
    ['FIELD_NAME' => 'UF_IMAGE',      'USER_TYPE_ID' => 'file',      'SORT' => 40],
];

foreach ($fields as $field) {
    $USER_FIELD_MANAGER->Add(array_merge([
        'ENTITY_ID'  => 'HLBLOCK_' . $hlId,
        'MULTIPLE'   => 'N',
        'MANDATORY'  => 'N',
    ], $field));
}
```

```php
// 3. Сервис для работы со слайдами
namespace MyVendor\MyModule\Service;

use Bitrix\Highloadblock\HighloadBlockTable;
use Bitrix\Main\Result;
use Bitrix\Main\Error;
use CFile;

class SliderService
{
    private string $dataClass;

    public function __construct()
    {
        $hlblock = HighloadBlockTable::getRow(['filter' => ['=NAME' => 'ProductSliders']]);
        $entity  = HighloadBlockTable::compileEntity($hlblock);
        $this->dataClass = $entity->getDataClass();
    }

    public function getSlides(int $elementId): array
    {
        return ($this->dataClass)::getList([
            'filter' => ['=UF_ELEMENT_ID' => $elementId],
            'order'  => ['UF_SORT' => 'ASC'],
            'select' => ['ID', 'UF_SORT', 'UF_TITLE', 'UF_IMAGE'],
        ])->fetchAll();
    }

    public function addSlide(int $elementId, string $title, array $fileArray, int $sort = 100): Result
    {
        $result = new Result();

        $fileId = CFile::SaveFile($fileArray, 'product_sliders');
        if (!$fileId) {
            return $result->addError(new Error('Ошибка сохранения файла'));
        }

        $addResult = ($this->dataClass)::add([
            'UF_ELEMENT_ID' => $elementId,
            'UF_SORT'       => $sort,
            'UF_TITLE'      => $title,
            'UF_IMAGE'      => $fileId,
        ]);

        if (!$addResult->isSuccess()) {
            CFile::Delete($fileId);  // откат файла
            return $result->addErrors($addResult->getErrors());
        }

        return $result->setData(['id' => $addResult->getId()]);
    }

    public function deleteSlide(int $slideId): void
    {
        $row = ($this->dataClass)::getRow(['filter' => ['=ID' => $slideId]]);
        if ($row) {
            ($this->dataClass)::delete($slideId);
            if ($row['UF_IMAGE']) {
                CFile::Delete($row['UF_IMAGE']);
            }
        }
    }

    public function getSlidesWithThumbs(int $elementId, int $width = 300, int $height = 200): array
    {
        $slides = $this->getSlides($elementId);

        foreach ($slides as &$slide) {
            $slide['THUMB'] = null;
            if ($slide['UF_IMAGE']) {
                $thumb = CFile::ResizeImageGet(
                    $slide['UF_IMAGE'],
                    ['width' => $width, 'height' => $height],
                    BX_RESIZE_IMAGE_PROPORTIONAL
                );
                $slide['THUMB'] = $thumb ?: null;
            }
        }
        unset($slide);

        return $slides;
    }
}
```

---

## Gotchas

- `ENTITY_ID` для HL-блока = `'HLBLOCK_' . $hlblock['ID']` — не путай с `'IBLOCK_ELEMENT'`
- `EditFormAddFields` изменяет `$data` по ссылке — после вызова в `$data['UF_IMAGE']` уже int, не массив `$_FILES`
- `BASE_TYPE_FILE` вызывает `CFile::Delete` автоматически только при удалении самого UF-поля (через admin). При удалении HL-строки через `::delete()` — файл НЕ удаляется автоматически. Удаляй вручную
- Глубокая вложенность (HL→HL) работает только если `VERSION=2` для ИБ-элементов (ElementV2Table), но для HL→HL join всегда runtime Reference — VERSION не важен
- `compileEntity` кешируется Bitrix, но первый вызов — тяжёлый (собирает UF-поля). Кешируй `$dataClass` в сервисе
- `UF_*` поля на HL хранятся в той же таблице (не UTM) — в отличие от UF на IblockElement
- `onBeforeSave` НЕ вызывается если использовать `$dataClass::add()` напрямую без `EditFormAddFields`. Только через `EditFormAddFields` или admin-save
- При использовании `RENDER_COMPONENT` режим `MODE='edit'` — для формы редактирования, component_epilog может получить POST-данные
