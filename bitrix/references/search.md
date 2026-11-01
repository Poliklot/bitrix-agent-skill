# Поиск (модуль search)

> Audit note: ниже сверено с текущим `www/bitrix/modules/search`. Подтверждены события `BeforeIndex`, `OnSearch`, `OnSearchGetURL` и типовой порядок `Search(...) -> NavStart(...) -> GetNext()`. Детальный контракт `NavStart`, `PAGEN_N` и `GetNavPrint` смотри в `pagination.md`.

```php
use Bitrix\Main\Loader;
Loader::includeModule('search');
```

## Архитектура

Модуль `search` индексирует контент в таблице `b_search_content`. Каждая единица контента идентифицируется парой `(MODULE_ID, ITEM_ID)`. При индексации событие `BeforeIndex` позволяет трансформировать данные.

---

## Индексация: CSearch::Index

```php
CSearch::Index(
    string $MODULE_ID,    // 'my.module' — идентификатор модуля-источника
    string $ITEM_ID,      // '42' — ID элемента в источнике
    array  $arFields,     // поля индекса (см. ниже)
    bool   $bOverWrite = false,  // true — перезаписать если уже есть
    string $SEARCH_SESS_ID = ''  // сессия переиндексации (для пакетного обновления)
);
```

### Поля $arFields

| Поле | Обязательно | Описание |
|------|-------------|----------|
| `TITLE` | да | Заголовок документа |
| `BODY` | да | Текст для индексации (без HTML-тегов) |
| `URL` | да | URL страницы с документом |
| `SITE_ID` | да | Ассоц. массив `['s1' => '']` или простой `['s1']` |
| `PARAM1` | нет | Группировка первого уровня (напр. тип контента) |
| `PARAM2` | нет | Группировка второго уровня (напр. ID раздела) |
| `TAGS` | нет | Строка тегов через запятую |
| `DATE_CHANGE` | да | Дата изменения источника в формате legacy API проекта |
| `PERMISSIONS` | да для безопасного примера | Список ID групп с правом чтения из источника |

```php
// $dateChange — дата изменения источника в формате проекта.
CSearch::Index('my.module', (string)$elementId, [
    'TITLE'         => 'Название новости',
    'BODY'          => strip_tags($content),   // убираем HTML
    'URL'           => '/news/' . $code . '/',
    'SITE_ID'       => [SITE_ID => ''],        // текущий сайт
    'PARAM1'        => 'my.module',            // модуль
    'PARAM2'        => (string)$sectionId,     // раздел
    'TAGS'          => 'новость, важное',
    'DATE_CHANGE'   => $dateChange,
    'PERMISSIONS'   => $readGroupIds,          // проверенные права источника; [2] только для публичного
], true);
```

> **Gotcha:** `SITE_ID` передаётся как ассоц. массив `['s1' => '']`, а не строка. Если передать строку `'s1'` — ядро само приведёт к `['s1' => '']`.

---

## Удаление из индекса: CSearch::DeleteIndex

```php
// Удалить один элемент
CSearch::DeleteIndex('my.module', (string)$elementId);

// Удалить все элементы модуля
CSearch::DeleteIndex('my.module');

// Удалить по PARAM1 (все элементы раздела)
CSearch::DeleteIndex('my.module', false, 'my.module', (string)$sectionId);

// ITEM_ID поддерживает wildcard с %
CSearch::DeleteIndex('my.module', '42%');
```

---

## Полная переиндексация: CSearch::ReIndexAll

```php
// Один шаг. $savedState — сохранённое состояние этого же задания либо [].
$next = CSearch::ReIndexAll(false, 10, $savedState);
if (is_array($next)) {
    // Сохранить $next целиком; следующий шаг — отдельный запуск задания.
} else {
    // Завершено: $next — число, 0 тоже допустим.
}
```

> `ReIndexAll` вызывает события `OnReindex` у всех модулей. Для включения своего модуля нужно зарегистрировать обработчик.

---

## Поиск: CSearch::Search

