# Bitrix Безопасность — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с защитой от XSS, SQL-инъекций, CSRF, проверкой прав доступа, аутентификацией или работой с текущим пользователем.

## Содержание
- XSS: HtmlFilter::encode(), htmlspecialchars, контекстное экранирование
- SQL-инъекции: ORM как защита, forSql() для raw SQL
- CSRF: bitrix_sessid_post(), check_bitrix_sessid(), ActionFilter\Csrf
- Текущий пользователь: CurrentUser (D7), глобальный $USER (legacy)
- Проверка прав: IsAdmin, CanDoOperation, CIBlock::GetPermission
- ActionFilter: Authentication, Csrf, HttpMethod в Controllers
- Общие gotchas безопасности

---

## XSS — экранирование вывода

Любые данные из БД, параметров запроса или пользовательского ввода **обязательно** экранировать перед выводом в HTML.

```php
use Bitrix\Main\Text\HtmlFilter;

// D7-способ — предпочтительный
// HtmlFilter::encode() — это просто htmlspecialchars($str, ENT_COMPAT, 'UTF-8')
echo HtmlFilter::encode($value);

// PHP-способ — эквивалентен, допустим
echo htmlspecialchars($value, ENT_QUOTES, 'UTF-8');

// Экранирование для атрибутов HTML — ENT_QUOTES важен
echo '<input value="' . HtmlFilter::encode($value) . '">';

// Для URL — только urlencode(), не htmlspecialchars
echo '<a href="/page/?q=' . urlencode($searchQuery) . '">';

// Для JSON в JS-контексте — json_encode защищает от XSS
echo '<script>var data = ' . json_encode($data, JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_HEX_AMP) . ';</script>';
```

### Что НЕ является защитой от XSS

```php
// НЕ защищает: strip_tags не убирает атрибуты с JS
echo strip_tags($value); // уязвимо: <img onerror="alert(1)" src="x">

// НЕ защищает: addslashes — только для строк в JS, не для HTML
echo addslashes($value); // не экранирует < > &

// НЕПРАВИЛЬНО: ENT_COMPAT не закрывает одинарные кавычки
echo htmlspecialchars($value, ENT_COMPAT); // уязвимо в атрибутах с '
// ПРАВИЛЬНО:
echo htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
```

### Bitrix Application::getHtmlEncoder() — для сложных случаев

```php
$encoder = \Bitrix\Main\Application::getInstance()->getHtmlEncoder();
// Используется для настраиваемых правил экранирования в модулях
// В большинстве случаев достаточно HtmlFilter::encode()
```

---

## SQL-инъекции — ORM как основная защита

ORM DataManager полностью защищает от SQL-инъекций — параметры передаются через подготовленные выражения.

```php
// БЕЗОПАСНО: ORM экранирует всё автоматически
$result = OrderTable::getList([
    'filter' => ['=TITLE' => $userInput, '%DESCRIPTION' => $searchQuery],
]);

// БЕЗОПАСНО: getById принимает только скалярный тип
$row = OrderTable::getById((int)$_GET['id'])->fetch();

// БЕЗОПАСНО: add/update экранируют значения полей
OrderTable::add(['TITLE' => $userInput]);
```

### Raw SQL — только через forSql()

```php
$connection = \Bitrix\Main\Application::getConnection();
$helper = $connection->getSqlHelper();

// ВСЕГДА экранируй через forSql() перед подстановкой в SQL
$safeTitle = $helper->forSql($userInput);  // добавляет экранирование спецсимволов
$safeId    = (int)$id;                      // числа — просто привести к int

$result = $connection->query(
    "SELECT * FROM my_table WHERE TITLE = '{$safeTitle}' AND ID = {$safeId}"
);

// forSql() не добавляет кавычки — только экранирует содержимое
// Кавычки добавляешь сам: '{$safeTitle}'

// НИКОГДА так:
$connection->query("SELECT * FROM t WHERE ID = " . $_GET['id']); // уязвимость!
$connection->query("SELECT * FROM t WHERE TITLE = '" . $title . "'"); // уязвимость!
```

---

## CSRF — защита форм и AJAX

### Legacy-формы: `bitrix_sessid_post()`

