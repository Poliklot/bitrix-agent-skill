# Bitrix REST API — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с регистрацией REST-методов, событиями REST, Webhook, интеграциями через REST API или внешними вызовами Bitrix24 REST.

## Содержание
- Регистрация REST-методов через OnRestServiceBuildDescription
- Сигнатура callback-функции, CRestServer, пагинация
- RestException — обработка ошибок
- REST-события (webhook-like outbound events)
- CRestUtil константы: GLOBAL_SCOPE, EVENTS, PLACEMENTS
- Вызов внешнего REST API через HttpClient (OAuth)
- Gotchas

---

## Регистрация REST-методов

REST-методы регистрируются через событие `OnRestServiceBuildDescription` модуля `rest`.

### Регистрация в include.php модуля

```php
// local/modules/my.module/include.php
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandler(
    'rest',
    'OnRestServiceBuildDescription',
    ['\\MyVendor\\MyModule\\RestService', 'onBuildDescription']
);
```

### Структура описания методов

```php
namespace MyVendor\MyModule;

use Bitrix\Rest\RestException;
use CRestServer;
use CRestUtil;

class RestService
{
    public static function onBuildDescription(): array
    {
        return [
            // scope — группа методов; используется для OAuth-разрешений
            'my_scope' => [
                'my.item.list'   => [__CLASS__, 'itemList'],
                'my.item.get'    => [__CLASS__, 'itemGet'],
                'my.item.add'    => [__CLASS__, 'itemAdd'],
                'my.item.update' => [__CLASS__, 'itemUpdate'],
                'my.item.delete' => [__CLASS__, 'itemDelete'],
            ],
            // GLOBAL_SCOPE — методы доступны в любом scope (без OAuth-ограничений по scope)
            CRestUtil::GLOBAL_SCOPE => [
                'my.server.time' => [__CLASS__, 'serverTime'],
            ],
        ];
    }
}
```

---

## Сигнатура callback-функции

Каждый callback вызывается с тремя параметрами:

```php
/**
 * @param array      $params  — параметры запроса (из GET/POST)
 * @param int        $start   — смещение для пагинации (значение параметра 'start')
 * @param CRestServer $server — объект сервера, даёт доступ к auth, scope, методу
 */
public static function itemList(array $params, int $start, CRestServer $server): array
{
    // Получить данные о приложении / пользователе из auth
    $auth = $server->getAuth();
    // $auth['user_id']   — ID пользователя Bitrix, сделавшего запрос
    // $auth['client_id'] — CLIENT_ID OAuth-приложения
    // $auth['scope']     — строка через запятую: 'crm,tasks,my_scope'
    // $auth['domain']    — домен портала (только Bitrix24)

    $userId = (int)($auth['user_id'] ?? 0);

    // Пагинация: стандарт Bitrix REST — 50 элементов на страницу
    $limit = 50;

    $items = [];
    $total = 0;
    // ... логика получения данных с учётом $start и $limit ...

    $result = ['items' => $items, 'total' => $total];

    // Если есть следующая страница — добавь 'next'
    if ($start + $limit < $total) {
        $result['next'] = $start + $limit;
    }

    return $result;
    // Движок оборачивает в {"result": ..., "next": ..., "total": ...}
}
```

### Получение одного элемента

```php
public static function itemGet(array $params, int $start, CRestServer $server): array
{
    $id = (int)($params['ID'] ?? 0);
    if ($id <= 0) {
        throw new RestException(
            'ID обязателен',
            RestException::ERROR_ARGUMENT,
            \CRestServer::STATUS_WRONG_REQUEST
        );
    }

    $row = MyItemTable::getById($id)->fetch();
    if (!$row) {
        throw new RestException(
            'Элемент не найден',
            RestException::ERROR_NOT_FOUND,
            \CRestServer::STATUS_NOT_FOUND
        );
    }

    return $row;
    // Движок оборачивает в {"result": {...}}
}
```

### Создание элемента