```php
$obSearch = new CSearch();
$obSearch->Search([
    'QUERY'   => 'поисковый запрос',
    'SITE_ID' => SITE_ID,
    'MODULE_ID' => 'iblock',         // документированный фильтр по модулю
    'CHECK_DATES' => 'Y',            // учитывать сроки активности
    'PARAM1'  => $iblockTypeId,      // тип инфоблока из индексатора
    'PARAM2'  => '5',                // фильтр по подгруппе
]);

if ($obSearch->errorno != 0) {
    // ошибка поиска
    echo $obSearch->error;
} else {
    while ($arResult = $obSearch->GetNext()) {
        // $arResult['TITLE']    — заголовок
        // $arResult['BODY']     — отрывок с подсветкой
        // $arResult['URL']      — ссылка
        // $arResult['MODULE_ID']
        // $arResult['PARAM1'], $arResult['PARAM2']
        // $arResult['RANK']     — релевантность
        echo htmlspecialchars($arResult['TITLE']) . '<br>';
    }
}
```

### Параметры поиска

| Параметр | Описание |
|----------|----------|
| `QUERY` | Поисковая фраза |
| `SITE_ID` | ID сайта |
| `MODULE_ID` | Фильтр по модулю |
| `PARAM1` | Фильтр первого уровня |
| `PARAM2` | Фильтр второго уровня |
| `TAGS` | Поиск по тегам |

### Пагинация

```php
$obSearch = new CSearch();
$obSearch->Search([...]);
$obSearch->NavStart(20, false);    // PAGE_RESULT_COUNT, без "показать всё"

// Страницы
$obSearch->NavPrint('Поиск');      // стандартная навигация Bitrix
$totalCount = $obSearch->GetRecordCount();
```

---

## AJAX-подсказки и быстрый поиск: CSearchTitle + search.suggest.input

В текущем core подтверждены:

- `CSearchTitle::Search`
- стандартный компонент `bitrix:search.suggest.input`
- шаблоны `bitrix:search.form` и `bitrix:search.page`, которые уже используют `bitrix:search.suggest.input`

```php
$searchTitle = new CSearchTitle();
$searchTitle->Search(
    $phrase,
    10,
    ['SITE_ID' => SITE_ID]
);

while ($item = $searchTitle->GetNext()) {
    echo $item['NAME'] . PHP_EOL;
}
```

Если задача звучит как:

- “сделать быстрый AJAX-поиск”
- “вывести подсказки под строкой поиска”
- “почему suggest не отдаёт URL”

то сначала проверь:

1. `bitrix:search.suggest.input`
2. `CSearchTitle::Search`
3. событие `OnSearchGetURL`
4. индексацию сущности и её `SITE_ID`

---

## Событие BeforeIndex — трансформация перед записью в индекс

Позволяет изменить или отфильтровать данные перед индексацией:

```php
// В include.php или install/index.php модуля
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandler(
    'search',
    'BeforeIndex',
    ['\MyVendor\MyModule\SearchHandler', 'onBeforeIndex']
);
```

```php
namespace MyVendor\MyModule;

class SearchHandler
{
    public static function onBeforeIndex(array $arFields): array
    {
        if ($arFields['MODULE_ID'] === 'iblock' && $arFields['PARAM1'] === 'private') {
            $arFields['TAGS'] .= ', private';
        }

        // Можно изменить данные
        $arFields['TAGS'] .= ', дополнительный тег';
        return $arFields;
    }
}
```

> **Gotcha:** В текущем core `BeforeIndex` обрабатывает только массив, который вернул обработчик. `return null/false` не отменяет индексацию автоматически, а просто игнорируется. Если нужно пропустить запись, делай это до вызова `CSearch::Index()`.

---

## Событие OnSearch — дополнительные параметры URL поисковой страницы

```php
// Обработчик возвращает строку для добавления к URL результатов
EventManager::getInstance()->addEventHandler(
    'search',
    'OnSearch',
    function(string $query): string {
        // $query — поисковая строка
        // Вернуть строку query-параметра или ''
        return '';
    }
);
```

## Событие OnSearchGetURL — построение итогового URL результата

