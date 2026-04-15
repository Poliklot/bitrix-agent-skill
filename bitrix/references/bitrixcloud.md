# Bitrix Cloud: backup, monitoring и remote policy (модуль bitrixcloud)

> Audit note: ниже сверено с текущим `www/bitrix/modules/bitrixcloud` версии `25.0.0`. Подтверждены `CBitrixCloudBackup`, `CBitrixCloudMonitoring`, `CBitrixCloudOption`, `CBitrixCloudWebService`, `CBitrixCloudBackupWebService`, `CBitrixCloudMonitoringWebService`, `CBitrixCloudMobile`, а также `CBitrixCloudBackupBucket` при установленном модуле `clouds`.

## Для чего использовать

`bitrixcloud` в этом core - не “просто настройка облака”. Это отдельный модульный контур для:

- облачного backup-а через policy/webservice Bitrix;
- мониторинга доменов, лицензии и uptime;
- хранения состояния backup/monitoring в собственной таблице `b_bitrixcloud_option`;
- mobile monitoring-экрана в админке;
- интеграции backup-а с временными bucket-ами через `clouds`.

Если задача звучит как:

- “как получить список облачных backup-файлов”
- “где хранится monitoring state”
- “как стартует monitoring на домен”
- “почему bitrix cloud backup не видит bucket”

то первым маршрутом должен быть `bitrixcloud`, а не только `clouds` или общая инфраструктура.

## Архитектура модуля

По текущему ядру:

- у модуля нет `lib/`, рабочий API живёт в `classes/general/*`;
- state хранится в `b_bitrixcloud_option`, а не в `b_option`;
- доступ к remote service идёт через `CBitrixCloudWebService` и наследников;
- backup-маршрут при необходимости завязан на модуль `clouds`.

Практическое правило:

- для backup/monitoring сначала смотри `bitrixcloud`;
- `clouds` подключай как соседний слой только там, где реально нужен bucket/object storage.

## Инсталлятор, права и зависимости

Инсталлятор подтверждает:

- version `25.0.0`;
- задачи:
  - `bitrixcloud_deny`
  - `bitrixcloud_control`
- операции:
  - `bitrixcloud_monitoring`
  - `bitrixcloud_backup`

Зависимости:

- `main:OnAdminInformerInsertItems` -> `CBitrixCloudBackup::OnAdminInformerInsertItems`
- `mobileapp:OnBeforeAdminMobileMenuBuild` -> `CBitrixCloudMobile::OnBeforeAdminMobileMenuBuild`

Что это значит:

- backup умеет светиться в admin informer;
- mobile monitoring меню появляется только при наличии `mobileapp`;
- задачи backup/monitoring надо проверять через `CanDoOperation('bitrixcloud_backup')` и `CanDoOperation('bitrixcloud_monitoring')`.

## `CBitrixCloudOption`

Это собственный storage модуля поверх таблицы `b_bitrixcloud_option`.

Подтверждены ключевые методы:

- `getOption($name)`
- `isExists()`
- `getArrayValue()`
- `getStringValue()`
- `setArrayValue($value)`
- `setStringValue($value)`
- `delete()`

Важно:

- это не `\Bitrix\Main\Config\Option`;
- значения могут храниться как ordered key/value набор;
- модуль кеширует все записи через `CACHED_b_bitrixcloud_option`.

## `CBitrixCloudWebService`

Это базовый HTTP/XML-клиент для policy server.

Подтверждены ключевые методы:

- `setDebug($bActive)`
- `setTimeout($timeout)`
- `getServerStatus()`
- `getServerResult()`
- внутренний `action($action)` с `Bitrix\Main\Web\HttpClient`

Что важно:

- ответ обязательно парсится как XML через `CDataXML`;
- не-200 и XML parse failure превращаются в `CBitrixCloudException`;
- ошибка policy server приходит через `/error/code`.

## Backup-контур

### `CBitrixCloudBackup`

Подтверждены ключевые методы:

- `getInstance()`
- `listFiles()`
- `getQuota()`
- `getUsage()`
- `getLastTimeBackup()`
- `getBucketToReadFile($check_word, $file_name)`
- `getBucketToWriteFile($check_word, $file_name)`
- `clearOptions()`
- `saveToOptions()`
- `loadFromOptions()`

Практически это значит:

- backup state можно брать либо у remote service, либо из сохранённого snapshot-а в `b_bitrixcloud_option`;
- quota, usage и список backup-файлов - штатные методы модуля, а не “надо самому читать XML”.