```php
public static function itemAdd(array $params, int $start, CRestServer $server): array
{
    $auth   = $server->getAuth();
    $userId = (int)($auth['user_id'] ?? 0);

    $addResult = MyItemTable::add([
        'TITLE'       => $params['TITLE'] ?? '',
        'CREATED_BY'  => $userId,
    ]);

    if (!$addResult->isSuccess()) {
        throw new RestException(
            implode(', ', $addResult->getErrorMessages()),
            RestException::ERROR_CORE,
            \CRestServer::STATUS_INTERNAL
        );
    }

    return ['ID' => $addResult->getId()];
}
```

---

## RestException — обработка ошибок

```php
use Bitrix\Rest\RestException;

// Конструктор: (message, errorCode, httpStatus)
throw new RestException('Текст ошибки', RestException::ERROR_ARGUMENT, \CRestServer::STATUS_WRONG_REQUEST);

// Константы кодов ошибок
RestException::ERROR_ARGUMENT         // некорректный аргумент
RestException::ERROR_NOT_FOUND        // элемент не найден
RestException::ERROR_CORE             // внутренняя ошибка
RestException::ERROR_OAUTH            // ошибка авторизации
RestException::ERROR_METHOD_NOT_FOUND // метод не найден

// HTTP-статусы (из CRestServer)
\CRestServer::STATUS_OK               // '200 OK'
\CRestServer::STATUS_WRONG_REQUEST    // '400 Bad Request'
\CRestServer::STATUS_UNAUTHORIZED     // '401 Unauthorized'
\CRestServer::STATUS_FORBIDDEN        // '403 Forbidden'
\CRestServer::STATUS_NOT_FOUND        // '404 Not Found'
\CRestServer::STATUS_INTERNAL         // '500 Internal Server Error'
```

Ответ при исключении:
```json
{
  "error": "ERROR_NOT_FOUND",
  "error_description": "Элемент не найден"
}
```

---

## REST-события (исходящие, webhook-like)

REST-события позволяют уведомлять внешние приложения об изменениях в системе.
Приложения подписываются через `event.bind`, ядро отправляет POST на их URL.

### Регистрация исходящего события в описании методов

```php
use CRestUtil;

public static function onBuildDescription(): array
{
    return [
        'my_scope' => [
            'my.item.list' => [__CLASS__, 'itemList'],

            // _events — исходящие события этого scope
            CRestUtil::EVENTS => [
                // 'ИмяСобытияДляPRISTи' => ['module_id', 'bitrix_event', [callback], $options]
                'OnMyItemAdd' => [
                    'my.module',          // ID модуля — откуда событие
                    'OnAfterMyItemAdd',   // имя события в EventManager Bitrix
                    [__CLASS__, 'onItemAddHandler'],
                    [
                        'sendAuth' => true,   // слать ли данные авторизации в payload
                    ],
                ],
                'OnMyItemUpdate' => [
                    'my.module',
                    'OnAfterMyItemUpdate',
                    [__CLASS__, 'onItemUpdateHandler'],
                ],
                'OnMyItemDelete' => [
                    'my.module',
                    'OnAfterMyItemDelete',
                    [__CLASS__, 'onItemDeleteHandler'],
                ],
            ],
        ],
    ];
}

// Обработчик события — формирует payload для отправки
// Возвращает массив данных, который будет отправлен на URL приложения
public static function onItemAddHandler(\Bitrix\Main\Event $event): array
{
    $fields = $event->getParameter('fields');
    return [
        'data' => [
            'FIELDS' => [
                'ID' => $fields['ID'] ?? null,
            ],
        ],
    ];
}
```

---

## CRestUtil — важные константы

```php
use CRestUtil;

CRestUtil::GLOBAL_SCOPE   // '_global'  — методы видны без привязки к scope
CRestUtil::EVENTS         // '_events'  — ключ для исходящих событий в описании
CRestUtil::PLACEMENTS     // '_placements' — ключ для виджетов/встраиваний
CRestUtil::BATCH_MAX_LENGTH  // 50 — максимум команд в batch-запросе
CRestUtil::METHOD_DOWNLOAD   // 'download' — специальный тип метода для скачивания
CRestUtil::METHOD_UPLOAD     // 'upload'   — специальный тип метода для загрузки
```

---

