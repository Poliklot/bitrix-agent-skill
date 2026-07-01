# Bitrix Composite Cache — справочник

> Reference для Bitrix-скилла. Загружай, когда задача связана с “Композитным сайтом”, `/bitrix/html_pages/`, `X-Bitrix-Composite`, `setFrameMode`, `COMPOSITE_FRAME_*`, `createFrame`, `FrameHelper`, dynamic areas, персонализацией в публичном HTML, вторым запросом/cache pass, “пользователь видит чужие данные”, “корзина/цены моргают” или “изменения не видны только при включённом composite”. Для component result cache дополнительно читай [components.md](components.md), для `Data\Cache`/tagged cache — [cache-infra.md](cache-infra.md), для SEO/index visibility — [index-cache-diagnostics.md](index-cache-diagnostics.md) и [seo-cache-access.md](seo-cache-access.md), для security/session — [security.md](security.md) и [session-auth.md](session-auth.md).

## Core audit note

Справочник сверялся по `main` 26.150.0 из локального core:

| Core file | Подтверждённый контракт |
|---|---|
| `bitrix/modules/main/classes/general/component.php` | `CBitrixComponent::setFrameMode`, `getFrameMode`, `getDefaultFrameMode`, `COMPOSITE_FRAME_MODE`, negative component vote |
| `bitrix/modules/main/classes/general/component_template.php` | `CBitrixComponentTemplate::setFrameMode`, `createFrame`, template cached data `frameMode`/`frames` |
| `bitrix/modules/main/lib/composite/internals/automaticarea.php` | auto-wrapper first-level components, `COMPOSITE_FRAME_TYPE`, dynamic-with-stub modes |
| `bitrix/modules/main/lib/composite/bufferarea.php` | `begin`, `beginStub`, `end`, stub/dynamic buffering, class alias `FrameHelper` |
| `bitrix/modules/main/lib/composite/staticarea.php` | dynamic area registry, nested-area guard, `setBrowserStorage`, `setAutoUpdate`, `setAnimation`, `setAssetMode` |
| `bitrix/modules/main/lib/composite/page.php` | current-page cache key/storage, `delete`, `deleteAll`, `markNonCacheable`, `isCacheable`, class alias `Data\StaticHtmlCache` |
| `bitrix/modules/main/lib/composite/responder.php` | early static response, request exclusions, `X-Bitrix-Composite: Cache (...)` |
| `bitrix/modules/main/lib/composite/engine.php` | AJAX dynamic response, `X-Bitrix-Composite: Ajax (...)`, `replaceSessid`, legacy `Page\Frame` alias |
| `bitrix/modules/main/lib/composite/helper.php` | options, default masks/params, cache key path, cookies `_NCC`, `_CC`, `_PK` |

Если версия `main` в проекте отличается, сначала сверяй эти файлы в локальном core и только потом применяй примеры.

---

## 1. Ментальная модель

Composite cache — это **page-level static HTML cache** поверх обычного Bitrix-рендера. Обычная цепочка:

```text
source data → component/data/managed cache → template HTML → composite static HTML → browser/CDN
```

Разводи слои:

| Слой | Что кеширует | Где проявляется | Типичный API/файл |
|---|---|---|---|
| Component result cache | `$arResult`, output компонента, дочерние component side effects | `CACHE_TYPE`, `CACHE_TIME`, `StartResultCache()` | `CBitrixComponent`, [components.md](components.md) |
| Data/managed/tagged cache | произвольные данные, ORM/options, зависимости по тегам | `/bitrix/cache`, `/bitrix/managed_cache`, `b_cache_tag` | `Bitrix\Main\Data\Cache`, `TaggedCache` |
| Composite/static HTML | **финальный HTML страницы** с dynamic-area заглушками | `/bitrix/html_pages/`, `X-Bitrix-Composite` | `Bitrix\Main\Composite\Page`, `BufferArea`, `StaticArea` |
| Legacy compatibility aliases | старые имена поверх current composite classes | встречаются в старом коде | `Data\StaticHtmlCache` → `Composite\Page`, `Page\FrameHelper` → `Composite\BufferArea`, `Page\Frame` → `Composite\Engine` |
| Browser/CDN/proxy | ответ или ассеты вне Bitrix PHP | devtools/network/CDN headers | конфиг веб-сервера/CDN |

Практический вывод: “очистить кеш компонента” не равно “обновить уже созданный HTML-файл composite”, а “`setFrameMode(true)`” не равно “не кешировать компонент”.

---

## 2. Request gate: когда composite вообще включается

В `Responder::isValidRequest()` текущий core исключает статическую выдачу до запуска полного PHP, если есть:

