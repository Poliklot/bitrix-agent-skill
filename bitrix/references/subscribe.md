# Bitrix Subscribe — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с рубриками рассылок, подписками, posting-рассылками и auto-template workflow модуля `subscribe`.
>
> Audit note: проверено по текущему core `subscribe/classes/general/*`, `subscribe/install/components/*`. Для shop-core различий между legacy `subscribe.*`, modern `sender.subscribe` и `catalog.product.subscribe*` дополнительно открывай `shop-marketing-analytics.md`.

## Содержание
- Архитектура модуля `subscribe`
- `CRubric`
- `CSubscription`
- Подтверждение / отписка
- `CPosting`
- `CPostingTemplate`
- Gotchas

---

## Архитектура модуля `subscribe`

В текущем core подтверждены следующие основные классы:

```text
CRubric
  └── рубрика / список рассылки

CSubscription
  └── подписка: email, user_id, confirmed, active, набор RUB_ID

CPosting
  └── конкретная рассылка / письмо / очередь отправки

CPostingTemplate
  └── файловые шаблоны для auto-рубрик
```

Не подтверждены как core-API этого модуля:

- `CSender`
- `CSubscribe`
- `CSending`

Не опирайся на них в reference для текущего ядра.

---

## `CRubric`

`CRubric` управляет рубриками рассылок.

### Получить список рубрик

```php
use Bitrix\Main\Loader;

Loader::includeModule('subscribe');

$rubrics = CRubric::GetList(
    ['SORT' => 'ASC'],
    ['ACTIVE' => 'Y', 'LID' => SITE_ID]
);

while ($rubric = $rubrics->Fetch())
{
    // ID, NAME, CODE, SORT, LID, ACTIVE, DESCRIPTION, AUTO, VISIBLE,
    // LAST_EXECUTED, FROM_FIELD, DAYS_OF_MONTH, DAYS_OF_WEEK, TIMES_OF_DAY, TEMPLATE
}
```

### Получить рубрику по ID

```php
$rubric = CRubric::GetByID($rubricId)->Fetch();
```

### Создать / обновить / удалить рубрику

```php
$rubric = new CRubric();

$rubricId = $rubric->Add([
    'NAME' => 'Новости компании',
    'CODE' => 'company_news',
    'LID' => SITE_ID,
    'ACTIVE' => 'Y',
    'VISIBLE' => 'Y',
    'SORT' => 100,
    'DESCRIPTION' => 'Еженедельная рассылка',
    'FROM_FIELD' => 'noreply@example.com',
    'AUTO' => 'N',
]);

if (!$rubricId)
{
    $error = $rubric->LAST_ERROR;
}

$rubric->Update($rubricId, [
    'NAME' => 'Актуальные новости компании',
]);

CRubric::Delete($rubricId);
```

Если рубрика `ACTIVE=Y` и `AUTO=Y`, ядро может добавить агент `CPostingTemplate::Execute();`.

---

## `CSubscription`

`CSubscription` хранит email-подписки и привязку к рубрикам.

### Получить список подписок

```php
$subscriptions = CSubscription::GetList(
    ['DATE_INSERT' => 'DESC'],
    [
        'ACTIVE' => 'Y',
        'CONFIRMED' => 'Y',
        'RUBRIC_MULTI' => [$rubricId],
    ]
);

while ($subscription = $subscriptions->Fetch())
{
    // ID, USER_ID, EMAIL, FORMAT, CONFIRM_CODE, CONFIRMED, DATE_INSERT, DATE_UPDATE
}
```

### Получить по ID

```php
$subscription = CSubscription::GetByID($subscriptionId)->Fetch();
```

### Получить по email

```php
$subscription = CSubscription::GetByEmail('user@example.com', false)->Fetch();
```

Важная деталь текущего core:

- второй аргумент `GetByEmail($email, $user_id = false)` — это **`USER_ID`**, а не `SITE_ID`

### Получить рубрики подписки