### `CBitrixCloudBackupWebService`

Подтверждены методы:

- `actionGetInformation()`
- `actionReadFile($check_word, $file_name)`
- `actionWriteFile($check_word, $file_name)`
- `actionAddBackupJob($secret_key, $url, $time = 0, $weekdays = [])`
- `actionDeleteBackupJob()`
- `actionGetBackupJob()`

Подтверждённые детали:

- URL policy берётся из `bitrixcloud:backup_policy_url` или из store-license домена;
- в запросы уходят `license`, `lang`, `region`, `spd`, `CHHB`, `CSAB`;
- `actionAddBackupJob(...)` жёстко валидирует URL, время и дни недели.

### `CBitrixCloudBackupBucket`

Если установлен `clouds`, доступен `CBitrixCloudBackupBucket extends CCloudStorageBucket`.

Подтверждены методы:

- `getFileName()`
- `getHeaders()`
- `setPublic($isPublic)`
- `unsetCheckWordHeader()`
- `setCheckWordHeader()`

Практический вывод:

- backup-бакет не равен обычному пользовательскому bucket-у `clouds`;
- это временный адаптер поверх `CCloudStorageBucket` с выданными policy server credentials.

## Monitoring-контур

### `CBitrixCloudMonitoring`

Подтверждены ключевые методы:

- `getInstance()`
- `getConfiguredDomains()`
- `getList()`
- `addDevice($domain, $deviceId)`
- `deleteDevice($domain, $deviceId)`
- `getDevices($domain)`
- `startMonitoring($domain, $is_https, $language_id, $emails, $tests)`
- `stopMonitoring($domain)`
- `setInterval($interval)`
- `getInterval()`
- `getMonitoringResults($interval = false)`
- `getAlertsCurrentResult()`
- `getAlertsStored()`
- `storeAlertsCurrentResult()`
- `getWorstUptime($testId = '', $domainName = '')`
- `startMonitoringAgent()`

Что важно:

- допустимые интервалы жёстко ограничены: `7`, `30`, `90`, `365`;
- configured domains берутся из `main:server_name` и активных site domains;
- monitoring devices хранятся в `bitrixcloud` option storage как `domain|device`.

### `CBitrixCloudMonitoringWebService`

Подтверждены методы:

- `actionGetList()`
- `actionStart($domain, $is_https, $language_id, $emails, $tests)`
- `actionStop($domain)`
- `actionGetInfo()`

Подтверждённые детали:

- policy URL берётся из `bitrixcloud:monitoring_policy_url` или из store-license домена;
- `actionStart(...)` передаёт email-ы, test IDs и зарегистрированные devices;
- `actionGetInfo()` использует `monitoring_interval` из option storage.

### `CBitrixCloudMonitoringResult`

Подтверждены:

- `GREEN_LAMP` / `RED_LAMP` статусы;
- `isExpired()`
- `setExpirationTime($time)`
- `loadFromOptions()`
- `saveToOptions()`

А также объекты:

- `CBitrixCloudMonitoringTest`
- `CBitrixCloudMonitoringDomainResult`

Это значит:

- monitoring state реально кешируется локально;
- “сейчас нет данных” может означать не только failure remote API, но и работу из сохранённого snapshot-а.

## Mobile monitoring

Подтверждён `CBitrixCloudMobile`:

- `OnBeforeAdminMobileMenuBuild()`
- `getUserDevices($userId)`

И mobile-компоненты:

- `bitrixcloud.mobile.monitoring.list`
- `bitrixcloud.mobile.monitoring.detail`
- `bitrixcloud.mobile.monitoring.edit`
- `bitrixcloud.mobile.monitoring.push`

Что важно:

- mobile-ветка требует `mobileapp`;
- push device discovery внутри `getUserDevices(...)` дополнительно смотрит модуль `pull`.

## Gotchas

- `bitrixcloud` и `clouds` - не одно и то же. Backup/monitoring route сначала ищи в `bitrixcloud`.
- У модуля свой option storage `b_bitrixcloud_option`; не ищи эти данные в обычных `b_option`.
- `CBitrixCloudBackupBucket` доступен только если включён модуль `clouds`.
- Policy URL может быть переопределён через options; не жёстко предполагай один endpoint.
- Monitoring interval принимает только `7/30/90/365`, всё остальное модуль нормализует.
