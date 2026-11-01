# Eval-набор бытовых Bitrix-запросов

Используй при доработке compact-версии. Оцени: правильный route, нет плохого первого шага, есть полезный Bitrix-native ответ по `answer-contracts.md`. Если ответ должен показать “где проверить в проекте”, grep-команды бери из `core-grep-cookbook.md`.

| ID | Prompt | Expected route | Must not start with |
|---|---|---|---|
| B001 | Как в PHP поставить meta title в Битриксе? | `developer-primitives`, `first-answer-pitfalls`, `developer-cards`, `components-admin-ui`, `search-seo-ops` | ручной `<meta name="title">` |
| B002 | Где менять meta description? | primitives/cards + search/seo | meta руками в каждом файле |
| B003 | Как добавить canonical на детальной? | cards + search/seo + commerce if confirmed | правка ядра component |
| B004 | Как подключить CSS? | Asset/cards/components-admin-ui | echo `<link>` |
| B005 | Как подключить JS в компоненте? | Asset/cards/components-admin-ui | random inline script |
| B006 | Как добавить OG meta? | AddHeadString/Asset/search-seo | echo в body |
| B007 | Как сделать редактируемый текст? | IncludeFile/cards | hardcode text |
| B008 | Как вывести включаемую область? | IncludeFile/cards | custom mini-CMS |
| B009 | Как добавить хлебную крошку? | AddChainItem/cards | manual breadcrumbs HTML |
| B010 | Почему крошки дублируются? | cards/components | clear all cache first |
| B011 | Как получить текущего пользователя? | `$USER`/users-security | `$_SESSION` |
| B012 | Показать блок авторизованным | `$USER`, cache caveat | personalized cached HTML |
| B013 | Как получить GET-параметр? | Context request | raw `$_REQUEST` |
| B014 | Как обработать POST? | request + sessid/security | no CSRF |
| B015 | Добавить параметр к URL | `GetCurPageParam` | concat `REQUEST_URI` |
| B016 | Подключить iblock | `Loader::includeModule` | call API before include |
| B017 | Проверить sale | module dir + Loader | assume sale exists |
| B018 | Сделать 404 | `CHTTP::SetStatus`, `ERROR_404`, `404.php` | echo 404 |
| B019 | 404 отдаёт 200 | status/routing/component | redirect home first |
| B020 | Redirect after form | `LocalRedirect`, no output | JS redirect first |
| B021 | Вывести картинку элемента | `CFile::GetPath/ResizeImageGet` | hardcode `/upload` |
| B022 | Сделать превью | `ResizeImageGet` | HTML width/height only |
| B023 | Вывести свойство инфоблока | component params/arResult/API | SQL property table |
| B024 | PROPERTY пустой | params/cache/result_modifier | assume property exists |
| B025 | Изменения не видны | component/managed/tagged cache + `/bitrix/html_pages/` + `X-Bitrix-Composite` + second request/cache pass | disable all cache |
| B026 | Кешировать компонент | cache keys, `StartResultCache`, отличие component cache от composite | cache user-specific data |
| B027 | Чужие данные в кеше | personalization, `CACHE_GROUPS`, `createFrame`/`FrameHelper`, `/bitrix/html_pages/` | clear cache only |
| B028 | Отправить письмо | mail events/templates | PHP `mail()` first |
| B029 | Форма не шлёт письмо | event/template/SITE_ID/agents | “SMTP сломан” first |
| B030 | AJAX в компоненте | project ajax/controller + sessid | endpoint without sessid |
| B031 | Обработчик события | EventManager/local module | code in template |
| B032 | Где писать класс | local module/project namespace | edit core classes |
| B033 | Добавить агента | CAgent/project scheduler | random cron only |
| B034 | Очистить кеш инфоблока | tagged/managed cache | delete all cache first |
| B035 | Путь к ресурсу шаблона | `$this->GetFolder()` | unverified `GetTemplatePath` |
| B036 | Пагинация списка | PageNavigation/NavStart | raw LIMIT only |
| B037 | Вторая страница пустая | filter/count/sort/nav/cache | page size tweak only |
| B038 | Добавить lang-фразу | `Loc::getMessage` | hardcode reusable string |
| B039 | Пользовательское поле | UF API/migration | manual DB change |
| B040 | HL-блок справочник | highloadblock API/migration | raw table only |
| B041 | Обновить цену | catalog API after module check | SQL price update |
| B042 | Статус заказа | sale API after module check | SQL order update |
| B043 | Обмен 1С | checkauth/init/file/import/logs | “just upload XML” |
| B044 | Товар есть в админке, нет на сайте | visibility chain + catalog/1C refs | clear cache only |
| B045 | REST webhook | scopes/auth/permissions | token in public template |
| B046 | Сделай аудит проекта и обнови BITRIX_PROJECT_CONTEXT.md | behavior-routing + project-intake + core-grep + template | общие советы без чтения проекта |
| B047 | В проекте уже есть BITRIX_PROJECT_CONTEXT.md | project-intake + answer-contracts + core-grep | верить снимку проекта вслепую |
| B048 | Можно ли считать магазин runtime-проверенным? | runtime smoke + shop matrix + release gate | “да, покрыто справочником” |
| B049 | P1 smoke без safe write sandbox | runtime smoke | запускать заказ/оплату на production |
| B050 | CommerceML без production 1С | runtime smoke + commerce | подключить реальную 1С |
| B051 | REST webhook scopes неизвестны | runtime smoke + REST/webservice | сохранить токен в evidence |
| B052 | Проверить evidence pack перед релизом | release gate + runtime smoke validator | принять папку без validation |
| B053 | Композитный кеш компонента | `setFrameMode(true)` = vote, `createFrame` = dynamic, headers verification | say setFrameMode makes dynamic |
| B054 | Корзина моргает при композите | dynamic area stub, `CACHE_TYPE=N`, guest/user A/user B | clear all cache only |
| B060 | Аудит оптимизаций проекта | `search-seo-ops` + static helper + evidence pack | Redis/CDN/clear all cache без чтения проекта |
| B061 | N+1 в шаблоне каталога | `search-seo-ops` db-orm + perfmon + preload/map | index/raw SQL first |
| B062 | Каталог/filter тормозит после импорта | `commerce-shop` shop-performance + `search-seo-ops` agents/perfmon | full production rebuild first |
| B063 | Agents/imports грузят сайт | `search-seo-ops` agents-imports + operations/stepper | `set_time_limit(0)` as fix |
| B064 | Тяжёлые images/JS | `search-seo-ops` frontend-assets + components-admin-ui | CDN first |
| B065 | Update-safe кастомизация админки | components-admin-ui + php-architecture/events | edit core/admin files first |
| B066 | Вкладка в форме админки | components-admin-ui + events + content-data if iblock | CSS/admin_header first |
| B067 | Групповое действие/кнопка списка | components-admin-ui + users-security | no sessid/rights |
| B068 | Раздел в меню админки | components-admin-ui + php-architecture/modules | edit `.left.menu.php`/core menu |
| B069 | Где хранить admin-страницы | components-admin-ui + php-architecture/modules | business logic in `/bitrix/admin` |
| B070 | Куда положить global block | project-layout-and-includes + project-intake + components | universal `/include`/rigid placement without project facts |
| B071 | `.section.php` для name/SEO | project-layout-and-includes + components/search-seo | mix `$sSectionName`/properties/SetTitle or manual meta |
| B072 | `.env`/`Option`/constant/lookup для `IBLOCK_ID` | project-configuration + php/content | add Dotenv automatically or lookup only by `CODE` |
| B073 | Query flag для reset registry cache | project-configuration + users-security/search-seo | anonymous cache reset |
| B074 | Изменить выборку stock component | project-layout-and-includes + components-admin-ui + php-architecture | copy core `component.php` into template |

