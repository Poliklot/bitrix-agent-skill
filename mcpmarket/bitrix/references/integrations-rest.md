# Integrations Rest
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `rest.md`

# Bitrix REST API — core-first справочник

> Reference для Bitrix-скилла. Загружай, когда задача связана с `rest`, `OnRestServiceBuildDescription`, `CRestServer`, исходящими REST-событиями, `event.bind`, placement'ами или серверной регистрацией REST-методов. Для shop-core sale/catalog REST controllers, webhooks/events/placements and `webservice`/SOAP integration extras сначала открывай `shop-integrations-webservice.md`.

## Область применимости новых контрактов

K21–K38 и K40 ниже — внешнее REST API и приложения **Битрикс24** по официальной документации, не подтверждение наличия этих возможностей в любом 1С-Битрикс: Управление сайтом. Сначала установи продукт, модуль, версию REST, способ авторизации и доступность метода. Не переноси облачные ограничения, BX24.js или REST 3.0 на локальное CMS-ядро автоматически. Исторический core-аудит ниже не распространяется на новые documentation-backed дополнения.

## Что подтверждено в текущем core

- Точка входа методов собирается через событие `rest:OnRestServiceBuildDescription`.
- Описание сервисов агрегирует `CRestProvider::getDescription()`.
- Базовый сервер запросов — `CRestServer` из `www/bitrix/modules/rest/classes/general/rest.php`.
- Специальные ключи описания:
  - `CRestUtil::GLOBAL_SCOPE` = `_global`
  - `CRestUtil::EVENTS` = `_events`
  - `CRestUtil::PLACEMENTS` = `_placements`
- Исключения REST — `Bitrix\Rest\RestException`.

---

## Регистрация методов

```php
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandler(
    'rest',
    'OnRestServiceBuildDescription',
    ['\\MyVendor\\MyModule\\RestService', 'onBuildDescription']
);
```

Для постоянной регистрации в install-логике модуля тоже допустим `registerEventHandler(...)`.

---

## Формат описания

```php
use CRestUtil;

class RestService
{
    public static function onBuildDescription(): array
    {
        return [
            'my_scope' => [
                'my.item.list' => [__CLASS__, 'itemList'],
                'my.item.get' => [
                    'callback' => [__CLASS__, 'itemGet'],
                    'options' => [],
                ],
                CRestUtil::EVENTS => [
                    'OnMyItemAdd' => [
                        'my.module',
                        'OnAfterMyItemAdd',
                        [__CLASS__, 'onItemAdd'],
                        [
                            'sendAuth' => true,
                        ],
                    ],
                ],
                CRestUtil::PLACEMENTS => [
                    'MY_WIDGET' => [
                        'private' => true,
                    ],
                ],
            ],
            CRestUtil::GLOBAL_SCOPE => [
                'my.server.time' => [__CLASS__, 'serverTime'],
            ],
        ];
    }
}
```

### Что важно про сборку описания

- `CRestProvider` делает `array_merge_recursive(...)` для всех обработчиков `OnRestServiceBuildDescription`.
- Имена методов и scope затем приводятся к нижнему регистру.
- Ключи внутри `_events` и `_placements` приводятся к верхнему регистру.

---

## Сигнатура callback

Текущий core вызывает callback так:

```php
public static function itemList(array $query, int $start, \CRestServer $server): array
{
    $authData = $server->getAuthData();
    $userId = (int)($authData['user_id'] ?? 0);
    $clientId = (string)($authData['client_id'] ?? '');

    $items = [];
    $total = 0;

    return [
        'items' => $items,
        'total' => $total,
    ];
}
```

### Поведение `CRestServer::processCall()`

- параметр `start` берётся из `$query['start']`, затем удаляется из входного массива;
- callback получает `($query, $start, $server)`;
- если callback вернул массив с `next` и `total`, сервер выносит их на верхний уровень ответа;
- итоговый успешный JSON строится как `['result' => ..., 'next' => ..., 'total' => ...]`.

---

## `CRestServer`: что брать откуда

```php
$server->getAuthData();   // полные auth-данные провайдера
$server->getAuthScope();  // scope из authData['scope']
$server->getClientId();   // CLIENT_ID приложения
$server->getMethod();     // текущее REST-имя метода
$server->getScope();      // найденный scope текущего метода
$server->setStatus(\CRestServer::STATUS_CREATED);
```

