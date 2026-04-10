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
