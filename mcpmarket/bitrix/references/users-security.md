# Users Security
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `users.md`

# Пользователи (CUser / UserTable)

> Reference для Bitrix-скилла. Загружай когда задача связана с `CUser`, `Bitrix\Main\UserTable`, текущим пользователем или пользовательскими UF-полями.
>
> Audit note: проверено по текущему core `main/classes/general/user.php`, `main/lib/user.php`, `main/lib/engine/currentuser.php`.

## Текущий пользователь

```php
global $USER; // объект CUser, всегда доступен в контексте сайта

// Основные проверки
$USER->IsAuthorized(); // bool — авторизован ли
$USER->IsAdmin();      // bool — системный администратор
$USER->GetID();        // int — ID, 0 если не авторизован
$USER->GetLogin();     // string — логин
$USER->GetEmail();     // string — email
$USER->GetFullName();  // string — "Имя Фамилия"

// Группы
$groups = $USER->GetUserGroupArray(); // [1, 5, 8] — массив ID групп

// D7-обёртка (без глобальных переменных)
use Bitrix\Main\Engine\CurrentUser;
$currentUser = CurrentUser::get();
$id    = $currentUser->getId();
$login = $currentUser->getLogin();
$email = $currentUser->getEmail();
$isAdmin = $currentUser->isAdmin();
```

---

## D7 ORM: UserTable

```php
use Bitrix\Main\UserTable;

// Поиск пользователей
$result = UserTable::getList([
    'select' => ['ID', 'LOGIN', 'EMAIL', 'NAME', 'LAST_NAME', 'ACTIVE', 'LAST_LOGIN'],
    'filter' => [
        '=ACTIVE' => 'Y',
        '%EMAIL'  => '@example.com',   // LIKE
    ],
    'order'  => ['DATE_REGISTER' => 'DESC'],
    'limit'  => 50,
]);
while ($row = $result->fetch()) { ... }

// Один пользователь по ID
$user = UserTable::getById($userId)->fetch();

// Один пользователь по email
$user = UserTable::getRow([
    'filter' => ['=EMAIL' => 'user@example.com'],
    'select' => ['ID', 'LOGIN', 'NAME', 'LAST_NAME', 'ACTIVE'],
]);

// Пользователи определённой группы (через relation)
$result = UserTable::getList([
    'select' => ['ID', 'LOGIN', 'EMAIL'],
    'filter' => ['=GROUPS.GROUP_ID' => 5],  // OneToMany GROUPS → UserGroupTable
]);
```

### Все поля UserTable (основные)

| Поле | Тип | Описание |
|------|-----|---------|
| `ID` | int | — |
| `LOGIN` | string | логин |
| `EMAIL` | string | email |
| `NAME` / `LAST_NAME` / `SECOND_NAME` | string | имя |
| `ACTIVE` | bool (Y/N) | активен |
| `BLOCKED` | bool (Y/N) | заблокирован |
| `DATE_REGISTER` | datetime | дата регистрации |
| `LAST_LOGIN` | datetime | последний вход |
| `PERSONAL_PHONE` / `PERSONAL_MOBILE` | string | телефоны |
| `PERSONAL_BIRTHDAY` | date | день рождения |
| `PERSONAL_GENDER` | string | `M`/`F`/`` |
| `PERSONAL_PHOTO` | int | ID файла в b_file |
| `LANGUAGE_ID` | string | язык интерфейса |
| `IS_ONLINE` | expr | `Y`/`N` — онлайн ли (active < 15 мин) |

---

## Создание пользователя

```php
$obUser = new CUser();
$userId = $obUser->Add([
    'LOGIN'      => 'ivan_petrov',
    'EMAIL'      => 'ivan@example.com',
    'PASSWORD'   => 'SecurePass123!',
    'CONFIRM_PASSWORD' => 'SecurePass123!',
    'NAME'       => 'Иван',
    'LAST_NAME'  => 'Петров',
    'ACTIVE'     => 'Y',
    'GROUP_ID'   => [5, 8],  // ID групп, ЗАМЕНЯЕТ все группы
    'PERSONAL_PHONE' => '+79991234567',
    'LANGUAGE_ID'    => 'ru',
]);

if (!$userId) {
    $error = $obUser->LAST_ERROR; // строка с ошибкой
}
```

> **Gotcha:** `PASSWORD` хешируется внутри `Add()` через `Password::hash()` — передавай открытый пароль, не хеш.

---

## Обновление пользователя

```php
$obUser = new CUser();
$result = $obUser->Update($userId, [
    'NAME'            => 'Иван',
    'LAST_NAME'       => 'Петров',
    'PERSONAL_MOBILE' => '+79991234567',
    'EMAIL'           => 'new@example.com',
]);

if (!$result) {
    $error = $obUser->LAST_ERROR;
}

// Сменить пароль
$obUser->Update($userId, [
    'PASSWORD'         => 'NewPassword456!',
    'CONFIRM_PASSWORD' => 'NewPassword456!',
]);
```

---

## Авторизация пользователя

```php
global $USER;

// Авторизация по логину/паролю
$result = $USER->Login('ivan_petrov', 'SecurePass123!', 'Y'); // 'Y' = запомнить

if ($result !== true) {
    // $result — массив ['MESSAGE' => '...', 'TYPE' => 'ERROR']
    $error = $result['MESSAGE'];
}

// Авторизовать пользователя по ID (без пароля — только для доверенного кода)
$USER->Authorize($userId);

// Выйти
$USER->Logout();
```

> **Gotcha:** `Login()` возвращает `true` при успехе и массив с ошибкой при неудаче — не bool.

---

## Восстановление пароля

```php
// Отправить письмо с новым паролем / ссылкой на смену
$result = CUser::SendPassword(
    'ivan_petrov',     // логин
    'ivan@example.com', // email (должен совпасть с пользователем)
    SITE_ID            // сайт
);

if ($result['TYPE'] === 'OK') {
    // письмо отправлено
} else {
    $error = $result['MESSAGE'];
}
```

---

## Пользовательские поля (UF) пользователя

UF-сущность пользователя: `USER`.

### Читать UF-поля

```php
// Через CUser::GetByID (возвращает все поля включая UF_*)
$res = CUser::GetByID($userId);
$user = $res->Fetch();
// $user['UF_DEPARTMENT'], $user['UF_CUSTOM_FIELD']

// Для сложных UF-сценариев safest-path:
// читать через CUser::GetByID() или USER_FIELD_MANAGER
global $USER_FIELD_MANAGER;
$ufValues = $USER_FIELD_MANAGER->GetUserFields('USER', $userId, LANGUAGE_ID);
// $ufValues['UF_MY_FIELD']['VALUE']
```

