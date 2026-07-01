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

## Composite Cache + личные данные

Для полного маршрута по `setFrameMode`, `createFrame`, `/bitrix/html_pages/`, `X-Bitrix-Composite`, очистке и диагностике открывай [composite-cache.md](composite-cache.md). В security-контексте главное правило: **персональные данные нельзя замораживать в static HTML**.

### Что опасно в composite

Composite cache хранит финальный HTML страницы. Если в static HTML попали `USER_ID`, имя, email, корзина, персональная цена, регион, session token или custom CSRF hidden field, этот фрагмент может быть показан другому пользователю или останется устаревшим до очистки HTML-кеша.

Не путай механизмы:

- `$this->setFrameMode(true)` — шаблон компонента голосует “за” совместимость с composite и считается адаптированным;
- `COMPOSITE_FRAME_MODE/TYPE` + `AutomaticArea` могут автоматически вынести неадаптированный first-level component в dynamic area;
- `$this->createFrame(...)->begin()/end()` — создаёт manual dynamic area;
- `CACHE_TYPE=N` у персонального компонента защищает component result cache, но не создаёт dynamic boundary само по себе.

### Паттерн персонального блока

```php
<?php
/** @var CBitrixComponentTemplate $this */
$this->setFrameMode(true);

$frame = $this->createFrame('header-user-block')->begin('');
?>
<?php if ($arResult['USER_ID'] > 0): ?>
    <a href="/personal/">
        <?= htmlspecialcharsbx($arResult['USER_NAME']) ?>
    </a>
<?php else: ?>
    <a href="/auth/">Войти</a>
<?php endif ?>
<?php $frame->end(); ?>
```

Для компонента, который отдаёт персональные данные, ставь `CACHE_TYPE = 'N'` либо делай строго персональный cache key и документируй причину. Для маленьких header/cart/profile блоков предпочтительнее dynamic area + no component cache.

### CSRF и формы

Стандартные Bitrix helpers (`bitrix_sessid_post`, component action filters, `check_bitrix_sessid`) учитывают composite лучше, чем самодельные hidden fields. В `main` 26.150.0 `Engine::replaceSessid()` очищает value стандартного `bitrix_sessid_post()` в static HTML. Если форма кастомная:

1. не записывай session-derived token в static HTML;
2. проверяй DOM после composite dynamic update;
3. проверяй submit без composite (`?ncc=1`) и с composite;
4. для AJAX используй `bitrix_sessid()`/заголовок `X-Bitrix-Csrf-Token` по проектному контракту.

### JS и персональные данные

`BX.message()` можно использовать для runtime-передачи значений, но не считай его persistent storage. Для пользовательских настроек используй `BX.userOptions` или проектный endpoint. Если значение зависит от пользователя/сессии, оно должно попадать в JS из dynamic area или через отдельный безопасный запрос, а не из общего cached `<script>`.

### Security checklist

- Проверить guest, user A, user B: static HTML не содержит чужих данных.
- Проверить `?ncc=1` и обычный URL: различия должны быть только в ожидаемых dynamic blocks.
- Проверить `X-Bitrix-Composite` и composite AJAX-hit.
- Проверить, что custom CSRF/session fields не заморожены.
- При обнаружении утечки: немедленно отключить/очистить composite для затронутых страниц, исправить frame boundary, затем повторить second request/cache pass.

### Gotchas Composite + безопасность

- Не называй `setFrameMode(true)` dynamic-frame: сам по себе он не выносит HTML в dynamic area.
- `createFrame()` не исправит персональный `StartResultCache()` с общим ключом.
- Dynamic areas нельзя вкладывать друг в друга; `StaticArea::startDynamicArea()` не стартует новую область при уже текущей dynamic area.
- Условный CSS/JS/head по пользователю вызывает перезапись composite или утечку состояния; выноси в JS/dynamic.
- Компонент в `bitrix:ajax.updater` и composite dynamic area — разные механизмы; не смешивай их без проверки.

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

- **Не добавляй заголовки после вывода**: `$response->addHeader()` нужно вызывать до любого вывода (`echo`, `?>`). После начала вывода в composite-режиме заголовки могут не примениться.
- **CSP `connect-src`** должен включать `wss:` (WebSocket), если используется Push&Pull — иначе браузер заблокирует WebSocket-соединение.
- **Dynamic area может вставить новый DOM/inline script после загрузки страницы**: проверяй CSP violations в браузере после composite AJAX-hit, а не только первичный HTML.
- **`BX.message()`** сбрасывается при каждой загрузке страницы. Для persistentного хранения используй `BX.userOptions` или `localStorage`; персональные значения отдавай из dynamic area или отдельного endpoint-а.
- **Composite и AJAX-компоненты**: компонент, вызванный через `bitrix:ajax.updater`, и composite dynamic area — разные механизмы. Не смешивай их без проверки headers/DOM.