```php
// В шаблоне формы: вставляет скрытый input с токеном
<form method="POST">
    <?= bitrix_sessid_post() ?>
    <!-- Выводит: <input type="hidden" name="sessid" value="TOKEN"> -->
    <input type="text" name="title">
    <button type="submit">Сохранить</button>
</form>

// Проверка на стороне сервера
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!check_bitrix_sessid()) {
        // Неверный CSRF-токен
        ShowError('Неверный токен сессии');
        return;
    }
    // ...обрабатывай форму...
}

// Вспомогательные функции
bitrix_sessid();             // возвращает текущий токен (string)
bitrix_sessid_get();         // возвращает строку 'sessid=TOKEN' (для URL)
check_bitrix_sessid();       // bool: проверяет POST/GET параметр 'sessid' ИЛИ заголовок X-Bitrix-Csrf-Token
check_bitrix_sessid('csrf'); // проверяет параметр с другим именем
```

### D7 Controllers: `ActionFilter\Csrf`

В D7-контроллерах CSRF-фильтр добавляется явно. По умолчанию `Controller` добавляет его автоматически только для POST-экшенов.

```php
use Bitrix\Main\Engine\Controller;
use Bitrix\Main\Engine\ActionFilter;

class OrderController extends Controller
{
    public function configureActions(): array
    {
        return [
            // Явный CSRF-фильтр — работает только в SCOPE_AJAX
            'create' => [
                'prefilters' => [
                    new ActionFilter\Authentication(),
                    new ActionFilter\Csrf(),      // проверяет 'sessid' в запросе
                    new ActionFilter\HttpMethod(['POST']),
                ],
            ],
            // Отключить CSRF для webhook (например, внешние вызовы)
            'webhook' => [
                'prefilters' => [
                    new ActionFilter\Csrf(false), // false = отключить проверку
                ],
            ],
        ];
    }

    public function createAction(string $title): ?array
    {
        return ['id' => 42];
    }

    public function webhookAction(): ?array
    {
        return ['ok' => true];
    }
}
```

### CSRF в AJAX из JS

```javascript
// Получить токен для AJAX запроса
const sessid = BX.bitrix_sessid(); // глобальная функция Bitrix JS

// Или из мета-тега (добавляется ядром автоматически)
const sessid = BX('bx-' + BX.message('bitrix_sessid_key'));

// Передать в fetch
fetch('/bitrix/services/main/ajax.php?action=mymodule.order.create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Bitrix-Csrf-Token': BX.bitrix_sessid(),  // заголовок — check_bitrix_sessid() его принимает
    },
    body: JSON.stringify({ sessid: BX.bitrix_sessid(), title: 'Test' }),
});
```

---

## Текущий пользователь

### D7: `Engine\CurrentUser` (предпочтительно в сервисах и контроллерах)

```php
use Bitrix\Main\Engine\CurrentUser;

$user = CurrentUser::get(); // никогда не возвращает null

$user->getId();             // int|string|null — null если не авторизован
$user->getLogin();          // string|null
$user->getEmail();          // string|null
$user->getFullName();       // string|null
$user->getFirstName();
$user->getLastName();
$user->getUserGroups();     // array с ID групп ['1', '4', '13']
$user->isAdmin();           // bool
$user->canDoOperation('название_операции'); // bool

// Проверка авторизации
if ($user->getId()) {
    // пользователь авторизован
}
```

### Legacy: глобальный `$USER` (обязателен в компонентах и шаблонах)

```php
global $USER;

// Всегда проверяй что объект существует перед вызовом методов
if (is_object($USER) && $USER->IsAuthorized()) {
    $userId  = (int)$USER->GetID();
    $login   = $USER->GetLogin();
    $email   = $USER->GetEmail();
    $groups  = $USER->GetUserGroupArray();  // array ID групп ['1', '4', '13']
    $isAdmin = $USER->IsAdmin();            // bool
}

// Проверка операции (права в модуле 'main')
if ($USER->CanDoOperation('edit_php')) { ... }
if ($USER->CanDoOperation('view_all')) { ... }

// Получить ID текущего пользователя безопасно
$userId = is_object($USER) ? (int)$USER->GetID() : 0;
```

---

## Проверка прав доступа

### Права доступа к инфоблоку

