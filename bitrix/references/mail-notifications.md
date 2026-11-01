# Почтовые события и уведомления

> Reference для Bitrix-скилла. Загружай когда задача связана с `CEvent`, `Bitrix\Main\Mail\Event`, шаблонами почтовых событий или перехватом отправки. Если задача уже про SMS-провайдера, ограничения, callback-и, sender management или REST-интеграцию, дополнительно загружай `messageservice.md`: это отдельный модульный слой, а не просто расширение mail-событий. Если задача shop-specific про рассылки, сегменты, клики/opens, отписки, sender triggers или report/statistic side effects, дополнительно загружай `shop-marketing-analytics.md`.
>
> Audit note: проверено по текущему core `main/lib/mail/event.php`, `main/classes/general/event.php`.

## Архитектура

В текущем core цепочка такая:

1. **Тип события** (`b_event_type`) — описание полей и типа доставки
2. **Шаблон сообщения** (`b_event_message`) — текст, тема, сайты
3. **Очередь** (`b_event`) — запись на отправку

`Bitrix\Main\Mail\Event::send()` пишет в очередь.  
`Bitrix\Main\Mail\Event::sendImmediate()` отправляет сразу.

Legacy-обёртка:

- `CEvent::Send()` -> возвращает ID записи в очереди или `false`
- `CEvent::SendImmediate()` -> возвращает строковый статус отправки

---

## Создание типа почтового события

```php
use Bitrix\Main\Mail\Internal\EventTypeTable;

$exists = EventTypeTable::getList([
    'filter' => [
        '=EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
        '=LID' => 'ru',
    ],
])->fetch();

if (!$exists)
{
    CEventType::Add([
        'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
        'LID' => 'ru', // язык, не SITE_ID
        'NAME' => 'Новый заказ',
        'DESCRIPTION' => "Поля:\n#ORDER_ID#\n#EMAIL#\n#TOTAL#",
        'SORT' => 100,
        'EVENT_TYPE' => EventTypeTable::TYPE_EMAIL, // или TYPE_SMS
    ]);
}
```

---

## Создание шаблона письма

```php
$eventMessage = new CEventMessage();

$messageId = $eventMessage->Add([
    'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
    'LID' => ['s1'],
    'ACTIVE' => 'Y',
    'EMAIL_FROM' => '#EMAIL_FROM#',
    'EMAIL_TO' => '#EMAIL#',
    'SUBJECT' => 'Ваш заказ #ORDER_ID# принят',
    'MESSAGE' => "Здравствуйте!\nЗаказ №#ORDER_ID# на сумму #TOTAL# принят.",
    'BODY_TYPE' => 'text',
]);
```

---

## Отправка события

### Через очередь

```php
use Bitrix\Main\Mail\Event;

$result = Event::send([
    'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
    'LID' => SITE_ID,
    'C_FIELDS' => [
        'ORDER_ID' => $orderId,
        'EMAIL' => $email,
        'TOTAL' => $total,
    ],
]);

if (!$result->isSuccess())
{
    // ошибки записи в очередь
}
```

### Немедленно

```php
use Bitrix\Main\Mail\Event;

$sendResult = Event::sendImmediate([
    'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
    'LID' => SITE_ID,
    'C_FIELDS' => [
        'ORDER_ID' => $orderId,
        'EMAIL' => $email,
    ],
]);
```

Подтверждённые статусы `sendImmediate()`:

- `Event::SEND_RESULT_SUCCESS` = `'Y'`
- `Event::SEND_RESULT_ERROR` = `'F'`
- `Event::SEND_RESULT_PARTLY` = `'P'`
- `Event::SEND_RESULT_TEMPLATE_NOT_FOUND` = `'0'`
- `Event::SEND_RESULT_NONE` = `'N'`

### Legacy API

```php
$queueId = CEvent::Send(
    'MY_MODULE_ORDER_NEW',
    SITE_ID,
    [
        'ORDER_ID' => $orderId,
        'EMAIL' => $email,
    ]
);
```