### Обновить UF-поля

```php
global $USER_FIELD_MANAGER;

// Вариант 1: через CUser::Update (передать UF в массиве)
$obUser = new CUser();
$obUser->Update($userId, [
    'UF_DEPARTMENT' => 5,
    'UF_BIO'        => 'Текст...',
]);

// Вариант 2: напрямую через USER_FIELD_MANAGER
$USER_FIELD_MANAGER->Update('USER', $userId, [
    'UF_DEPARTMENT' => 5,
]);
```

### Создать UF-поле для пользователей

```php
$oUserTypeEntity = new CUserTypeEntity();
$oUserTypeEntity->Add([
    'ENTITY_ID'         => 'USER',
    'FIELD_NAME'        => 'UF_TELEGRAM',
    'USER_TYPE_ID'      => 'string',
    'SORT'              => 100,
    'MULTIPLE'          => 'N',
    'MANDATORY'         => 'N',
    'SHOW_FILTER'       => 'I',
    'SHOW_IN_LIST'      => 'Y',
    'EDIT_IN_LIST'      => 'Y',
    'EDIT_FORM_LABEL'   => ['ru' => 'Telegram', 'en' => 'Telegram'],
    'LIST_COLUMN_LABEL' => ['ru' => 'Telegram', 'en' => 'Telegram'],
]);
```

---

## Группы пользователей

```php
// Назначить группы (ЗАМЕНЯЕТ все существующие)
CUser::SetUserGroup($userId, [5, 8, 14]);

// Добавить в группу (сохранив остальные)
$currentGroups = $USER->GetUserGroupArray();
if (!in_array(5, $currentGroups)) {
    CUser::SetUserGroup($userId, array_merge($currentGroups, [5]));
}

// Проверить группу у произвольного пользователя
$res = CUser::GetByID($userId);
$user = $res->Fetch();
// группы в отдельном запросе:
$groupRes = CUser::GetUserGroup($userId); // устаревший способ
// Через UserTable D7:
$result = \Bitrix\Main\UserGroupTable::getList([
    'filter' => ['=USER_ID' => $userId],
    'select' => ['GROUP_ID'],
]);
$groupIds = array_column($result->fetchAll(), 'GROUP_ID');
```

---

## Поиск пользователей (legacy)

```php
// Legacy GetList — все ещё широко используется
$res = CUser::GetList(
    $sort = 'ID',
    $order = 'ASC',
    $arFilter = [
        'ACTIVE'      => 'Y',
        'GROUPS_ID'   => [5],          // пользователи из группы 5
        'NAME_SEARCH' => 'Иван',       // поиск по имени
    ],
    $arParams = [
        'SELECT' => ['UF_DEPARTMENT'], // добавить UF-поля в выборку
        'NAV_PARAMS' => ['nPageSize' => 20],
    ]
);
while ($user = $res->Fetch()) { ... }
```

---

## События пользователя

```php
use Bitrix\Main\EventManager;
use Bitrix\Main\Application;

$em = EventManager::getInstance();

// OnBeforeUserAdd / OnBeforeUserUpdate — legacy-события main.
// Чтобы изменить $arFields по ссылке или отменить операцию — нужен addEventHandlerCompatible.
// addEventHandler оборачивает параметры в Event-объект и ссылка теряется.
$em->addEventHandlerCompatible('main', 'OnBeforeUserAdd',
    ['\MyVendor\MyModule\UserHandler', 'onBeforeAdd']);

class UserHandler
{
    // $arFields — по ссылке: можно читать и изменять
    public static function onBeforeAdd(array &$arFields): void
    {
        // Нормализация
        $arFields['EMAIL'] = mb_strtolower(trim($arFields['EMAIL'] ?? ''));

        // Отмена операции: ThrowException, ядро проверит GetException() после события
        if (empty($arFields['EMAIL'])) {
            global $APPLICATION;
            $APPLICATION->ThrowException('Email обязателен');
        }
    }

    // OnAfterUserAdd — читаем результат, arFields['ID'] = ID нового пользователя
    public static function onAfterAdd(array &$arFields): void
    {
        $userId = (int)$arFields['ID'];
        // отправить welcome-письмо и т.д.
    }
}

// OnAfterUserAdd через addEventHandler тоже работает если не нужна ссылка
$em->addEventHandler('main', 'OnAfterUserAdd', function(\Bitrix\Main\Event $event) {
    $fields = $event->getParameter('arFields');
    $userId = (int)($fields['ID'] ?? 0);
    // логика после добавления
});

// После авторизации
$em->addEventHandler('main', 'OnUserLoginComplete', function(\Bitrix\Main\Event $event) {
    $userId = (int)$event->getParameter('USER_ID');
});
```

> **Gotcha:** `OnBeforeUserAdd` / `OnBeforeUserUpdate` — legacy-события `main`. Если нужно изменить `$arFields` или отменить операцию через `ThrowException` — обязательно `addEventHandlerCompatible`. `addEventHandler` (D7-обёртка) передаёт параметры как копию внутри `Event`-объекта, ссылка на массив теряется.

---

## Gotchas

- `GROUP_ID` в `CUser::Add` **заменяет** все группы. Не передавай если не хочешь сбросить группы
- `CUser::SetUserGroup` тоже **заменяет** все группы — сначала считай текущие
- Для произвольных UF-полей safest-path — `CUser::GetByID` или `USER_FIELD_MANAGER->GetUserFields`. Не обещай вслепую одинаковое поведение всех UF через `UserTable::getList`
- `$USER->IsAdmin()` — только системный администратор (группа 1). Для проверки других групп используй `GetUserGroupArray()`
- `CUser::GetByID` возвращает db_result, надо вызвать `->Fetch()`
- Пароль в `Add/Update` всегда открытый — ядро само хеширует через `Password::hash()`

---

## Source: `access-rbac.md`

# Bitrix Access RBAC — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с D7-доступами на базе `Bitrix\Main\Access\*`: `PermissionDictionary`, `RoleDictionary`, `BaseAccessController`, `AbstractRule`, `AccessPermissionTable`, `AccessRoleTable`.
>
> Audit note: проверено по текущему core `main/lib/access/*`.

## Содержание
- Архитектура RBAC
- `PermissionDictionary`
- `RoleDictionary`
- `BaseAccessController`
- `AbstractRule`
- `AccessPermissionTable` / `AccessRoleTable`
- Naming convention rule/filter factory
- Gotchas

---

## Архитектура RBAC

Текущий D7-access слой строится вокруг четырёх сущностей:

- **Permission** — строковый код права
- **Role** — роль, которой потом сопоставляют значения permission
- **AccessibleUser** — модель пользователя, умеющая вернуть роли, access-codes и значение permission
- **AccessController** — orchestration-слой, который грузит пользователя/элемент и запускает rule/filter factory

Схема:

```text
AccessibleUser
    └── getPermission(permissionId)

BaseAccessController
    ├── check()
    ├── checkByItemId()
    ├── batchCheck()
    └── getEntityFilter()

RuleControllerFactory
    └── \Vendor\Module\Access\Rule\<Action>Rule

FilterControllerFactory
    └── \Vendor\Module\Access\Filter\<Action>Filter
```

---

## `PermissionDictionary`

В текущем core `PermissionDictionary` не требует `getPermissions()`. Базовый класс уже умеет:

- `getList()`
- `getPermission($permissionId)`
- `getTitle($permissionId)`
- `getType($permissionId)`

Минимальный словарь выглядит так:

```php
namespace MyVendor\MyModule\Access\Permission;

use Bitrix\Main\Access\Permission\PermissionDictionary;

class MyPermissionDictionary extends PermissionDictionary
{
    public const ITEM_VIEW   = 'item.view';
    public const ITEM_EDIT   = 'item.edit';
    public const ITEM_DELETE = 'item.delete';
    public const REPORT_MODE = 'report.mode';

    public static function getType($permissionId): string
    {
        return match ($permissionId) {
            self::REPORT_MODE => self::TYPE_VARIABLES,
            default => self::TYPE_TOGGLER,
        };
    }
}
```

Подтверждённые типы:

- `TYPE_TOGGLER`
- `TYPE_VARIABLES`
- `TYPE_MULTIVARIABLES`
- `TYPE_DEPENDENT_VARIABLES`

Подтверждённые значения:

```php
PermissionDictionary::VALUE_NO  = 0;
PermissionDictionary::VALUE_YES = 1;
```

`getList()` строится по константам класса, поэтому локализация обычно идёт через `Loc::loadMessages()` и имена констант.

---

## `RoleDictionary`

В текущем core `RoleDictionary` не даёт универсальный метод `getRoles()`. Подтверждён только базовый helper:

```php
use Bitrix\Main\Access\Role\RoleDictionary;

class MyRoleDictionary extends RoleDictionary
{
    public const ROLE_ADMIN  = 'MY_MODULE_ADMIN';
    public const ROLE_EDITOR = 'MY_MODULE_EDITOR';
    public const ROLE_VIEWER = 'MY_MODULE_VIEWER';
}

$title = MyRoleDictionary::getRoleName(MyRoleDictionary::ROLE_ADMIN);
```

Практический вывод:

- роли в reference лучше описывать через константы + локализацию
- хранение и CRUD ролей зависят уже от твоих конкретных таблиц/сервисов модуля

---

## `BaseAccessController`

`BaseAccessController` уже реализует основной runtime:

- `getInstance($userId)`
- `can($userId, $action, $itemId = null, $params = null)`
- `checkByItemId(...)`
- `check(...)`
- `batchCheck(...)`
- `getEntityFilter(...)`

От наследника требуются только две вещи:

```php
namespace MyVendor\MyModule\Access;

use Bitrix\Main\Access\AccessibleItem;
use Bitrix\Main\Access\BaseAccessController;
use Bitrix\Main\Access\User\AccessibleUser;

class MyAccessController extends BaseAccessController
{
    protected function loadItem(int $itemId = null): ?AccessibleItem
    {
        return $itemId ? MyItemModel::createFromId($itemId) : MyItemModel::createNew();
    }

    protected function loadUser(int $userId): AccessibleUser
    {
        return MyUserModel::createFromId($userId);
    }
}
```

Использование:

```php
if (!MyAccessController::can($USER->GetID(), 'item_view', $itemId))
{
    ShowError('Недостаточно прав');
    return;
}

$controller = MyAccessController::getInstance((int)$USER->GetID());
$canEdit = $controller->checkByItemId('item_edit', $itemId);
```

---

## `AbstractRule`

Правило в текущем core получает `AccessibleController` в конструкторе, а внутри уже имеет `$this->user`.

```php
namespace MyVendor\MyModule\Access\Rule;

use Bitrix\Main\Access\AccessibleItem;
use Bitrix\Main\Access\Rule\AbstractRule;
use MyVendor\MyModule\Access\Permission\MyPermissionDictionary;

class ItemEditRule extends AbstractRule
{
    public function execute(AccessibleItem $item = null, $params = null): bool
    {
        if ($this->user->isAdmin())
        {
            return true;
        }

        $permission = $this->user->getPermission(MyPermissionDictionary::ITEM_EDIT);

        return $permission !== null && $permission >= MyPermissionDictionary::VALUE_YES;
    }
}
```

Подтверждённая сигнатура:

```php
abstract public function execute(AccessibleItem $item = null, $params = null): bool;
```

---

## `AccessPermissionTable` / `AccessRoleTable`

Обе таблицы в `main` — абстрактные базовые классы. Их нельзя использовать как готовые таблицы “из коробки” без собственного наследника с `getTableName()`.

### Роли

```php
namespace MyVendor\MyModule\Access\Role;

use Bitrix\Main\Access\Role\AccessRoleTable;

class MyAccessRoleTable extends AccessRoleTable
{
    public static function getTableName()
    {
        return 'b_my_module_role';
    }
}
```

### Права роли

```php
namespace MyVendor\MyModule\Access\Permission;

use Bitrix\Main\Access\Permission\AccessPermissionTable;

class MyAccessPermissionTable extends AccessPermissionTable
{
    public static function getTableName()
    {
        return 'b_my_module_permission';
    }
}
```

После этого уже можно делать обычный ORM-CRUD:

```php
MyAccessPermissionTable::add([
    'ROLE_ID' => 10,
    'PERMISSION_ID' => MyPermissionDictionary::ITEM_EDIT,
    'VALUE' => MyPermissionDictionary::VALUE_YES,
]);
```

Важно: `AccessPermissionTable` в текущем core сам валидирует иерархию permission-path. Если родительское permission выключено (`VALUE_NO`), дочерние значения могут быть автоматически зажаты вниз.

---

## Naming convention rule/filter factory

`BaseAccessController` по умолчанию использует:

- `RuleControllerFactory`
- `FilterControllerFactory`

Имена классов собираются автоматически из action:

```text
Controller namespace: MyVendor\MyModule\Access
Action: item_edit

Rule class:   MyVendor\MyModule\Access\Rule\ItemEditRule
Filter class: MyVendor\MyModule\Access\Filter\ItemEditFilter
```

То есть action `my_item_delete` превратится в `Rule\MyItemDeleteRule`.