- AJAX-маркеры: `HTTP_BX_AJAX`, `bxajaxid`, `X-Requested-With: XMLHttpRequest`;
- query `ncc`;
- путь в `/bitrix/` или `/index_controller.php`;
- `REQUEST_METHOD !== GET`;
- query `sessid`;
- NCC cookie из настроек (`<cookie_prefix>_NCC`, обычно `BITRIX_SM_NCC=Y`);
- stored authorization cookies без CC cookie (`<cookie_prefix>_LOGIN/_UIDH` без `<cookie_prefix>_CC=Y`);
- exclude masks / exclude params;
- отсутствие попадания в include masks;
- host не из composite domains.

`Page::isCacheable()` дополнительно не кеширует страницу, если:

- storage не создан;
- custom `CacheProvider::isCacheable()` вернул `false`;
- включены debug-флаги в kernel session (`SESS_SHOW_TIME_EXEC`, `SHOW_SQL_STAT`, `SHOW_CACHE_STAT`);
- последний HTTP-статус не `200` и не `0`;
- страница получила `markNonCacheable()` или negative component vote.

### Cache key

`Helper::convertUriToPath()` строит ключ как:

```text
/<host>/<normalized-path>/index@<filtered-query><private-key>.html
```

Примеры из core-комментария:

```text
/                 → /index.html
/index.php        → /index.html
/aa/bb/           → /aa/bb/index.html
/?a=b&b=c         → /index@a=b&b=c.html
```

Query сначала проходит `removeIgnoredParams()`: UTM/gclid/yclid/openstat/from и другие ignored parameters по умолчанию не должны плодить HTML-файлы. В проекте проверяй `ONLY_PARAMETERS`, `IGNORED_PARAMETERS`, `EXCLUDE_PARAMS`, `INDEX_ONLY/NO_PARAMETERS` и custom provider/private key.

---

## 3. Headers и режимы ответа

| Header | Что значит |
|---|---|
| `X-Bitrix-Composite: Cache (200)` | PHP `Responder` отдал сохранённый HTML из composite cache |
| `X-Bitrix-Composite: Cache (304)` | PHP `Responder` ответил 304 по условному запросу |
| `X-Bitrix-Composite: Ajax (stable)` | dynamic-area AJAX-hit, static HTML не изменился |
| `X-Bitrix-Composite: Ajax (changed)` | dynamic-area AJAX-hit обнаружил изменение static HTML |
| `X-Bitrix-Composite: Ajax (error:...)` | dynamic AJAX не смог корректно собрать ответ |
| `X-Bitrix-Composite: Nginx (...)` | HTML отдал nginx по composite-конфигу, PHP мог не стартовать |

Для отладки сравнивай:

```text
/page/               # обычный путь, composite может сработать
/page/?ncc=1         # No Composite Cache для проверки без static HTML
/page/?clear_cache=Y # админский clear cache, если есть право cache_control
```

---

## 4. `setFrameMode`: голосование, не dynamic boundary

В core это буквально “голосование шаблона компонента”:

- `CBitrixComponentTemplate::setFrameMode($mode)` хранит `true|false|null` в template state;
- `CBitrixComponent::setFrameMode($mode)` хранит `true|false|null` в component state;
- `getDefaultFrameMode()` берёт `COMPOSITE_FRAME_MODE = Y/N` из параметров компонента, иначе глобальный `FRAME_MODE`;
- если итоговый frame mode `false`, `Page::getInstance()->giveNegativeComponentVote()` помечает страницу как non-cacheable, но **не внутри уже текущей dynamic area**.

```php
<?php
/** @var CBitrixComponentTemplate $this */
$this->setFrameMode(true); // явный vote “за” composite compatibility
?>
<div class="news-list">...одинаковый для всех пользователей HTML...</div>
```

```php
$this->setFrameMode(false); // явный vote “против”: страница не должна попасть в composite cache
```

Важно: `setFrameMode(true)` **не создаёт dynamic area**. Dynamic boundary создают `createFrame()`, `FrameHelper`/`BufferArea` или legacy `Frame::startDynamicWithID()`.

---

## 5. AutoComposite / `AutomaticArea`

Текущий core автоматически оборачивает **first-level components** через `Bitrix\Main\Composite\Internals\AutomaticArea`, если:

- HTML cache включён;
- компонент верхнего уровня (`component stack <= 1`);
- сейчас не выполняется другая dynamic area;
- default frame mode не `false`;
- frame type не `STATIC`;
- компонент не `bitrix:breadcrumb`, не `bitrix:main.include`, не delayed `bitrix:menu`.

