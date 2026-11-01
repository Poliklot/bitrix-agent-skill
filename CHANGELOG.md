# Changelog

Формат: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), версионирование: [Semantic Versioning](https://semver.org/).

## [Unreleased]

- K124: user_id в Add задаёт автора, не субъекта проверки прав — дополнены знания, full/compact и сценарий B203.

- K123: Check возвращает ошибки и знает редактируемый результат — дополнены знания, full/compact и сценарий B202.

- K122: values=false читает REQUEST, а не пустую форму — дополнены знания, full/compact и сценарий B201.

- K121: HTML-имена ответов зависят от типа вопроса — дополнены знания, full/compact и сценарий B200.

## [1.45.0] — 2026-11-01

### Added
- K101: UF-поля раздела требуют области инфоблока — дополнены знания, full/compact и сценарий B180.
- K102: ELEMENT_CNT зависит от политики подсчёта — дополнены знания, full/compact и сценарий B181.
- K103: Пустая навигация разделов ограничивает десятью — дополнены знания, full/compact и сценарий B182.
- K104: Проверка прав разделов от имени заданного пользователя — дополнены знания, full/compact и сценарий B183.
- K105: Порядок дерева не равен глобальной сортировке SORT — дополнены знания, full/compact и сценарий B184.
- K106: GetNavChain: область и форма результата — дополнены знания, full/compact и сценарий B185.
- K107: Перемещение раздела сохраняет вычисляемые границы — дополнены знания, full/compact и сценарий B186.
- K108: Удаление раздела затрагивает больше одной строки — дополнены знания, full/compact и сценарий B187.
- K109: Связи элемента с разделами меняются публичным Update — дополнены знания, full/compact и сценарий B188.
- K110: GetElementGroups включает связи из свойств — дополнены знания, full/compact и сценарий B189.
- K111: bOverWrite не создаёт второй документ индекса — дополнены знания, full/compact и сценарий B190.
- K112: Дата поискового документа — DATE_CHANGE — дополнены знания, full/compact и сценарий B191.
- K113: PERMISSIONS поиска — список читателей, не карта R/D — дополнены знания, full/compact и сценарий B192.
- K114: Изменение прав источника синхронизируется с индексом — дополнены знания, full/compact и сценарий B193.
- K115: ChangeSite изменяет привязки и пути индекса — дополнены знания, full/compact и сценарий B194.
- K116: ReIndexAll возвращает состояние или итоговый счётчик — дополнены знания, full/compact и сценарий B195.
- K117: ReIndexAll нельзя вкладывать в незавершённую транзакцию импорта — дополнены знания, full/compact и сценарий B196.
- K118: OnReindex использует callback поискового модуля — дополнены знания, full/compact и сценарий B197.
- K119: Ограничение поиска задаётся MODULE_ID — дополнены знания, full/compact и сценарий B198.
- K120: aParamsEx объединяет альтернативные области через ИЛИ — дополнены знания, full/compact и сценарий B199.

## [1.44.0] — 2026-11-01

### Added
- K91: Периодический агент догоняет пропущенные интервалы — дополнены знания, full/compact и сценарий B170.
- K92: Агент не наследует надёжный контекст посетителя — дополнены знания, full/compact и сценарий B171.
- K93: NAME агента является кодом, а не параметризованным заданием — дополнены знания, full/compact и сценарий B172.
- K94: DATE_CHECK не заменяет NEXT_EXEC при первом запуске — дополнены знания, full/compact и сценарий B173.
- K95: loadMessages регистрирует отложенную загрузку — дополнены знания, full/compact и сценарий B174.
- K96: Коды Loc не изолированы PHP-файлом — дополнены знания, full/compact и сценарий B175.
- K97: Подстановка Loc не экранирует значение для HTML — дополнены знания, full/compact и сценарий B176.
- K98: Явный язык передаётся документированному getMessage — дополнены знания, full/compact и сценарий B177.
- K99: Версия модуля читается из arModuleVersion — дополнены знания, full/compact и сценарий B178.
- K100: includeSharewareModule возвращает состояние лицензии — дополнены знания, full/compact и сценарий B179.

## [1.43.0] — 2026-11-01

### Added
- K81: Группы изменяемого пользователя не равны группам оператора — дополнены знания, full/compact и сценарий B160.
- K82: Замена групп должна сохранять временные членства — дополнены знания, full/compact и сценарий B161.
- K83: SetUserGroup не обновляет уже авторизованную сессию — дополнены знания, full/compact и сценарий B162.
- K84: Отмена OnBeforeUserAdd требует false вместе с ThrowException — дополнены знания, full/compact и сценарий B163.
- K85: OnAfterUserAdd вызывается после попытки, а не только успеха — дополнены знания, full/compact и сценарий B164.
- K86: Register не является административным Add — дополнены знания, full/compact и сценарий B165.
- K87: Email не гарантирует уникальную учётную запись — дополнены знания, full/compact и сценарий B166.
- K88: CUser::GetList принимает сортировку по ссылке — дополнены знания, full/compact и сценарий B167.
- K89: LOGIN в legacy-фильтре не равно точному поиску — дополнены знания, full/compact и сценарий B168.
- K90: SendPassword отправляет контрольную строку, а не новый пароль — дополнены знания, full/compact и сценарий B169.

## [1.42.0] — 2026-11-01

### Added
- K61: MIME из браузера не подтверждает содержимое — дополнены знания, full/compact и сценарий B140.
- K62: CheckFile возвращает текст ошибки, а не success boolean — дополнены знания, full/compact и сценарий B141.
- K63: Размеры ResizeImageGet нужно запросить явно — дополнены знания, full/compact и сценарий B142.
- K64: Папка upload сама не регистрирует файл в b_file — дополнены знания, full/compact и сценарий B143.
- K65: MakeFileArray различает путь, URL и ID — дополнены знания, full/compact и сценарий B144.
- K66: Картинка элемента записывается файловым дескриптором — дополнены знания, full/compact и сценарий B145.
- K67: old_file и del нельзя переносить из запроса без нормализации — дополнены знания, full/compact и сценарий B146.
- K68: CheckImageFile ограничивает геометрию до обработки — дополнены знания, full/compact и сценарий B147.
- K69: Uploader не должен присваивать себе все входящие файлы — дополнены знания, full/compact и сценарий B148.
- K70: CSV требует исходных значений, а не HTML из GetNext — дополнены знания, full/compact и сценарий B149.
- K71: Формат DateTime нельзя угадывать по строке — дополнены знания, full/compact и сценарий B150.
- K72: format использует зону объекта, не всегда сервера — дополнены знания, full/compact и сценарий B151.
- K73: Арифметика Bitrix DateTime изменяет исходный объект — дополнены знания, full/compact и сценарий B152.
- K74: Сутки в ORM задаются двумя границами в согласованной зоне — дополнены знания, full/compact и сценарий B153.
- K75: createFromUserTime зависит от текущего пользователя — дополнены знания, full/compact и сценарий B154.
- K76: Составной primary передаётся целиком — дополнены знания, full/compact и сценарий B155.
- K77: Незагруженное поле объекта не равно NULL в базе — дополнены знания, full/compact и сценарий B156.
- K78: ExpressionField не параметризует произвольный SQL-текст — дополнены знания, full/compact и сценарий B157.
- K79: LIKE-паттерн задаётся явно, wildcard не является SQL injection — дополнены знания, full/compact и сценарий B158.
- K80: TTL ORM-кеша не включает кеширование JOIN автоматически — дополнены знания, full/compact и сценарий B159.
- Итоговая самопроверка: добавлен отказ при неразобранной дате до операций DateTime.

## [1.41.0] — 2026-11-01

### Added
- K51: Штатный тег инфоблока и проектные теги — дополнены знания, full/compact и сценарий B130.
- K52: Явная область чтения Option — дополнены знания, full/compact и сценарий B131.
- K53: Отсутствующая настройка и сохранённая пустая строка — дополнены знания, full/compact и сценарий B132.
- K54: Макросы D7 почты передаются через C_FIELDS — дополнены знания, full/compact и сценарий B133.
- K55: Список сайтов в Legacy и D7 почте различается — дополнены знания, full/compact и сценарий B134.
- K56: Совместимая регистрация OnBeforeEventSend — дополнены знания, full/compact и сценарий B135.
- K57: Отмена постановки письма до очереди — дополнены знания, full/compact и сценарий B136.
- K58: Явный почтовый шаблон и языковой фильтр — дополнены знания, full/compact и сценарий B137.
- K59: DUPLICATE управляет копией, а не идемпотентностью — дополнены знания, full/compact и сценарий B138.
- K60: Вложение по ID и по пути имеет разную стоимость — дополнены знания, full/compact и сценарий B139.

## [1.40.0] — 2026-11-01

### Added
- K41: HTML-кеш компонента уже выводится на cache hit — дополнены знания, full/compact и сценарий B120.
- K42: SetResultCacheKeys не удаляет персональные данные из HTML — дополнены знания, full/compact и сценарий B121.
- K43: Эпилог и сохранённые данные вместо вымышленного component_prolog — дополнены знания, full/compact и сценарий B122.
- K44: Шаблон сайта переопределяет встроенный шаблон компонента — дополнены знания, full/compact и сценарий B123.
- K45: Дополнительные зависимости ключа компонента — дополнены знания, full/compact и сценарий B124.
- K46: Подписанные параметры компонента: целостность, не право доступа — дополнены знания, full/compact и сценарий B125.
- K47: Действие компонента и действие модуля имеют разные маршруты — дополнены знания, full/compact и сценарий B126.
- K48: Authentication не ограничивает выборку объектами владельца — дополнены знания, full/compact и сценарий B127.
- K49: Метод запроса BX.ajax и обработка отклонённого Promise — дополнены знания, full/compact и сценарий B128.
- K50: PHP-тип параметра действия не задаёт бизнес-диапазон — дополнены знания, full/compact и сценарий B129.

## [1.39.0] — 2026-11-01

### Added
- K21: Пакет REST не является транзакцией — дополнены знания, full/compact и сценарий B100.
- K22: Постраничная REST-выгрузка и условие завершения — дополнены знания, full/compact и сценарий B101.
- K23: Версия REST определяется маршрутом и схемой метода — дополнены знания, full/compact и сценарий B102.
- K24: Входящий вебхук наследует права владельца — дополнены знания, full/compact и сценарий B103.
- K25: Продление OAuth без гонки между обработчиками — дополнены знания, full/compact и сценарий B104.
- K26: Портал идентифицируется member_id, а не доменом — дополнены знания, full/compact и сценарий B105.
- K27: Проверка подлинности REST-события — дополнены знания, full/compact и сценарий B106.
- K28: Офлайн-очередь не является журналом всех изменений — дополнены знания, full/compact и сценарий B107.
- K29: Получение офлайн-событий по умолчанию удаляет их — дополнены знания, full/compact и сценарий B108.
- K30: Подтверждение офлайн-пакета имеет опасные пустые значения — дополнены знания, full/compact и сценарий B109.
- K31: Повторная обработка ошибочных офлайн-событий — дополнены знания, full/compact и сценарий B110.
- K32: Лимиты частоты и ресурсоёмкости REST различаются — дополнены знания, full/compact и сценарий B111.
- K33: Файловое поле REST не равно объекту Диска — дополнены знания, full/compact и сценарий B112.
- K34: Готовность BX24.js не равна готовности DOM — дополнены знания, full/compact и сценарий B113.
- K35: Установка приложения и первый запуск пользователя — разные этапы — дополнены знания, full/compact и сценарий B114.
- K36: Контекст встройки не является разрешением на объект — дополнены знания, full/compact и сценарий B115.
- K37: Общие и пользовательские настройки REST-приложения — дополнены знания, full/compact и сценарий B116.
- K38: feature.get не является булевой проверкой существования API — дополнены знания, full/compact и сценарий B117.
- K39: Транспортная ошибка HttpClient не доказывает отсутствие записи — дополнены знания, full/compact и сценарий B118.
- K40: Idempotency-Key REST 3.0 не заменяет блокировку конкурентных записей — дополнены знания, full/compact и сценарий B119.

## [1.38.0] — 2026-11-01

### Added
- K11: Корзина заказа сохраняется через агрегат Order — дополнены знания, full/compact и сценарий B090.
- K12: FUSER и пользователь — разные идентификаторы — дополнены знания, full/compact и сценарий B091.
- K13: Идентичность строки корзины не равна PRODUCT_ID — дополнены знания, full/compact и сценарий B092.
- K14: Системная отгрузка и распределение количества — дополнены знания, full/compact и сценарий B093.
- K15: Частичные оплаты и повтор подтверждения — дополнены знания, full/compact и сценарий B094.
- K16: Финальный пересчёт и сумма неоплаченной оплаты — дополнены знания, full/compact и сценарий B095.
- K17: Контекст менеджера купонов — дополнены знания, full/compact и сценарий B096.
- K18: Существующая доставка не обязательно доступна отгрузке — дополнены знания, full/compact и сценарий B097.
- K19: Ручная цена корзины и источник истины — дополнены знания, full/compact и сценарий B098.
- K20: События сохранения заказа и повторный save — дополнены знания, full/compact и сценарий B099.

## [1.37.0] — 2026-11-01

### Added
- K01: Три результата CIBlockElement::GetList — дополнены знания, full/compact и сценарий B080.
- K02: Result внутри транзакции и граница отката — дополнены знания, full/compact и сценарий B081.
- K03: OnAfter ORM не равен после commit — дополнены знания, full/compact и сценарий B082.
- K04: Пагинация объектов со связями 1:N — дополнены знания, full/compact и сценарий B083.
- K05: Публичная ORM-выборка и версии документооборота — дополнены знания, full/compact и сценарий B084.
- K06: Частичная запись свойств и явное очищение — дополнены знания, full/compact и сценарий B085.
- K07: Множественные файлы: ID файла и ID значения — дополнены знания, full/compact и сценарий B086.
- K08: Отдельный lifecycle записи свойств — дополнены знания, full/compact и сценарий B087.
- K09: Enum: стабильный внешний ключ и локальный ID — дополнены знания, full/compact и сценарий B088.
- K10: Мутация метаданных свойства и VERSION=2 — дополнены знания, full/compact и сценарий B089.

## [1.36.0] — 2026-11-01

### Added
- 23 поведенческих и CLI-теста без сторонних зависимостей, `make test` внутри общего CI/release gate.
- Eval prompts B075–B079, контракт диагностических доказательств в full/compact `release-gate.md` и аудит 10 пробелов с проверками в PLAN.

### Fixed
- Генераторы проверяют весь набор назначений до записи, включая `--all`; защищены от коллизий, символьных ссылок и одновременного запуска. `--force` сохраняет существующий static report; замена каждого файла атомарна, весь каталог не является транзакцией.
- Optimization evidence требует локальный finding-файл, уникальные ID и совпадение метаданных; `confirmed`/`fixed` требуют отдельный runtime artifact и `Status: pass`. Исправлено несовпадение priority в генераторе и sample pack.
- Runtime evidence проверяет точные локальные ссылки из таблицы, уникальные известные scenario ID, совпадение ID/verdict и причину каждого `fail`/`blocked`; `pass` требует раздел Evidence.
- Оба evidence-валидатора используют общую проверку секретов; непроверяемые, двоичные, слишком большие и linked-вложения отклоняются вместо молчаливого пропуска.
- Обход диагностики ограничен обычными файлами внутри выбранного корня; символьные ссылки не читаются, `--module` не принимает пути.
- Файловый preflight больше не возвращает `pass`: только `candidate`/`blocked` и `runtime_status: not_checked`; регистрация модулей не предполагается по наличию файлов.
- Preflight распознаёт `SM_VERSION` через `define`/`const` и массив версии; full/compact согласованы по приоритету main version file. Назначение `SM_VERSION`: [официальная документация](https://dev.1c-bitrix.ru/api_help/main/general/constants.php).
- Preflight сохраняет только origin HTTP(S)-адреса, без credentials, пути, query и fragment.
- Диагностические отчёты больше не экспортируют строки исходного кода: только координаты и фиксированные признаки; N+1-классификация сохранена.

### Compatibility
- Preflight `status: pass` заменён на `candidate`, runtime отдельно отмечен `not_checked`; URL и source snippets больше не экспортируются целиком.
- Runtime summary должен быть таблицей с точными локальными ссылками. Старые неполные packs, внешние evidence URL и файлы, которые невозможно просканировать, теперь отклоняются; обновить их по контракту `release-gate.md`, а не ослаблять проверки.
- Существующие заполненные evidence не перезаписываются без `--force`. Групповая генерация не является транзакцией всего каталога; при сбое записи проверить оставшиеся файлы перед повторным запуском.

## [1.35.0] — 2026-07-16

### Added
- `project-layout-and-includes.md` в full и MCP Market compact версиях: project-first карта public root, active template, `.section.php`, `header.php`/`footer.php`/page, `IncludeFile`/`main.include`, delayed areas, copied templates, multisite/edit/cache/composite verification.
- `project-configuration.md` в full и compact версиях: классификация secrets/deployment/admin options/entity references/content, выбор между environment/`Option`/constants/registry, type validation, stable-key scope, missing/duplicate contract и защищённая cache invalidation.
- Eval prompts `B070–B074` для placement, `.section.php`, выбора config/ID, защиты registry cache reset и изменения логики stock component без копирования ядра.

### Changed
- `behavior-routing.md`, `project-intake.md`, `task-playbooks.md`, `developer-primitives.md`, `developer-cards.md`, `first-answer-pitfalls.md`, `answer-contracts.md`, `core-grep-cookbook.md`, `reference-map.md` и `release-gate.md` связаны с новыми project layout/config маршрутами.
- `BITRIX_PROJECT_CONTEXT.template.md` сохраняет include/delayed-area convention и безопасный config/stable-ID contract без значений secrets; `validate_skill.py` контролирует full/compact sync и regression `B070–B074`.
- README, PLAN и обе skill-версии обновлены под релиз `1.35.0`.

## [1.34.0] — 2026-07-08

### Added
- `admin-ui.md` получил расширенный update-safe слой по кастомизации админки: core → docs/forums → core методика, матрица выбора между `CAdmin*`, `OnAdmin*`, `OnBuildGlobalMenu`, custom admin pages и modern grid.
- Eval prompts `B065–B069` покрывают безопасную кастомизацию админки, вкладки форм, групповые действия списков, admin-меню и размещение module admin pages.

### Changed
- Full и MCP Market compact `components-admin-ui.md` синхронизированы с новым admin UI playbook: `/local/modules`, tiny wrappers в `/bitrix/admin`, persistent event handlers, стабильные `table_id`/`grid_id`/tab ids, права, `sessid`, smoke-чеклист и anti-patterns правки ядра.
- README, PLAN, release gate и `validate_skill.py` обновлены под версию `1.34.0` и расширенный admin/backoffice regression set.

## [1.33.0] — 2026-07-03

### Added
- `scripts/bitrix_static_optimization_audit.py` — read-only статический helper для Markdown/JSON-аудита оптимизаций Bitrix-проекта.
- `bitrix/assets/optimization-audit-report.template.md` и MCP Market copy — шаблон итогового отчёта по оптимизациям.
- `db-orm-performance.md`, `frontend-assets-performance.md`, `agents-imports-performance.md`, `shop-performance.md` — углублённая база по DB/ORM/N+1, images/assets, agents/imports/cron/stepper и catalog/sale/shop bottlenecks.
- `scripts/init_optimization_evidence.py`, `scripts/validate_optimization_evidence.py`, шаблоны `bitrix/assets/optimization-evidence/*` и `examples/optimization-evidence/sample-candidate/` — воспроизводимый evidence pack для findings аудита оптимизаций.
- Eval prompts `B061–B064` для DB/ORM/N+1, catalog/filter, agents/imports и frontend/assets optimization routes.

### Changed
- `project-optimization-audit.md`, README и Makefile подключены к `make optimization-audit`; `validate_skill.py` теперь проверяет наличие optimization-audit helper/template.
- Full и MCP Market compact-навигация связаны с новыми optimization references, включая compact-блоки в `search-seo-ops.md` и `commerce-shop.md`.
- Makefile, release gate и `validate_skill.py` теперь проверяют optimization evidence templates, initializer, validator и sample candidate pack.
- Release gate и recommended eval set расширены optimization-аудитом `B060–B064`, чтобы регрессия ловила Redis/CDN/index/rebuild/cache-clear anti-patterns.

## [1.32.0] — 2026-07-02

### Added
- `bitrix/references/project-optimization-audit.md` — сквозной playbook для запроса “изучи проект и скажи как оптимизировать”: карта уже существующих оптимизаций, ошибки cache/composite/N+1/images/agents/imports/shop, safe wins, runtime/perfmon evidence и формат audit-report.

### Changed
- Full и MCP Market compact-навигация, `core-grep-cookbook`, `developer-cards`, `answer-contracts`, `task-playbooks` и eval-набор связаны с новым маршрутом аудита оптимизаций.

## [1.31.0] — 2026-07-01

### Added
- `bitrix/references/composite-cache.md` — отдельный core-backed reference по “Композитному сайту” на базе `main` 26.150.0: отличие composite от component/data cache, `setFrameMode` как голосование, `AutomaticArea`/`COMPOSITE_FRAME_*`, `createFrame`/`FrameHelper` как dynamic boundary, `/bitrix/html_pages/`, `X-Bitrix-Composite`, персонализация, очистка и second request/cache pass.

### Changed
- Components/templates/cache/security references в full и MCP Market compact-версии синхронизированы с новым composite-слоем: убраны формулировки, где `setFrameMode(true)` фактически смешивался с динамическим блоком, добавлены canonical `Bitrix\Main\Composite\Page`, compatibility alias `Data\StaticHtmlCache`, `BufferArea`/stub-механика, core-grep маршруты и security-проверки персональных блоков.

## [1.30.0] — 2026-06-29

### Added
- `.github/workflows/validate.yml` — CI-gate для проверки навыка: `validate_skill.py`, sample blocked evidence, preflight-helper и shell syntax check.
- `scripts/bitrix_runtime_preflight.py` — read-only helper для Bitrix sandbox: проверяет public root, версии модулей, safety markers и route candidates без вывода secrets.
- `Makefile` с короткими командами `validate`, `release-check`, `evidence-p1`, `evidence-all` и `preflight`.
- `examples/runtime-smoke/blocked-p1/` — безопасный пример blocked evidence pack, который проходит `validate_runtime_evidence.py` и не заявляет runtime pass.

### Changed
- Release workflow теперь сначала запускает validation gate и не публикует релиз поверх несинхронизированного skill/reference/evidence слоя.
- `scripts/validate_skill.py` усилен проверкой version/changelog/PLAN sync, compact coverage manifest, repo automation files, preflight-helper и режима `init_runtime_evidence.py --all`.
- `scripts/init_runtime_evidence.py` теперь умеет создавать все пакеты `P1–P4` одной командой `--all` и поддерживает стабильный `--date` для default output.
- `scripts/validate_runtime_evidence.py` расширил secret scan для Bitrix cookies, DB credentials, license keys, OAuth tokens и webhook URLs.
- MCP Market `reference-map.md` получил full-to-compact coverage manifest, чтобы compact-версия не отставала молча.
- README, release gate и PLAN обновлены под runtime evidence workflow, CI/self-check команды и regression checklist перед релизом.

## [1.29.0] — 2026-06-23

### Changed
- Пользовательская терминология сценария проекта выровнена на “аудит проекта” и “снимок проекта” в README, `SKILL.md`, full/compact `project-intake.md`, reference-map, template `BITRIX_PROJECT_CONTEXT.md` и MCP Market compact-навигации.
- `PLAN.md` обновлён как living-status документ: `version-impact.md`, shop-core tail modules и сценарий `BITRIX_PROJECT_CONTEXT.md` отмечены как закрытые code-first/UX слои, а главным следующим этапом оставлен Docker/runtime smoke evidence.
- В full и compact `eval-prompts.md` добавлены regression prompts для команды аудита проекта и повторного чтения `BITRIX_PROJECT_CONTEXT.md`.
- `runtime-smoke-verification.md` и compact `core-routing.md` дополнены порядком smoke-прохода: preflight, fixtures, read-only, write-mode, cache pass, evidence pack и перенос findings обратно в references.
- Добавлены конкретные runtime smoke-пакеты `P1–P4`: catalog/SKU/basket/order, CommerceML, REST/webservice, marketing/automation/realtime; compact `core-routing.md` и `shop-task-matrix.md` синхронизированы с очередью smoke-проверок и naming convention для evidence pack.
- Добавлены шаблоны `assets/runtime-smoke/*`, helper `scripts/init_runtime_evidence.py`, валидатор `scripts/validate_runtime_evidence.py` и проверки в `scripts/validate_skill.py`, чтобы runtime evidence pack был воспроизводимо создаваемым, структурно проверяемым и не содержал очевидных secrets.
- README и release gate обновлены под runtime evidence workflow: code-first coverage отделён от runtime pass, а релиз с evidence требует `validate_runtime_evidence.py`.
- В full и compact `eval-prompts.md` добавлены runtime smoke prompts: граница code-first/runtime, blocked write-mode, CommerceML без production 1С, REST scopes и проверка evidence pack.

## [1.28.0] — 2026-06-22

### Added
- `version-impact.md` в полной и MCP Market версиях: правила проверки module version mismatch, version-sensitive контрактов и осторожных ответов при отличии локального core от baseline.
- `shop-core-tail-modules.md` в полной и MCP Market версиях: code-first route для `calendar`, `idea`, `learning`, `support`, `wiki`, а также shop-specific частей `b24connector`, `landing`, `mobileapp`.
- `BITRIX_PROJECT_CONTEXT.template.md` в полной и MCP Market версиях: шаблон корневого файла `BITRIX_PROJECT_CONTEXT.md` для безопасного снимка проекта после полного аудита проекта.

### Changed
- README, `SKILL.md`, `project-intake.md`, `behavior-routing.md`, `reference-map.md` и MCP Market compact-версия закрепляют сценарий аудита проекта: агент читает `BITRIX_PROJECT_CONTEXT.md` после `AGENTS.md`, а после полного аудита создаёт или обновляет этот файл.
- `runtime-smoke-verification.md` и MCP Market compact bundle усилены Docker execution plan: sandbox harness без распространения ядра, secrets, DB dumps и production данных.
- `shop-core-module-inventory.md` обновлён: хвостовые модули больше не остаются в `needs deep audit`, но runtime pass по-прежнему требует sandbox/fixtures smoke.
- `PLAN.md` актуализирован под версию `1.28.0` и roadmap `v1.28+`: Docker/runtime smoke, version impact layer, доаудит хвоста shop-core modules и `BITRIX_PROJECT_CONTEXT.md` workflow.

## [1.27.0] — 2026-06-19

### Added
- `scripts/validate_skill.py` — repo-local release/eval gate без внешних Python-зависимостей: проверяет frontmatter, `agents/openai.yaml`, MCP Market file-count, внутренние markdown-ссылки, синхронизацию critical references, eval prompt coverage, forbidden markers и `git diff --check`.
- `bitrix/agents/openai.yaml` и `mcpmarket/bitrix/agents/openai.yaml` — UI metadata для Codex/OpenAI skill-карточки: понятное имя, короткое описание и default prompt с `$bitrix`.
- `bitrix/references/task-playbooks.md` и compact `mcpmarket/bitrix/references/task-playbooks.md` — практические маршруты “найти → понять слой → изменить → проверить” для meta/head, assets, component/template, iblock property, visibility chain, 404/redirect, form mail, ajax, cache/personalization, shop/catalog/sale, 1С/CommerceML и custom logic задач.
- `bitrix/references/reference-map.md` и compact `mcpmarket/bitrix/references/reference-map.md` — вынесенная из главного `SKILL.md` карта доменных references и guardrails, чтобы основной skill быстрее маршрутизировал задачу и не загружал длинную навигационную простыню.
- `bitrix/references/behavior-routing.md`, `bitrix/references/project-intake.md` и compact-версии в `mcpmarket/bitrix/references/` — проектный UX-слой: режимы работы агента, 30-секундное определение маршрута, быстрый аудит структуры Bitrix-проекта, факты по module/template/head/component перед ответом и запрет отвечать общей теорией при доступном проекте.
- `bitrix/references/release-gate.md` и compact `mcpmarket/bitrix/references/release-gate.md` — pre-release checklist для бытового слоя: validate full/compact skills, `git diff --check`, MCP Market file-count, changelog/version sync, full/compact reference sync и минимум 15 eval prompts с `fail = 0`.
- `bitrix/references/answer-contracts.md` и compact `mcpmarket/bitrix/references/answer-contracts.md` — контракты первого ответа для бытовых задач: short how-to, project-confirmed answer, debug chain, layer answer, module-dependent answer и dangerous data confirmation, чтобы агент отвечал коротко, Bitrix-native и с project checks/side effects.
- `bitrix/references/core-grep-cookbook.md` и compact `mcpmarket/bitrix/references/core-grep-cookbook.md` — read-only grep cookbook для быстрых project-evidence проверок: public root/modules, meta/head/assets, components/templates, component params, iblock/HL, cache/composite, routing/404/redirect, request/user/CSRF, events/agents, ajax/controllers, mail/webforms, SEO/search, sale/catalog/currency, 1С/CommerceML, admin/grid и logs.
- `bitrix/references/eval-prompts.md` и compact `mcpmarket/bitrix/references/eval-prompts.md` — regression-набор бытовых Bitrix-запросов с expected references, обязательными тезисами и запрещёнными первыми шагами; gate перед релизом бытового слоя: минимум 15 prompt из разных доменов, `fail = 0`.
- `bitrix/references/first-answer-pitfalls.md` и compact `mcpmarket/bitrix/references/first-answer-pitfalls.md` — стоп-лист анти-паттернов первого ответа: meta вручную, echo CSS/JS, правка `www/bitrix`, `$_SESSION`/`$_REQUEST`, прямой SQL, глобальное отключение кеша, `mail()`, самодельный ajax, прямой SQL для sale/catalog и другие неправильные стартовые маршруты.
- `bitrix/references/developer-cards.md` и compact `mcpmarket/bitrix/references/developer-cards.md` — слой бытовых карточек в формате “Запрос → Не делай → Делай → Где проверить → Побочные эффекты” для meta/head, Asset, IncludeFile, компоненты, breadcrumbs, request/current user, URL, Loader, 404/redirect, images, iblock properties, cache, mail/form, AJAX, event handlers, catalog/sale/currency changes и 1С/CommerceML кейсов.

### Changed
- В compact bundles MCP Market некликабельные ссылки на full-only source references превращены в inline names, чтобы агент не пытался открыть отсутствующие файлы внутри `mcpmarket/bitrix/references/`.
- `README.md` и `mcpmarket/bitrix/SKILL.md` больше не фиксируют устаревающий точный счётчик reference-файлов; используется “80+”, чтобы витрина не врала после добавления бытовых маршрутов.
- `developer-primitives.md` в full и compact версиях теперь явно маршрутизирует короткие вопросы к карточкам, stop-list, grep cookbook и answer contracts.

## [1.26.0] — 2026-06-16

### Changed
- Добавлен и расширен базовый reference `developer-primitives.md` в полную и MCP Market версии: быстрые ответы на бытовые Bitrix-вопросы разработчика (`meta title/description`, `ShowHead`/`ShowTitle`, Asset, `IncludeFile`, breadcrumbs, `GetCurPageParam`, `Context`, current user, `Loader::includeModule`, `CFile::ResizeImageGet`, `Loc::getMessage`, `ShowPanel`) с ссылками на официальную документацию, чтобы агент не уходил в чистый PHP там, где есть штатный механизм Bitrix.
- Уточнены `templates.md` и compact `components-admin-ui.md`: meta/title/head теперь описаны через свойства страницы/раздела, SEO-параметры компонентов, `SetTitle`/`SetPageProperty`, `ShowHead`/`ShowTitle` и отложенный вывод, с явным запретом первым делом вставлять `<meta>` руками.
- Усилен frontmatter `description` в `bitrix/SKILL.md` и `mcpmarket/bitrix/SKILL.md`: добавлены явные русские/английские триггеры (`Битрикс`, `1С-Битрикс`, `БУС`, `www/bitrix`, `/local`, `CIBlock*`, `Bitrix\Main`, D7/legacy, shop/1C/REST и production diagnostics), чтобы агент чаще выбирал навык без ручного `/bitrix`.
- Нестандартное поле frontmatter `compatibility` перенесено в тело обоих `SKILL.md`, чтобы skill проходил базовую Codex-валидацию.
- Уточнён `README.md`: принцип «сначала ядро» теперь описан как рабочий процесс агента при доступе к рабочей копии проекта, а версии модулей — как маркеры проверенного контракта, а не полная база совместимости по всем релизам Bitrix.
- Переработан и полностью русифицирован `README.md`: корневой README стал компактной витриной навыка с короткой установкой, таблицей покрытия, моделью безопасности и командами сопровождения вместо большой справочной матрицы.

## [1.25.0] — 2026-06-04

### Added
- `bitrix/references/production-best-practices.md` — cross-cutting production reference по update-safe Bitrix-разработке: truth stack, где держать код, D7 vs legacy, boundary/service слой, side effects, cache/index/RBAC, performance, security и verification matrix.
- `bitrix/references/pitfalls-matrix.md` — матрица типовых Bitrix-граблей: visibility, components/templates, iblock/HL, catalog/SKU, basket/checkout/order, 1С/CommerceML, REST/webservice, search/SEO/cache, auth, mail/SMS, agents/realtime и release/update pitfalls.
- `bitrix/references/runtime-smoke-verification.md` — план runtime smoke verification для Docker/sandbox: safe fixtures, catalog/sale/1С/REST/webservice/marketing/bizproc сценарии, evidence format и pass/fail/block criteria.

### Changed
- `bitrix/SKILL.md`, `README.md`, `PLAN.md`, `shop-task-matrix.md`, `noncommerce-task-matrix.md`, `core-audit-matrix.md`, `shop-core-module-inventory.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с production best-practices baseline `1.25.0`.
- Навык теперь явно разделяет code-first coverage и runtime-smoke evidence: нельзя говорить “весь core production-проверен”, пока нет sandbox/fixtures smoke.

## [1.24.0] — 2026-06-03

### Added
- `bitrix/references/shop-integrations-webservice.md` — отдельный core-first reference по integration extras интернет-магазина: `webservice` 26.0.0, `webservice.sale`, `webservice.statistic`, SOAP/WSDL, `stssync`, REST apps/webhooks/events/placements, sale REST controllers/events и catalog REST controllers/events/placement.

### Changed
- `shop-core-module-inventory.md` теперь считает webservice/integration extras покрытыми и сдвигает ordered roadmap к Docker/runtime smoke.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с webservice/REST baseline `1.24.0`.

## [1.23.0] — 2026-06-03

### Added
- `bitrix/references/shop-automation-bizproc.md` — отдельный core-first reference по automation/bizproc слою интернет-магазина: `bizproc`, `bizprocdesigner`, legacy `workflow`, `lists`, `pull`, workflow templates/states/tasks, robots/triggers, list processes, REST surface и realtime diagnostics.

### Changed
- `shop-core-module-inventory.md` теперь считает automation/bizproc покрытыми и сдвигает ordered roadmap к `shop-integrations-webservice.md` и Docker/runtime smoke.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с automation/bizproc baseline `1.23.0`.

## [1.22.0] — 2026-06-03

### Added
- `bitrix/references/shop-marketing-analytics.md` — отдельный core-first reference по маркетингово-аналитическому слою интернет-магазина: `sender`, `mail`, `messageservice`, `subscribe`, `advertising`, `abtest`, `conversion`, `report`, `statistic`, eShop hooks и sale-side sender/statistic connectors.

### Changed
- `shop-core-module-inventory.md` теперь считает marketing/analytics покрытыми и сдвигает ordered roadmap к automation/bizproc и webservice/integration extras.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с marketing/analytics baseline `1.22.0`.

## [1.21.0] — 2026-06-02

### Added
- `bitrix/references/shop-standard-components.md` — отдельный core-first reference по стандартным компонентам интернет-магазина: `bitrix:catalog`, `catalog.section`, `catalog.element`, `catalog.smart.filter`, compare, basket, `sale.order.ajax`, `sale.order.checkout`, personal order pages, catalog productcard/store/report components, `bitrix.eshop` wizard layer и quick map параметров 1С components.

### Changed
- `shop-core-module-inventory.md` теперь считает standard shop components покрытыми и сдвигает ordered roadmap к marketing/analytics, automation и webservice.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы со standard-components baseline `1.21.0`.
- Windows `update.ps1` больше не передаёт `-Claude`/`-Codex` в installer как версию; `install.ps1` также умеет восстановиться после старого broken forwarding из уже установленных updater-копий.

## [1.20.0] — 2026-06-02

### Added
- `bitrix/references/storeassist.md` — отдельный core-first reference по `storeassist` 24.0.0: мастер магазина, `storeassist_1c_*` onboarding pages, admin toolbar, task whitelist, options `storeassist_settings`/`progress_percent`/`num_orders`, AJAX endpoint `/bitrix/tools/storeassist.php`, menu hooks и daily order-progress agent.

### Changed
- `shop-core-module-inventory.md` теперь считает `storeassist` покрытым и сдвигает ordered roadmap к `shop-standard-components.md`, marketing/analytics, automation и webservice.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы со StoreAssist baseline `1.20.0`.

## [1.19.0] — 2026-06-02

### Added
- `bitrix/references/shop-core-module-inventory.md` — полный inventory 49 модулей shop-core: версии, counts по components/admin/lib/classes, shop/1С relevance, coverage status и ordered roadmap для `storeassist`, shop standard components, marketing/analytics, automation и webservice.

### Changed
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `core-audit-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с module-inventory baseline `1.19.0`.
- Shop-route теперь явно не обещает глубокое покрытие `storeassist`, `sender`, `report`, `statistic`, `conversion`, `abtest`, `advertising`, `bizproc`, `webservice` без отдельного deep-reference.

## [1.18.0] — 2026-06-02

### Added
- `bitrix/references/pagination.md` — отдельный core-first reference по пагинации из `main` 26.150.0: `CDBResult::NavStart`, `GetNavPrint`, `PAGEN_N`/`SIZEN_N`/`SHOWALL_N`, `system.pagenavigation`, D7 `PageNavigation`, `AdminPageNavigation`, `ReversePageNavigation`, `main.pagenavigation`, admin/grid navigation и ajax/lazy load.

### Changed
- `bitrix/SKILL.md` теперь явно маршрутизирует задачи про пустые/дублирующие страницы, `PAGEN_N`, lazy load, admin/grid navigation и `PageNavigation` в отдельный pagination-layer.
- `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с pagination baseline `1.18.0`.

## [1.17.0] — 2026-06-02

### Added
- `bitrix/references/currency.md` — отдельный core-first reference по модулю `currency` 26.0.0: валюты, курсы, форматирование денег, `CurrencyManager`, `CurrencyTable`, `CurrencyRateTable`, связь с catalog prices и sale sums.
- `bitrix/references/commerce-1c-integration.md` — отдельный reference по 1С / CommerceML: `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`, `checkauth/init/file/import`, `BX_CML2_IMPORT`, `BX_CML2_EXPORT`, temp files, zip/chunks, `secure_1c_exchange`, exchange logs.
- `bitrix/references/shop-task-matrix.md` — быстрый routing интернет-магазина: товары, SKU, цены, остатки, корзина, checkout, оплата, доставка, скидки, заказы и 1С diagnostics.
- `mcpmarket/bitrix/` — компактная read-only версия навыка для импорта через MCP Market: reference-файлы сгруппированы в bundles, чтобы skill folder оставался ниже лимита 50 файлов.

### Changed
- `bitrix/references/catalog.md` переаудирован по shop-core с `catalog` 25.550.0: product/SKU/price/store/store document/measure/VAT/admin component/1C import layers.
- `bitrix/references/sale.md` переаудирован по shop-core с `sale` 26.0.0: basket/order/payment/shipment/discount/location/cashbox/exchange side effects.
- `bitrix/references/commerce-workflows.md` переведён из deferred в подтверждённый shop-route после локальной проверки `catalog`, `sale`, `currency` и 1С components.
- `bitrix/references/core-audit-matrix.md` теперь описывает фазовую матрицу: active non-commerce route, active shop-core route и deferred zones per project.
- `bitrix/SKILL.md`, `README.md`, `PLAN.md` и `bitrix/VERSION` синхронизированы с commerce/1С baseline `1.17.0`.

## [1.16.0] — 2026-04-24

### Added
- `bitrix/references/core-audit-matrix.md` — матрица текущего non-commerce core: активные модули, deferred-домены и ловушки вроде `catalog.*` компонентов внутри `iblock` без установленного модуля `catalog`
- `bitrix/references/noncommerce-task-matrix.md` — быстрый routing типовых и нетиповых задач без интернет-магазина в правильные reference-файлы
- `bitrix/references/diagnostic-visibility.md` — диагностика “в админке есть, на сайте нет”: права, site binding, component params, filters, templates, cache/index/SEO chain
- `bitrix/references/index-cache-diagnostics.md` — отдельный слой по component/tagged/managed/composite cache, search index и SEO artifacts
- `bitrix/references/component-dataflow-debugging.md` — трассировка standard component flow от `.parameters.php` до `component_epilog.php` и AJAX
- `bitrix/references/php-quality.md` — PHP quality gates для Bitrix-проектов: phpstan/psalm/fixer/sniffer/rector без навязывания нового toolchain
- `bitrix/references/php-legacy-modernization.md` — безопасная legacy modernization: boundary extraction, D7 vs `C*` write paths, selective modern PHP
- `bitrix/references/standard-components-noncommerce.md` — standard components без магазина и stock template truth layer
- `bitrix/references/operations-runbook.md` — эксплуатационный runbook без магазина: переносы, agents/cron/stepper, импорты, backup/monitoring, perf diagnostics, обновления core

### Changed
- `bitrix/SKILL.md` теперь маршрутизирует весь non-commerce контур по audit matrix, diagnostic layers, PHP quality/legacy modernization, standard components и operations runbook
- `bitrix/references/php-workflow.md` и `bitrix/references/php-testing.md` связаны с новыми PHP quality и legacy modernization слоями
- `README.md` синхронизирован с новым non-commerce покрытием и полной матрицей новых reference-файлов

## [1.15.0] — 2026-04-24

### Added
- `bitrix/references/php-testing.md` — отдельный reference по PHP testing и verification в Bitrix-проекте: unit/integration, smoke без готового PHPUnit-контура, test seams, fixtures и разведение project contour от vendor noise внутри core

### Changed
- `bitrix/references/php-workflow.md` теперь явно исключает vendor noise внутри `www/bitrix/modules/*/vendor` при диагностике project tooling и ссылается на новый testing-layer
- `bitrix/SKILL.md` теперь маршрутизирует PHP testing/verification в новый `php-testing.md`, различает project contour и vendor noise и фиксирует safe-подход к проверке boundary-кода
- `README.md` синхронизирован с новым testing-покрытием PHP-слоя и дополнен `php-testing.md` в матрице reference-файлов

## [1.14.0] — 2026-04-24

### Added
- `bitrix/references/php-workflow.md` — отдельный reference по PHP-heavy задачам в Bitrix-проекте: service-layer, DTO/value-object границы, exceptions vs `Result/Error`, project toolchain (`composer`, `phpunit`, `phpstan`/`psalm`, fixer/sniffer, `rector`) и минимальные quality gates без конфликта с Bitrix-нормами

### Changed
- `bitrix/SKILL.md` теперь явно маршрутизирует PHP-heavy Bitrix-задачи в новый `php-workflow.md`, учитывает project-tooling-first подход и фиксирует границы для `strict_types`, exceptions и foreign framework patterns
- `README.md` синхронизирован с новым PHP-покрытием и дополнен `php-workflow.md` в матрице reference-файлов

## [1.13.0] — 2026-04-15

### Changed
- `bitrix/references/sitecorporate.md` дополнен реальным wizard template/public слоем и зафиксированным фактом, что `corp_furniture` skeleton местами тянет `bitrix:catalog`, не доказывая наличие магазинного core
- `bitrix/references/blog-socialnet.md` дополнен stock template layer для случая без `www/local`: `micro`, `old_version`, `socialnetwork`, `result_modifier.php`, JS и upload hooks
- `bitrix/references/webforms.md` дополнен stock component/template layer для случая без `www/local`: `intranet`-templates, cache/tags/error-style слой и component-level развилки `form.result.new`
- `bitrix/SKILL.md` теперь явно учитывает checkout без `local/*` и ведёт аудит в stock templates и wizard assets текущего core
- `README.md` синхронизирован с новым покрытием template/public слоя поверх уже проверенного core

## [1.12.0] — 2026-04-15

### Added
- `bitrix/references/sitecorporate.md` — отдельный core-first справочник по модулю `bitrix.sitecorporate`, wizard-решениям `corp_services` / `corp_furniture` и stock `furniture.*` компонентам

### Changed
- `bitrix/references/blog-socialnet.md` переписан под реально установленный `blog`: D7 read-only таблицы, `CBlog*`, mail reply handlers, search reindex и условный `socialnet`-контур
- `bitrix/references/webforms.md` расширен до реального `form`-workflow: статусы, handlers, validators, CRM link, secure file access и стандартные `form.*` компоненты
- `bitrix/SKILL.md` теперь явно маршрутизирует задачи в `sitecorporate.md` и фиксирует core-first ограничения для `blog` и `form`
- `README.md` синхронизирован с новым покрытием текущего core и обновлёнными описаниями `sitecorporate`, `blog` и `form`

## [1.11.0] — 2026-04-15

### Added
- `bitrix/references/mobileapp.md` — отдельный core-first справочник по модулю `mobileapp`
- `bitrix/references/b24connector.md` — отдельный core-first справочник по модулю `b24connector`

### Changed
- `bitrix/SKILL.md` теперь явно считает `mobileapp` и `b24connector` активными модулями текущего core и маршрутизирует задачи в правильные reference-файлы
- `README.md` синхронизирован с новым покрытием текущего core и дополнен `mobileapp.md` и `b24connector.md`

## [1.10.0] — 2026-04-15

### Added
- `bitrix/references/bitrixcloud.md` — отдельный core-first справочник по модулю `bitrixcloud`

### Changed
- `bitrix/references/security.md` расширен до реально установленного модуля `security`: WAF, redirect/IP rules, session hardening, OTP/MFA, recovery codes, antivirus, site checker и xscan
- `bitrix/SKILL.md` теперь явно считает `security` и `bitrixcloud` активными модулями текущего core и маршрутизирует задачи в правильные reference-файлы
- `README.md` синхронизирован с новым покрытием текущего core и дополнен `bitrixcloud.md`

## [1.9.0] — 2026-04-15

### Added
- `bitrix/references/photogallery.md` — отдельный core-first справочник по модулю `photogallery`

### Changed
- `bitrix/SKILL.md` расширен на подтверждённый активный модуль `photogallery` и теперь ведёт gallery/upload/comment-задачи в отдельный маршрут
- `README.md` синхронизирован с новым покрытием текущего core и дополнен новым reference-файлом

## [1.8.0] — 2026-04-15

### Added
- `bitrix/references/highloadblock.md` — отдельный core-first справочник по модулю `highloadblock`
- `bitrix/references/clouds.md` — отдельный core-first справочник по модулю `clouds`

### Changed
- `bitrix/SKILL.md` расширен на подтверждённый активный модуль `clouds`, получил отдельные маршруты для `highloadblock` и `clouds`, а также новые core-first эвристики для HL и внешнего файлового хранения
- `bitrix/references/iblock-hl-relations.md` явно разведён с новым `highloadblock.md`
- `bitrix/references/import-export.md` явно разведён с новым `clouds.md`, чтобы задачи по `HANDLER_ID` и cloud-storage не ехали в общий `CFile`-маршрут
- `README.md` синхронизирован с новым покрытием текущего core и дополнен новыми reference-файлами

## [1.7.0] — 2026-04-15

### Added
- `bitrix/references/location.md` — отдельный core-first справочник по модулю `location`
- `bitrix/references/messageservice.md` — отдельный core-first справочник по модулю `messageservice`
- `bitrix/references/fileman.md` — отдельный core-first справочник по модулю `fileman`
- `bitrix/references/translate.md` — отдельный core-first справочник по модулю `translate`

### Changed
- `bitrix/SKILL.md` расширен на подтверждённые активные модули `fileman`, `location`, `messageservice`, `translate` и теперь маршрутизирует задачи в новые reference-файлы
- `bitrix/references/mail-notifications.md` явно разведён с `messageservice`, чтобы SMS-задачи шли в правильный модульный слой
- `README.md` синхронизирован с новым покрытием текущего core и дополнен новыми reference-файлами

## [1.6.0] — 2026-04-10

### Added
- `bitrix/versions.sh` и `bitrix/versions.ps1` — просмотр доступных release-версий навыка
- `bitrix/uninstall.sh` и `bitrix/uninstall.ps1` — удаление установленной копии навыка для `Claude` и `Codex`
- поддержка установки и обновления конкретной версии через `--version` и `-Version`

### Changed
- `install.sh` и `install.ps1` теперь в первую очередь ставят навык из release/tag-архива, а не из branch tarball
- `bitrix/update.sh` и `bitrix/update.ps1` теперь умеют обновлять и откатывать навык на конкретную release-версию
- `README.md` дополнен полноценным lifecycle: установка, обновление, просмотр версий, удаление и пути с учётом `$CODEX_HOME`

## [1.5.1] — 2026-04-10

### Changed
- `README.md` переведён на новый bootstrap URL репозитория `bitrix-agent-skill`
- changelog compare/release links переведены на новый GitHub slug
- репозиторий после rename зафиксирован как основной, при этом legacy fallback в install/update-скриптах сохранён для мягкой миграции старых установок

## [1.5.0] — 2026-04-10

### Added
- dual-target install/update flow для `Claude Code` и `Codex`
- автоматическое определение текущего и legacy slug репозитория: сначала `bitrix-agent-skill`, затем `claude-bitrix-skill`
- флаги таргетинга installer-ов: `--claude/--codex/--both` и `-Claude/-Codex/-Both`

### Changed
- `README.md` переведён из Claude-only документации в общий формат `Bitrix Agent Skill` для двух агентов
- `bitrix/SKILL.md` обновлён под совместимость с `Claude Code` и `Codex`
- `install.sh`, `install.ps1`, `bitrix/update.sh`, `bitrix/update.ps1` отвязаны от жёсткой привязки к старому slug и готовы к rename репозитория
- PowerShell installer больше не зависит от шаблона архива `claude-bitrix-skill-*`
- `PLAN.md` синхронизирован с текущей версией и rename-safe install/update слоем

## [1.4.1] — 2026-04-10

### Added
- `bitrix/references/forum.md` — отдельный core-first справочник по модулю `forum`
- `bitrix/references/vote.md` — отдельный core-first справочник по модулю `vote`
- `bitrix/references/landing.md` — отдельный core-first справочник по модулю `landing`
- `bitrix/references/socialservices.md` — отдельный core-first справочник по модулю `socialservices`
- `bitrix/references/perfmon.md` — отдельный core-first справочник по модулю `perfmon`

### Changed
- `bitrix/SKILL.md` расширен на подтверждённые модули `forum`, `vote`, `landing`, `socialservices`, `perfmon`
- `bitrix/references/search.md` дополнен подтверждённым fast-search маршрутом через `CSearchTitle` и `bitrix:search.suggest.input`
- `bitrix/references/seo-cache-access.md` дополнен подтверждённым путём для `OpenGraph` и `JSON-LD` через `$APPLICATION->AddHeadString(...)`
- `README.md` синхронизирован с новым покрытием текущего core без partial-зон в блоговом и стандартном контуре

## [1.4.0] — 2026-04-10

### Added
- `install.ps1` — нативная установка навыка на Windows через PowerShell
- `bitrix/update.ps1` — нативное обновление и `-Check` для Windows через PowerShell
- `bitrix/allow-update.ps1` — helper для глобального разрешения автообновления на Windows

### Changed
- `README.md` переписан под три платформы: macOS, Linux и Windows
- `bitrix/allow-update.sh` теперь добавляет разрешения и для bash-, и для PowerShell-апдейтера
- `SKILL.md` учитывает Windows/PowerShell при проверке новой версии навыка

## [1.3.11] — 2026-04-08

### Added
- `bitrix/allow-update.sh` — helper-скрипт, который одной командой добавляет глобальное разрешение на запуск `update.sh` в `~/.claude/settings.json`

### Changed
- `README.md` больше не предлагает руками редактировать проектный `.claude/settings.local.json` для автообновления навыка
- Инструкция по постоянному разрешению на `update.sh` упрощена до одной команды и переведена на глобальный `~/.claude/settings.json`

## [1.3.10] — 2026-04-08

### Added
- GitHub Actions workflow, который на push в `master` автоматически публикует tag и GitHub Release для текущей версии из `bitrix/VERSION`, если их ещё нет

### Changed
- `README.md` дополнен описанием fully-automatic release flow без ручного создания тега и release в GitHub UI
- В README добавлен шаг с постоянным разрешением на запуск `update.sh`, чтобы агент мог держать навык свежим без повторных запросов

## [1.3.9] — 2026-04-08

### Changed
- Выпущен повторный тестовый релиз для проверки предложения обновить навык при появлении новой версии

## [1.3.8] — 2026-04-08

### Changed
- Выпущен тестовый релиз для проверки сценария с предложением обновить навык при появлении новой версии

## [1.3.7] — 2026-04-08

### Added
- `bitrix/update.sh --check` — явная проверка новой версии без немедленного обновления
- Правило в `SKILL.md`: при первом `/bitrix` сначала проверить версию навыка и при наличии новой версии предложить обновление в явной форме

### Changed
- `README.md` дополнен сценарием проверки новой версии без апдейта

## [1.3.6] — 2026-04-08

### Changed
- Завершена полная core-first ревизия всех `bitrix/references/*.md` по реально установленному ядру
- `README.md` и `PLAN.md` синхронизированы с текущим состоянием скилла и его deferred-доменов
- Маршруты `catalog`, `sale`, `commerce-workflows`, `bizproc`, `pull` и `socialnet` зафиксированы как условные до появления соответствующих модулей в core

### Fixed
- Убраны неподтверждённые API и устаревшие формулировки в reference-файлах по `blog`, `search`, `seo`, `session`, `access`, `subscribe`, `grid`, `file uploader`, `validation`, `templates`, `import/export`, `stepper`, `numerator` и связанным подсистемам
- Исправлены описания покрытия в `README.md`, чтобы они соответствовали реальным контрактам текущего ядра

## [1.1.0] — 2026-03-19

### Added
- `bitrix/VERSION` — файл версии, единый источник истины
- `install.sh` — идемпотентный скрипт установки и обновления (bash + curl)
- `bitrix/update.sh` — встроенный обновлятор: один вызов для обновления навыка
- `CHANGELOG.md` — этот файл
- 35 reference-файлов по всем подсистемам Bitrix

### Changed
- Версия в `SKILL.md` frontmatter обновлена до `"1.1"`
- `README.md` — добавлена секция "Обновление", упрощена установка

## [1.0.0] — 2026-02-XX

### Added
- Первый публичный релиз: `SKILL.md`, progressive disclosure архитектура

[Unreleased]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.45.0...HEAD
[1.45.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.44.0...v1.45.0
[1.44.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.43.0...v1.44.0
[1.43.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.42.0...v1.43.0
[1.42.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.41.0...v1.42.0
[1.41.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.40.0...v1.41.0
[1.40.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.39.0...v1.40.0
[1.39.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.38.0...v1.39.0
[1.38.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.37.0...v1.38.0
[1.37.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.36.0...v1.37.0
[1.36.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.35.0...v1.36.0
[1.35.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.34.0...v1.35.0
[1.34.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.33.0...v1.34.0
[1.33.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.32.0...v1.33.0
[1.32.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.31.0...v1.32.0
[1.31.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.30.0...v1.31.0
[1.30.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.29.0...v1.30.0
[1.29.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.28.0...v1.29.0
[1.28.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.27.0...v1.28.0
[1.27.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.26.0...v1.27.0
[1.26.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.25.0...v1.26.0
[1.25.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.24.0...v1.25.0
[1.24.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.23.0...v1.24.0
[1.23.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.22.0...v1.23.0
[1.22.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.21.0...v1.22.0
[1.21.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.20.0...v1.21.0
[1.20.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.19.0...v1.20.0
[1.19.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.18.0...v1.19.0
[1.18.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.17.0...v1.18.0
[1.17.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.16.0...v1.17.0
[1.16.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.15.0...v1.16.0
[1.15.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.14.0...v1.15.0
[1.14.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.13.0...v1.14.0
[1.13.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.12.0...v1.13.0
[1.12.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.11.0...v1.12.0
[1.11.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.10.0...v1.11.0
[1.10.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.9.0...v1.10.0
[1.9.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.11...v1.4.0
[1.3.11]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.10...v1.3.11
[1.3.10]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.9...v1.3.10
[1.3.9]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.8...v1.3.9
[1.3.8]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.7...v1.3.8
[1.3.7]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.6...v1.3.7
[1.3.6]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.1.0...v1.3.6
[1.1.0]: https://github.com/Poliklot/bitrix-agent-skill/releases/tag/v1.1.0
[1.0.0]: https://github.com/Poliklot/bitrix-agent-skill/releases/tag/v1.0.0