Если такого класса нет, `check()` завершится `UnknownActionException`.

---

## Gotchas

- `PermissionDictionary::getList()` строится по константам класса. Не выдумывай отдельный обязательный `getPermissions()` — он не является core-contract текущего `main`.
- `RoleDictionary` в базовом виде умеет только `getRoleName()`. Полный “список ролей” — ответственность конкретного модуля.
- `AccessPermissionTable` и `AccessRoleTable` абстрактные. Для реального хранения прав нужен собственный наследник с `getTableName()`.
- `BaseAccessController::can()` кеширует экземпляр контроллера по `userId`. Если в этом же запросе ты поменял роли/права и хочешь свежую проверку, создавай новый controller осознанно.
- `AbstractRule::$this->user->isAdmin()` проверяет суперадмина Bitrix, а не произвольную бизнес-роль модуля.
- `$item` в `execute()` может быть `null`. Rule должна это корректно переживать.
- Для массовых выборок полезен `getEntityFilter()`, но фильтр появится только если для action существует соответствующий `Filter\<Action>Filter`.

---

## Source: `session-auth.md`

# Bitrix Session + Authentication — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с сессиями (`Bitrix\Main\Session\Session`, `KernelSession`, `CompositeSessionManager`), action-фильтрами авторизации/CSRF или конфигурацией обработчиков сессий.
>
> Audit note: проверено по текущему core `main/lib/session/*`, `main/lib/engine/actionfilter/*`, `main/lib/authentication/policy/*`.

## Содержание
- Архитектура сессий
- `Session`: основные методы
- `KernelSession` и `KernelSessionProxy`
- `CompositeSessionManager`
- `SessionConfigurationResolver`
- Action-фильтры авторизации
- `Bitrix\Main\Authentication\Policy`
- Gotchas

---

## Архитектура сессий

В текущем core публичная D7-сессия получается через `Application::getInstance()->getSession()` и реализуется классом `Bitrix\Main\Session\Session`.

**Реальная схема выглядит так:**

```text
Application::getInstance()->getSession()
    └── Session

SessionConfigurationResolver
    ├── mode=default   -> Session + KernelSessionProxy
    └── mode=separated -> Session + KernelSession

CompositeSessionManager
    └── координирует kernel/general session и умеет regenerateId()
```

`KernelSession` не является наследником `Session` и не является singleton.

---

## `Session`: основные методы

```php
use Bitrix\Main\Application;

$session = Application::getInstance()->getSession();

// ArrayAccess
$session['cart'] = ['product_id' => 42, 'qty' => 1];
$item = $session['cart'] ?? null;
unset($session['cart']);

// Статус
$session->isActive();      // bool
$session->isAccessible();  // bool
$session->isStarted();     // bool

// ID / имя
$session->getId();         // string
$session->getName();       // обычно PHPSESSID
// setId()/setName() допустимы только до старта активной session

// Lazy start
$session->enableLazyStart();
$session->disableLazyStart();

// Явный старт / сохранение / очистка
$session->start();
$session->save();
$session->clear();
$session->destroy();

// Ротация session id
$session->regenerateId();
```

> В текущем core метод называется именно `regenerateId()`. `migrate()` не подтверждён.

---

## Полный пример

```php
use Bitrix\Main\Application;

$session = Application::getInstance()->getSession();

if ($session->isAccessible())
{
    if (!isset($session['draft_form']))
    {
        $session['draft_form'] = [];
    }

    $draft = $session['draft_form'];
    $draft['name'] = 'Иван';
    $session['draft_form'] = $draft;
}
```

---

## `KernelSession` и `KernelSessionProxy`

`KernelSession` в текущем core хранит kernel-данные через cookie-handler и используется как внутренний слой авторизации/служебной сессии.

```php
use Bitrix\Main\Session\KernelSession;

$kernelSession = new KernelSession(3600);
$kernelSession->start();

$kernelSession['my_flag'] = 'Y';
$kernelSession->save();
```

Что важно:

- в `mode=default` resolver создаёт не прямой `KernelSession`, а `KernelSessionProxy`, оборачивающий обычный `Session`
- в `mode=separated` resolver создаёт отдельный `KernelSession`
- `KernelSession::getInstance()` в текущем core не подтверждён

Не трогай kernel session без необходимости: это чувствительный слой авторизации.

---

## `CompositeSessionManager`

`CompositeSessionManager` получает две `SessionInterface`: kernel и general.

```php
use Bitrix\Main\Session\CompositeSessionManager;

$manager = new CompositeSessionManager($kernelSession, $generalSession);

$manager->start();
$manager->regenerateId();
$manager->clear();
$manager->destroy();
```

Особенность текущего core:

- `regenerateId()` вызывает ротацию kernel session всегда
- general session ротируется только если kernel session не является `KernelSessionProxy`

---

## `SessionConfigurationResolver`

Resolver читает `session` из `.settings.php` и собирает нужные обработчики.

```php
'session' => [
    'value' => [
        'mode' => 'default', // или 'separated'
        'lifetime' => 3600,
        'handlers' => [
            'general' => [
                'type' => 'file', // file, database, redis, memcache, array, null, save_handler.php.ini
            ],
        ],
    ],
],
```

Подтверждённые типы general-handler в текущем core:

- `file`
- `database`
- `redis`
- `memcache`
- `array`
- `null`
- `save_handler.php.ini`

Для `mode=separated` есть жёсткое ограничение:

```php
'session' => [
    'value' => [
        'mode' => 'separated',
        'handlers' => [
            'general' => ['type' => 'redis'],
            'kernel' => 'encrypted_cookies',
        ],
    ],
],
```

> В текущем resolver не подтверждён generic-формат вида `'type' => 'custom', 'class' => ...`. Не придумывай такой контракт без дополнительной проверки.

---

## Action-фильтры авторизации

### `ActionFilter\Authentication`

```php
use Bitrix\Main\Engine\Controller;
use Bitrix\Main\Engine\ActionFilter;

class DemoController extends Controller
{
    public function configureActions(): array
    {
        return [
            'secure' => [
                'prefilters' => [
                    new ActionFilter\Authentication(),
                ],
            ],
        ];
    }
}
```

В текущем core:

- по умолчанию фильтр отдаёт `401`
- если передать `new ActionFilter\Authentication(true)`, то для не-AJAX запроса делает `LocalRedirect(.../auth/?backurl=...)`

### `ActionFilter\Csrf`

```php
use Bitrix\Main\Engine\ActionFilter;

new ActionFilter\Csrf();
```

Используй его для AJAX/D7-controller сценариев. Для обычных форм на сайте по-прежнему нужен `bitrix_sessid_post()` и `check_bitrix_sessid()`.