```php
// CIBlock::GetPermission возвращает: 'D' (Deny), 'R' (Read), 'W' (Write), 'X' (Full)
// CIBlockRights::PUBLIC_READ = 'R', ::EDIT_ACCESS = 'W', ::FULL_ACCESS = 'X'

$permission = CIBlock::GetPermission($iblockId);

if ($permission < 'R') {
    // нет доступа даже на чтение
    ShowError('Нет доступа к инфоблоку');
    return;
}

if ($permission >= 'W') {
    // есть права на редактирование
}

// В GetList автоматически с CHECK_PERMISSIONS
$res = CIBlockElement::GetList(
    [],
    [
        'IBLOCK_ID'        => $iblockId,
        'ACTIVE'           => 'Y',
        'CHECK_PERMISSIONS' => 'Y',    // фильтрует по правам текущего пользователя
        'MIN_PERMISSION'   => 'R',     // минимальный требуемый уровень
    ]
);
```

### Проверка прав на модуль (`$APPLICATION->GetGroupRight`)

```php
global $APPLICATION;

// Права текущего пользователя на модуль
$right = $APPLICATION->GetGroupRight('iblock'); // 'D', 'R', 'W' или 'X'
if ($right < 'W') {
    ShowError('Недостаточно прав');
    return;
}

// Проверка прав для конкретного пользователя
// В компонентах admin-панели — стандартная проверка:
if (!$USER->CanDoOperation('edit_iblock') && $APPLICATION->GetGroupRight('iblock') < 'W') {
    $APPLICATION->AuthForm("Доступ запрещён");
}
```

### Проверка в AdminSection

```php
// Стандартный паттерн для страниц /bitrix/admin/
require_once($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_before.php');

// После подключения пролога $USER и $APPLICATION доступны глобально
\Bitrix\Main\Loader::includeModule('my.module');

$right = $APPLICATION->GetGroupRight('my.module'); // читает из таблицы прав
if ($right === 'D') {
    $APPLICATION->AuthForm('Доступ запрещён');
}

require_once($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_admin_after.php');
```

### ActionFilter\Authentication — защита Controller-экшенов

```php
// Добавь в configureActions() чтобы требовать авторизацию
'prefilters' => [
    new ActionFilter\Authentication(),
    // Authentication(true) — перенаправляет на форму логина для non-AJAX запросов
    // Authentication(false) — только 401 ответ без редиректа (по умолчанию)
],
```

---

## Шифрование и хеширование паролей

```php
// НЕ используй md5/sha1 для паролей — только CUser::HashPassword
// Bitrix использует собственную логику хеширования с солью

// Хеширование нового пароля
$hashedPassword = CUser::HashPassword($plainPassword);

// Проверка пароля — через метод авторизации, не напрямую сравнивая хеши
// Для проверки используй $USER->Login() или CUser::Authorize()
```

---

## Gotchas безопасности

- **`HtmlFilter::encode()` использует `ENT_COMPAT`** по умолчанию (не `ENT_QUOTES`) — экранирует `"` но не `'`. Для атрибутов с одинарными кавычками передай флаг явно: `HtmlFilter::encode($v, ENT_QUOTES)`
- **`check_bitrix_sessid()` принимает токен из двух мест**: POST/GET параметр `sessid` ИЛИ заголовок `X-Bitrix-Csrf-Token`. Если шлёшь через заголовок — в теле параметр не нужен.
- **`ActionFilter\Csrf` работает только в `SCOPE_AJAX`** (проверено в `listAllowedScopes()`). В `SCOPE_REST` или `SCOPE_DEFAULT` фильтр пропускается — нужен отдельный механизм защиты.
- **`CIBlock::GetPermission()` кешируется в статике** внутри запроса — повторные вызовы с теми же `$IBLOCK_ID` и группами не идут в БД.
- **Права 'D' < 'R' < 'W' < 'X'** — сравнение строк работает корректно для этих букв в ASCII. `$p < 'R'` значит нет чтения.
- **`CurrentUser::get()` никогда не возвращает null** — возвращает объект у которого `getId()` вернёт `null`. Всегда проверяй `$user->getId()` а не наличие объекта.
- **`$USER->IsAdmin()`** возвращает `true` только если пользователь в группе с ID=1 (администраторы) — обычные `bitrix_admin` операции этого не дают.
- **Не полагайся на `$_SESSION`** напрямую для хранения прав — используй только механизмы Bitrix (`$USER`, `$APPLICATION->GetGroupRight`).