`$queueId` здесь будет ID записи в очереди или `false`.

---

## Отправка с вложением

```php
use Bitrix\Main\Mail\Event;

Event::send([
    'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
    'LID' => SITE_ID,
    'C_FIELDS' => [
        'ORDER_ID' => $orderId,
        'EMAIL' => $email,
    ],
    'FILE' => [
        $fileId,
        '/path/to/file.pdf',
    ],
]);
```

---

## Прямое письмо без события

```php
use Bitrix\Main\Mail\Mail;

Mail::send([
    'TO' => 'user@example.com',
    'FROM' => 'noreply@example.com',
    'SUBJECT' => 'Тема письма',
    'BODY' => '<b>HTML-тело</b>',
    'CONTENT_TYPE' => 'html',
    'CHARSET' => 'UTF-8',
    'HEADER' => ['X-Custom-Header: value'],
]);
```

---

## `OnBeforeEventSend`

Регистрация:

```php
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandlerCompatible(
    'main',
    'OnBeforeEventSend',
    [MyModule\EventHandler::class, 'onBeforeEventSend']
);
```

Обработчик:

```php
class EventHandler
{
    public static function onBeforeEventSend(
        array &$fields,
        array &$eventMessage,
        $context,
        array &$result
    )
    {
        $fields['EXTRA_INFO'] = '...';

        if (($fields['EMAIL'] ?? '') === 'blocked@example.com')
        {
            return false;
        }

        return null;
    }
}
```

Что подтверждено по текущему core:

- обработчик вызывается с `(&$arFields, &$eventMessage, $context, &$arResult)`
- если обработчик вернул `false`, текущий шаблон пропускается через `continue 2`
- `StopException` существует, но она ловится уже на этапе compile/send и не является единственным способом остановить отправку

---

## SMS-события

```php
use Bitrix\Main\Mail\Internal\EventTypeTable;

CEventType::Add([
    'EVENT_NAME' => 'MY_SMS_STATUS',
    'LID' => 'ru',
    'NAME' => 'SMS: смена статуса',
    'DESCRIPTION' => '#PHONE#, #ORDER_ID#',
    'EVENT_TYPE' => EventTypeTable::TYPE_SMS,
]);
```

Дальше создаётся обычный `CEventMessage`, а отправка идёт через тот же `Event::send(...)`.

Но это только слой event-type/event-message. Если вопрос про:

- выбор SMS-провайдера;
- sender ID и from list;
- лимиты и ограничения;
- status callback / result URL;
- REST-методы по сообщениям;

то реальная точка входа уже `messageservice`, а не только `main/mail`.

---

## Очередь и история

```php
use Bitrix\Main\Mail\Internal\EventTable;

$result = EventTable::getList([
    'filter' => ['=SUCCESS' => 'N'],
    'order' => ['DATE_INSERT' => 'ASC'],
    'limit' => 50,
]);

while ($row = $result->fetch())
{
    // $row['EVENT_NAME'], $row['DATE_INSERT'], $row['C_FIELDS']
}
```

---

## Gotchas

- В `CEventType::Add()` поле `LID` — это язык (`ru`, `en`), а в `CEventMessage::Add()` `LID` — это массив `SITE_ID`.
- `Event::send()` возвращает `AddResult`, а `CEvent::Send()` — ID очереди или `false`.
- `Event::sendImmediate()` возвращает строковый статус, а не bool.
- `OnBeforeEventSend` в текущем core реально может отменить шаблон через `return false`; не пиши в reference обратное.
- Если шаблон не найден, `sendImmediate()` вернёт `'0'`, а не `false`.
- `CEvent::Send()` только кладёт событие в очередь. Письмо уйдёт, когда отработает mail-event manager/агент.

## K54 — Макросы D7 почты передаются через C_FIELDS