---

## `Bitrix\Main\Authentication\Policy`

В текущем core namespace `Bitrix\Main\Authentication\Policy` существует, но это не интерфейс `Policy`.

Подтверждённые базовые классы:

- `Bitrix\Main\Authentication\Policy\Rule`
- `Bitrix\Main\Authentication\Policy\RulesCollection`
- `BooleanRule`, `GreaterRule`, `LesserRule`, `IpMaskRule`, `WeakPassword`

Пример работы с preset-коллекцией:

```php
use Bitrix\Main\Authentication\Policy\RulesCollection;

$policy = RulesCollection::createByPreset(RulesCollection::PRESET_MIDDLE);

$sessionTimeout = $policy->getSessionTimeout();
$values = $policy->getValues();
```

Это advanced-layer для security-policy и админских сценариев, а не обычный интерфейс “проверить авторизацию пользователя”.

---

## Gotchas

- `isAccessible()` и `isActive()` — не одно и то же: `isActive()` про факт старта, `isAccessible()` про возможность безопасно открыть session при текущих заголовках.
- После успешной авторизации или смены security-контекста используй `regenerateId()`, а не несуществующий `migrate()`.
- `KernelSession` и general `Session` могут жить раздельно; не делай вывод, что `$_SESSION` всегда отражает всё состояние авторизации.
- В separated mode kernel handler должен быть именно `'encrypted_cookies'`. Любая другая строка приведёт к `NotSupportedException`.
- Не меняй kernel session вручную без явной причины: легко сломать авторизацию и служебные флаги.
- Если нужно только проверить авторизацию в controller, почти всегда достаточно `ActionFilter\Authentication`, а не прямой работы с session internals.

---

## Source: `security.md`

# Bitrix Безопасность и модуль security — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с защитой от XSS, SQL-инъекций, CSRF, проверкой прав доступа, аутентификацией, WAF/OTP/session hardening, redirect/IP rules, antivirus, site checker или xscan.
>
> Audit note (core-verified, current project): справочник сверялся по `www/bitrix/modules/main/lib/text/htmlfilter.php`, `engine/actionfilter/{csrf,authentication}.php`, `main/tools.php`, `main/classes/general/user.php`, `iblock/classes/general/iblock.php`, а также по текущему `www/bitrix/modules/security` версии `24.0.300`, включая `include.php`, `install/index.php`, `classes/general/{filter,redirect,iprule,session,antivirus,user,site_checker,xscan}.php`, `lib/mfa/{otp,recoverycodes}.php` и стандартные `security.*` компоненты.

## Содержание
- XSS: HtmlFilter::encode(), htmlspecialchars, контекстное экранирование
- SQL-инъекции: ORM как защита, forSql() для raw SQL
- CSRF: bitrix_sessid_post(), check_bitrix_sessid(), ActionFilter\Csrf
- Текущий пользователь: CurrentUser (D7), глобальный $USER (legacy)
- Проверка прав: IsAdmin, CanDoOperation, CIBlock::GetPermission
- ActionFilter: Authentication, Csrf, HttpMethod в Controllers
- Модуль `security`: WAF filter, redirect/IP rules, antivirus, frame headers
- MFA/OTP: `Bitrix\Security\Mfa\Otp`, recovery codes, `security.user.*` компоненты
- Site checker и `xscan`
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