```php
$rubrics = CSubscription::GetRubricList($subscriptionId);
while ($rubric = $rubrics->Fetch())
{
    // ID, NAME, SORT, LID, ACTIVE, VISIBLE
}
```

### Создать подписку

```php
$subscription = new CSubscription();

$subscriptionId = $subscription->Add([
    'USER_ID' => $USER->IsAuthorized() ? (int)$USER->GetID() : false,
    'EMAIL' => 'user@example.com',
    'FORMAT' => 'html',
    'ACTIVE' => 'Y',
    'CONFIRMED' => 'N',
    'RUB_ID' => [$rubricId],
    'SEND_CONFIRM' => 'Y',
], SITE_ID);

if (!$subscriptionId)
{
    $error = $subscription->LAST_ERROR;
}
```

Подтверждённые полезные поля:

- `USER_ID`
- `EMAIL`
- `FORMAT` (`html` / `text`)
- `ACTIVE`
- `CONFIRMED`
- `RUB_ID`
- `SEND_CONFIRM`
- `ALL_SITES`

### Обновить подписку

```php
$subscription = new CSubscription();

$ok = $subscription->Update($subscriptionId, [
    'ACTIVE' => 'Y',
    // CONFIRMED не меняем: редактирование рубрик не подтверждает адрес.
    'RUB_ID' => [$rubricId1, $rubricId2],
], SITE_ID);
```

### Удалить подписку

```php
CSubscription::Delete($subscriptionId);
```

---

## Подтверждение / отписка

При `SEND_CONFIRM <> 'N'` ядро отправляет событие `SUBSCRIBE_CONFIRM` и использует `CONFIRM_CODE`.

Есть подтверждённый helper:

```php
CSubscription::Authorize($subscriptionId, $confirmCode);
```

Также можно подтвердить подписку через `Update()`:

```php
$subscription = new CSubscription();
$subscription->Update($subscriptionId, [
    'CONFIRM_CODE' => $confirmCode,
], SITE_ID);
```

В текущем core не нужно придумывать поле `CODE` или endpoint `unsubscribe.php` как базовый контракт модуля. Legacy subscribe-flow работает через `ID` + `CONFIRM_CODE` и компонент `subscribe.edit`.

---

## `CPosting`

`CPosting` — это конкретная рассылка.

### Создать posting

```php
$posting = new CPosting();

$postingId = $posting->Add([
    'FROM_FIELD' => 'noreply@example.com',
    'TO_FIELD' => 'noreply@example.com',
    'SUBJECT' => 'Новости недели',
    'BODY_TYPE' => 'html',
    'BODY' => '<p>Контент письма</p>',
    'DIRECT_SEND' => 'Y', // персональный режим для ограниченных шагов отправки
    'SUBSCR_FORMAT' => 'html',
    'RUB_ID' => [$rubricId],
    'GROUP_ID' => [],
]);

if (!$postingId)
{
    $error = $posting->LAST_ERROR;
}
```

Ключевые поля, подтверждённые по текущему core/admin UI:

- `FROM_FIELD`
- `TO_FIELD`
- `SUBJECT`
- `BODY_TYPE`
- `BODY`
- `DIRECT_SEND`
- `SUBSCR_FORMAT`
- `RUB_ID`
- `GROUP_ID`
- `EMAIL_FILTER`
- `AUTO_SEND_TIME`

### Получить posting

```php
$posting = CPosting::GetByID($postingId)->Fetch();
```

### Получить список posting

```php
$postingApi = new CPosting();

$list = $postingApi->GetList(
    ['ID' => 'DESC'],
    ['STATUS_ID' => 'D'],
    ['ID', 'STATUS', 'FROM_FIELD', 'TO_FIELD', 'SUBJECT', 'DATE_SENT'],
    false
);

while ($row = $list->Fetch())
{
    // ...
}
```

### Обновить / удалить