Если компонент/шаблон явно адаптирован (`getRealFrameMode() !== null` у component или template), auto-wrapper просто выпускает буфер как есть. Если адаптации нет, core создаёт `StaticArea` вокруг вывода компонента и берёт тип из `COMPOSITE_FRAME_TYPE` или глобального `FRAME_TYPE`:

| `COMPOSITE_FRAME_TYPE` | Что делает auto-wrapper |
|---|---|
| `STATIC` | не оборачивает dynamic area |
| `DYNAMIC_WITH_STUB` | dynamic area, stub = первичный HTML компонента |
| `DYNAMIC_WITH_STUB_LOADING` | dynamic area, stub = `<div class="bx-composite-loading"></div>` |
| `DYNAMIC_WITHOUT_STUB` | dynamic area без явной заглушки |

Практический вывод:

- `setFrameMode(true)` не просто “разрешает composite”, но и помечает компонент/шаблон как адаптированный — auto-wrapper больше не будет считать его неадаптированным;
- если ты ставишь `setFrameMode(true)`, ты обязан сам вынести персональные части в `createFrame()`;
- если ставишь `COMPOSITE_FRAME_MODE=N`, это negative vote, а не “сделать весь компонент dynamic”.

---

## 6. Dynamic areas: `createFrame` / `BufferArea`

`CBitrixComponentTemplate::createFrame($id, $autoContainer)`:

- принудительно ставит template `frameMode = true`;
- создаёт `Bitrix\Main\Composite\BufferArea`;
- сохраняет frame state в template cached data (`frames`), чтобы dynamic-area metadata переживала component result cache;
- если есть parent component — добавляет frame к parent child frames.

### Blank stub

```php
<?php
/** @var CBitrixComponentTemplate $this */
$this->setFrameMode(true);

$frame = $this->createFrame('header-cart-counter')->begin('');
?>
<span class="header-cart-counter"><?= (int)$arResult['COUNT'] ?></span>
<?php $frame->end(); ?>
```

В static HTML попадёт пустая заглушка; реальный счётчик придёт dynamic AJAX-hit.

### Explicit stub

```php
<?php $frame = $this->createFrame('header-cart-counter')->begin('<span class="header-cart-counter">0</span>'); ?>
<span class="header-cart-counter"><?= (int)$arResult['COUNT'] ?></span>
<?php $frame->end(); ?>
```

Нельзя после `begin($stub)` вызывать `beginStub()` — `BufferArea::end()` в этом случае бросит `NotSupportedException`.

### `beginStub()`

```php
<?php $frame = $this->createFrame('profile-link')->begin(); ?>
<a href="/personal/">Здравствуйте, <?= htmlspecialcharsbx($arResult['USER_NAME']) ?></a>
<?php $frame->beginStub(); ?>
<a href="/auth/">Войти</a>
<?php $frame->end(); ?>
```

Core-механика:

- `begin()` запускает dynamic area и буфер;
- `beginStub()` сохраняет накопленное как dynamic part, очищает буфер и начинает stub part;
- `end()` при `beginStub()` выводит dynamic part текущему хиту, а stub сохраняет для static HTML;
- если `beginStub()` не вызван и `begin()` был без `$stub`, static part = dynamic part: первичный HTML станет заглушкой.

### Frame options

`StaticArea` поддерживает:

```php
$frame = $this->createFrame('promo')->begin('');
$frame->setContainerId('promo-container');     // если нужен конкретный DOM-container
$frame->setBrowserStorage(true);               // storageBlocks / browser storage
$frame->setAutoUpdate(false);                  // не автообновлять блок
$frame->setAnimation(true);                    // animation flag
$frame->setAssetMode(\Bitrix\Main\Page\AssetMode::ALL); // до startDynamicArea
// output
$frame->end();
```

Не включай browser storage или `setAutoUpdate(false)` без UX-причины и проверки stale state.

### Dynamic area вне компонента

```php
<?php
$frame = new \Bitrix\Main\Page\FrameHelper('header-region'); // alias к Composite\BufferArea
$frame->begin('');
?>
<span class="header-region"><?= htmlspecialcharsbx($regionName) ?></span>
<?php $frame->end(); ?>
```

Legacy-низкоуровневый вариант:

```php
\Bitrix\Main\Page\Frame::getInstance()->startDynamicWithID('header-region');
// dynamic content
\Bitrix\Main\Page\Frame::getInstance()->finishDynamicWithID('header-region', '');
```

`Page\Frame` — alias к `Composite\Engine`; методы `startDynamicWithID/finishDynamicWithID` в core помечены deprecated. Для нового кода предпочитай `createFrame()`/`FrameHelper`.

### Nested areas