В текущем core у `Engine\Controller` default prefilters уже включают `Authentication + HttpMethod(GET|POST) + Csrf`. Дополнительная автоподстановка `Csrf` есть ещё и в том случае, когда ты переопределил `prefilters`, оставил POST-метод, но сам не добавил `Csrf`.

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
            // Отключить CSRF для webhook (например, внешние вызовы).
            // Важно: здесь ты заменяешь default prefilters, поэтому добавляй нужные HttpMethod/Auth явно.
            'webhook' => [
                'prefilters' => [
                    new ActionFilter\Csrf(false), // false = отключить проверку
                    new ActionFilter\HttpMethod(['POST']),
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
// НЕ используй md5/sha1 для паролей
// В текущем core хеширование делает \Bitrix\Main\Security\Password::hash()

use Bitrix\Main\Security\Password;

$hashedPassword = Password::hash($plainPassword);

// Но в прикладном коде обычно лучше не хешировать пароль вручную:
// CUser::Add / CUser::Update / ChangePassword сами используют Password::hash()
// Проверку делай через стандартные потоки авторизации, а не прямым сравнением хеша
```

---

## Когда именно нужен модуль `security`

Общий appsec-слой из `main` и реальный модуль `security` - это два разных контура.

Модуль `security` нужен, если задача звучит как:

- “включить или отладить WAF / security filter”
- “разобраться с open redirect защитой”
- “настроить OTP / mandatory OTP / recovery codes”
- “включить session hardening”
- “почему сработало IP rule”
- “проверить antivirus / site checker / xscan”

Если задача уже про это, не ограничивайся `HtmlFilter`, `check_bitrix_sessid()` и общими советами по `$USER`.

### Права и операции модуля

Инсталлятор подтверждает задачи:

- `security_denied`
- `security_filter`
- `security_otp`
- `security_view_all_settings`
- `security_full_access`

И подтверждённые операции:

- `security_filter_bypass`
- `security_edit_user_otp`
- `security_module_settings_read/write`
- `security_filter_settings_read/write`
- `security_otp_settings_read/write`
- `security_iprule_admin_settings_read/write`
- `security_session_settings_read/write`
- `security_redirect_settings_read/write`
- `security_stat_activity_settings_read/write`
- `security_iprule_settings_read/write`
- `security_antivirus_settings_read/write`
- `security_frame_settings_read/write`
- `security_file_verifier_sign/collect/verify`

Практический вывод:

- для security-admin задач обычно недостаточно просто быть авторизованным;
- проверяй либо `$APPLICATION->GetGroupRight('security')`, либо конкретные `CanDoOperation(...)`.

## WAF и `CSecurityFilter`

Подтверждён `CSecurityFilter` и его связка с `Bitrix\Security\Filter\Request/Server`.

Ключевые точки:

- `OnBeforeProlog()`
- `IsActive()`
- `SetActive($bActive = false)`
- `GetAuditTypes()`
- `OnAdminInformerInsertItems()`
- `processVar(...)`

Что важно:

- по умолчанию аудиторы WAF включают `XSS`, `SQL` и `PHP/path`;
- `SetActive(true)` регистрирует `main:OnBeforeProlog` и `main:OnEndBufferContent` для `CSecurityXSSDetect`;
- mask bypass идёт через `CSecurityFilterMask::Check(SITE_ID, $_SERVER["REQUEST_URI"])`;
- при `check_bitrix_sessid()` и праве `security_filter_bypass` ядро может пропускать фильтр.

Это значит:

- задачи “почему filter пропускает/блокирует запрос” надо разбирать через сам модульный pipeline, а не только через код контроллера.

## Redirect/IP rules/frame/antivirus

В модуле это отдельные подсистемы, а не один “security toggle”.

### `CSecurityRedirect`

Подтверждены:

- `BeforeLocalRedirect(&$url, $skip_security_check)`
- `EndBufferContent(&$content)`
- `IsActive()`
- `SetActive($bActive = false)`

Подтверждено:

- защита сидит на `main:OnBeforeLocalRedirect` и `main:OnEndBufferContent`;
- модуль проверяет referer/site/sign seed и может логировать `SECURITY_REDIRECT`;
- при плохом redirect либо отдаёт warning page, либо подменяет URL на option `security:redirect_url`.

### `CSecurityIPRule`

Подтверждены:

- `GetActiveCount()`
- `IsActive()`
- `SetActive($bActive = false, $end_time = 0)`
- `CheckAntiFile($return_message = false)`
- `OnPageStart($use_query = false)`
- `CleanUpAgent()`

Что важно:

- активная защита вешается на `main:OnPageStart`;
- disable-file (`ipcheck_disable_file`) реально выключает IP check;
- модуль нормализует URI и может увести на `security_403.php`.

### `CSecurityFrame`

Подтверждены:

- `IsActive()`
- `SetActive($bActive = false)`

`SetActive(true)` регистрирует `main:OnPageStart` -> `CSecurityFrame::SetHeader`.

### `CSecurityAntiVirus`

Подтверждены:

- `IsActive()`
- `SetActive($bActive = false)`
- `GetAuditTypes()`
- `OnPageStart()`

Что важно:

- модуль вешается сразу на три события: `OnPageStart`, `OnEndBufferContent`, `OnAfterEpilog`;
- audit type `SECURITY_VIRUS` реально пишется модулем;
- в install events отдельно заводится почтовый контур `VIRUS_DETECTED`.

## Session hardening и `CSecuritySession`

Подтверждён legacy-класс `CSecuritySession` с пометкой `@deprecated`, но он всё ещё живой в модуле.

Ключевые методы:

- `Init()`
- `CleanUpAgent()`
- `UpdateSessID()`
- `checkSessionId($id)`
- `activate()`
- `deactivate()`
- `createSid()`

Что важно:

- storage выбирается между `Virtual`, `MC`, `Redis` и `DB` handlers;
- `activate()` включает option `security:session`, регистрирует handler и GC agent;
- old session ID хранится отдельно до момента записи.

Практическое правило:

- для новых задач сначала предпочитай `\Bitrix\Main\Session\Session`;
- но если трогаешь legacy security settings или отладку session hardening, смотреть надо именно в `CSecuritySession`.

## MFA / OTP

В текущем core основной OTP-контур уже в `Bitrix\Security\Mfa\Otp`, а `CSecurityUser` отмечен как deprecated-обёртка.

### `Bitrix\Security\Mfa\Otp`

Подтверждены:

- `getByUser($userId)`
- `getByType($type)`
- `getProvisioningUri(array $opts = [])`
- `regenerate($newSecret = null)`
- `verify($input, $updateParams = true)`
- `activate()`
- `deactivate($days = 0)`
- `verifyUser(array $params)`
- `setSkipMandatoryDays($days = 2)`
- `setMandatoryUsing($isMandatory = true)`
- `isMandatoryUsing()`
- `setMandatoryRights(array $rights)`
- `getMandatoryRights()`

Что важно:

- доступны типы `hotp` и `totp`;
- mandatory OTP реально управляется через options `otp_mandatory_using`, `otp_mandatory_skip_days`, `otp_mandatory_rights`;
- provisioning URI и app secret - штатный путь для подключения устройства.

### `CSecurityUser`

Подтверждены:

- `getCachedOtp($userId)`
- `onBeforeUserLogin(&$arParams)`
- `update($arFields)`
- `onUserDelete($userId)`
- `isActive()`
- `setActive($pActive = false)`
- `OnAfterUserLogout()`

Что важно:

- при старых login forms OTP может браться из хвоста `PASSWORD`;
- `setActive(true)` регистрирует login/logout hooks и recheck-agent `Bitrix\Security\Mfa\OtpEvents::onRecheckDeactivate();`.

### Recovery codes

Подтверждён `Bitrix\Security\Mfa\RecoveryCodesTable`:

- `CODES_PER_USER = 10`
- `CODE_PATTERN = '#^[a-z0-9]{4}-[a-z0-9]{4}$#D'`
- `clearByUser($userId)`
- `regenerateCodes($userId)`
- `useCode($userId, $searchCode)`

Это значит:

- recovery codes - не произвольная логика проекта, а штатная ORM-таблица `b_sec_recovery_codes`.

## Стандартные security-компоненты

Подтверждены:

- `bitrix:security.user.otp.init`
- `bitrix:security.user.recovery.codes`
- `bitrix:security.auth.otp.mandatory`

### `security.user.otp.init`

Компонент:

- требует авторизованного пользователя;
- использует `Otp::getByUser(...)->regenerate()`;
- отдаёт `PROVISION_URI`, app secret и флаг `TWO_CODE_REQUIRED`;
- POST-ветка проверяет `check_bitrix_sessid()` и действие `otp_check_activate`.

### `security.user.recovery.codes`

Компонент:

- работает только если OTP уже активирован;
- умеет `view`, `print`, `download`;
- при отсутствии кодов может регенерировать их через `RecoveryCodesTable::regenerateCodes(...)`.

## Site checker и `xscan`

### `CSecuritySiteChecker`

Подтверждены:

- `runTestPackage($type = "", $isFirstStart = false, $isCheckRequirementsNeeded = true)`
- `addResults($results)`
- `getLastTestingInfo()`
- `clearTemporaryData()`
- `isNewTestNeeded()`
- `OnAdminInformerInsertItems()`

Что важно:

- результаты живут в ORM `SiteCheckTable`;
- модуль кеширует last check и сам решает, когда нужен новый прогон.

### `CBitrixXscan`

Подтверждён отдельный malware/static-analysis контур:

- `clean()`
- `CheckEvents()`
- `CheckAgents()`

И ORM-таблица результатов:

- `Bitrix\Security\XScanResultTable`

Практический вывод:

- задачи “просканировать ядро/проект на вредоносный код” в этом core уже имеют штатный модульный маршрут, а не только внешний grep.

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
- **`CSecurityUser` и `CSecuritySession` частично deprecated**, но в текущем core всё ещё участвуют в реальном security-flow. Не вырезай их из диагностики только потому, что рядом есть D7.
- **`security` модуль состоит из нескольких независимых подсистем**. “Включить безопасность” не равно автоматически включить filter, redirect, IP rules, antivirus и frame headers.
- **`bitrix:security.user.recovery.codes` зависит от уже активированного OTP**. Если OTP не поднят, компонент корректно вернёт модульную ошибку, а не пустой список.

---

## Composite Cache + личные данные (bx-dynamic)

### Архитектура Composite

Bitrix Composite — механизм кеширования полной страницы с выделением «динамических» (персональных) блоков:
- **Статическая часть** кешируется целиком на диск/nginx как HTML.
- **Динамические блоки** (`bx-dynamic`) вырезаются и подгружаются отдельным AJAX-запросом.
- Результат: авторизованные пользователи получают кешированную основу страницы, а персональные данные (корзина, имя, лайки) подгружаются асинхронно.

### CBitrixComponent::setFrameMode(true)

```php
// В component.php компонента-«оболочки» (статический блок)
// Включает composite-режим: компонент участвует в composite-кешировании
if ($this->startResultCache()) {
    // Весь код внутри кешируется
    $this->arResult['ITEMS'] = $this->getItems();
    $this->includeComponentTemplate();
    $this->endResultCache();
}

// Включить frame-режим (composite) для компонента
$this->setFrameMode(true);
// После этого компонент получит <div id="bx_..."> обёртку
// которую composite-движок умеет вырезать и подставлять
```

### Правильный паттерн: оболочка + динамический блок

```php
// template.php статического компонента (каталог, список новостей)
// Весь шаблон кешируется. Внутри — вызов персонального компонента:

/** @var CBitrixComponentTemplate $this */
/** @var array $arResult */

// Подключить "личный" компонент как динамический блок
// APPLICATION->IncludeComponent с setFrameMode обеспечивает bx-dynamic
$APPLICATION->IncludeComponent(
    'vendor:user.cart.mini',   // персональный компонент (корзина, избранное, etc.)
    '',
    [
        'CACHE_TYPE' => 'N',   // НИКОГДА не кешировать персональный компонент
    ],
    $component,                // родительский компонент
    ['HIDE_ICONS' => 'Y']      // параметры для dynamic-блока
);
```

```php
// component.php персонального компонента (bx-dynamic блок)
// Этот компонент НЕ должен использовать кеш — он всегда персональный

global $USER;

// Включить режим dynamic-frame (компонент будет подгружаться через AJAX)
$this->setFrameMode(true);

// Получить персональные данные
$this->arResult['USER_ID']    = is_object($USER) ? (int)$USER->GetID() : 0;
$this->arResult['CART_COUNT'] = $this->getCartCount($this->arResult['USER_ID']);
$this->arResult['USER_NAME']  = is_object($USER) ? $USER->GetFirstName() : '';

// Без кеша — данные всегда актуальные
$this->includeComponentTemplate();
```

### CCompositeHelper::Init()

```php
// CCompositeHelper::Init() вызывается ядром автоматически при загрузке страницы
// Что он делает:
// 1. Определяет, включён ли composite для текущего сайта (настройки в /bitrix/admin/)
// 2. Проверяет, подходит ли страница для composite (не POST, не ajax, нет ?clear_cache=Y)
// 3. Если страница в кеше — отдаёт HTML из кеша немедленно, без выполнения PHP
// 4. Если не в кеше — запускает обычный цикл выполнения и сохраняет результат

// Явная инициализация (редко нужна — обычно делается ядром автоматически):
\CCompositeHelper::Init([
    'CACHE_TIME' => 3600,         // TTL кеша в секундах
    'CACHE_TYPE' => 'A',          // A = авто, N = не кешировать, Y = всегда
]);

// Проверить, работает ли composite сейчас
$isComposite = \CCompositeHelper::IsEnabled(); // bool
```

### setFrameMode + SetCacheProperty

```php
// setFrameMode(true) без SetCacheProperty не даёт эффекта в шаблоне!
// Нужно явно объявить какие свойства arResult участвуют в кеше

// В component.php:
$this->setFrameMode(true);

// Кешировать только эти ключи arResult (остальные будут переданы в dynamic-режим)
$frame = $this->createFrame()->begin(); // создать frame-объект

$this->arResult['CACHED_DATA'] = $this->getCachedData();   // кешируется
$this->arResult['USER_SPECIFIC'] = null;                    // не кешируется — заполнится dynamic

$frame->end(); // закрыть frame — всё что внутри begin/end кешируется
$this->includeComponentTemplate();
```

### JS: BX.message / BX.userOptions для персональных данных

```javascript
// Передать персональные данные в JS без пробива кеша (в шаблоне компонента)
// BX.message() — глобальный JS-словарь, заполняется через PHP

// В PHP шаблоне dynamic-компонента (не кешируется):
?>
<script>
BX.message({
    'USER_ID':    <?= (int)$arResult['USER_ID'] ?>,
    'USER_NAME':  '<?= CUtil::JSEscape($arResult['USER_NAME']) ?>',
    'CART_COUNT': <?= (int)$arResult['CART_COUNT'] ?>,
});
</script>
<?php

// В JS-коде:
// Получить данные
const userId    = BX.message('USER_ID');
const cartCount = BX.message('CART_COUNT');

// BX.userOptions — хранение пользовательских настроек (persistentные)
// Сохранить настройку
BX.userOptions.save('mymodule', 'sidebar_open', 'Y');

// Получить настройку
const sidebarState = BX.userOptions.get('mymodule', 'sidebar_open', 'N'); // 'N' — default
```

### CSP-заголовки: добавление через Response

```php
use Bitrix\Main\Application;

$response = Application::getInstance()->getResponse();

// Добавить заголовок Content-Security-Policy
$response->addHeader(
    'Content-Security-Policy',
    "default-src 'self'; " .
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.bitrix24.com; " .
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " .
    "img-src 'self' data: https:; " .
    "font-src 'self' https://fonts.gstatic.com; " .
    "connect-src 'self' wss: https:; " .  // wss: для WebSocket (Push&Pull)
    "frame-ancestors 'self'; " .
    "base-uri 'self'"
);

// Добавить X-Frame-Options (защита от clickjacking)
$response->addHeader('X-Frame-Options', 'SAMEORIGIN');

// Добавить X-Content-Type-Options (защита от MIME-sniffing)
$response->addHeader('X-Content-Type-Options', 'nosniff');

// Referrer-Policy
$response->addHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
```

### Типичная CSP-политика для Bitrix-сайта

```
Content-Security-Policy:
  default-src 'self';
  script-src  'self' 'unsafe-inline' 'unsafe-eval'
              https://api-maps.yandex.ru
              https://mc.yandex.ru
              https://www.googletagmanager.com
              https://www.google-analytics.com;
  style-src   'self' 'unsafe-inline'
              https://fonts.googleapis.com;
  img-src     'self' data: blob:
              https://mc.yandex.ru
              https://www.google-analytics.com;
  font-src    'self' data:
              https://fonts.gstatic.com;
  connect-src 'self' wss: https:;
  frame-src   'self' https://www.youtube.com https://vk.com;
  frame-ancestors 'self';
  base-uri    'self';
  form-action 'self';
```

> `'unsafe-inline'` и `'unsafe-eval'` обязательны для Bitrix — ядро и большинство компонентов используют inline-скрипты. Убрать их можно только при полном отказе от стандартных компонентов.

### Gotchas Composite + CSP

- **Composite не работает для авторизованных пользователей без dynamic-блоков**: если на странице есть персональные данные прямо в кешируемом шаблоне (имя пользователя, корзина) — composite либо отключится автоматически, либо покажет чужие данные. Выноси всё персональное в отдельный компонент с `setFrameMode(true)` и `CACHE_TYPE = 'N'`.
- **`setFrameMode(true)` без `$this->createFrame()->begin()/end()`** не разделяет кешируемую и динамическую части — весь компонент уйдёт в dynamic (то есть никакого кеша не будет). Оборачивай кешируемую часть в `begin/end`.
- **`$APPLICATION->IncludeComponent()` внутри кешируемого шаблона** — dynamic-подкомпонент корректно выделяется только если вызов находится внутри уже запущенного composite-frame. Вне frame вызов выполнится синхронно без dynamic-механики.
- **Не добавляй заголовки после вывода**: `$response->addHeader()` нужно вызывать до любого вывода (`echo`, `?>`). После начала вывода в composite-режиме заголовки могут не примениться.
- **CSP `connect-src`** должен включать `wss:` (WebSocket) если используется Push&Pull — иначе браузер заблокирует WebSocket-соединение.
- **`BX.message()`** сбрасывается при каждой загрузке страницы. Для persistentного хранения используй `BX.userOptions` (сохраняет на сервере в `b_user_option`) или `localStorage`.
- **Composite и AJAX-компоненты**: компонент вызванный через `$APPLICATION->IncludeComponent()` внутри `bitrix:ajax.updater` не участвует в composite — это разные механизмы. Не смешивай их.

---

## Source: `socialservices.md`

# Соц-авторизация и внешние провайдеры (модуль socialservices)

> Audit note: ниже сверено с текущим `www/bitrix/modules/socialservices`. Подтверждены `CSocServAuthManager`, базовый `CSocServAuth`, провайдеры `CSocServFacebook`, `CSocServGoogleOAuth`, `CSocServVKontakte`, `CSocServYandexAuth`, `CSocServApple`, `CSocServZoom` и др., D7-таблицы `\Bitrix\Socialservices\UserTable`, `UserLinkTable`, controller `\Bitrix\Socialservices\Controller\AuthFlow`, а также `\Bitrix\Socialservices\OAuth\StateService`. Подтверждены компоненты `bitrix:socserv.auth.form`, `bitrix:socserv.auth.split`, `bitrix:socserv.contacts`.

## Архитектура

Текущий core делит модуль на три слоя:

- `CSocServAuthManager` и `CSocServAuth` — orchestration и legacy-интеграция с авторизацией
- provider-классы `CSocServ*` — конкретные OAuth/OpenID провайдеры
- D7-слой для controller/state/storage: `AuthFlow`, `StateService`, `UserTable`, `UserLinkTable`

---

## CSocServAuthManager

Подтверждены методы:

- `GetAuthServices`
- `GetActiveAuthServices`
- `GetSettings`
- `Authorize`
- `SetUniqueKey`

```php
use Bitrix\Main\Loader;

Loader::includeModule('socialservices');

$manager = new CSocServAuthManager();
$services = $manager->GetActiveAuthServices([
    'BACKURL' => '/',
]);

foreach ($services as $service) {
    // обычно объект провайдера, совместимый с CSocServAuth
}
```

Если задача связана с кнопками входа на сайте, первым делом проверяй:

1. `CSocServAuthManager`
2. стандартные компоненты `socserv.auth.form` / `socserv.auth.split`
3. конкретный provider-класс

---

## Провайдеры

В текущем core подтверждены провайдеры с методами `getUrl`, `Authorize`, `GetAuthUrl`, например:

- `CSocServGoogleOAuth`
- `CSocServVKontakte`
- `CSocServFacebook`
- `CSocServYandexAuth`
- `CSocServApple`
- `CSocServZoom`

Практическое правило:

- не строй OAuth URL вручную, если у провайдера уже есть `getUrl`/`GetAuthUrl`
- callback и обмен токеном веди через штатный provider-класс, иначе легко сломать state/redirect flow

---

## D7: storage и flow

Подтверждены:

- `\Bitrix\Socialservices\UserTable`
- `\Bitrix\Socialservices\UserLinkTable`
- `\Bitrix\Socialservices\Controller\AuthFlow`
- `\Bitrix\Socialservices\OAuth\StateService`

```php
use Bitrix\Main\Loader;
use Bitrix\Socialservices\OAuth\StateService;
use Bitrix\Socialservices\UserLinkTable;

Loader::includeModule('socialservices');

$state = StateService::getInstance()->createState([
    'site_id' => SITE_ID,
    'backurl' => '/',
]);

$links = UserLinkTable::getList([
    'select' => ['ID', 'USER_ID', 'LINKED'],
    'order' => ['ID' => 'DESC'],
    'limit' => 20,
]);
```

`AuthFlow` в текущем core подтверждён как `Main\Engine\Controller`; у него уже есть отдельный маршрут `signInAppleAction()` с ослабленными prefilters по CSRF/Auth.

---

## Стандартные компоненты

Подтверждены:

- `bitrix:socserv.auth.form`
- `bitrix:socserv.auth.split`
- `bitrix:socserv.contacts`

Обычный порядок работы:

1. проверить настройки провайдера
2. открыть контракт стандартного компонента
3. только потом делать кастомный шаблон или свой controller

---

## Gotchas

- Не смешивай `socialservices` с `socialnet`: это разные контуры. В текущей фазе `socialservices` активен, `socialnet` всё ещё deferred.
- Если авторизация “иногда ломается”, почти всегда смотри `state`, redirect URI и связку `UserLinkTable`/provider settings раньше, чем шаблон кнопки.
- Не хардкодь URL callback, если провайдер уже умеет собрать его сам.