### Важная разница: `getAuth()` vs `getAuthData()`

- `getAuthData()` — основной источник auth-метаданных (`user_id`, `client_id`, `scope`, `auth_connector`, `parameters` и т.д.).
- `getAuth()` не равен полному auth payload; туда попадают только параметры, которые auth-провайдер вынес из входного query через `parameters_clear`.

Если нужен `user_id`, в текущем core безопаснее брать его из `getAuthData()`, а не из `getAuth()`.

---

## Ошибки

```php
use Bitrix\Rest\RestException;

throw new RestException(
    'ID обязателен',
    RestException::ERROR_ARGUMENT,
    \CRestServer::STATUS_WRONG_REQUEST
);
```

Подтверждённые коды в core:

- `ERROR_ARGUMENT`
- `ERROR_NOT_FOUND`
- `ERROR_CORE`
- `ERROR_OAUTH`
- `ERROR_METHOD_NOT_FOUND`
- `ERROR_OPERATION_TIME_LIMIT`

Подтверждённые HTTP-статусы в `CRestServer`:

- `STATUS_OK`
- `STATUS_CREATED`
- `STATUS_WRONG_REQUEST`
- `STATUS_UNAUTHORIZED`
- `STATUS_FORBIDDEN`
- `STATUS_NOT_FOUND`
- `STATUS_TO_MANY_REQUESTS`
- `STATUS_INTERNAL`

---

## Исходящие события и `event.bind`

Серверные `_events` в описании метода только объявляют доступные события. Реальная отправка наружу происходит после `event.bind`.

Что проверено в `Bitrix\Rest\Api\Event`:

- `event.bind` требует OAuth-auth type;
- для offline-ивентов нужны права администратора;
- `EVENT` приводится к верхнему регистру;
- `EVENT_TYPE` поддерживает `online` и `offline`;
- для `online` обязателен `HANDLER`;
- для событий с опцией `disableOffline => true` offline-регистрация запрещена.

Пример обработчика исходящего события:

```php
public static function onItemAdd(\Bitrix\Main\Event $event): array
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

## Placement и userfieldtype

В текущем core есть отдельный REST API для пользовательских UF-type placements:

- `Bitrix\Rest\Api\UserFieldType`
- scope: `placement`
- placement code: `USERFIELD_TYPE`

Если задача про REST-встраивание UF-типа, сначала смотри `rest/lib/api/userfieldtype.php`, а не общие примеры из памяти.

---

## Gotchas

- `OnRestServiceBuildDescription` вызывается на каждом REST-запросе: handler должен быть лёгким.
- Не полагайся вслепую на `$server->getAuth()['user_id']`: в текущем core надёжнее `$server->getAuthData()['user_id']`.
- `_events` и `_placements` после сборки нормализуются по регистру, поэтому не завязывайся на исходный case.
- `RestException::__construct()` принимает строковый error code, но PHP exception code внутри всё равно приводится к `int`; для логики REST смотри `getErrorCode()`, а не `getCode()`.
- `event.bind` валидирует callback через `HandlerHelper::checkCallback(...)`, поэтому внешний URL надо проверять по реальному app context.

## K21 — Пакет REST не является транзакцией

Классический batch: ≤50, без вложенного batch; проверять result.result_error по ключам. halt останавливает, но не откатывает. Не повторять успешные записи всего пакета.

Проверка: Три команды на тестовых данных: успех, ошибка, успех; сравнить halt=0/1 и отсутствие дубля при восстановлении.

[Официальный контракт](https://apidocs.bitrix24.ru/settings/how-to-call-rest-api/batch.html); documentation-backed, 2026-11-01, не runtime pass.

## K22 — Постраничная REST-выгрузка и условие завершения

Для классических list: next → start до отсутствия next. Не угадывать конец по длине result/total; вложенность зависит от метода. Offset не даёт snapshot при параллельных изменениях.

Проверка: Выборка на несколько страниц без total: все ID прочитаны; вложенный items не принят за одну запись.

[Официальный контракт](https://apidocs.bitrix24.ru/settings/how-to-call-rest-api/list-methods-pecularities.html); documentation-backed, 2026-11-01, не runtime pass.

## K23 — Версия REST определяется маршрутом и схемой метода

REST 3.0 (/rest/api/) не заменяет все классические методы. Проверить схему метода и поддержку SDK; простая подмена URL без адаптации параметров/ответа неверна.

Проверка: Для одного метода сравнить обе страницы контракта и маршруты; отсутствующая версия даёт контролируемый отказ.

[Официальный контракт](https://apidocs.bitrix24.ru/api-reference/); documentation-backed, 2026-11-01, не runtime pass.

## K24 — Входящий вебхук наследует права владельца

Вебхук = права создателя ∩ выбранные scope. Недостаток объектных прав не лечится одним scope. URL — секрет, а не публичная ссылка; app-only методы требуют приложения.

Проверка: Одна доступная и одна запрещённая владельцу запись; доступы и секретный URL не утекли в клиент.

[Официальный контракт](https://apidocs.bitrix24.ru/first-steps/first-rest-api-call.html); documentation-backed, 2026-11-01, не runtime pass.

## K25 — Продление OAuth без гонки между обработчиками

На expired_token обновлять и атомарно сохранять оба токена. Один refresher на запись авторизации, остальные перечитывают результат. Не refresh перед каждым запросом и не retry любого отказа.

Проверка: Два конкурентных потребителя одной пары: один refresh, оба используют сохранённую пару; постоянная ошибка останавливает цикл.

[Официальный контракт](https://apidocs.bitrix24.ru/settings/oauth/auto-renewal.html); documentation-backed, 2026-11-01, не runtime pass.

## K26 — Портал идентифицируется member_id, а не доменом

member_id стабилен при смене домена; client_endpoint обновляется из проверенной авторизации. Не создавать второго клиента по новому домену и не принимать URL отправки токенов из произвольного POST.

Проверка: Проверенная смена домена сохраняет клиента; поддельный endpoint отклонён до исходящего запроса.

[Официальный контракт](https://apidocs.bitrix24.ru/settings/how-to-call-rest-api/change-domen.html); documentation-backed, 2026-11-01, не runtime pass.

## K27 — Проверка подлинности REST-события

Проверять auth.application_token по сохранённой установке/member_id до действий. ONAPPINSTALL требует верифицированной авторизации; ONAPPUPDATE учитывает смену секрета; ONAPPUNINSTALL нельзя проверять уже отозванным access_token.

Проверка: Верный, отсутствующий и чужой токены; только верный вызывает согласованный обработчик, без записи секретов в журнал.

[Официальный контракт](https://apidocs.bitrix24.ru/api-reference/events/safe-event-handlers.html); documentation-backed, 2026-11-01, не runtime pass.

## K28 — Офлайн-очередь не является журналом всех изменений

Офлайн-очередь объединяет одинаковые ключи MESSAGE_ID. Читать актуальное состояние, не обещать полную историю или количество всех изменений; избегать безусловной обратной записи.

Проверка: Несколько обновлений одного объекта до чтения: итог синхронизирован, промежуточная история не выдумана.

[Официальный контракт](https://apidocs.bitrix24.ru/api-reference/events/offline-events.html); documentation-backed, 2026-11-01, не runtime pass.

## K29 — Получение офлайн-событий по умолчанию удаляет их

event.offline.get: default clear=1 удаляет; для recoverable обработки явно clear=0 и сохранённый process_id. Повтор пакета с clear=1 удаляет и строки за пределами limit. Проверить доступность режима.

Проверка: На отдельной тестовой очереди упасть после резервирования и повторно получить тот же пакет без удаления.

[Официальный контракт](https://apidocs.bitrix24.ru/api-reference/events/event-offline-get.html); documentation-backed, 2026-11-01, не runtime pass.

## K30 — Подтверждение офлайн-пакета имеет опасные пустые значения

Непустой известный process_id; при частичном успехе — непустой список успешных message_id. Пустой список очищает весь пакет, пустой process_id затрагивает незарезервированные события. Ноль успехов = не вызывать clear.

Проверка: Контроль запроса до отправки: ноль успехов не вызывает clear; частичный успех не удаляет оставшиеся записи.

[Официальный контракт](https://apidocs.bitrix24.ru/api-reference/events/event-offline-clear.html); documentation-backed, 2026-11-01, не runtime pass.
