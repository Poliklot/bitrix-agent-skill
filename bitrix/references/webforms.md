# Веб-формы и обратная связь

```php
use Bitrix\Main\Loader;
Loader::includeModule('form');
```

## Два подхода к формам в Bitrix

| Подход | Когда использовать |
|--------|--------------------|
| **Модуль `form`** (CForm) | Произвольные формы с вопросами, статусами, правами, ограничениями повторной отправки |
| **Форма на инфоблоке** (CIBlockElement::Add) | Простой сбор заявок в структуру инфоблока — быстрее, проще |

---

## Модуль form — CForm / CFormResult

### Получить список форм

```php
$res = CForm::GetList($by = 'c_sort', $order = 'asc', $arFilter = ['ACTIVE' => 'Y']);
while ($form = $res->Fetch()) {
    // $form['ID'], $form['NAME'], $form['SID'] (символьный код)
}
```

### Получить данные формы по ID

```php
$arForm = $arQuestions = $arAnswers = $arDropDown = $arMultiSelect = [];
$formId = CForm::GetDataByID(
    $WEB_FORM_ID,   // int — ID формы
    $arForm,        // заполняется данными формы
    $arQuestions,   // заполняется вопросами
    $arAnswers,     // заполняется вариантами ответов
    $arDropDown,    // выпадающие списки
    $arMultiSelect  // множественные списки
);
// $arForm['NAME'], $arForm['SID'], $arForm['USE_CAPTCHA'], ...
```

### Сохранить результат формы из кода

```php
global $strError;

// $arrValues — массив ответов в формате ['form_<SID>_q<QUESTION_ID>' => 'значение']
// Обычно берётся из $_POST
$arrValues = $_POST; // уже содержит нужные ключи если использована стандартная верстка

$resultId = CFormResult::Add(
    $WEB_FORM_ID,   // ID формы
    $arrValues,     // массив значений
    'Y',            // проверять права ('N' — обходить)
    false           // USER_ID (false = текущий)
);

if ($resultId <= 0) {
    // $strError — глобальная переменная с текстом ошибки (legacy)
    $error = $strError;
} else {
    // Результат сохранён, отправить почтовое событие
    CFormResult::SendMail($resultId);
}
```

### Получить результаты формы

```php
$res = CFormResult::GetListEx(
    $arOrder  = ['DATE_CREATE' => 'DESC'],
    $arFilter = ['WEB_FORM_ID' => $formId],
    $arParams = ['nPageSize' => 20]
);
while ($row = $res->Fetch()) {
    // $row['ID'], $row['DATE_CREATE'], $row['USER_ID']

    // Получить значения полей конкретного результата
    $answers = CFormResult::GetDataByID($row['ID']);
    // $answers — массив вопросов с ответами
}
```

### Отправить почтовое событие для результата

```php
// Отправляет письмо по шаблонам, привязанным к статусам формы
CFormResult::SendMail($resultId);
```

---

## Простая форма на инфоблоке (рекомендуется для заявок)

Если нужна простая форма обратной связи — проще хранить в инфоблоке:

### Создать элемент-заявку из POST

```php
use Bitrix\Main\Application;
use Bitrix\Main\Loader;

Loader::includeModule('iblock');

$request = Application::getInstance()->getContext()->getRequest();

// Только POST-запрос
if ($request->isPost() && check_bitrix_sessid()) {
    $name    = htmlspecialchars($request->getPost('name') ?? '', ENT_QUOTES, 'UTF-8');
    $email   = $request->getPost('email') ?? '';
    $message = htmlspecialchars($request->getPost('message') ?? '', ENT_QUOTES, 'UTF-8');

    // Валидация
    if (empty($name) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error = 'Заполните все обязательные поля';
    } else {
        $el = new CIBlockElement();
        $elementId = $el->Add([
            'IBLOCK_ID'   => FEEDBACK_IBLOCK_ID,  // константа или из настроек
            'NAME'        => $name . ' — ' . date('d.m.Y H:i'),
            'ACTIVE'      => 'Y',
            'PROPERTY_VALUES' => [
                'NAME'    => $name,
                'EMAIL'   => $email,
                'MESSAGE' => $message,
                'IP'      => $request->getServer()->get('REMOTE_ADDR'),
            ],
        ]);

        if ($elementId) {
            // Отправить уведомление
            use Bitrix\Main\Mail\Event;
            Event::send([
                'EVENT_NAME' => 'FEEDBACK_NEW',
                'LID'        => SITE_ID,
                'FIELDS'     => ['NAME' => $name, 'EMAIL' => $email, 'MESSAGE' => $message],
            ]);
            $success = true;
        } else {
            $error = $el->LAST_ERROR;
        }
    }
}
```