Gate: перед релизом бытового слоя выбрать минимум 15 prompt из разных доменов; `fail = 0`. Полный checklist — `release-gate.md`.

## Диагностические границы

| ID | Prompt | Expected references | Must say | Must not say first |
|---|---|---|---|---|
| B075 | Preflight нашёл папку modules. Можно считать sandbox проверенным? | `release-gate` | Только static candidate; runtime и регистрация модулей не проверены | Все smoke пройдены |
| B076 | Прикрепи вывод сканера с URL webhook и исходным PHP | `release-gate` | Без исходных строк и приватных частей URL; проверить пути/hostname вручную | Публиковать raw payload |
| B077 | В summary pass, а в файле blocked — можно выпускать? | `release-gate` | Отклонить противоречие, сверить точную локальную ссылку и ID | Доверять только summary |
| B078 | Файл с логом слишком большой для проверки — пропустим? | `release-gate` | Отказ автоматического gate, подготовить обезличенный текст и отдельную проверку оригинала | Проверка секретов пройдена |
| B079 | Повтори генерацию поверх заполненных доказательств | `release-gate` | Без force отказ без перезаписи; force только осознанно, static report сохраняется | Молча перезаписать pack |
| B080 | Как посчитать элементы, не загружая список? | `iblocks` / `content-data` | Передать [] третьим аргументом CIBlockElement::GetList, читать скаляр; сохранить фильтр списка и проверить 0/несколько элементов. | Вызвать Fetch на COUNT или принять обычную выборку за число. |
| B081 | Дочерняя запись вернула ошибку Result, но родитель сохранился — почему? | `orm` / `php-architecture` | Неуспешный Result не бросает исключение сам; проверить дочерний результат и откатить собственную транзакцию до commit, обработать Throwable. | Коммитить потому, что исключения не было. |
| B082 | Можно отправить webhook из OnAfterAdd внутри транзакции? | `orm` / `php-architecture` | Не считать событие commit: отложить внешний эффект до успешного завершения операции либо использовать согласованный transactional outbox. | OnAfterAdd гарантирует сохранность после любого rollback. |
| B083 | Почему ORM LIMIT 20 возвращает меньше 20 карточек? | `orm` / `php-architecture` | JOIN размножает строки до LIMIT; отделить страницу уникальных ID от загрузки отношений, проверить полный набор значений и стабильный порядок. | Добавить DISTINCT ко всему select или увеличить LIMIT наугад. |
| B084 | После перехода на ORM посетителям видны черновики: что проверить? | `iblocks` / `content-data` | Сопоставить со stock public selection, проверить getPublicElementsOrmFilter и отдельно права, активность, даты, сайт и кеш. | Считать ACTIVE=Y полной моделью публикации и доступа. |
| B085 | Как обновить одно свойство и очистить TAGS, не потеряв остальные? | `iblocks` / `content-data` | Использовать SetPropertyValuesEx с нужными ключами, TAGS=false; после записи перечитать значения, не проверять isSuccess у null. | Передать неполный набор в SetPropertyValues без PROPERTY_CODE. |
| B086 | Как удалить два фото и добавить одно в множественное свойство? | `iblocks` / `content-data` | Прочитать связи, проверить принадлежность элементу, сформировать один пакет удаления/добавления и перечитать новые value IDs. | Два последовательных удаления по старым value IDs или прямой CFile::Delete. |
| B087 | Обработчик OnAfterIBlockElementUpdate не видит запись через Ex — почему? | `iblocks` / `content-data` | Трассировать отдельные property events; выбрать нужную фазу, scope и защиту повторного вызова, не подменять before событие post-save. | Добавить второй Update ради запуска обработчика. |
| B088 | Вариант имеет разные ID на dev/prod: как перенести значение? | `iblocks` / `content-data` | Разрешить XML_ID внутри конкретного свойства, проверить одну точную запись и сохранить её локальный ID; проверить повтор миграции. | Копировать dev ID или искать первый вариант по подписи. |
| B089 | Можно добавить свойство VERSION=2 через PropertyTable::add? | `iblocks` / `content-data` | Выбрать CIBlockProperty API, согласовать миграцию схемы/значений и проверить чтение новым процессом; ORM метаданных оставить для чтения. | Прямой INSERT метаданных и ручное создание одной колонки. |
| B090 | Можно поменять количество в оформленном заказе и вызвать basket->save? | `sale` / `commerce-shop` | Нет: загрузить заказ, изменить его корзину и согласованные зависимые сущности, проверить Result и сохранить Order. | Сохранить только basket заказа или обновить b_sale_basket. |
| B091 | В CLI подставить userId в loadItemsForFUser — правильно? | `sale` / `commerce-shop` | Нет: отдельно разрешить FUSER целевого пользователя и site, обработать отсутствие; web-клиент не выбирает чужого владельца. | Считать USER_ID и FUSER_ID взаимозаменяемыми. |
| B092 | У одного товара две строки с разной гравировкой: как изменить одну? | `sale` / `commerce-shop` | Выбрать конкретную строку в авторизованной корзине, сохранить её свойства; не искать по одному PRODUCT_ID. | Обновить все строки товара или привести basket code к числу. |
| B093 | Почему в заказе есть системная отгрузка и можно ли её удалить? | `sale` / `commerce-shop` | Это часть модели распределения: не удалять; работать с обычными Shipment и сверять quantities с корзиной. | Удалить системную отгрузку или отметить её как доставленную. |
| B094 | Пришло подтверждение одной из двух оплат — отметить весь заказ? | `sale` / `commerce-shop` | Подтвердить только найденный Payment после проверки callback и повтора; сохранить Order, не трогать вторую оплату и отгрузки. | foreach всех оплат setPaid(Y), затем DEDUCTED всем отгрузкам. |
| B095 | После купона сумма заказа изменилась, а Payment остался прежним — что делать? | `sale` / `commerce-shop` | Проверить final calculation и Result, согласовать неоплаченную часть с итогом; paid сумму не переписывать, затем save/reload. | Считать doFinalAction сохранением или менять уже подтверждённую оплату. |
| B096 | В одном CLI-процессе создаются заказы разных покупателей: что с купонами? | `sale` / `commerce-shop` | Изолировать контекст manager по заказу/владельцу и режиму, проверить переинициализацию и применение; не наследовать предыдущий coupon state. | Один глобальный MODE_CLIENT на весь пакет покупателей. |
| B097 | Доставка существует по ID, но почему её нельзя принять из POST? | `sale` / `commerce-shop` | Проверить ограничения для текущей заполненной отгрузки и клиентский режим, затем расчёт; ID из запроса не доказательство доступности. | Считать getById успешной проверкой или принять цену доставки из браузера. |
| B098 | Поставить CUSTOM_PRICE=Y, чтобы цена перестала меняться? | `sale` / `commerce-shop` | Только для согласованной ручной котировки; иначе разобраться с provider. Проверить скидки, налоги, валюту, refresh и серверный источник суммы. | Копировать PRICE и CUSTOM_PRICE из POST или отключать provider ради симптома. |
| B099 | В OnSaleOrderSaved меняю поле и вызываю save: почему цикл? | `sale` / `commerce-shop` | Изменение перенести в подходящую before-фазу, реакцию ограничить IS_NEW/VALUES; внешние повторы дедуплицировать устойчивым ключом. | Добавить безусловный save в Saved или считать IS_NEW защитой от любого повтора. |
| B100 | В batch третья команда упала: первые две отменились? | `rest` / `integrations-rest` | Нет: разобрать результаты по ключам, учитывать halt; сохранить успешные операции и определить безопасный повтор остальных. | Считать HTTP 200 полным успехом или halt=1 транзакционным откатом |
| B101 | В списке нет total: как дочитать все страницы? | `rest` / `integrations-rest` | Следовать next → start, разбирать форму result конкретного метода и не менять сортировку/фильтр. | Остановиться после первой страницы или считать count(result) количеством записей |
| B102 | Можно весь старый REST-клиент перевести добавлением /api/ в URL? | `rest` / `integrations-rest` | Нет: проверить доступность и схему каждого метода новой версии, затем адаптировать клиент. | Объявить все классические методы доступными в REST 3.0 |
| B103 | Выбран scope crm, но вебхук не читает чужую сделку — отключить проверку? | `rest` / `integrations-rest` | Нет: проверить права владельца на сделку и scope отдельно, использовать разрешённую учётную запись. | Считать scope автоматическим правом на все объекты или опубликовать URL в браузере |
| B104 | Два воркера одновременно получили expired_token: что делать? | `rest` / `integrations-rest` | Сериализовать refresh по записи авторизации, сохранить пару атомарно, ожидающему перечитать и повторить с новым access_token. | Независимо обновлять токены в каждом воркере без ограничения повторов |
| B105 | Портал сменил домен: создавать новую запись клиента? | `rest` / `integrations-rest` | Найти установку по member_id и приложению, проверить авторизационные данные и обновить client_endpoint. | Хранить tenant только по domain или отправить секрет на URL из неподтверждённого события |
| B106 | Пришёл ONAPPUNINSTALL без access_token: удалять данные клиента? | `rest` / `integrations-rest` | Только после сверки application_token с сохранённым секретом нужной установки; неизвестное событие отклонить. | Доверять одному имени события, member_id или домену в POST |
| B107 | Три обновления сделки дали одну offline-запись — события потерялись? | `rest` / `integrations-rest` | Одинаковые ключи объединяются; использовать очередь для синхронизации актуального состояния, не как полный аудит. | Считать каждую запись ровно одной бизнес-операцией и восстанавливать всю историю по очереди |
| B108 | Воркер упал сразу после event.offline.get: очередь сохранит события? | `rest` / `integrations-rest` | При default clear=1 — нет; использовать разрешённое резервирование clear=0 и отдельное подтверждение. | Считать get чистым чтением или повторять пакет с clear=1 и маленьким limit |
| B109 | Все записи пакета упали: отправить clear с message_id=[]? | `rest` / `integrations-rest` | Нет: пустой список удалит пакет. Не подтверждать ошибки; проверить process_id и фиксировать только успешные записи. | Использовать пустые параметры как безопасный no-op |
| B110 | event.offline.error вернул true, но ошибка не появилась — почему? | `rest` / `integrations-rest` | Проверить MESSAGE_ID, принадлежность process_id и непустой список; читать ошибочную ветку error=1. | Передать ID сделки вместо MESSAGE_ID или чужой process_id и довериться true |
| B111 | После operating_reset_at метод всё ещё заблокирован: менять токен? | `rest` / `integrations-rest` | Нет: часть временного окна могла остаться; снизить нагрузку и проверить operating, не обходить блокировку токенами. | Ускорить параллельные повторы или объявить единый лимит для любого Битрикс24 |
| B112 | Можно передать FILE_ID из disk.file.get в любое файловое поле? | `rest` / `integrations-rest` | Нет: выяснить нужный тип идентификатора и формат поля, выполнить загрузку/прикрепление по контракту метода. | Подменять Disk ID значением FILE_ID или Base64 локальным путём |
| B113 | DOM загрузился, но BX24.isAdmin() false у администратора — что проверить? | `rest` / `integrations-rest` | Подключение BX24.js, запуск во фрейме приложения и выполнение после BX24.init. | Считать DOMContentLoaded готовностью авторизации или зашить admin-токен в HTML |
| B114 | event.bind успешен, но новое приложение не получает события — где причина? | `rest` / `integrations-rest` | Проверить завершение установки и INSTALLED; не путать мастер установки с первым запуском пользователя. | Безусловно завершать проваленный мастер или ждать JS finish в REST-only обработчике |
| B115 | В options пришёл ID сделки: можно сразу читать её своим admin-токеном? | `rest` / `integrations-rest` | Нет: проверить конкретный placement, тип/ID и права текущего пользователя на backend. | Считать клиентский options доказательством доступа или ожидать callback от placement.info |
| B116 | Сервер сохранил user.option.set, но второй сотрудник не видит настройку — почему? | `rest` / `integrations-rest` | Настройка принадлежит пользователю токена; выбрать персональный либо общий app.option слой осознанно. | Ожидать глобальное действие user.option.set или удаление ключа пустой строкой |
| B117 | feature.get для придуманного CODE вернул Y: функция точно существует? | `rest` / `integrations-rest` | Нет: метод не проверяет существование кода. Использовать опубликованные CODE и проверять сам метод. | Привести N к true или объявить поддержку по Y неизвестного кода |
| B118 | HttpClient получил timeout после создания заказа во внешней системе: повторить POST? | `http` / `php-architecture` | Не вслепую: операция могла выполниться; сверить внешний ключ/результат или безопасную идемпотентность. | Считать любой timeout гарантией, что сервер не получил запрос |
| B119 | Два воркера одновременно создали объект с одним Idempotency-Key — дубль невозможен? | `rest` / `integrations-rest` | Возможен: заголовок не является конкурентным lock. Сериализовать и учитывать версию REST, тело и срок хранения. | Обещать exactly-once навсегда или использовать заголовок как защиту классического REST |
| B120 | Почему второй запрос компонента выводит HTML дважды? | `components` / `components-admin-ui` | Проверить шаблон вне StartResultCache: на hit HTML уже выведен. Разделить HTML и data-only режимы. | Безусловно исполнять шаблон после выдачи HTML-кеша |
| B121 | Убрал CURRENT_USER из cache keys: имя теперь безопасно в общем HTML? | `components` / `components-admin-ui` | Нет: HTML уже содержит имя; изменить границу/ключ кеша, не только состав arResult. | Считать cache keys механизмом очистки персонального HTML |
| B122 | Где ставить заголовок из результата, чтобы он работал при тёплом кеше? | `templates` / `components-admin-ui` | В component_epilog, предварительно сохранив нужные значения; не в result_modifier или недоказанном component_prolog. | Обещать автоматический вызов component_prolog с готовым arResult |
| B123 | Правлю local/components/.../templates, но сайт показывает старый вид: почему? | `templates` / `components-admin-ui` | Проверить переопределение в активном site-template и шаблоне комплексного родителя, затем кеш. | Утверждать, что любой local/components template всегда приоритетнее site-template |
| B124 | У компонента один arParams, но разные региональные цены: почему смешались? | `components` / `components-admin-ui` | Добавить нормализованный регион/контекст доступа в additionalCacheID и проверять права до кеша. | Читать контекст только внутри miss и считать CACHE_GROUPS автоматической защитой |
| B125 | ID подписан компонентом: можно пропустить проверку прав в AJAX? | `components` / `components-admin-ui` | Нет: проверить актуального пользователя и объект; подпись защищает целостность параметров, не полномочия. | Поместить секрет в подпись или доверять всему data рядом с ней |
| B126 | Вызвал vendor:widget через runAction: почему action не найден? | `components` / `components-admin-ui` | Разделить модульный и компонентный диспетчер, выбрать mode по месту реализации действия. | Подменить компонентный маршрут модульным либо обращаться напрямую к файлу ajax.php |
| B127 | Авторизованный пользователь передал чужой userId/id: допустимо? | `events-routing` / `php-architecture` | Нет без отдельного разрешения; ограничить запись/чтение серверным правилом и тем же правилом count. | Доверять userId клиента или возвращать глобальный total приватного списка |
| B128 | getList не проходит HttpMethod, хотя имя верное — причина? | `events-routing` / `php-architecture` | Сверить default POST клиента с GET фильтром; явно указать GET и обработать reject. | Убрать серверный фильтр ради несовпадения клиента или бесконечно повторять мутацию |
| B129 | У limit тип int — значит -1 и миллион уже безопасны? | `events-routing` / `php-architecture` | Нет: проверить бизнес-диапазон и остановить запрос при нарушении, типизацию не считать валидацией. | Передать любой integer в limit/offset без ограничений |
| B130 | Будет ли iblock_id_el_17 сам сброшен после Update? | `cache-infra` / `search-seo-ops` | Без подтверждённого invalidator нет; выбрать штатный тег инфоблока или реализовать парный проектный сброс. | Считать любое похожее имя встроенным тегом |
| B131 | Почему Option::get без siteId вернул значение текущего сайта? | `modules-loader` / `php-architecture` | Не считать пропуск аргумента глобальным чтением; задать сайт либо пустую общую область явно. | Убирать четвёртый аргумент ради гарантированно общего значения |
| B132 | Как не перезаписать сохранённый ноль при установке default? | `modules-loader` / `php-architecture` | Получить реальное значение и сравнить с null строго; get с fallback не доказывает наличие записи. | Если empty(Option::get(...)), записать default |
| B133 | Письмо поставилось в очередь, но ORDER_ID пуст — что проверить первым? | `mail-notifications` / `content-modules` | Ключ C_FIELDS в D7 и соответствие макросу шаблона; успешная очередь не подтверждает содержимое. | Передавать FIELDS по аналогии с другим API |
| B134 | Можно ли без изменений передать массив lid из CEvent в Event::send? | `mail-notifications` / `content-modules` | Нет по документированному контракту: D7 LID — строка с ID через запятую. | Считать массив сайтов одинаковым аргументом обоих API |
| B135 | Почему callback OnBeforeEventSend с массивами не совместим с регистрацией? | `mail-notifications` / `content-modules` | Согласовать legacy-сигнатуру и addEventHandlerCompatible; не заменять callback объектом Event вслепую. | Оставить объектный режим для ссылочных массивов |
| B136 | Нужно не создавать событие определённого типа — какой hook? | `mail-notifications` / `content-modules` | OnBeforeEventAdd, ограниченный типом события; проверить отсутствие новой записи и сохранение прочих типов. | Использовать OnBeforeEventSend как запрет записи b_event |
| B137 | Почему с MESSAGE_ID письмо пришло не на выбранном языке? | `mail-notifications` / `content-modules` | Языковой фильтр не выполняется при явном ID; проверить язык выбранного шаблона и mapping окружения. | Считать languageId гарантией языка при любом MESSAGE_ID |
| B138 | Защитит duplicate=N от двух одинаковых CEvent::Send? | `mail-notifications` / `content-modules` | Нет: это копия на адрес из настроек, два вызова могут создать два события. | Использовать duplicate как ключ дедупликации |
| B139 | Почему при отправке сохранённого файла по пути появилась ещё одна копия? | `mail-notifications` / `content-modules` | Путь сохраняется повторно; использовать разрешённый ID CFile и согласовать срок жизни с очередью. | Передавать GetPath как локальный путь или сразу удалять файл асинхронного письма |
| B140 | Можно ли разрешить загрузку по type=image/jpeg из запроса? | `import-export` / `content-data` | Нет: это поле клиента; проверить содержимое на сервере и политику расширений/размеров. | Считать MIME браузера доказательством JPEG |
| B141 | CheckFile вернул строку: можно сохранять? | `import-export` / `content-data` | Нет: остановить сохранение; пустой результат допускает следующий этап проверки. | Трактовать непустой текст CheckFile как успешную проверку |
| B142 | Почему после ResizeImageGet отсутствует width? | `import-export` / `content-data` | Проверить bInitSizes=true и успешность вызова; не подменять размеры файла рамкой. | Читать width/height без bInitSizes или растягивать до рамки |
| B143 | Появится ли запись b_file после обычного copy в upload? | `import-export` / `content-data` | Нет по контракту SaveFile; для регистрации нужен соответствующий API. | Считать размещение в upload автоматической регистрацией |
| B144 | Можно ли передать любой путь из формы в MakeFileArray? | `import-export` / `content-data` | Нет: определить разрешённый тип источника и корень; сайт-relative путь явно преобразовать. | Полагаться на автоматическое добавление DOCUMENT_ROOT или разрешать любой URL/путь |
| B145 | Как прикрепить новое изображение при Add элемента? | `import-export` / `content-data` | Передать проверенный файловый массив; дать API элемента сохранить файл, проверить ID/LAST_ERROR. | Предварительно SaveFile и передать его ID как новый DETAIL_PICTURE |
| B146 | Безопасно ли слить POST с файловым массивом, включая old_file/del? | `import-export` / `content-data` | Нет: служебные ключи задаёт сервер после проверки владельца и намерения удаления. | Доверять old_file из POST или передавать del=N как ложь |
| B147 | Маленький по байтам файл имеет огромные dimensions — достаточно CheckFile? | `import-export` / `content-data` | Нет: ограничить геометрию CheckImageFile и ресурсы обработки до ресайза. | Считать лимит байтов ограничением числа пикселей |
| B148 | Можно ли после IsAuthorized пометить все fileId как свои? | `file-upload-modern` / `components-admin-ui` | Нет: подтвердить каждый файл и операции по серверному объекту-владельцу; не выдумывать разрешающую модель. | Безусловный markAsOwn и canRemove=true |
| B149 | Почему название A & B выгрузилось как A &amp; B? | `import-export` / `content-data` | GetNext преобразовал HTML; выбрать Fetch и сериализовать исходное значение. | Использовать GetNext как универсальный raw fetch |
| B150 | Почему new DateTime с Y-m-d строкой работает на одном сайте и падает на другом? | `http` / `php-architecture` | Не задан format, используется culture; указать Y-m-d H:i:s либо нужный контракт строки. | Полагаться на автоматическое распознавание ISO конструктором |
| B151 | Вернёт ли format серверное время после setTimeZone(UTC)? | `http` / `php-architecture` | Нет, он форматирует в установленной зоне объекта; для серверной зоны установить её явно. | Считать format или disableUserTime принудительной серверной зоной |
| B152 | Почему после расчёта deadline изменился createdAt? | `http` / `php-architecture` | Обе переменные ссылались на один DateTime; клонировать перед add. | Присвоить объект второй переменной и считать его immutable |
| B153 | Как выбрать все записи пользовательского дня на переходе DST? | `http` / `php-architecture` | Построить календарные границы в нужной зоне, привести к storage-контракту, использовать >= и <. | Прибавить 86400 или сравнивать локализованные строки |
| B154 | Можно ли одинаково импортировать UTC через createFromUserTime в web и cron? | `http` / `php-architecture` | Нет: контексты различаются; использовать явный машинный контракт времени. | Повторно применять пользовательский сдвиг к UTC |
| B155 | Можно ли удалить связь с ключом LEFT_ID+RIGHT_ID по одному LEFT_ID? | `orm` / `php-architecture` | Нет: нужен полный primary либо отдельный явно ограниченный сценарий удаления набора. | Передать один scalar или неполный ключ |
| B156 | getTitle вернул null после select ID — надо очистить TITLE в БД? | `orm` / `php-architecture` | Нет: сначала загрузить TITLE; null неполной проекции не доказывает значение в БД. | Сохранить null из незагруженного getter обратно |
| B157 | Защитит ли %s выражение, в которое уже вставлен текст пользователя? | `orm` / `php-architecture` | Нет: отказаться от конкатенации; значения передать фильтром, поля выбрать по allowlist. | Считать ExpressionField универсальным prepared statement |
| B158 | Почему подчёркивание в коде сопоставилось с другим символом? | `orm` / `php-architecture` | Это wildcard LIKE; определить буквальный или шаблонный поиск и явно задать его. | Считать underscore буквальным символом или гарантировать prefix без маски |
| B159 | Почему JOIN-запрос снова обращается к БД при заданном ttl? | `orm` / `php-architecture` | Проверить cache_joins и настройки кеширования; включать лишь с корректной инвалидизацией зависимостей. | Считать ttl достаточным для любого JOIN и любого способа записи |
| B160 | Администратор добавляет клиента в группу: откуда брать существующий набор? | `users` / `users-security` | Из записи клиента по целевому userId, не из USER оператора; проверить право назначения. | Копировать группы администратора клиенту |
| B161 | Как добавить постоянную группу, не сделать временную бессрочной? | `users` / `users-security` | Считать полный GetUserGroupList и сохранить интервалы при записи структурированного groups. | Свести все членства к одним ID |
| B162 | Группу удалили, но открытая сессия ещё видит доступ — почему? | `users` / `users-security` | Запись членства не равна обновлению активной сессии; проверить механизм отзыва и повторную авторизацию. | Обещать немедленный отзыв во всех сессиях по SetUserGroup |
| B163 | Достаточно ли ThrowException внутри void-обработчика до Add? | `users` / `users-security` | Нет: документированный отказ — сообщение и return false; сигнатура должна разрешать этот результат. | Оставить void и считать ThrowException остановкой исполнения PHP |
| B164 | Можно ли отправлять welcome при каждом OnAfterUserAdd? | `users` / `users-security` | Нет: проверить успешный результат и положительный ID; ошибка попытки тоже достигает after hook. | Считать сам вызов after гарантией создания |
| B165 | Чем создавать пользователей импортом, не меняя сессию администратора? | `users` / `users-security` | CUser::Add; Register относится к публичному потоку с дополнительными эффектами. | Подменить Add методом Register в административном импорте |
| B166 | Можно ли взять первый UserTable::getRow по email и связать заказ/аккаунт? | `users` / `users-security` | Не без проверки уникальности кандидата и политики идентификации; email не универсальный ключ. | Молча выбрать первого пользователя с общим email |
| B167 | Как исправить ошибку передачи первого аргумента CUser::GetList по ссылке? | `users` / `users-security` | Объявить by/order отдельно и передать переменные; не выражения присваивания. | Передать строковый литерал или assignment expression в ссылочный аргумент |
| B168 | Поиск LOGIN=ivan вернул ivan_petrov — ошибка ядра? | `users` / `users-security` | Нет: LOGIN — подстрока; для точного поиска LOGIN_EQUAL или GetByLogin. | Выбирать первую строку подстрочного поиска как точную учётку |
| B169 | Получен OK от SendPassword — пароль уже сменён? | `users` / `users-security` | Нет: создан запрос с контрольной строкой; отдельно выполняется подтверждённая смена. | Обещать новый пароль или считать login+email независимой проверкой личности |
| B170 | После часа простоя десятиминутный агент внезапно повторяется — почему? | `cache-infra` / `search-seo-ops` | Проверить IS_PERIOD=Y и догоняющие интервалы; выбрать N для пересчёта только текущего состояния. | Назначать Y всем задачам ради точности времени |
| B171 | Почему письмо агента уходит с языком/сайтом случайного хита? | `cache-infra` / `search-seo-ops` | Фоновому заданию нужен явный сайт и язык; USER/SITE_ID не считать гарантированными. | Авторизовать клиента внутри агента ради контекста |
| B172 | Как передать текст клиента агенту без включения текста в eval? | `cache-infra` / `search-seo-ops` | Сохранить данные в серверном задании и передать фиксированному методу проверенный ID. | Конкатенировать PHP-вызов из POST с именем метода и аргументами |
| B173 | Как отложить первый запуск агента, не перепутав аргументы дат? | `cache-infra` / `search-seo-ops` | Задать next_exec в требуемом языковом формате; datecheck имеет другой смысл. | Использовать datecheck как единственный контракт времени первого исполнения |
| B174 | Почему helper не нашёл перевод компонента после loadMessages(__FILE__)? | `modules-loader` / `php-architecture` | Проверить, чей путь передан: lazy loading привязано к исходному файлу регистрации. | Считать getMessage поиском рядом с местом каждого вызова |
| B175 | Можно ли в каждом файле объявлять собственный MESS[TITLE]? | `modules-loader` / `php-architecture` | Нет гарантированной изоляции; использовать уникальные префиксные коды. | Полагаться на приватность lang-файла для общего ключа |
| B176 | Безопасно ли echo Loc::getMessage с именем из формы? | `modules-loader` / `php-architecture` | Подстановка не sanitizer; экранировать результат для конкретного контекста вывода. | Считать переведённую строку автоматически HTML-безопасной |
| B177 | Как получить английский текст без выдуманного getMessageByLang? | `modules-loader` / `php-architecture` | Загрузить нужный файл и вызвать getMessage(code, replacements, en). | Вызывать getMessageByLang как гарантированный публичный метод |
| B178 | Почему версия модуля пустая после include стандартного version.php? | `modules-loader` / `php-architecture` | Читать arModuleVersion, а не version; проверить оба обязательных значения. | Считать имя локальной переменной произвольным при штатном формате |
| B179 | Можно ли проверять includeSharewareModule только на truthy? | `modules-loader` / `php-architecture` | Нет: разобрать константы установленного, demo, истёкшего и отсутствующего состояния. | Считать любое ненулевое состояние успешной загрузкой |