## Incoming Webhook — простейший вызов без OAuth

Входящий вебхук — URL вида `/rest/{userId}/{token}/` — готовый endpoint без OAuth.

```php
// Создаётся в интерфейсе: Настройки → Разработчикам → Входящий вебхук
// URL: https://my.bitrix24.ru/rest/1/abc123xyz/

// Вызов через curl (PHP):
$url = 'https://my.bitrix24.ru/rest/1/abc123xyz/crm.contact.list';
$params = ['filter' => ['TYPE_ID' => 'PERSON'], 'select' => ['ID', 'NAME']];

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($params));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = json_decode(curl_exec($ch), true);
curl_close($ch);
```

---

## Вызов внешнего REST API через HttpClient (OAuth)

Для вызова внешнего Bitrix24 через OAuth используй `HttpClient`.

```php
use Bitrix\Main\Web\HttpClient;
use Bitrix\Main\Web\Json;

// OAuth-токен хранится в приложении (app.option) или получается через OAuth flow
$accessToken = \Bitrix\Rest\AppTable::getAccessToken($appId);
$domain      = 'my.bitrix24.ru';

$http = new HttpClient();
$http->setHeader('Content-Type', 'application/json');

// GET-запрос
$http->get("https://{$domain}/rest/crm.contact.list?auth={$accessToken}");
$result = Json::decode($http->getResult());

// POST-запрос
$http->post(
    "https://{$domain}/rest/crm.contact.add",
    Json::encode([
        'auth'   => $accessToken,
        'fields' => ['NAME' => 'Иван', 'LAST_NAME' => 'Иванов'],
    ])
);
$result = Json::decode($http->getResult());

if (!empty($result['error'])) {
    // Ошибка: $result['error'], $result['error_description']
}
$contactId = $result['result'] ?? null;
```

### Обновление OAuth токена

```php
use Bitrix\Main\Web\HttpClient;
use Bitrix\Main\Web\Json;

// При ошибке 'expired_token' — обновить через refresh_token
$http = new HttpClient();
$http->post('https://oauth.bitrix.info/oauth/token/', [
    'grant_type'    => 'refresh_token',
    'client_id'     => $clientId,
    'client_secret' => $clientSecret,
    'refresh_token' => $refreshToken,
]);
$tokenData = Json::decode($http->getResult());
// $tokenData['access_token'], $tokenData['refresh_token'], $tokenData['expires_in']
```

---

## Полный пример: модуль с REST-методами