```php
EventManager::getInstance()->addEventHandler(
    'search',
    'OnSearchGetURL',
    function(array $row): ?string {
        if ($row['MODULE_ID'] === 'my.module') {
            return '/custom/path/' . $row['ITEM_ID'] . '/';
        }

        return null;
    }
);
```

`OnSearch` и `OnSearchGetURL` — разные этапы: первый добавляет query-параметры к URL выдачи, второй может подменить сам URL результата при `Fetch()/GetNext()`, в том числе для `CSearchTitle`.

---

## Регистрация модуля для ReIndexAll

Legacy-событие OnReindex передаёт позиционные аргументы. Зарегистрируй постоянную зависимость в инсталляторе, удали её при деинсталляции:

```php
RegisterModuleDependences(
    'search', 'OnReindex', 'vendor.module',
    'Vendor\\Module\\SearchReindex', 'onReindex'
);
```

Схема обработчика ниже иллюстрирует протокол, а не готовый индексатор. Проектный iterateDocuments нужно реализовать: он выдаёт документы по возрастанию ID после курсора с DATE_CHANGE, TITLE, BODY, URL, SITE_ID и реальными PERMISSIONS источника. Не считывай неэкранированный индекс из уже HTML-экранированного представления.

```php
namespace Vendor\Module;

class SearchReindex
{
    public static function onReindex($NS, $callback, $method)
    {
        $afterId = ($NS['MODULE'] ?? '') === 'vendor.module'
            ? (int)($NS['ID'] ?? 0) : 0;
        foreach (static::iterateDocuments($afterId) as $document) {
            if (!call_user_func([$callback, $method], $document)) {
                return $document['ID'];
            }
        }
        return false;
    }
}
```

---

## Синхронизация источника и индекса

Для обычных инфоблоков сначала используй штатную индексацию iblock, не создавай второй документ под my.module без отдельной необходимости. Для собственного источника сохраняй в документе его права, сайты и дату изменения. Изменение ACL синхронизируй отдельно (K114), даже если текст не менялся.

Не удаляй custom-индекс в OnBeforeIBlockElementDelete: последующий обработчик может запретить удаление источника. Запускай синхронизацию после подтверждённого изменения и используй повторяемое задание; OnAfter сам по себе не доказывает commit (K03).

---

## Готовые параметры компонента bitrix:search.title

Для отображения формы и результатов поиска используй стандартный компонент:

```php
$APPLICATION->IncludeComponent('bitrix:search.title', '', [
    'SITE_ID'       => SITE_ID,
    'USE_LANGUAGE_GUESS' => 'Y',
    'USE_SUGGEST'   => 'Y',
    'RESULT_URL'    => '/search/',
]);
```

```php
// На странице результатов: bitrix:search.page
$APPLICATION->IncludeComponent('bitrix:search.page', '', [
    'SITE_ID'         => SITE_ID,
    'USE_SUGGEST'     => 'Y',
    'SHOW_WHEN_EMPTY' => 'Y',
    'USE_LANGUAGE_GUESS' => 'Y',
]);
```

---

## Gotchas

- `CSearch::Index` — работает только если модуль `search` подключён через `Loader::includeModule('search')`
- `BODY` — передавай текст без HTML (`strip_tags`), иначе теги попадут в индекс
- `SITE_ID` может быть строкой `'s1'` — ядро само приведёт к `['s1' => '']`
- `bOverWrite` управляет перезаписью существующего документа, не созданием дублей (K111).
- `DeleteIndex` без `$ITEM_ID` удаляет **весь** индекс модуля — используй осторожно
- `ReIndexAll(true)` очищает индекс на первом шаге; сохраняй NS продолжения (K116).
- `PERMISSIONS` — список читателей, не карта уровней; группа 2 включает гостя (K113).

## K111 — bOverWrite не создаёт второй документ индекса

Идентичность CSearch::Index остаётся парой MODULE_ID/ITEM_ID. bOverWrite управляет перезаписью уже индексированного документа, а не созданием дубля. Для принудительного обновления существующего документа передай true; не меняй ITEM_ID ради обновления.