`StaticArea::startDynamicArea()` возвращает `false`, если:

- такой id уже зарегистрирован;
- id равен текущему dynamic id;
- уже есть текущая dynamic area.

То есть вложенные dynamic areas не являются нормальным паттерном: вложенный старт просто не станет новой границей, и диагностика может быть неочевидной.

---

## 7. Персонализация: что нельзя класть в static HTML

Не записывай в composite static HTML:

- `USER_ID`, login, email, имя пользователя, персональные ссылки кабинета;
- корзину, избранное, сравнение, viewed products, count/order state;
- цены/доступность/скидки, если они зависят от группы, пользователя, региона, склада или договора;
- custom CSRF/session hidden fields;
- HTML, зависящий от cookie, User-Agent, A/B bucket, георегиона, текущего времени;
- random DOM IDs/`randString()` без стабильной причины;
- условные `Asset::addCss/addJs` для разных пользователей.

Правила:

1. Если блок различается по пользователю — выноси в dynamic area и отключай component result cache (`CACHE_TYPE = 'N'`) либо делай строго персональный cache key и документируй причину.
2. Если блок различается только по группам прав — проверь `CACHE_GROUPS` и всё равно проверь composite static HTML под гостем и авторизованным.
3. Если блок зависит от региона/cookie — выбирай: dynamic area, JS-переключение по cookie или осознанный provider/private-key strategy. Не добавляй регион в общий HTML “на глаз”.
4. Для форм используй стандартные Bitrix helpers. Core в `Engine::replaceSessid()` очищает значение стандартного `bitrix_sessid_post()` в static HTML, но custom hidden tokens он не знает.

---

## 8. Component cache + composite: безопасная связка

Типовой безопасный маршрут:

```text
Тяжёлый список/карточка → component cache + tagged cache
Персональный маленький блок → dynamic area + CACHE_TYPE=N
Финальная публичная страница → composite static HTML
```

```php
// catalog.section: статичный для текущих params/filter/sort, можно component cache
$APPLICATION->IncludeComponent('bitrix:catalog.section', '', [
    'CACHE_TYPE' => 'A',
    'CACHE_TIME' => 36000000,
    'CACHE_GROUPS' => 'Y',
]);

// vendor:header.cart: персональный; в template.php должен быть createFrame(...)
$APPLICATION->IncludeComponent('vendor:header.cart', '', [
    'CACHE_TYPE' => 'N',
]);
```

Проверяй не только первый HTML, но и второй запрос: component cache может быть корректен при `?ncc=1`, а уже готовый composite HTML — нет.

---

## 9. Очистка и отключение

Composite cache хранит HTML через `Composite\Page` storage:

- file storage: `Application::getPersonalRoot() . '/html_pages' . cacheKey`;
- memcached storage: если проект включил `STORAGE=memcached`/`memcached_cluster` и extension доступен;
- `PageTable` хранит metadata страниц.

Текущий canonical API:

```php
use Bitrix\Main\Composite\Page;

// Удалить текущую страницу по текущему request cache key
Page::getInstance()->delete();

// Удалить весь composite HTML cache и PageTable metadata
Page::getInstance()->deleteAll();

// Не сохранять текущий hit в composite
Page::getInstance()->markNonCacheable();
```

Legacy alias в этом core:

```php
\Bitrix\Main\Data\StaticHtmlCache::getInstance()->deleteAll();
\Bitrix\Main\Data\StaticHtmlCache::getInstance()->markNonCacheable();
```

Пиши `Composite\Page` как current-core путь. `Data\StaticHtmlCache` упоминай как compatibility alias, если видишь старый проектный код.

Для cron/операций используй штатный tool, если он есть в локальном core:

```bash
php -f /path/to/site/bitrix/modules/main/tools/cron_html_pages.php 10
```

Не начинай с ручного удаления `/bitrix/html_pages/<domain>/`. Если проект уже в таком состоянии, проверь `.enabled`, `.config.php`, `.size`, права ФС, storage backend и PageTable metadata.

---

## 10. Что очищать после изменений

| Изменение | Обычно нужно |
|---|---|
| Изменились данные инфоблока/HL | tagged/component cache; composite проверять вторым хитом |
| Изменился шаблон сайта/header/footer/layout | сбросить composite HTML cache |
| Изменилась структура dynamic areas/id/container/stub | сбросить composite HTML cache, проверить AJAX-hit |
| Изменились CSS/JS paths или asset mode | composite + asset cache, проверить head/body |
| Изменилась логика `COMPOSITE_FRAME_MODE/TYPE` | сбросить composite HTML cache, проверить component voting |
| Утечка персональных данных в static HTML | немедленно отключить/очистить composite для затронутых страниц, исправить dynamic boundary, проверить guest/user A/user B |