```php
// local/modules/my.module/include.php
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandler(
    'rest',
    'OnRestServiceBuildDescription',
    ['\\MyVendor\\MyModule\\RestService', 'onBuildDescription']
);

// local/modules/my.module/lib/RestService.php
namespace MyVendor\MyModule;

use Bitrix\Rest\RestException;
use CRestServer;
use CRestUtil;

class RestService
{
    public static function onBuildDescription(): array
    {
        return [
            'mymodule' => [
                'mymodule.item.list'   => [__CLASS__, 'itemList'],
                'mymodule.item.get'    => [__CLASS__, 'itemGet'],
                'mymodule.item.add'    => [__CLASS__, 'itemAdd'],
                'mymodule.item.update' => [__CLASS__, 'itemUpdate'],
                'mymodule.item.delete' => [__CLASS__, 'itemDelete'],

                CRestUtil::EVENTS => [
                    'OnMyModuleItemAdd' => [
                        'my.module',
                        'OnAfterItemAdd',
                        [__CLASS__, 'onItemAdd'],
                    ],
                ],
            ],
        ];
    }

    public static function itemList(array $params, int $start, CRestServer $server): array
    {
        $limit  = 50;
        $filter = [];

        if (!empty($params['FILTER']) && is_array($params['FILTER'])) {
            $filter = $params['FILTER'];
        }

        $dbResult = MyItemTable::getList([
            'filter' => $filter,
            'limit'  => $limit,
            'offset' => $start,
            'count_total' => true,
        ]);

        $total = $dbResult->getCount();
        $items = $dbResult->fetchAll();

        $result = ['items' => $items, 'total' => $total];
        if ($start + $limit < $total) {
            $result['next'] = $start + $limit;
        }

        return $result;
    }

    public static function itemGet(array $params, int $start, CRestServer $server): array
    {
        $id = (int)($params['ID'] ?? 0);
        if ($id <= 0) {
            throw new RestException('ID обязателен', RestException::ERROR_ARGUMENT, \CRestServer::STATUS_WRONG_REQUEST);
        }

        $row = MyItemTable::getById($id)->fetch();
        if (!$row) {
            throw new RestException('Не найдено', RestException::ERROR_NOT_FOUND, \CRestServer::STATUS_NOT_FOUND);
        }

        return $row;
    }

    public static function itemAdd(array $params, int $start, CRestServer $server): array
    {
        $auth   = $server->getAuth();
        $userId = (int)($auth['user_id'] ?? 0);

        $r = MyItemTable::add(['TITLE' => $params['TITLE'] ?? '', 'CREATED_BY' => $userId]);
        if (!$r->isSuccess()) {
            throw new RestException(implode(', ', $r->getErrorMessages()), RestException::ERROR_CORE, \CRestServer::STATUS_INTERNAL);
        }

        return ['ID' => $r->getId()];
    }

    public static function itemUpdate(array $params, int $start, CRestServer $server): array
    {
        $id = (int)($params['ID'] ?? 0);
        if ($id <= 0) {
            throw new RestException('ID обязателен', RestException::ERROR_ARGUMENT, \CRestServer::STATUS_WRONG_REQUEST);
        }

        $fields = $params['FIELDS'] ?? [];
        unset($fields['ID'], $fields['CREATED_BY']);

        $r = MyItemTable::update($id, $fields);
        if (!$r->isSuccess()) {
            throw new RestException(implode(', ', $r->getErrorMessages()), RestException::ERROR_CORE, \CRestServer::STATUS_INTERNAL);
        }

        return true;
    }

    public static function itemDelete(array $params, int $start, CRestServer $server): array
    {
        $id = (int)($params['ID'] ?? 0);
        if ($id <= 0) {
            throw new RestException('ID обязателен', RestException::ERROR_ARGUMENT, \CRestServer::STATUS_WRONG_REQUEST);
        }

        $r = MyItemTable::delete($id);
        if (!$r->isSuccess()) {
            throw new RestException(implode(', ', $r->getErrorMessages()), RestException::ERROR_CORE, \CRestServer::STATUS_INTERNAL);
        }

        return true;
    }

    public static function onItemAdd(\Bitrix\Main\Event $event): array
    {
        $fields = $event->getParameter('fields');
        return ['data' => ['FIELDS' => ['ID' => $fields['ID'] ?? null]]];
    }
}
```

---

## Gotchas

- **Callback вызывается с `($params, $start, $server)`** — не `($query, $server)`. Третий аргумент — `CRestServer`, не `CRestUtil`.
- **Пагинация: `next` и `total`** должны быть в корне возвращаемого массива. Движок извлекает их из `result` и поднимает на уровень выше в JSON: `{"result":{"items":[...]}, "next":50, "total":143}`.
- **`CRestUtil::GLOBAL_SCOPE`** методы видны всем приложениям независимо от scope OAuth-токена — не клади туда методы с доступом к данным пользователя.
- **`$server->getAuth()['user_id']`** — ID пользователя, который совершает REST-вызов. В Bitrix CMS это может быть 0 для вебхуков без привязки к пользователю.
- **Событие `OnRestServiceBuildDescription`** собирается при каждом REST-запросе — держи handler лёгким, не делай запросы в БД внутри `onBuildDescription()`.
- **`CRestUtil::EVENTS` ключ `_events`** — исходящие события регистрируются только если приложение вызвало `event.bind`. Просто добавить в описание недостаточно — нужна подписка со стороны приложения.
- **HttpClient для внешних вызовов** — не используй `file_get_contents` с контекстом или `curl` напрямую в D7-коде; используй `Bitrix\Main\Web\HttpClient` (поддерживает proxy, timeout, SSL).
- **AccessException vs RestException** — `AccessException` (403) для ошибок прав, `RestException` для всего остального.