### HTML-форма с CSRF-защитой

```html
<form method="POST" action="">
    <?php echo bitrix_sessid_post(); ?>  <!-- CSRF-токен -->
    <input type="text" name="name" required>
    <input type="email" name="email" required>
    <textarea name="message"></textarea>
    <button type="submit">Отправить</button>
</form>
```

---

## AJAX-форма (без перезагрузки страницы)

### PHP-обработчик (D7 Controller)

```php
namespace MyVendor\MyModule\Controller;

use Bitrix\Main\Engine\Controller;
use Bitrix\Main\Engine\ActionFilter;
use Bitrix\Main\Error;
use Bitrix\Main\Loader;
use Bitrix\Main\Mail\Event;

class Feedback extends Controller
{
    public function configureActions(): array
    {
        return [
            'send' => [
                'prefilters' => [
                    new ActionFilter\HttpMethod(['POST']),
                    new ActionFilter\Csrf(),
                ],
            ],
        ];
    }

    public function sendAction(string $name, string $email, string $message): ?array
    {
        if (empty($name)) {
            $this->addError(new Error('Имя обязательно', 'EMPTY_NAME'));
            return null;
        }
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $this->addError(new Error('Неверный email', 'BAD_EMAIL'));
            return null;
        }

        Loader::includeModule('iblock');
        $el = new \CIBlockElement();
        $id = $el->Add([
            'IBLOCK_ID' => FEEDBACK_IBLOCK_ID,
            'NAME'      => $name,
            'PROPERTY_VALUES' => ['EMAIL' => $email, 'MESSAGE' => $message],
        ]);

        if (!$id) {
            $this->addError(new Error($el->LAST_ERROR));
            return null;
        }

        Event::send([
            'EVENT_NAME' => 'FEEDBACK_NEW',
            'LID'        => SITE_ID,
            'FIELDS'     => compact('name', 'email', 'message'),
        ]);

        return ['id' => $id];
        // Engine автоматически вернёт {"status":"success","data":{"id":42}}
    }
}
```

### JS-клиент

```javascript
BX.ajax.runAction('myvendor.mymodule.feedback.send', {
    data: {
        sessid: BX.bitrix_sessid(),     // CSRF-токен
        name:    document.getElementById('name').value,
        email:   document.getElementById('email').value,
        message: document.getElementById('message').value,
    }
}).then(function(response) {
    // response.data.id
    console.log('Отправлено, ID:', response.data.id);
}).catch(function(response) {
    // response.errors[0].message
    console.error(response.errors);
});
```

> `BX.ajax.runAction` автоматически добавляет `sessid` если он передан в `data`, подставляет правильный URL контроллера по имени (`myvendor.mymodule.feedback.send` → `/bitrix/services/main/ajax.php?action=...`).

---

## Валидация на сервере

```php
// Типичные проверки при обработке формы
$errors = [];

$name = trim($request->getPost('name') ?? '');
if (mb_strlen($name) < 2 || mb_strlen($name) > 100) {
    $errors[] = 'Имя должно быть от 2 до 100 символов';
}

$email = trim($request->getPost('email') ?? '');
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'Некорректный email';
}

$phone = preg_replace('/[^0-9+]/', '', $request->getPost('phone') ?? '');
if (!preg_match('/^\+?[0-9]{10,15}$/', $phone)) {
    $errors[] = 'Некорректный телефон';
}

// Защита от флуда — один IP не чаще 1 раза в 60 секунд
$ip = $request->getServer()->get('REMOTE_ADDR');
$cacheKey = 'feedback_flood_' . md5($ip);
$cache = \Bitrix\Main\Application::getInstance()->getCache();
if ($cache->initCache(60, $cacheKey, '/feedback_flood')) {
    $errors[] = 'Слишком частые отправки';
} elseif (empty($errors)) {
    $cache->startDataCache();
    $cache->endDataCache(['ts' => time()]);
}
```

---

## Gotchas

- `CFormResult::Add` читает форму из БД по ID — при каждом вызове идёт запрос. Кешируй `CForm::GetDataByID` если нужно
- `$strError` в `CFormResult::Add` — **глобальная переменная**, объявляй `global $strError` перед использованием
- `check_bitrix_sessid()` — обязательно для любой POST-обработки, иначе CSRF-уязвимость
- При сохранении в инфоблок через `CIBlockElement::Add` — данные из `$request->getPost()`, не из `$_POST` напрямую
- `BX.ajax.runAction` требует, чтобы контроллер был зарегистрирован в модуле (файл существует и PSR-4 настроен)