В массиве параметров `Bitrix\Main\Mail\Event` передавай макросы через `C_FIELDS`. `FIELDS` — не документированная замена этого ключа. Не переноси форму аргументов из иных API: у CEvent::Send поля идут третьим позиционным аргументом. После постановки проверяй AddResult и подстановку контрольного макроса, а не только отсутствие исключения.

**Проверка на стенде:** Контрольный ORDER_ID появляется в скомпилированном письме тестового получателя.

[Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/mail/event/send.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K55 — Список сайтов в Legacy и D7 почте различается

У CEvent::Send lid может быть массивом сайтов; документированный D7 Event::send ожидает строку, несколько ID разделяются запятой. Перед преобразованием проверь допустимые сайты на сервере. Не путай LID события с языком. Для независимых писем с разными полями создавай отдельные события вместо общего набора макросов для всех сайтов.

**Проверка на стенде:** Два сайта с разными шаблонами и отдельный язык проверяются на тестовой очереди.

[Официальный контракт](https://dev.1c-bitrix.ru/api_d7/bitrix/main/mail/event/send.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K56 — Совместимая регистрация OnBeforeEventSend

Для legacy-сигнатуры OnBeforeEventSend применяй `addEventHandlerCompatible` либо AddEventHandler. Обычный addEventHandler рассчитан на объект Main\Event; замена имени без изменения callback нарушает контракт. Ссылочные параметры и число аргументов сверяй с вызовом события в установленном ядре; не добавляй второй обработчик поверх ошибочного первого.

**Проверка на стенде:** Один обработчик меняет контрольный макрос без TypeError и повторной регистрации.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/functions/module/addeventhandler.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K57 — Отмена постановки письма до очереди

OnBeforeEventAdd работает до записи события в b_event. Возврат false отменяет добавление (контракт с версии 11.0.16); OnBeforeEventSend действует позже на уровне выбранного шаблона. Ограничивай обработчик EVENT_NAME и нужным контекстом, иначе отменишь чужие уведомления. Не считай фильтрацию одного шаблона доказательством отсутствия записи в очереди.

**Проверка на стенде:** Запрещённый тип не попадает в очередь, разрешённый продолжает отправляться.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/events/onbeforeeventadd.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K58 — Явный почтовый шаблон и языковой фильтр

Без выбора шаблона событие может обработать несколько подходящих шаблонов. MESSAGE_ID задавай серверным доверенным ID, а не произвольным значением клиента. Документация OnBeforeEventAdd отдельно предупреждает: при заданном messageId языковой фильтр не выполняется. Поэтому выбранный шаблон проверь на нужный язык/сайт до отправки; ID шаблонов не переноси между базами как неизменяемую константу.

**Проверка на стенде:** Два языка: автоподбор и явный ID дают ожидаемый, отдельно проверенный шаблон.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/events/onbeforeeventadd.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K59 — DUPLICATE управляет копией, а не идемпотентностью

У CEvent::Send четвёртый аргумент duplicate разрешает копию на адреса дублирования из настроек главного модуля; N не дедуплицирует повторные вызовы. При переносе в D7 сверяй соответствующий параметр DUPLICATE установленной версии. Защиту от повторной постановки по бизнес-событию обеспечивай отдельно; не меняй настройку всех писем ради одного типа.

**Проверка на стенде:** Два вызова и отдельный адрес копии: проверить количество событий и получателей.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cevent/send.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K60 — Вложение по ID и по пути имеет разную стоимость

Для уже сохранённого CFile передавай ID. Передача абсолютного пути в CEvent::Send вызывает дополнительное сохранение файла; документированный вариант с путём также отличается именованием вложения. Не выдавай URL из GetPath за путь файловой системы. Право отправить файл проверяй по его объекту-владельцу; не принимай произвольные пути/ID от клиента. Очистку согласуй с жизненным циклом очереди, не удаляй исходник сразу после send по аналогии с sendImmediate.

**Проверка на стенде:** Тестовое вложение сохраняет ожидаемое имя и доступно при отложенной отправке без лишней копии.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/main/reference/cevent/send.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.
