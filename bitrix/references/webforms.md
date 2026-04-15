# Веб-формы и результаты в текущем core

> Reference для Bitrix-скилла. Загружай, когда задача связана с модулем `form`, формами, вопросами и ответами, результатами, статусами, почтовыми шаблонами, validators, CRM link, secure file download или стандартными `form.*` компонентами.
>
> Audit note: проверено по текущему core `form` версии `25.0.0` через `install/index.php`, `install/components`, `install/tools`, `classes/general/*` и `classes/mysql/*`.

```php
use Bitrix\Main\Loader;

Loader::includeModule('form');
```

## Что реально есть в модуле `form`

В текущем core модуль `form` значительно шире, чем "просто отправить письмо":

- формы и их структура: `CForm`
- результаты: `CFormResult`
- поля/вопросы: `CFormField`
- варианты ответов: `CFormAnswer`
- статусы: `CFormStatus`
- валидаторы: `CFormValidator`
- CRM связка: `CFormCrm`
- стандартные компоненты `form.*`
- безопасная отдача файлов по hash
- status handlers до/после смены статуса

Если задача требует права, workflow статусов, повторное редактирование, CRM или безопасную выдачу файлов, это маршрут точно в `form`, а не в "простую форму на инфоблоке".

## Подтверждённые стандартные компоненты

В текущем ядре есть:

- `bitrix:form`
- `bitrix:form.result.new`
- `bitrix:form.result.edit`
- `bitrix:form.result.view`
- `bitrix:form.result.list`
- `bitrix:form.result.list.my`

Если задача упирается в типовой UI формы/результатов, сначала считай контракт стандартного компонента, а потом уже проектный шаблон.

## Когда брать `form`, а когда достаточно инфоблока

| Подход | Когда использовать |
|--------|--------------------|
| `form` | Нужны вопросы/ответы, статусы, права, редактирование результата, почтовые шаблоны, админский список, validators, CRM-link |
| Инфоблок или свой D7 controller | Нужен простой lead-capture без workflow и без штатной form-админки |

## Формы и права

Подтверждённые методы верхнего слоя:

- `CForm::GetList()`
- `CForm::GetByID()`
- `CForm::GetBySID()`
- `CForm::GetDataByID()`
- `CForm::Set()`
- `CForm::Copy()`
- `CForm::Delete()`
- `CForm::Reset()`
- `CForm::SetMailTemplate()`
- `CForm::GetPermission()`
- `CForm::GetPermissionList()`

`CForm::GetPermissionList()` в текущем core возвращает уровни:

- `1` — denied
- `10` — fill
- `15` — fill + edit own results
- `20` — view results
- `25` — view results with additional params
- `30` — full write/admin on form

```php
$permission = CForm::GetPermission($formId);

if ($permission < 10)
{
    throw new \RuntimeException('Недостаточно прав для заполнения формы');
}
```

## Получить форму и её структуру

```php
$forms = CForm::GetList(
    $by = 's_sort',
    $order = 'asc',
    ['ACTIVE' => 'Y']
);

while ($form = $forms->Fetch())
{
    // $form['ID'], $form['SID'], $form['NAME']
}
```

```php
$arForm = $arQuestions = $arAnswers = $arDropDown = $arMultiSelect = [];

CForm::GetDataByID(
    $formId,
    $arForm,
    $arQuestions,
    $arAnswers,
    $arDropDown,
    $arMultiSelect,
    'N',
    'N'
);
```

`CForm::GetDataByID()` остаётся основным способом получить полноценную структуру формы с вопросами и вариантами ответов.

## Результаты: базовый lifecycle

Подтверждённые методы `CFormResult`:

- `GetList()`
- `GetByID()`
- `GetPermissions()`
- `GetFileByAnswerID()`
- `GetFileByHash()`
- `SetEvent()`
- `GetDataByID()`
- `GetDataByIDForHTML()`
- `Add()`
- `Update()`
- `SetField()`
- `Delete()`
- `Reset()`
- `SetStatus()`
- `Mail()`
- `SetCRMFlag()`

### Создать результат

```php
global $strError;

$resultId = CFormResult::Add(
    $formId,
    $_POST,
    'Y',
    false
);

if ((int)$resultId <= 0)
{
    throw new \RuntimeException($strError ?: 'Не удалось сохранить результат формы');
}

CFormResult::Mail($resultId);
```

### Получить список результатов

```php
$isFiltered = false;

$dbResults = CFormResult::GetList(
    $formId,
    $by = 's_timestamp',
    $order = 'desc',
    ['STATUS_ID' => 1],
    $isFiltered,
    'Y',
    false
);

while ($row = $dbResults->Fetch())
{
    $resultMeta = [];
    $answers = [];

    CFormResult::GetDataByID($row['ID'], [], $resultMeta, $answers);
}
```

### Обновить отдельные поля результата

`CFormResult::SetField()` в текущем core:

- отдельно обрабатывает additional fields
- умеет file/image answers
- пишет `USER_FILE_HASH`
- обновляет поисковые поля `ANSWER_TEXT_SEARCH`, `ANSWER_VALUE_SEARCH`, `USER_TEXT_SEARCH`

Если задача про "дописать одно поле в существующий результат" или "обновить файл без полной перезаписи результата", смотри сюда, а не только в `Update()`.

## Статусы и status handlers

Подтверждённые методы `CFormStatus`:

- `GetList()`
- `GetByID()`
- `GetPermissionList()`
- `GetPermissions()`
- `GetDefault()`
- `Set()`
- `Delete()`
- `Copy()`
- `SetMailTemplate()`

Статусные permission buckets в текущем core:

- `VIEW`
- `MOVE`
- `EDIT`
- `DELETE`

```php
$defaultStatusId = CFormStatus::GetDefault($formId);

CFormResult::SetStatus($resultId, $defaultStatusId);
```

### Что происходит при смене статуса

`CFormResult::SetStatus()` в текущем core:

- проверяет права на форму и результат
- проверяет право перемещения в новый статус
- вызывает `onBeforeResultStatusChange`
- запускает `CForm::ExecHandlerBeforeChangeStatus(..., "SET_STATUS", $NEW_STATUS_ID)`
- сохраняет статус
- вызывает `onAfterResultStatusChange`
- запускает `CForm::ExecHandlerAfterChangeStatus(..., "SET_STATUS")`

### `HANDLER_OUT` / `HANDLER_IN`

У статусов реально есть поля:

- `HANDLER_OUT`
- `HANDLER_IN`

`CForm::ExecHandlerBeforeChangeStatus()` и `ExecHandlerAfterChangeStatus()` включают эти PHP-файлы из document root. Это не абстрактные callbacks в БД, а реальный `include` файловой логики.

Следствие: задачи по status handlers надо вести как аудит PHP-файлов и их side effects, а не как "настройку строки в админке".

## События результата, удаления и reset

Важные подтверждённые точки lifecycle:

- `Delete()` вызывает `onBeforeResultDelete`
- `Delete()` запускает `CForm::ExecHandlerBeforeChangeStatus($RESULT_ID, "DELETE")`
- `SetStatus()` вызывает `onBeforeResultStatusChange` и `onAfterResultStatusChange`
- `Reset()` умеет очищать ответы выборочно
- `Reset()` умеет не трогать additional fields, если явно не просили `DELETE_ADDITIONAL = "Y"`

Если задача про "частично очистить результат" или "не потерять служебные поля", сначала смотри `Reset()`, а не делай `Delete()+Add()`.

## Почта и site binding

`CFormResult::Mail($RESULT_ID, $TEMPLATE_ID = false)` подтверждён в текущем core.

Важно: внутри `Mail()` есть проверка, что текущий `SITE_ID` входит в список сайтов формы. Если форма привязана не к тому сайту, письма могут "молча" не уйти.

Это один из первых пунктов диагностики для задачи "результат сохранился, но письмо не отправилось".

## Валидаторы

Подтверждённый validator-layer:

- `CFormValidator::GetList()`
- `CFormValidator::GetListForm()`
- `CFormValidator::GetAllList()`
- `CFormValidator::Execute()`
- `CFormValidator::Set()`
- `CFormValidator::SetBatch()`

Реестр валидаторов собирается через module events:

- `GetModuleEvents("form", "onFormValidatorBuildList", true)`

В текущем core уже есть встроенные validator-ы в `modules/form/validators/*`, включая:

- длину текста
- числовые диапазоны
- INN
- размер файла
- тип файла
- размер изображения
- возраст/дату

Если задача про кастомный validator, его надо проектировать как event-driven descriptor с `HANDLER`, а не как произвольную if-ветку в шаблоне формы.

## CRM link

Подтверждённый CRM-layer живёт в `CFormCrm`:

- `GetByID()`
- `GetByFormID()`
- `GetFields()`
- `SetForm()`
- `onResultAdded()`
- `AddLead()`

Типы связи:

- `CFormCrm::LINK_AUTO = 'A'`
- `CFormCrm::LINK_MANUAL = 'M'`

`SetForm()` в текущем core умеет:

- сохранять link формы к CRM-коннектору
- строить field mapping
- при необходимости автоматически создавать form field под CRM field

`onResultAdded()` автоматически вызывает `AddLead()` только для `LINK_AUTO`.

Если задача про "почему лид не улетает после отправки формы", сначала проверь:

- есть ли link у формы
- какой `LINK_TYPE`
- какие поля реально сматчены

## Файлы и безопасная выдача

Подтверждённые методы:

- `CFormResult::GetFileByAnswerID($RESULT_ID, $ANSWER_ID)`
- `CFormResult::GetFileByHash($RESULT_ID, $HASH)`

`GetFileByHash()` в текущем core отдаёт файл только если:

- право на форму `>= 20`
- или право `>= 15` и текущий пользователь владелец результата

Также в модуле есть:

- `install/tools/form_show_file.php`

Но это только wrapper на:

- `/bitrix/modules/form/admin/form_show_file.php`

Если задача про публичную выдачу вложения формы по hash, не ломай этот security-layer ручным `CFile::GetFileArray()` без проверки прав.

## Sender и соседние интеграции

В `install/index.php` подтверждена зависимость:

- `sender:OnConnectorList -> Bitrix\Form\SenderEventHandler::onConnectorListForm`

То есть модуль `form` умеет встраиваться в контур `sender`, но это соседний integration point, а не основная модель формы. Если `sender` не участвует в задаче, не тащи его туда без необходимости.

## Простейший fallback без `form`

Если нужен только лёгкий lead-capture без workflow, прав и статусной машины, действительно можно использовать инфоблок или свой D7 controller. Но это отдельный маршрут, а не замена возможностей `form`.

## Gotchas

- Не своди `form` к одной операции `CFormResult::Add()`: в реальном core здесь есть статусы, handlers, validators, CRM, secure files и права.
- `CFormResult::Mail()` зависит от привязки формы к `SITE_ID`.
- `GetFileByHash()` уже содержит permission-логику. Не обходи её самописной выдачей файла.
- Status handlers выполняют PHP-файлы с диска. Их надо ревьюить как код с побочными эффектами.
- `Reset()` и `Delete()` ведут себя по-разному; для частичного очищения результата не подменяй одно другим.
