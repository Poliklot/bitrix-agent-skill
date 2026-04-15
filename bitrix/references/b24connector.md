# Bitrix24 Connector, site buttons и Bitrix24.Network bridge (модуль b24connector)

> Audit note: ниже сверено с текущим `www/bitrix/modules/b24connector` версии `24.0.100`. Подтверждены `\Bitrix\B24Connector\Connection`, `Button`, `Helper`, `Cache`, ORM-таблицы `\Bitrix\B24connector\ButtonTable` и `ButtonSiteTable`, стандартные компоненты `bitrix:b24connector.button.list` и `bitrix:b24connector.openline.info`, а также admin-страницы `buttons`, `chat`, `recall`, `crm_forms`, `open_lines`, `telefonia`.

## Для чего использовать

`b24connector` в этом core - это отдельный интеграционный контур для:

- привязки сайта к Bitrix24/Bitrix24.Network;
- вывода connect button и reconnect/disconnect flow;
- локальной активации виджетов/кнопок, уже созданных в удалённом Bitrix24;
- ограничения показа виджета по сайтам;
- автоподмешивания widget script в public section;
- openline info payload для чата/виджета.

Если задача звучит как:

- “как подключить сайт к Bitrix24”
- “почему виджет Битрикс24 не выводится на сайте”
- “как ограничить кнопку только определёнными SITE_ID”
- “где хранится локальная активация CRM form/openline/callback button”
- “как получить ссылку на настройки телефонии/openlines/webforms/widgets”

то первым маршрутом должен быть `b24connector`, а не абстрактный `rest` или только `socialservices`.

## Архитектура модуля

По текущему ядру:

- модуль регистрирует таблицы:
  - `b_b24connector_buttons`
  - `b_b24connector_button_site`
- installer вешает события:
  - `main:OnBuildGlobalMenu -> \Bitrix\B24Connector\Helper::onBuildGlobalMenu`
  - `main:OnBeforeProlog -> \Bitrix\B24Connector\Helper::onBeforeProlog`
- основной remote bridge идёт через `socialservices`:
  - `ApTable`
  - `ApClient`
  - `CBitrix24NetOAuthInterface`
  - `CSocServBitrix24Net`

Практическое правило:

- сначала разделяй remote Bitrix24 connection и local activation state на сайте
- без `socialservices` модульный connect-flow в текущем core не работает полноценно

## Права и install-контур

Инсталлятор подтверждает:

- уровни прав:
  - `D`
  - `R`
  - `W`

Практически это значит:

- `R` достаточно, чтобы видеть интерфейс и список кнопок
- `W` нужен для connect/disconnect и редактирования module options

## `Connection`

Подтверждён `\Bitrix\B24Connector\Connection`.

Ключевые методы:

- `delete()`
- `getButtonHtml($title = '')`
- `getOptionButtonHtml($title)`
- `getFields()`
- `getDomain()`
- `isExist()`
- `isRestAvailable()`
- `getOpenLinesConfigUrl()`
- `getTelephonyConfigUrl()`
- `getWebformConfigUrl()`
- `getWidgetsConfigUrl()`

Внутренняя логика подтверждает:

- при необходимости модуль сам пытается привязать сайт к Bitrix24.Network через `CSocServBitrix24Net::registerSite($host)`
- данные network-link хранятся в options модуля `socialservices`:
  - `bitrix24net_domain`
  - `bitrix24net_id`
  - `bitrix24net_secret`
- активное подключение берётся из `ApTable::getConnection()`

### REST availability

`isRestAvailable()` подтверждённо:

- использует `ApClient::init()`
- вызывает `app.info`
- кеширует результат на 1 час через cache id `b24connector_rest_status`

Это важно для диагностики:

- “коннект есть, но методы не работают” может быть проблемой тарифа/REST-доступности, а не локального PHP-кода

### Ссылки на конфигурацию в Bitrix24

Подтверждённые методы:

- `getOpenLinesConfigUrl()`
- `getTelephonyConfigUrl()`
- `getWebformConfigUrl()`
- `getWidgetsConfigUrl()`

Подтверждённое поведение:

- сначала пробуют получить данные через REST
- если REST не вернул путь, строят fallback URL по домену подключённого портала

## Типы кнопок и расположения

Подтверждён `\Bitrix\B24Connector\Button`.

Типы:

- `openline`
- `crmform`
- `callback`

Позиции:

- `TOP_LEFT`
- `TOP_MIDDLE`
- `TOP_RIGHT`
- `BOTTOM_RIGHT`
- `BOTTOM_MIDDLE`
- `BOTTOM_LEFT`

Практически это значит:

- тип и location - это не произвольные строки, а ограниченный контракт модуля

## Локальное хранение и site restrictions

### `ButtonTable`

Таблица:

- `b_b24connector_buttons`

Подтверждены поля:

- `ID`
- `APP_ID`
- `ADD_DATE`
- `ADD_BY`
- `NAME`
- `SCRIPT`

Это локальный слой активации на сайте, а не источник истины о существовании remote widget.

### `ButtonSiteTable`

Таблица:

- `b_b24connector_button_site`

Подтверждены методы:

- `getAllRestrictions()`
- `deleteByButtonId($buttonId)`

Смысл:

- per-site доступ виджета хранится отдельно от самой записи кнопки
- отсутствие restriction rows трактуется как “доступно на всех активных сайтах”

## Public injection: `Helper::onBeforeProlog()`

Подтверждён `\Bitrix\B24Connector\Helper::onBeforeProlog()`.

Ключевые особенности:

- в admin section не работает
- если определён `B24CONNECTOR_SKIP === true`, модуль ничего не подмешивает
- берёт активное connection через `Connection::getFields()`
- читает локальные кнопки через `ButtonTable`
- фильтрует их по `ButtonSiteTable::getAllRestrictions()`
- добавляет `SCRIPT` в `AssetLocation::BODY_END`
- дополнительно подмешивает `bitrix:b24connector.openline.info`

Практическое правило:

- если виджет “есть в Б24, но нет на сайте”, проверь не только remote portal, а ещё:
  - есть ли локальная запись в `b_b24connector_buttons`
  - не ограничен ли widget конкретными `SITE_ID`
  - не выставлен ли `B24CONNECTOR_SKIP`

## Admin menu

Подтверждён `\Bitrix\B24Connector\Helper::onBuildGlobalMenu()`.

Модуль добавляет разделы:

- buttons
- chat
- recall
- crm forms
- open lines
- telephony

Это важно для задач:

- “куда пропала админка модуля”
- “почему раздел не виден пользователю”

Сначала проверь module rights `b24connector`, а не только код меню.

## `bitrix:b24connector.button.list`

Это основной admin-компонент для локальной активации remote buttons.

Подтверждённые особенности:

- комбинирует remote `crm.button.list` и local state из `ButtonTable`
- подтягивает список активных сайтов через `CSite::GetList(...)`
- показывает, кто и когда локально активировал кнопку
- использует `ButtonSiteTable::getAllRestrictions()`

Подтверждён AJAX controller `ajax.php` с действиями:

- `activate`
- `deactivate`
- `saveSiteRestrictions`

И проверками:

- module rights
- `POST`
- `check_bitrix_sessid()`

Практический вывод:

- активация виджета на сайте - это отдельное локальное действие поверх remote button
- site restrictions меняются не в Bitrix24-портале, а в локальной таблице `b_b24connector_button_site`

## `bitrix:b24connector.openline.info`

Компонент подтверждён как источник visitor/session payload для openline widget.

Подтверждённые шаги:

- `prepareAuthData()`
- `prepareSessionData()`
- `formatOperatorMessage()`
- `prepareVariableForTemplate()`

Подтверждённое поведение:

- для авторизованного пользователя hash строится из user id и license public hash
- для гостя используется cookie/session `LIVECHAT_GUEST_HASH`
- если установлен `statistic`, подтягиваются searcher/country/first visit данные
- отправляется событие `b24connector:onOpenlineInfoFormatOperatorMessage`

Практически:

- openline info можно кастомно расширять через модульное событие, а не только переписыванием шаблона
- отсутствие `statistic` не ломает компонент, но сужает session context

## Gotchas

- `b24connector` и `socialservices` здесь тесно связаны. Если `socialservices` не подключается, connect-flow и REST layer не заработают как ожидается.
- Наличие кнопки в удалённом Bitrix24 ещё не означает её локальную активацию на сайте.
- Ограничения по сайтам живут в отдельной таблице, не в `SCRIPT` и не в настройках шаблона.
- `B24CONNECTOR_SKIP` штатно выключает public injection; это нужно проверять до поиска “сломался Asset”.
- Для openline/chat задач сначала проверь `bitrix:b24connector.openline.info`, а не выдумывай свой источник user/session payload.