**Проверка на стенде:** Два вызова с одной идентичностью не размножают документы.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/indexs.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K112 — Дата поискового документа — DATE_CHANGE

В документированном формате CSearch::Index дата изменения передаётся в DATE_CHANGE. Бери время изменения источника в формате, ожидаемом legacy API проекта; не подменяй его временем запуска переиндексации. LAST_MODIFIED не является показанным официальным полем этого вызова.

**Проверка на стенде:** Документы сохраняют порядок реальных изменений после повторной индексации.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/indexs.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K113 — PERMISSIONS поиска — список читателей, не карта R/D

Для показанного legacy группового контракта PERMISSIONS передаёт список ID групп с правом чтения, не карту G2→R/G1→D. Группа 2 — все посетители, включая гостя: добавляй её только для публичного документа. Разрешённый список выводится из прав источника, не из групп оператора.

**Проверка на стенде:** Гость не видит частный документ, разрешённая группа видит; публичный виден гостю.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/changepermission.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K114 — Изменение прав источника синхронизируется с индексом

Изменение ACL без изменения текста тоже требует обновления индекса. ChangePermission принимает новый список читателей и область MODULE_ID/ITEM_ID/PARAM1/PARAM2/SITE_ID; false снимает соответствующее ограничение. Для одного документа задай ITEM_ID явно. Страница источника всё равно обязана проверять доступ.

**Проверка на стенде:** Отзыв доступа убирает результат и сниппет, соседние документы не затронуты.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/changepermission.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K115 — ChangeSite изменяет привязки и пути индекса

ChangeSite получает карту сайт→путь и ограничения набора документов. Для одного документа используй точный MODULE_ID/ITEM_ID; для миграции сначала сформируй список затронутых записей. В официальной странице есть опечатка ChangePermission в сигнатуре: название и пример относятся к ChangeSite. Не копируй её как вызов ACL.

**Проверка на стенде:** Меняется только нужный документ, выдача соседнего сайта не загрязнена.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/changesite.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K116 — ReIndexAll возвращает состояние или итоговый счётчик

Массив результата ReIndexAll — продолжение, число — завершение (включая 0). Сохраняй NS между запросами и передавай без потери полей; ограничивай время одного шага. Третий аргумент — состояние, не произвольный фильтр MODULE_ID/SITE_ID. Полный режим очищает индекс на первом шаге: не начинай новый пустой NS вместо продолжения.

**Проверка на стенде:** Продолжение не повторяет первый шаг; ноль элементов завершает процесс.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/reindexall.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K117 — ReIndexAll нельзя вкладывать в незавершённую транзакцию импорта

Документация предупреждает о внутренней транзакции ReIndexAll для MySQL/InnoDB. Не вызывай её внутри незавершённой транзакции импорта. Владелец операции сначала завершает изменение источника, затем запускает отдельное восстановимое задание индексации; helper не должен самовольно коммитить чужую транзакцию.

**Проверка на стенде:** При откате импорта задание не публикует незавершённые данные.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/reindexall.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K118 — OnReindex использует callback поискового модуля

Документированный OnReindex получает NS, объект callback и имя метода. Передавай подготовленный документ callback; если он просит остановку, возвращай ID позиции, после исчерпания — false. Не заменяй этот протокол собственным вызовом Index и возвратом массива NS. Регистрация legacy-обработчика должна сохранять позиционные аргументы.

**Проверка на стенде:** Два шага продолжаются после курсора без пропусков; callback ограничивает шаг.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/events/onreindex.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.

## K119 — Ограничение поиска задаётся MODULE_ID

В CSearch::Search используй MODULE_ID; PARAM1/PARAM2 должны соответствовать данным индексатора, а не случайно повторять имя модуля. Для штатного iblock PARAM1 — тип, PARAM2 — ID инфоблока. Сохранение SITE_ID и CHECK_DATES=Y делает область публичной выдачи явной; это не замена прав источника.

**Проверка на стенде:** Одинаковое слово в двух модулях не расширяет заданную область.

[Официальный контракт](https://dev.1c-bitrix.ru/api_help/search/classes/csearch/search.php). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.