```php
$posting = new CPosting();

$posting->Update($postingId, [
    'SUBJECT' => 'Новая тема письма',
]);

CPosting::Delete($postingId);
```

---

## Запуск отправки posting

Для боевой отправки posting обычно переводят из draft в processing:

```php
$posting = new CPosting();

if (!$posting->ChangeStatus($postingId, 'P')) {
    throw new \RuntimeException($posting->LAST_ERROR);
}
```

Что делает current core:

- собирает `b_posting_email`
- набирает получателей из рубрик / групп / BCC
- дальше `CPosting::AutoSend(...)` или cron/agent доотправляет батчами

Для ручного запуска:

```php
CPosting::AutoSend($postingId, true, SITE_ID);
```

Для управляемого шага реальной отправки есть (это не dry-run):

```php
$posting = new CPosting();
$result = $posting->SendMessage($postingId, 10, 100, false);
if ($result === 'CONTINUE') {
    // Запланировать следующий шаг того же выпуска, без сброса очереди.
} elseif ($result === false) {
    throw new \RuntimeException($posting->LAST_ERROR);
} elseif ($result === true) {
    // Шаг/выпуск завершён по контракту отправки; это не receipt доставки в inbox.
}
```

Но `SendMessage()` блокирует выполнение и не подходит как default-стратегия для массовой рассылки.

---

## `CPostingTemplate`

`CPostingTemplate` в текущем core работает не как DB-шаблон письма, а как файловый auto-template.

Шаблоны лежат в:

```text
getLocalPath('php_interface/subscribe/templates', BX_PERSONAL_ROOT)
```

### Получить список шаблонов

```php
$templates = CPostingTemplate::GetList();
// массив путей, а не DB result
```

### Получить шаблон по пути

```php
$paths = CPostingTemplate::GetList();
$template = CPostingTemplate::GetByID($paths[0] ?? '');
```

### Auto-run

Если рубрика настроена как `AUTO=Y`, агент вызывает:

```php
CPostingTemplate::Execute();
```

Он рассчитывает расписание рубрики, генерирует posting через шаблон и переводит его в отправку.

---

## Gotchas

- В текущем core модуля `subscribe` нет подтверждённого API `CSender`, `CSubscribe`, `CSending`. Не описывай их как штатный контракт этого ядра.
- `CSubscription::GetByEmail($email, $userId)` вторым параметром принимает `USER_ID`, а не `SITE_ID`.
- `CSubscription::GetRubricList($subscriptionId)` принимает именно ID подписки и возвращает строки рубрик с полями `ID/NAME/...`, а не `RUBRIC_ID`.
- Для `CPosting::Add()` используй `RUB_ID`, а не `RUBRIC_ID`.
- `CPostingTemplate::GetList()` возвращает массив путей, не `CDBResult`.
- `CPosting::ChangeStatus($id, 'P')` — нормальная точка входа в очередь отправки. Не выдумывай отдельную сущность “sending job”.
- `SendMessage()` синхронен. Для боевой рассылки ориентируйся на queue/agent/cron workflow.
- Если включаешь `SEND_CONFIRM`, не забывай, что подписка останется неподтверждённой до прохождения confirm-flow.

## K131 — Публичная подписка не должна сама устанавливать CONFIRMED=Y

Для новой публичной подписки не выставляй CONFIRMED=Y и SEND_CONFIRM=N: создай неподтверждённую запись и используй штатное подтверждение. Включение ACTIVE не доказывает владение адресом. Доверенный импорт ранее подтверждённых подписок — отдельная операция с доказанным источником, не режим формы сайта.

**Проверка на стенде:** Произвольный чужой адрес не становится подтверждённым после POST.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptionadd.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K132 — EMAIL подписки уникален, существующая запись не принадлежит заявителю автоматически

У CSubscription EMAIL уникален. Отказ Add для существующего адреса не разрешает обновить найденную подписку, присвоить USER_ID или заменить рубрики. Сначала штатная авторизация доступа к подписке; публичный ответ не должен раскрывать её наличие и код. Конкурентное создание обрабатывай как возможный конфликт.

