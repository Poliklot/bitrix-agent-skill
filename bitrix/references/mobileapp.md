# MobileApp, admin mobile и JN/native компоненты (модуль mobileapp)

> Audit note: ниже сверено с текущим `www/bitrix/modules/mobileapp` версии `24.200.0`. Подтверждены D7-части `\Bitrix\MobileApp\AppTable`, `AppResource`, `\Bitrix\MobileApp\Mobile`, `\Bitrix\MobileApp\Janative\Manager`, `\Bitrix\MobileApp\Designer\Manager`, legacy-слой `CMobile`, `CAdminMobilePush`, `CMobileAppPullSchema`, сервис `/bitrix/services/mobileapp/jn.php`, AJAX endpoint `mobileapp.push.token/call.ajax.php`, а также стандартные компоненты `bitrix:mobileapp.auth`, `bitrix:mobileapp.jnrouter`, `bitrix:mobileapp.push`, `bitrix:mobileapp.menu`, `bitrix:mobileapp.list`, `bitrix:mobileapp.filter`, `bitrix:mobileapp.edit`.

## Для чего использовать

`mobileapp` в этом core - не только “старый мобильный шаблон”. Это отдельный модульный контур для:

- mobile admin/prolog-а и мобильной авторизации;
- legacy mobile UI-компонентов;
- JN/native component и extension delivery через `/mobileapp/jn/*`;
- designer/app-builder с хранением app config в модуле;
- mobile push settings и device-token регистрации;
- bridge-логики к `pull`, если соответствующий модуль установлен.

Если задача звучит как:

- “как отдать JN extension в мобильное приложение”
- “почему mobile component не обновляется на клиенте”
- “где собирается admin mobile menu”
- “как хранится конфиг mobile designer app”
- “почему push token не регистрируется”

то первым маршрутом должен быть `mobileapp`, а не общий `rest` или отложенный `pull`.

## Архитектура модуля

По текущему ядру:

- модуль смешанный: есть D7 ORM/JN/designer-слой и большой legacy mobile/admin mobile слой;
- installer создаёт таблицу `b_mobileapp_app`;
- installer регистрирует зависимость `pull:OnGetDependentModule -> CMobileAppPullSchema::OnGetDependentModule`;
- installer добавляет rewrite:
  - `#^\/?\/mobileapp/jn\/(.*)\/.*#`
  - `PATH => /bitrix/services/mobileapp/jn.php`

Практическое правило:

- base-route задач по мобильному клиенту сначала ищи в `mobileapp`;
- в `pull` уходи только если задача реально про push transport, `CPullPush` или зависимые события.

## `AppTable` и app storage

Подтверждён `\Bitrix\MobileApp\AppTable` c таблицей `b_mobileapp_app`.

Подтверждены поля:

- `CODE` - primary key
- `SHORT_NAME`
- `NAME`
- `DESCRIPTION`
- `FILES` - serialized
- `LAUNCH_ICONS` - serialized
- `LAUNCH_SCREENS` - serialized
- `FOLDER`
- `DATE_CREATE`
- reference `CONFIG`

Подтверждены методы:

- `isAppExists($code)`
- `getSupportedPlatforms()`
- `onAfterDelete(Event $event)`
- `checkFields(Result $result, $primary, array $data)`

Важно:

- app code обязателен уже на уровне `checkFields`
- поддерживаемые платформы в текущем core ограничены `android` и `ios`
- удаление app очищает связанный config через `Designer\ConfigTable::delete(...)`

## `AppResource`

Подтверждён `\Bitrix\MobileApp\AppResource`.

Ключевые методы:

- `get($platformId)`
- `getIconsSet($platformId)`
- `getImagesSet($platformId)`
- `getAdditionalSet($platformId)`

Что это значит:

- наборы launch icons/screens берутся не “из произвольной папки”, а из resource-map модуля
- для задач designer/app packaging сначала проверяй `maps/resources.php`, а не только admin UI

## Designer manager

Подтверждён `\Bitrix\MobileApp\Designer\Manager`.

Ключевые методы:

- `createApp($appCode, $data, $initConfig)`
- `removeApp($appCode)`
- `registerFileInApp(&$fileArray, $appCode)`
- `unregisterFileInApp($fileId, $appCode)`
- `addConfig($appCode, $platform, $config)`
- `removeConfig($appCode, $platform)`
- `updateConfig($appCode, $platform, $config)`
- `getConfigJSON($appCode, $platform = false)`

Практические выводы:

- designer app хранится не в шаблоне сайта, а в модульном storage `mobileapp`
- привязка загруженных файлов идёт через `FILES` в `AppTable`
- preview для designer file upload строится через `CFile::ResizeImageGet(...)`
- `updateConfig(...)` фильтрует параметры через `ConfigMap`, лишние ключи молча выкидываются

## JN/native контур

### `/bitrix/services/mobileapp/jn.php`

Это подтверждённый вход в JN delivery layer.

Подтверждены режимы:

- `type=component`
- `type=extension`
- `onlyTextOfExt=true`
- `reload`

Для `type=component` сервис вызывает:

- `bitrix:mobileapp.jnrouter`

Для `type=extension` сервис:

- загружает `Extension::getInstance($componentName)`
- собирает dependency chain
- возвращает JS и lang-expression
- может прокидывать `availableComponents` для component dependencies