| B180 | Почему UF_COLOR раздела не выбирается? | `iblocks` / `content-data` | Задать IBLOCK_ID в фильтре и UF_COLOR в select. | Искать его как PROPERTY_COLOR элемента |

| B181 | Почему счётчик раздела больше списка товаров? | `iblocks` / `content-data` | Согласовать вложенность, активность и даты; не ждать SECTION_CNT. | Считать bIncCnt числом только активных прямых элементов |

| B182 | Почему экспорт с пятым аргументом [] теряет разделы? | `iblocks` / `content-data` | Это лимит десяти; использовать осознанную полную или постраничную выборку. | Считать [] синонимом отсутствия лимита |

| B183 | Как проверить дерево, доступное гостю, из админской сессии? | `iblocks` / `content-data` | PERMISSIONS_BY=0 при включённой проверке прав. | CHECK_PERMISSIONS=N как режим гостя |

| B184 | Почему ребёнок в меню оказывается раньше родителя? | `iblocks` / `content-data` | Проверить порядок дерева: LEFT_MARGIN ASC, не общий SORT. | Восстанавливать иерархию только по отсортированному SORT |

| B185 | Можно ли вызвать Fetch на GetNavChain(..., true)? | `iblocks` / `content-data` | Нет, это массив; сохранить проверку IBLOCK_ID и не ждать UF. | Передавать ноль вместо области и считать результат авторизацией |

| B186 | Можно ли ускорить перенос раздела, записав LEFT_MARGIN напрямую? | `iblocks` / `content-data` | Нет; Update родителя с пересчётом и проверкой результата. | Писать границы SQL или bResort=false без восстановления дерева |