**Проверка на стенде:** Два параллельных запроса не создают захват существующей подписки.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptiongeneralfields.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K133 — Обновление RUB_ID требует явной области сайта

При обновлении RUB_ID задавай SITE_ID явно; ALL_SITES расширяет область и не является удобным флагом исправления ошибок. Перед заменой списка прочитай текущие рубрики и сохрани те, которые операция не должна менять. На мультисайте отдельно проверь подписки второго сайта; сайт из запроса должен быть разрешён сервером.

**Проверка на стенде:** Рубрика второго сайта сохраняется при локальном изменении первого.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptionupdate.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K134 — Authorize с false безусловно открывает доступ к подписке

Authorize(ID, false) выполняет безусловную авторизацию подписки в PHP-сессии. Не вызывай его на чужом ID из запроса или после GetByEmail. Для анонимной подписки нужен непустой проверяемый код, для привязанной — штатный доступ владельца. Это доступ к подписке, не вход пользователя в аккаунт.

**Проверка на стенде:** Чужой ID и отсутствующий код не открывают редактирование.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptionauthorize.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K135 — Смена EMAIL снимает подтверждение подписки

При изменении EMAIL штатный Update снимает подтверждение и формирует письмо, если отправка не запрещена. Не возвращай CONFIRMED=Y автоматически. LAST_MESSAGE=CONF означает подтверждение, SENT — созданное событие письма, а не доставку. Сохраняй разделение успешной записи и подтверждённого нового адреса.

**Проверка на стенде:** Смена адреса переводит подписку в неподтверждённое состояние до корректного кода.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/csubscriptiongeneral/csubscriptionupdate.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K136 — Статусы posting изменяют очередь, а не только метку

D→P формирует очередь; W→P продолжает её, E→P возвращает ошибочные адреса на отправку. Возврат в D очищает очередь и не равен паузе. Создавай выпуск черновиком и запускай ChangeStatus, не присваивай P напрямую. Всегда проверяй bool/LAST_ERROR до следующего шага.

**Проверка на стенде:** Продолжение не отправляет уже обработанным адресам заново.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/cpostinggeneral/cpostingchangestatus.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K137 — SendMessage имеет три исхода, CONTINUE не является успехом

Различай строго true, false и строку CONTINUE. Продолжение возможно при лимите шага, занятой блокировке или несовпадении кодировки при её проверке; не объявляй всё отправленным по truthy. SendMessage реально отправляет очередь, это не dry-run. Ограничения timeout/maxcount относятся к персональному режиму.

**Проверка на стенде:** Все три значения дают разные ветви; CONTINUE не переводит отчёт в успех.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/cpostinggeneral/cpostingsendmessage.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K138 — DIRECT_SEND задаёт персональную отправку, а не синхронность

DIRECT_SEND=Y означает персонально каждому подписчику, не «отправить сейчас». Пакетные timeout/maxcount и BeforePostingSendMail нужно рассматривать вместе с этим режимом. До массового запуска проверь реальные заголовки на тестовых адресах; не складывай список подписчиков в открытое поле To.

**Проверка на стенде:** Тестовые письма не раскрывают адреса других получателей; пакетный лимит действует.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/cpostinggeneral/cpostingfields.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K139 — Счётчики очереди используют Y как ожидание и N как отправку

GetEmailStatuses возвращает статус→количество: Y ожидает, N отправлено, E ошибка; отсутствующий ключ означает ноль. Это не статусы выпуска D/P/S/W. Отсутствие Y не доказывает успех всех адресов: проверь E и общий ожидаемый объём, отличай пустую очередь от законченной рассылки.

**Проверка на стенде:** Пустая, ошибочная и успешная очереди дают разные отчёты.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/subscribe/classes/cpostinggeneral/getemailstatuses.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.