### `bitrix:mobileapp.jnrouter`

Подтверждены ключевые особенности:

- при `needAuth=true` пытается авторизовать через `LoginByHttpAuth()`
- для неавторизованного клиента отдаёт `401 Not Authorized`
- возвращает JSON с `bitrix_sessid`
- при отсутствии компонента ставит header `BX-Component-Not-Found: true`
- при совпадении версии клиента и компонента отдаёт `304 Not Modified`

Это важно для диагностики:

- “ничего не обновляется” может быть штатным `304`, а не багом сборки
- “компонент не грузится” может быть не в коде, а в отсутствии workspace/component registration

### `\Bitrix\MobileApp\Janative\Manager`

Подтверждены методы:

- `getExtensionPath($ext)`
- `getExtensionResourceList($ext)`
- `getComponentVersion($componentName)`
- `getComponentPath($componentName)`
- `getAvailableComponents()`
- `getComponentByName($name)`
- `isBundleEnabled()`

Подтверждённая механика:

- workspaces приходят через события `mobileapp:onJNComponentWorkspaceGet`
- manager ищет компоненты в `<workspace>/components/`
- extensions ищутся в `<workspace>/extensions/`
- bundle toggle берётся из option `mobileapp:jn_bundle_enabled`

Практическое правило:

- если JN component/extension не находится, сначала проверь workspace events и файловую структуру, а не только URL

## Mobile init и runtime

Подтверждён `\Bitrix\MobileApp\Mobile`.

Ключевые методы/точки:

- `Init()`
- `isAppBackground()`
- `setWebRtcSupport(...)`
- `setBXScriptSupported(...)`
- `getDevice()`
- `_Init()` регистрирует:
  - `main:OnBeforeEndBufferContent` -> init scripts
  - `main:OnEpilog` -> mobile init

Что важно:

- платформа и API version определяются по cookies/UA, а не только по request params
- модуль выставляет `BX-Cordova-Version`
- `MOBILE_API_VERSION`, `PG_VERSION`, `MOBILE_DEVICE`, `IS_WEBRTC_SUPPORTED`, `IS_BXSCRIPT_SUPPORTED` реально участвуют в runtime

## Admin mobile и меню

В `include/defines.php` подтверждены:

- `MOBILE_APP_ADMIN`
- `MOBILE_APP_ADMIN_PATH = /bitrix/admin/mobile`
- `MOBILE_APP_MENU_FILE = /bitrix/admin/mobile/.mobile_menu.php`
- `MOBILE_APP_BUILD_MENU_EVENT_NAME = OnBeforeAdminMobileMenuBuild`

`include/prolog_admin_mobile.php` и `include/prolog_admin_mobile_before.php` подтверждают типовой маршрут:

- подключается `bitrix:mobileapp.auth`
- стартовая страница берётся из `CAdminMobileMenu::getDefaultUrl(...)`

Это значит:

- задачи “добавить раздел в мобильную админку” надо вести через event `OnBeforeAdminMobileMenuBuild`
- не надо путать это меню с обычным `OnBuildGlobalMenu`

## Push settings и device tokens

### `CAdminMobilePush`

Подтверждены методы:

- `addData($branchName, $arData)`
- `getData($path = "")`
- `getOptions($path = "")`
- `saveOptions($path = "", $arOpts)`
- `OnAdminMobileGetPushSettings()`

Подтверждены события:

- `mobileapp:OnBeforeAdminMobilePushOptsLoad`
- `mobileapp:OnAdminMobileGetPushSettings`

### `mobileapp.push.token/call.ajax.php`

Подтверждено:

- endpoint требует модуль `pull`
- использует `CPullPush::GetList/Add/Update/Delete`
- поддерживает действия `register` и `remove`

Практически:

- при отсутствии `pull` это не “битый mobileapp”, а ожидаемое ограничение текущего core
- `register` и `remove` используют разные request keys для device id: `uuid` и `device_uuid`

## Стандартные компоненты

Подтверждены компоненты:

- `bitrix:mobileapp.auth`
- `bitrix:mobileapp.jnrouter`
- `bitrix:mobileapp.push`
- `bitrix:mobileapp.menu`
- `bitrix:mobileapp.list`
- `bitrix:mobileapp.filter`
- `bitrix:mobileapp.edit`
- `bitrix:mobileapp.demoapi`
- `bitrix:mobileapp.designer.file.input`
- `bitrix:mobileapp.interface.checkboxes`
- `bitrix:mobileapp.interface.radiobuttons`
- `bitrix:mobileapp.interface.topswitchers`
- `bitrix:mobileapp.colorpicker`
- `bitrix:mobileapp.list.enclosed`

Это означает:

- для mobile UI-экранов сначала проверяй готовый стандартный компонент
- custom JS-экран с нуля здесь часто не нужен

## Gotchas

- `mobileapp` и `pull` - не одно и то же. Base mobile route у нас активен уже сейчас, даже если часть push-функций условна.
- Для JN-задач сначала различай component route и extension route; у них разные контракты ответа.
- `304 Not Modified` и `BX-Component-Not-Found` - штатные сигналы модуля, а не “странности nginx”.
- Mobile admin menu строится через `OnBeforeAdminMobileMenuBuild`, а не через общий admin menu event.
- Для designer app не храни конфиг “рядом в local/” по привычке, если задача на самом деле про модульный app storage.
