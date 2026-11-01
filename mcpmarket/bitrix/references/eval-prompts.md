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