---

## 11. Диагностика по проекту

### Быстрый grep

```bash
rg -n 'setFrameMode|COMPOSITE_FRAME_MODE|COMPOSITE_FRAME_TYPE|createFrame|FrameHelper|startDynamicWithID|finishDynamicWithID|markNonCacheable|StaticHtmlCache|Composite\\Page|AutomaticArea|BX_COMPOSITE_DEBUG|X-Bitrix-Composite|ncc|_NCC|_CC|_PK' \
  local bitrix/templates www/bitrix/templates www/bitrix/modules --glob '*.php' --glob '*.js'
```

```bash
rg -n 'StartResultCache|AbortResultCache|setResultCacheKeys|CACHE_TYPE|CACHE_TIME|CACHE_GROUPS|RegisterTag|clearByTag|TaggedCache|USER->IsAuthorized|GetID\(' \
  local bitrix/templates www/bitrix/templates www/bitrix/modules --glob '*.php'
```

### Что смотреть

- `X-Bitrix-Composite`: `Cache`, `Ajax stable/changed`, `Ajax error` или nginx-mode;
- Network: был ли AJAX-hit с `X-Bitrix-Composite: get_dynamic`;
- DOM до/после dynamic update: не “моргает” ли критичная информация;
- query/cookies: `ncc`, `sessid`, `bxajaxid`, `BITRIX_SM_NCC`, `BITRIX_SM_CC`, project cookie prefix;
- `COMPOSITE_FRAME_MODE` / `COMPOSITE_FRAME_TYPE` в params компонента;
- с `?ncc=1`: отличается ли баг только composite-слоем или ниже по цепочке;
- под guest, authorized user A, authorized user B.

### Debug log

Для локальной/sandbox диагностики можно проверить, не включён ли project composite debug:

```php
define('BX_COMPOSITE_DEBUG', true);
define('LOG_FILENAME', $_SERVER['DOCUMENT_ROOT'] . '/upload/composite_log.txt');
```

Не включай подробный debug на production без явного решения: лог может быть шумным и раскрывать внутренние URL/состояния.

---

## 12. Verification checklist

Минимальная проверка после правки composite/cache:

1. Проверить локальный `main` core version и наличие `Composite\Page`, `BufferArea`, `AutomaticArea`.
2. Открыть страницу с `?ncc=1` и без `ncc`, сравнить ключевой HTML.
3. Сделать 2–3 последовательных хита: первый создаёт/обновляет, следующие должны показать `X-Bitrix-Composite`.
4. Проверить guest, user A, user B; персональные блоки не должны совпадать между пользователями.
5. Проверить dynamic AJAX response, `htmlCacheChanged`, `dynamicBlocks` и отсутствие JS errors после подстановки DOM.
6. Проверить POST/AJAX/form submit: `sessid`, CSRF, redirect/JSON headers не должны ломаться.
7. Изменить fixture data (товар/раздел/HL/регион/корзина) и повторить second request/cache pass.
8. Зафиксировать, какой слой инвалидирован: component/tagged/managed/composite/browser/CDN.

Для runtime smoke evidence используй [runtime-smoke-verification.md](runtime-smoke-verification.md): там есть `Second request/cache pass`.

---

## 13. Типовые ошибки

- Называть `setFrameMode(true)` “динамическим режимом”. Это vote/adaptation flag, не boundary.
- Ставить `setFrameMode(true)` на шаблон с персональным HTML и не добавлять `createFrame()`.
- Думать, что `COMPOSITE_FRAME_MODE=N` сделает компонент dynamic: это negative vote и page non-cacheable.
- Забывать про `AutomaticArea`: неадаптированный first-level component может быть auto dynamic по `COMPOSITE_FRAME_TYPE`.
- Оборачивать весь тяжёлый список в dynamic area вместо нормального component cache + tagged cache.
- Кешировать персональный component result cache и надеяться, что composite frame всё исправит.
- Делать `begin($stub)` и потом `beginStub()` — core бросит `NotSupportedException`.
- Использовать одинаковый dynamic id для нескольких блоков.
- Добавлять имя пользователя/корзину в `header.php` без frame.
- Делать random IDs, time-dependent HTML или cookie-dependent `<style>` в статическом шаблоне.
- Чистить весь cache stack без layer diagnosis.
- Проверять только `?ncc=1` и не делать second request/cache pass.
- Забывать, что nginx composite может отдать HTML без запуска PHP.
- Игнорировать `X-Bitrix-Composite: Ajax (error:...)` и смотреть только финальный DOM.
