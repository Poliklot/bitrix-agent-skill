# Site Cloud Mobile
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `landing.md`

# Лендинги и public pages (модуль landing)

> Audit note: ниже сверено с текущим `www/bitrix/modules/landing`. Подтверждены классы `\Bitrix\Landing\Landing`, `Site`, `Block`, `Hook`, `Rights`, `Manager`, а также стандартные компоненты `bitrix:landing.pub`, `bitrix:landing.landing_view`, `bitrix:landing.landing_edit`, `bitrix:landing.landings`, `bitrix:landing.sites`, `bitrix:landing.site_edit`, `bitrix:landing.domain_edit`, `bitrix:landing.mainpage.pub`.

## Архитектура

Модуль `landing` в текущем core строится вокруг нескольких сущностей:

- `Site` — сайт/контейнер лендингов
- `Landing` — конкретная страница
- `Block` — блок на странице
- `Hook` — SEO, дизайн и meta-конфиг для site/page
- `Rights` — права на сайты и функции

---

## Сайты и страницы

Подтверждены:

- `\Bitrix\Landing\Site::getList`
- `\Bitrix\Landing\Site::getPublicUrl`
- `\Bitrix\Landing\Site::delete`
- `\Bitrix\Landing\Site::copy`
- `\Bitrix\Landing\Landing::getList`
- `\Bitrix\Landing\Landing::delete`
- `\Bitrix\Landing\Landing::getPublicUrl`
- `\Bitrix\Landing\Landing::copy`

```php
use Bitrix\Landing\Landing;
use Bitrix\Landing\Site;
use Bitrix\Main\Loader;

Loader::includeModule('landing');

$sites = Site::getList([
    'select' => ['ID', 'CODE', 'TYPE', 'ACTIVE'],
    'filter' => ['=DELETED' => 'N'],
    'order' => ['ID' => 'DESC'],
]);

while ($site = $sites->fetch()) {
    $publicUrl = Site::getPublicUrl((int)$site['ID']);
    echo $site['ID'] . ' => ' . $publicUrl . PHP_EOL;
}

$landings = Landing::getList([
    'select' => ['ID', 'TITLE', 'CODE', 'SITE_ID'],
    'filter' => ['=DELETED' => 'N'],
    'order' => ['ID' => 'DESC'],
]);
```

---

## Блоки и режим мутаций

Подтверждены:

- `\Bitrix\Landing\Block::save`
- `\Bitrix\Landing\Block::add`
- `\Bitrix\Landing\Block::update`
- `\Bitrix\Landing\Block::delete`
- `\Bitrix\Landing\Block::getList`

Важная особенность текущего core: прямые `Block::add/update/delete` защищены проверкой `LANDING_MUTATOR_MODE`.

```php
define('LANDING_MUTATOR_MODE', true);

use Bitrix\Landing\Block;
use Bitrix\Main\Loader;

Loader::includeModule('landing');

$result = Block::getList([
    'select' => ['ID', 'LID', 'CODE', 'SORT', 'ACTIVE'],
    'filter' => ['=LID' => $landingId],
    'order' => ['SORT' => 'ASC'],
]);

while ($row = $result->fetch()) {
    var_dump($row);
}
```

Если задача звучит как:

- “поменять контент блока”
- “добавить блок программно”
- “перенести блоки между лендингами”

сначала проверь:

1. есть ли у тебя корректный mutator path
2. не безопаснее ли идти через штатные компоненты/редактор
3. какие hooks/rights завязаны на страницу

---

## Hooks и SEO

Подтверждены:

- `\Bitrix\Landing\Hook::getData`
- `\Bitrix\Landing\Hook::ENTITY_TYPE_SITE`
- `\Bitrix\Landing\Hook::ENTITY_TYPE_LANDING`

`Hook` здесь важен для:

- meta title/description
- OpenGraph и картинок
- дизайна
- шрифтов, тем, background

Отдельно в текущем core подтверждено, что внутри `Landing` используется `Hook\Page\MetaOg::getAllImages()` для извлечения OG-изображений.

```php
use Bitrix\Landing\Hook;
use Bitrix\Main\Loader;

Loader::includeModule('landing');

$pageHooks = Hook::getData($landingId, Hook::ENTITY_TYPE_LANDING);
$siteHooks = Hook::getData($siteId, Hook::ENTITY_TYPE_SITE);
```

---

## Права

Подтверждены:

- `\Bitrix\Landing\Rights`
- константы `ENTITY_TYPE_SITE`
- access types `denied/read/edit/sett/public/delete`
- дополнительные права `admin/create/menu24/...`

Практически это значит:

- задачи “почему лендинг открывается, но не редактируется” почти всегда упираются в `Rights`
- задачи “почему сайт не виден в меню/списке” могут упираться в дополнительное право, а не в сам факт существования записи

---

## Стандартные компоненты

Подтверждены:

- `bitrix:landing.pub`
- `bitrix:landing.landing_view`
- `bitrix:landing.landing_edit`
- `bitrix:landing.landings`
- `bitrix:landing.sites`
- `bitrix:landing.site_edit`
- `bitrix:landing.domain_edit`
- `bitrix:landing.mainpage.pub`

Для большинства задач по UI сначала смотри именно компонентный контракт, а не низкоуровневые таблицы.

---

## Gotchas

- `landing` нельзя вести как обычный `iblock`-сайт: здесь отдельная модель прав, hooks и publication path.
- `Block::add/update/delete` в текущем core не рассчитаны на произвольный прямой вызов без `LANDING_MUTATOR_MODE`.
- Для public URL всегда сверяйся с `Site::getPublicUrl` и `Landing::getPublicUrl`, а не строй ссылки вручную.

---

## Source: `sitecorporate.md`

# SiteCorporate, solution wizard и stock furniture components

> Reference для Bitrix-скилла. Загружай, когда задача связана с модулем `bitrix.sitecorporate`, повторным запуском решения `corp_services` / `corp_furniture`, демо-данными корпоративного сайта, panel-button мастера или стандартными `furniture.*`-компонентами.
>
> Audit note: проверено по текущему core `bitrix.sitecorporate` версии `24.0.0` через `install/index.php`, `include.php`, оба wizard `.description.php`, `wizard.php` и стандартные solution-компоненты.

## Что это за модуль в текущем core

`bitrix.sitecorporate` в текущем ядре не является общим runtime-модулем с бизнес-API. Это тонкий solution-layer вокруг двух мастеров установки:

- `bitrix:corp_services`
- `bitrix:corp_furniture`

При установке модуль:

- регистрирует `main:OnBeforeProlog -> CSiteCorporate::ShowPanel`
- копирует solution-компоненты в `/bitrix/components`
- добавляет в административную панель кнопку повторного запуска мастера

Если задача звучит как "переустановить корпоративный сайт", "обновить демо-данные решения", "перезапустить мастер", "поменять banner/logo/slogan решения", "разобраться со stock furniture component", это маршрут именно сюда.

## Как модуль выбирает нужный wizard

Панельная кнопка появляется только у администратора и только если в `main:wizard_solution` для текущего `SITE_ID` записано одно из значений:

- `corp_services`
- `corp_furniture`

Фактический переход идёт на:

- `/bitrix/admin/wizard_install.php?...&wizardName=bitrix:corp_services&wizardSiteID=SITE_ID`
- `/bitrix/admin/wizard_install.php?...&wizardName=bitrix:corp_furniture&wizardSiteID=SITE_ID`

```php
$solution = COption::GetOptionString('main', 'wizard_solution', '', SITE_ID);

if (in_array($solution, ['corp_services', 'corp_furniture'], true))
{
    $wizardUrl = '/bitrix/admin/wizard_install.php'
        . '?lang=' . LANGUAGE_ID
        . '&wizardName=bitrix:' . $solution
        . '&wizardSiteID=' . SITE_ID
        . '&' . bitrix_sessid_get();
}
```

Важно: в `include.php` обе ветки используют один и тот же panel button ID `corp_services_wizard`. Если задача связана с дублированием/перекрытием кнопки, это не "ошибка интегратора", а поведение текущего core.

## Подтверждённые wizard-решения

Оба мастера в `.description.php` описаны одинаково по типу запуска:

- `START_TYPE = WINDOW`
- `WIZARD_TYPE = INSTALL`
- `PARENT = wizard_sol`

Типовой набор шагов:

- `SelectSiteStep`
- `SelectTemplateStep`
- `SelectThemeStep`
- `SiteSettingsStep`
- `DataInstallStep`
- `FinishStep`

Если `wizardSiteID` уже передан, `SelectSiteStep` пропускается.

## Что реально меняет `corp_services`

В `install/wizards/bitrix/corp_services/wizard.php` `SiteSettingsStep` работает не через абстрактные "настройки решения", а через конкретные include-файлы и метаданные сайта.

Подтверждённые точки записи:

- `include/company_name.php`
- `include/banner.php`
- `include/banner_text.php`
- `include/company_slogan.php`
- `include/copyright.php`
- `siteMetaDescription`
- `siteMetaKeywords`
- `installDemoData`

Также мастер обрабатывает загрузки:

- `siteLogo` через `SaveFile(...)`
- `siteBanner` через `SaveFile(...)`

То есть задачи "поменять текст баннера решения", "переустановить логотип из wizard", "перегенерировать include-файлы корпоративного шаблона" надо вести через этот слой, а не искать несуществующий сервисный API модуля.

## Что реально меняет `corp_furniture`

В `install/wizards/bitrix/corp_furniture/wizard.php` набор похожий, но уже без баннерного контура `corp_services`.

Подтверждённые точки записи:

- логотип сайта
- slogan
- copyright
- `siteMetaDescription`
- `siteMetaKeywords`
- `installDemoData`

Загрузка файлов подтверждена через `SaveFile("siteLogo", ...)`.

## Stock components, которые модуль реально приносит

В текущем core у решения есть не универсальные catalog/business-компоненты, а solution-specific helpers:

- `bitrix:furniture.catalog.index`
- `bitrix:furniture.catalog.random`
- `bitrix:furniture.vacancies`

### `bitrix:furniture.catalog.index`

Используется в публичных страницах решения `corp_furniture`. Компонент работает как лёгкий solution-index по инфоблоку:

- читает разделы и элементы из указанного инфоблока
- строит верхнеуровневый вывод по каталогу
- кеширует результат с учётом групп пользователя

Если задача про "почему не выводятся разделы на главной корпоративного шаблона", сначала смотри именно этот компонент и его параметры из wizard-публички.

### `bitrix:furniture.catalog.random`

Используется как solution-блок случайного спецпредложения:

- берёт элементы из набора инфоблоков
- фильтрует по признаку спецпредложения
- выбирает случайный элемент
- учитывает права и кеширование

Это не общий механизм промо-каталога, а конкретный legacy helper решения.

### `bitrix:furniture.vacancies`

Используется на страницах вакансий решения:

- читает элементы инфоблока вакансий
- умеет формировать public edit/delete actions
- завязан на include-area/public-edit режимы

Если задача звучит как "в админке вакансии есть, а на сайте корпоративного решения не видны", сначала проверяй именно эту связку.

## Если `local/*` отсутствует: где следующий слой истины

В текущем checkout проектного `www/local` вообще нет. Для `bitrix.sitecorporate` это значит, что после модульного кода следующим правдивым слоем становятся сами wizard assets:

- `install/wizards/bitrix/corp_services/site/templates/corp_services`
- `install/wizards/bitrix/corp_furniture/site/templates/furniture`
- `install/wizards/bitrix/corp_services/site/public/{lang}/...`
- `install/wizards/bitrix/corp_furniture/site/public/{lang}/...`

Здесь подтверждены:

- `header.php` / `footer.php`
- `common.css`, `styles.css`, `template_styles.css`
- theme-папки `themes/*/colors.css`
- preview/screen assets и language-описания шаблонов

Если на проекте нет `local/templates` и `local/components`, именно этот wizard/template слой надо читать перед любыми предположениями о том, "как должен выглядеть типовой сайт решения".

## Public skeleton решения тоже часть контракта

Public-файлы решения в `site/public/*` не абстрактные заглушки, а реальные страницы, которые:

- подключают `/bitrix/header.php` и `/bitrix/footer.php`
- включают стандартные компоненты
- задают первоначальную карту страниц и разделов решения

Подтверждённые include-ы в public skeleton:

- `bitrix:furniture.catalog.index`
- `bitrix:furniture.catalog.random`
- `bitrix:furniture.vacancies`
- `bitrix:news`
- `bitrix:news.list`
- `bitrix:main.feedback`
- `bitrix:main.map`
- `bitrix:map.google.view`
- `bitrix:search.page`
- `bitrix:catalog`

Это важно для аудита "почему страница из мастера не работает": иногда проблема не в wizard и не в template, а в том, что stock public-страница тянет стандартный компонент, который требует соседний модуль.

## Важное ограничение `corp_furniture`

В public skeleton `corp_furniture` подтверждены страницы `services/index.php` и `products/index.php`, которые включают `bitrix:catalog`.

Следствие для текущего audited core:

- сам модуль `bitrix.sitecorporate` подтверждён и активен
- но часть stock public-страниц `corp_furniture` опирается на магазинный контур
- это не доказывает наличие `catalog` в проекте

Поэтому для задач вокруг `corp_furniture` всегда разделяй:

- wizard и template layer решения
- собственные `furniture.*` helpers
- внешние зависимости public skeleton на `catalog` и другие модули

## Что смотреть в проекте первым

1. `main:wizard_solution` для текущего `SITE_ID`
2. Есть ли в публичке вызов `wizard_install.php` или panel button
3. Какие include-файлы уже созданы мастером в `SITE_DIR/include/*`
4. Какие stock template-файлы решения лежат в `install/wizards/.../site/templates/*`
5. Какие public-страницы решения лежат в `install/wizards/.../site/public/*`
6. Есть ли оверрайд `furniture.*` компонентов в `local/components` или шаблонах

## Типовые маршруты задач

### Повторно прогнать решение для текущего сайта

- проверь `COption::GetOptionString('main', 'wizard_solution', '', SITE_ID)`
- если там `corp_services` или `corp_furniture`, веди в `wizard_install.php`
- отдельно проверь, не были ли уже руками изменены include-файлы, которые wizard перезапишет

### Понять, откуда берётся логотип/слоган/баннер

- для `corp_services` смотри `SiteSettingsStep` и include-файлы решения
- для `corp_furniture` смотри `SiteSettingsStep` без баннерного слоя
- не выдумывай отдельный "настроечный ORM" этого модуля: в текущем core его нет

### Разобраться с блоками каталога/вакансий на корпоративном шаблоне

- сначала смотри stock `furniture.*` компонент
- потом проектный шаблон/оверрайд
- только после этого решай, надо ли переносить страницу на более современный `iblock`/`news`/кастомный компонент

## Gotchas

- `bitrix.sitecorporate` не равно "корпоративный модуль сайта". Это wizard shell плюс несколько solution-компонентов.
- Изменения wizard могут переписывать include-файлы и демо-данные. Перед запуском мастера на существующем сайте оцени обратимость.
- Кнопка в panel зависит от `main:wizard_solution`, а не от "наличия шаблона" как такового.
- `corp_services` и `corp_furniture` надо различать: у них разный набор site settings.
- `furniture.*`-компоненты legacy и solution-specific. Не нужно описывать их как общий API каталога.
- В отсутствие `local/*` следующим truth layer становятся wizard `site/templates/*` и `site/public/*`, а не выдуманные project overrides.
- Stock public-страницы `corp_furniture` используют `bitrix:catalog`; это условная зависимость skeleton-слоя, а не доказательство, что магазинный core уже установлен.

---

## Source: `photogallery.md`

# Фото-галереи, альбомы, upload и комментарии (модуль photogallery)

> Audit note: ниже сверено с текущим `www/bitrix/modules/photogallery` версии `25.0.0`. Подтверждены инсталлятор модуля, legacy-классы `CPhotogalleryElement`, `CPGalleryInterface`, upload-контур `CPhotoUploader`, а также стандартные компоненты `bitrix:photogallery`, `bitrix:photogallery.user`, `bitrix:photogallery.section`, `bitrix:photogallery.detail`, `bitrix:photogallery.detail.list`, `bitrix:photogallery.detail.list.ex`, `bitrix:photogallery.upload`, `bitrix:photogallery.detail.comment`.

## Для чего использовать

`photogallery` в этом core - отдельный legacy-контур, который нельзя честно сводить к “обычному инфоблоку с картинками”.

Модуль нужен для задач вида:

- пользовательские или общие галереи;
- альбомы как разделы внутри галереи;
- загрузка фотографий с watermark/converters;
- пароль на альбом;
- slideshow, detail list, upload, gallery user routes;
- связка фото с комментариями blog/forum;
- пересчёт веса галереи и служебных UF.

Если задача звучит как:

- “почему фотогалерея не открывается по USER_ALIAS”
- “куда делся оригинал фото”
- “почему пароль на альбом не срабатывает”
- “почему размер галереи не пересчитался”
- “как работает upload в photogallery”

то маршрутом должен быть именно `photogallery`, а не общие `iblock/components`.

## Архитектура модуля

По текущему ядру картина такая:

- модуль почти целиком legacy;
- `lib/` как рабочий API-контур здесь практически пустой;
- основной контракт живёт в `install/components`, `classes/general` и `tools/components_lib.php`;
- логика держится на связке `iblock + section UF + element properties + component routes`.

Практический вывод:

- сначала смотри стандартный photogallery-компонент и `tools/components_lib.php`;
- не пытайся проектировать это как современную D7-сущность, если задача реально идёт через штатный UI.

## Модель данных

В текущем core фактически используются три уровня:

- корневой раздел инфоблока = галерея;
- вложенный раздел = альбом;
- элемент инфоблока = фото.

Подтверждённые служебные поля и свойства:

- `UF_DATE` - дата альбома/галереи;
- `UF_PASSWORD` - пароль альбома;
- `UF_GALLERY_SIZE` - накопленный размер файлов галереи;
- `UF_GALLERY_RECALC` - служебное состояние пересчёта;
- `REAL_PICTURE` - property с оригиналом файла;
- `PROPERTY_BLOG_POST_ID`, `PROPERTY_FORUM_TOPIC_ID` - связка фото с комментариями.

Важно:

- модуль реально завязан на section-UF, а не только на полях раздела/элемента;
- без `REAL_PICTURE` и gallery-UF часть штатной логики работает неполно;
- `gallery.edit` и `section.edit` умеют создавать недостающие UF, но runtime-логика уже предполагает их наличие.

## Инсталлятор и события

Инсталлятор модуля регистрирует зависимости:

- `iblock:OnBeforeIBlockElementDelete` -> `CPhotogalleryElement::OnBeforeIBlockElementDelete`
- `iblock:OnAfterIBlockElementAdd` -> `CPhotogalleryElement::OnAfterIBlockElementAdd`
- `search:BeforeIndex` -> `CRatingsComponentsPhotogallery::BeforeIndex`
- `im:OnGetNotifySchema` -> `CPhotogalleryNotifySchema::OnGetNotifySchema`
- `socialnetwork:OnSocNetGroupDelete` -> `\Bitrix\Photogallery\Integration\Socialnetwork\Group::onSocNetGroupDelete`

Что это значит practically:

- добавление и удаление фото меняет `UF_GALLERY_SIZE`;
- photogallery встроен в search/indexing;
- есть IM notify schema;
- socialnetwork-интеграция в ядре предусмотрена, но в текущем проекте её надо считать deferred, пока модуль `socialnetwork` не подтверждён.

## `CPhotogalleryElement`

Подтверждён legacy-класс `CPhotogalleryElement` в `classes/general/element.php`.

Ключевые методы:

- `CheckElement($ID, &$arElement, &$arSection, &$arGallery)`
- `OnBeforeIBlockElementDelete($ID)`
- `OnRecalcGalleries($ID, $INDEX)`
- `OnAfterRecalcGalleries($IBLOCK_ID, $INDEX)`
- `OnAfterIBlockElementAdd($res)`

Подтверждённое поведение:

- `CheckElement(...)` ищет элемент, его `REAL_PICTURE`, раздел, родительскую галерею и проверяет наличие `UF_GALLERY_SIZE`;
- `OnAfterIBlockElementAdd(...)` увеличивает `UF_GALLERY_SIZE` у галереи на размер файла;
- `OnBeforeIBlockElementDelete(...)` уменьшает `UF_GALLERY_SIZE`;
- пересчёт галереи ведётся через `UF_GALLERY_RECALC`.

Практически это значит:

- если размер галереи “поехал”, ищи не только шаблон, но и lifecycle фото-элемента;
- удаление/добавление фото влияет на section-UF, а не только на элемент.

## `CPGalleryInterface`

Подтверждён основной helper `CPGalleryInterface` в `tools/components_lib.php`.

Ключевые методы:

- `GetGallery($galleryId)`
- `GetSection($id, &$arSection, $params = [])`
- `GetSectionGallery($arSection = [])`
- `GetPermission()`
- `CheckPermission($permission = "D", $arSection = [], $bOutput = true)`
- `GetUserAlias(...)`
- `GetPathWithUserAlias(...)`
- `HandleUserAliases(...)`

Что важно:

- `GetGallery(...)` ищет галерею как корневой раздел по `CODE`;
- `GetSection(...)` возвращает не просто раздел, а готовит `PATH`, `DATE`, `PASSWORD`, `USER_FIELDS`, counts и картинки;
- при несовпадении section и gallery может вернуться `301`, а не просто ошибка;
- `GetPermission()` берёт базовое право через `CIBlock::GetPermission($iblockId)`, но для владельца своей галереи может повысить его до `W`;
- `CheckPermission(...)` умеет парольные альбомы через `UF_PASSWORD` и сессию `$_SESSION['PHOTOGALLERY']['SECTION']`.

### Парольные альбомы

Подтверждено:

- пароль хранится в `UF_PASSWORD`;
- в `section.edit` он кладётся как `md5($_REQUEST["PASSWORD"])`;
- при доступе `CheckPermission(...)` показывает HTML-форму и проверяет пароль через `check_bitrix_sessid()`.

Практическое правило:

- не считай `UF_PASSWORD` plain-text полем;
- если альбом не открывается, проверяй именно hash в UF и сессионный state.

## Стандартные компоненты

Подтверждены компоненты:

- `bitrix:photogallery`
- `bitrix:photogallery.user`
- `bitrix:photogallery.gallery.list`
- `bitrix:photogallery.gallery.edit`
- `bitrix:photogallery.section`
- `bitrix:photogallery.section.list`
- `bitrix:photogallery.section.edit`
- `bitrix:photogallery.section.edit.icon`
- `bitrix:photogallery.detail`
- `bitrix:photogallery.detail.edit`
- `bitrix:photogallery.detail.list`
- `bitrix:photogallery.detail.list.ex`
- `bitrix:photogallery.detail.comment`
- `bitrix:photogallery.upload`
- `bitrix:photogallery.imagerotator`
- `bitrix:photogallery.interface`

### `bitrix:photogallery`

Это комплексный компонент.

Подтверждены SEF-маршруты:

- `section`
- `section_edit`
- `section_edit_icon`
- `index`
- `search`
- `detail`
- `detail_edit`
- `detail_list`
- `detail_slide_show`
- `upload`

Что важно:

- при `SEF_MODE="Y"` компонент реально парсит путь и выставляет `404`, если route не распознан;
- для `ACTION=upload` страница принудительно переводится в `upload`;
- сортировка разделов по умолчанию идёт по `UF_DATE`;
- `USER_ALIAS` и `SECTION_ID/ELEMENT_ID` - базовые переменные маршрута.

### `bitrix:photogallery.section`

Компонент:

- создаёт `CPGalleryInterface`;
- грузит section через `GetSection(...)`;
- может отдавать `301` на каноничный путь;
- строит back/upload/edit/drop ссылки;
- учитывает лимит галереи через `UF_GALLERY_SIZE`.

### `bitrix:photogallery.user`

Компонент:

- работает с `USER_ALIAS`;
- кеширует список галерей пользователя;
- использует root sections инфоблока как галереи пользователя;
- sanitizes alias через regexp `[^a-z0-9_]`.

Практическое правило:

- если alias содержит другие символы, штатный route уже сам их вырежет;
- для диагностики URL-проблем смотри не только rewrite, но и sanitizing внутри компонента.

### `bitrix:photogallery.detail.comment`

Подтверждено:

- `COMMENTS_TYPE` может быть `forum` или `blog`;
- при `COMMENTS_TYPE="blog"` обязателен `BLOG_URL`;
- компонент требует установленный соответствующий модуль;
- photo comment route очищает cache фотогалереи при добавлении комментариев.

Это значит:

- комментарии photo не “встроены сами по себе”;
- для blog/forum сценариев надо параллельно смотреть соответствующий модуль.

## Upload-контур и `CPhotoUploader`

Подтверждён upload helper `CPhotoUploader` в `photogallery.upload/functions.php`.

Ключевые возможности:

- watermark rules из параметров и пользовательского POST;
- поиск шрифта и watermark-файла в файловой системе;
- создание нового альбома при загрузке;
- очистка кешей после upload;
- настройка инфоблока под upload-сценарий.

Особенно важно:

- `adjustIBlock(...)` умеет автоматически создавать file-properties для converters;
- там же создаются moderation properties `PUBLIC_ELEMENT` и `APPROVE_ELEMENT`, если их нет;
- `createAlbum(...)` создаёт новый section и пишет `UF_DATE`.

### Файлы фото

По upload-компоненту подтверждено стандартное разложение:

- `REAL_PICTURE` = оригинал;
- `PREVIEW_PICTURE` = thumbnail/preview;
- `DETAIL_PICTURE` и converter-файлы могут создаваться по настройкам upload-а.

Не путай:

- `REAL_PICTURE` - это не обязательно то же самое, что `DETAIL_PICTURE`;
- часть шаблонов и slideshow берёт размеры и `SRC` именно из `REAL_PICTURE`.

## Интеграция с blog/search/im

Из install step и компонентов подтверждено:

- модуль умеет создавать blog group/blog на установке, если `blog` установлен;
- comment-компонент умеет работать через `blog` или `forum`;
- есть search hook `BeforeIndex`;
- есть notify schema для `im`.

Практический вывод:

- для комментариев и активности photo почти всегда смотри соседний модуль `blog` или `forum`;
- socialnetwork-ветку не активируй в решении, пока сам модуль не подтверждён в текущем core.

## Gotchas

- `photogallery` в этом ядре - legacy и component-first. Не выдумывай для него D7-API, которого тут нет.
- Корневой раздел и вложенный альбом - не одно и то же: права, route и counters завязаны на иерархию разделов.
- `UF_PASSWORD` хранится как hash, а не как открытая строка.
- `UF_GALLERY_SIZE` и `UF_GALLERY_RECALC` - рабочие служебные поля, а не “опциональные метки”.
- `USER_ALIAS` в user-сценариях нормализуется до `[a-z0-9_]`.
- Для photo comments и social-связок обязательно проверяй наличие `blog`/`forum`/`socialnetwork`, а не предполагай их по памяти.

---

## Source: `fileman.md`

# Fileman, HTML Editor, карты и media UI (модуль fileman)

> Audit note: ниже сверено с текущим `www/bitrix/modules/fileman` версии `25.0.0`. Подтверждены D7-части `\Bitrix\Fileman\Controller\HtmlEditorAjax`, `\Bitrix\Fileman\UserField\Address`, `Geo`, `UserField\Types\AddressType`, legacy-слой `properties.php` с типами `map_google`, `map_yandex`, `video`, а также стандартные компоненты `bitrix:fileman.field.address`, `bitrix:fileman.light_editor`, `bitrix:map.google.*`, `bitrix:map.yandex.*`, `bitrix:pdf.viewer`, `bitrix:player`, `bitrix:mobile.player`.

## Для чего использовать

`fileman` в этом core — это не только “редактор файлов в админке”. Практически модуль нужен для:

- HTML editor и связанного AJAX/controller слоя
- пользовательских полей `address` и `geo`
- map/property user types для инфоблоков
- viewer/player-компонентов
- map UI через Google/Yandex компоненты

Если задача касается:

- редактора контента
- карты в инфоблоке
- адресного userfield
- PDF/video/media viewer

то проверяй именно `fileman`.

---

## Address и Geo user fields

Подтверждены:

- `\Bitrix\Fileman\UserField\Address`
- `\Bitrix\Fileman\UserField\Geo`
- `\Bitrix\Fileman\UserField\Types\AddressType`
- компонент `bitrix:fileman.field.address`

Для `AddressType` подтверждены:

- `USER_TYPE_ID = 'address'`
- `RENDER_COMPONENT = 'bitrix:fileman.field.address'`
- `getApiKey`
- `prepareSettings`
- `onBeforeSave`
- `renderEditForm`
- `renderView`
- `renderText`

```php
use Bitrix\Fileman\UserField\Address;
use Bitrix\Main\Loader;

Loader::includeModule('fileman');
Loader::includeModule('location');

$description = Address::getUserTypeDescription();
```

Что важно:

- `address`-поле из `fileman` жёстко связано с модулем `location`
- `Geo` в текущем core помечен как `@deprecated`
- если задача про адресный userfield, почти всегда смотри сразу `fileman` + `location`

---

## Google/Yandex map property types

В `properties.php` подтверждены legacy user type property:

- `CIBlockPropertyMapGoogle`
- `CIBlockPropertyMapYandex`
- `CIBlockPropertyVideo`

Их регистрация подтверждена в `install/index.php` через зависимости:

- `OnIBlockPropertyBuildList`
- `OnUserTypeBuildList` для video user type

Это означает:

- карта в инфоблоке здесь обычно legacy-property, а не современный D7 userfield
- если “карта в свойстве не рендерится”, открывай `fileman/properties.php`, а не только шаблон компонента инфоблока

---

## Стандартные компоненты

Подтверждены:

- `bitrix:fileman.field.address`
- `bitrix:fileman.light_editor`
- `bitrix:map.google.system`
- `bitrix:map.google.search`
- `bitrix:map.google.view`
- `bitrix:map.yandex.system`
- `bitrix:map.yandex.search`
- `bitrix:map.yandex.view`
- `bitrix:pdf.viewer`
- `bitrix:player`
- `bitrix:mobile.player`

Пример обычного map-route:

```php
$APPLICATION->IncludeComponent(
    'bitrix:map.google.view',
    '',
    [
        'INIT_MAP_TYPE' => 'ROADMAP',
        'MAP_DATA' => serialize([
            'google_lat' => 55.751244,
            'google_lon' => 37.618423,
            'google_scale' => 12,
            'PLACEMARKS' => [],
        ]),
        'MAP_WIDTH' => '100%',
        'MAP_HEIGHT' => '400',
    ]
);
```

Если задача про viewer/player, сначала смотри контракт готового компонента, а не пиши свой JS-виджет с нуля.

---

## HTML editor и AJAX

Подтверждён controller:

- `\Bitrix\Fileman\Controller\HtmlEditorAjax::getVideoOembedAction`

Это штатный путь для задач, где редактору нужно получить oEmbed по video source.

Также модуль содержит большой legacy-слой в:

- `classes/general/html_editor.php`
- `classes/general/light_editor.php`
- `classes/general/medialib.php`
- `classes/general/fileman_utils.php`

Практическое правило:

- если задача про сам редактор, смотри legacy `classes/general/*`
- если задача про AJAX endpoint редактора, смотри D7 controller в `lib/controller/*`

---

## Что важно помнить

- `fileman` — смешанный модуль: часть задач идёт через D7, часть по-прежнему сидит на старом legacy-слое.
- Для `address`-поля отдельно проверь ключи карты и настройки `fileman`/`bitrix24`, потому что `AddressType::getApiKey()` берёт их из module options.
- `Geo` user field в текущем core deprecated, поэтому не расширяй его без крайней необходимости.
- Карты в инфоблоках и адресные userfield-ы — это разные контуры внутри одного модуля; не смешивай `properties.php` и `UserField\Types\AddressType`.

---

## Source: `location.md`

# Геолокации, адреса и форматы (модуль location)

> Audit note: ниже сверено с текущим `www/bitrix/modules/location` версии `25.100.0`. Подтверждены константы `LOCATION_SEARCH_SCOPE_ALL`, `LOCATION_SEARCH_SCOPE_INTERNAL`, `LOCATION_SEARCH_SCOPE_EXTERNAL`, сервисы `\Bitrix\Location\Service\LocationService`, `AddressService`, `FormatService`, controller-слой `\Bitrix\Location\Controller\Location`, `Address`, `Format`, `RecentAddress`, `Source`, `StaticMap`, а также ORM-таблицы `LocationTable`, `LocationNameTable`, `HierarchyTable`, `AddressTable`, `AddressLinkTable`, `AreaTable`, `LocationFieldTable`, `SourceTable`, `RecentAddressTable`.

## Для чего использовать

`location` в этом core — это не “просто справочник местоположений”, а отдельный D7-контур для:

- поиска и автокомплита адресов
- работы с внутренними и внешними location source
- сохранения адресов как сущностей
- форматов адресов
- связки адресов с другими сущностями

У модуля нет своего стандартного component-layer, поэтому основной путь здесь почти всегда:

1. `install/version.php`
2. `lib/service/*`
3. `lib/controller/*`
4. `lib/model/*`

---

## Поисковые scope

Подтверждены константы из `include.php`:

- `LOCATION_SEARCH_SCOPE_ALL`
- `LOCATION_SEARCH_SCOPE_INTERNAL`
- `LOCATION_SEARCH_SCOPE_EXTERNAL`

Практическое правило:

- если задача про локальную базу адресов Bitrix, сначала смотри `INTERNAL`
- если задача про внешнюю геокодировку/подсказки, чаще нужен `EXTERNAL`
- если поведение “странно смешивается”, проверь, какой scope реально уходит в сервис или controller

---

## LocationService

Подтверждены методы:

- `findById`
- `findByExternalId`
- `findByCoords`
- `autocomplete`
- `findParents`
- `save`
- `delete`

```php
use Bitrix\Location\Service\LocationService;
use Bitrix\Main\Loader;

Loader::includeModule('location');

$location = LocationService::getInstance()->findById(
    123,
    LANGUAGE_ID,
    LOCATION_SEARCH_SCOPE_ALL
);

$suggestions = LocationService::getInstance()->autocomplete([
    'query' => 'Москва',
    'limit' => 10,
], LOCATION_SEARCH_SCOPE_EXTERNAL);
```

Если задача звучит как:

- “найти location по внешнему коду”
- “дать autocomplete адреса”
- “получить родителей location”

то первым делом открывай именно `LocationService`, а не ручные SQL или какие-то старые `CSaleLocation`.

---

## AddressService и форматы

Подтверждены:

- `AddressService::findById`
- `AddressService::findByLinkedEntity`
- `AddressService::save`
- `AddressService::delete`
- `FormatService::findByCode`
- `FormatService::findAll`
- `FormatService::findDefault`

```php
use Bitrix\Location\Service\AddressService;
use Bitrix\Main\Loader;

Loader::includeModule('location');

$addressCollection = AddressService::getInstance()->findByLinkedEntity(
    '42',
    'CRM_COMPANY'
);
```

Это ключевой путь, когда нужно:

- хранить адрес как отдельную сущность
- привязать адреса к своему entity type
- вывести адрес в нужном формате

---

## Controller-слой

Подтверждены `Main\Engine\Controller`:

- `\Bitrix\Location\Controller\Location`
- `\Bitrix\Location\Controller\Address`
- `\Bitrix\Location\Controller\Format`

У `Location` подтверждены action-методы:

- `findByIdAction`
- `autocompleteAction`
- `findParentsAction`
- `findByExternalIdAction`
- `findByCoordsAction`
- `saveAction`
- `deleteAction`

У `Address` подтверждены:

- `findById`
- `saveAction`
- `deleteAction`

У `Format` подтверждены:

- `findByCodeAction`
- `findAllAction`
- `findDefaultAction`

Это хороший маршрут для AJAX-задач и внутреннего UI, когда не хочется вручную собирать endpoint поверх service-слоя.

---

## ORM-таблицы

Подтверждены DataManager-таблицы:

- `\Bitrix\Location\Model\LocationTable`
- `\Bitrix\Location\Model\LocationNameTable`
- `\Bitrix\Location\Model\HierarchyTable`
- `\Bitrix\Location\Model\AddressTable`
- `\Bitrix\Location\Model\AddressLinkTable`
- `\Bitrix\Location\Model\AreaTable`
- `\Bitrix\Location\Model\LocationFieldTable`
- `\Bitrix\Location\Model\SourceTable`
- `\Bitrix\Location\Model\RecentAddressTable`

```php
use Bitrix\Location\Model\LocationTable;
use Bitrix\Main\Loader;

Loader::includeModule('location');

$rows = LocationTable::getList([
    'select' => ['ID', 'CODE', 'EXTERNAL_ID', 'SOURCE_CODE', 'TYPE'],
    'filter' => ['=CODE' => 'moskva'],
    'limit' => 10,
]);
```

Если задача касается миграций, массовой загрузки или аналитических выборок, ORM-слой обычно удобнее controller-методов.

---

## Что важно помнить

- У `location` нет привычного слоя стандартных компонентов, поэтому не ищи решение по шаблонам компонента там, где его нет.
- `EXTERNAL_ID`, `SOURCE_CODE`, `CODE` и внутренний `ID` — это не одно и то же. Ошибки интеграции часто начинаются с их смешения.
- Для адресных UX-задач `location` очень часто идёт в связке с `fileman`-полем `address`, так что при проблемах формы смотри оба модуля.
- Если пользователь говорит “локация не находится”, сначала проверь scope поиска и источник данных, а уже потом кеш и фронт.

---

## Source: `messageservice.md`

# Сообщения, SMS-провайдеры и ограничения (модуль messageservice)

> Audit note: ниже сверено с текущим `www/bitrix/modules/messageservice` версии `24.900.100`. Подтверждены `\Bitrix\MessageService\Message`, `Sender\SmsManager`, абстракции `Sender\Base` и `BaseConfigurable`, `Restriction\RestrictionManager`, `RestService`, controller `\Bitrix\MessageService\Controller\Sender`, internal ORM-таблицы сообщений и ограничений, стандартные компоненты `bitrix:messageservice.config.sender.sms` и `bitrix:messageservice.config.sender.limits`, а также callback-tools `tools/callback_*.php`. Для shop-core связки `messageservice` 25.200.100 с `sender` и SMS-лимитами смотри `shop-marketing-analytics.md`.

## Для чего использовать

`messageservice` в этом core нужен для:

- работы с SMS и внешними message providers
- отправки сообщений через конкретного sender-а
- ограничений и лимитов отправки
- REST-интеграции своих провайдеров
- callback/result URL от провайдера

Если задача звучит как:

- “какой SMS-провайдер сейчас активен”
- “почему SMS не отправляется”
- “как добавить своего sender-а”
- “как обновить статус сообщения по callback”

то это отдельный рабочий контур, а не просто кусок `mail-notifications.md`.

---

## SmsManager

Подтверждены ключевые методы:

- `getSenders`
- `getSenderSelectList`
- `getSenderInfoList`
- `getSenderById`
- `getDefaultSender`
- `getUsableSender`
- `canUse`
- `getManageUrl`
- `getRegisteredSenderList`

```php
use Bitrix\Main\Loader;
use Bitrix\MessageService\Sender\SmsManager;

Loader::includeModule('messageservice');

$senderInfo = SmsManager::getSenderInfoList();
$sender = SmsManager::getUsableSender();
```

Практическое правило:

- не выбирай sender вручную по памяти, если `SmsManager` уже умеет найти usable/default provider
- сначала смотри `canUse()`, потом `getFromList()` и только потом идёшь в реальную отправку

---

## Message и отправка

Подтверждены:

- `Message::loadById`
- `Message::loadByExternalId`
- `Message::createFromFields`
- `Message::send`
- `Message::sendDirectly`
- `Message::checkFields`

```php
use Bitrix\Main\Loader;
use Bitrix\MessageService\Message;
use Bitrix\MessageService\MessageType;
use Bitrix\MessageService\Sender\SmsManager;

Loader::includeModule('messageservice');

$sender = SmsManager::getUsableSender();

$message = Message::createFromFields([
    'TYPE' => MessageType::SMS,
    'MESSAGE_FROM' => $sender ? $sender->getDefaultFrom() : '',
    'MESSAGE_TO' => '+79990000000',
    'MESSAGE_BODY' => 'Bitrix test',
], $sender);

$result = $message->sendDirectly();
```

Отличие по смыслу:

- `send()` — сохраняет сообщение в модульный storage
- `sendDirectly()` — сразу отправляет через sender и возвращает `Sender\Result\SendMessage`

---

## Sender Base / BaseConfigurable

Подтверждено, что provider-контракт строится вокруг:

- `Sender\Base`
- `Sender\BaseConfigurable`

У `Base` подтверждены обязательные методы:

- `getId`
- `getName`
- `getShortName`
- `canUse`
- `getFromList`
- `sendMessage`

Это важно, если задача про свой кастомный sender или диагностику конкретного провайдера.

В текущем core подтверждены провайдеры из `lib/sender/sms/*`, включая:

- `SmsRu`
- `Twilio`
- `Twilio2`
- `SmsAssistentBy`
- `SmsLineBy`
- `SmsEdnaru`
- `Ednaru`
- `EdnaruImHpx`
- `ISmsCenter`
- `Rest`
- `Dummy`
- `DummyHttp`

---

## Ограничения и лимиты

Подтверждены:

- `Restriction\RestrictionManager::canUse`
- `Restriction\RestrictionManager::enableRestrictions`
- `Restriction\RestrictionManager::disableRestrictions`
- `Restriction\RestrictionManager::isCanSendMessage`

А также отдельные ограничения:

- `SmsPerUser`
- `SmsPerPhone`
- `PhonePerUser`
- `UserPerPhone`
- `IpPerUser`
- `IpPerPhone`
- `SmsPerIp`

Практически это значит:

- если сообщение “иногда не уходит”, проверь не только провайдера, но и restriction layer
- если пользователь просит “включить лимиты на отправку”, сначала смотри `RestrictionManager` и `Sender\Limitation`

---

## REST и callbacks

Подтверждён `\Bitrix\MessageService\RestService` со scope `messageservice` и методами:

- `messageservice.sender.add`
- `messageservice.sender.update`
- `messageservice.sender.delete`
- `messageservice.sender.list`
- `messageservice.message.status.update`
- `messageservice.message.status.get`

Подтверждён controller:

- `\Bitrix\MessageService\Controller\Sender::getTemplatesAction`

И подтверждены callback-интеграции в `tools/`:

- `callback_smsru.php`
- `callback_twilio.php`
- `callback_ismscenter.php`
- и другие `callback_*`

Если нужна интеграция со своим провайдером:

1. сначала проверь, решается ли это через REST sender-контракт
2. потом смотри callback path в `tools/`
3. только после этого пиши свой транспортный код

---

## Стандартные компоненты и admin UI

Подтверждены:

- `bitrix:messageservice.config.sender.sms`
- `bitrix:messageservice.config.sender.limits`

Первый работает с configurable sender-ом и его template/config page, второй — с лимитами по sender/from.

Это хороший маршрут для задач:

- “покажи настройки sender-а”
- “редактируй лимиты отправки в админке”

---

## Gotchas

- `mail` и `messageservice` — разные контуры. Email-шаблон не делает модуль SMS автоматически “правильным”.
- Прежде чем отправлять сообщение, проверь три вещи: `sender->canUse()`, корректный `from`, restriction/limitation layer.
- Для callback/result URL не выдумывай свои endpoint-ы, если у модуля уже есть штатные `tools/callback_*`.
- Если задача про шаблоны провайдера, смотри `Controller\Sender::getTemplatesAction` и `isTemplatesBased()`, а не только UI.

---

## Source: `clouds.md`

# Облачное файловое хранилище, bucket-ы и file hooks (модуль clouds)

> Audit note: ниже сверено с текущим `www/bitrix/modules/clouds` версии `25.100.0`. Подтверждены `CCloudStorage`, `CCloudStorageBucket`, `CCloudStorageUpload`, `CCloudTempFile`, абстракция `CCloudStorageService` и провайдеры S3/Yandex/Google/OpenStack/Selectel/HotBox, а также ORM-таблицы `FileBucketTable`, `FileSaveTable`, `FileUploadTable`, `FileResizeTable`, `CopyQueueTable`, `DeleteQueueTable`, `FileHashTable`.

## Для чего использовать

`clouds` в этом core нужен для:

- внешнего хранения файлов вместо локального `upload/`;
- выбора bucket-а по правилам файла;
- получения реального `SRC` из облака;
- `CFile::MakeFileArray(...)` для файлов с `HANDLER_ID` или cloud URL;
- delayed/remote resize cache;
- multipart upload;
- синхронизации, дедупликации и failover bucket-ов.

Если задача звучит как:

- “почему `SRC` у файла не локальный”
- “почему `MakeFileArray` скачивает файл”
- “куда ушёл resize cache”
- “почему файл сохраняется не в тот bucket”

то первым маршрутом должен быть `clouds`, а не только `CFile` и локальный `/upload`.

## Как модуль встраивается в файловый контур

Инсталлятор подтверждает зависимости:

- `main:OnFileSave`
- `main:OnAfterFileSave`
- `main:OnGetFileSRC`
- `main:OnFileCopy`
- `main:OnPhysicalFileDelete`
- `main:OnMakeFileArray`
- `main:OnBeforeResizeImage`
- `main:OnAfterResizeImage`
- `main:OnAfterFileDeleteDuplicate`
- `main:OnBeforeProlog`
- `main:OnAdminListDisplay`
- `main:OnBuildGlobalMenu`
- `clouds:OnGetStorageService`
- `perfmon:OnGetTableSchema`

И агент:

- `CCloudStorage::CleanUp();`

Вывод:

- `clouds` вмешивается в стандартный file lifecycle очень глубоко;
- если проект использует модуль, поведение `CFile` и resize может отличаться от “обычного локального Bitrix”.

## `CCloudStorage`

Это главный orchestration-класс вокруг файловых хуков.

Подтверждены ключевые методы:

- `FindBucketForFile($arFile, $strFileName)`
- `FindBucketByFile($file_name)`
- `OnBeforeResizeImage(...)`
- `OnAfterResizeImage(...)`
- `OnMakeFileArray($arSourceFile, &$arDestination)`
- `DeleteDirFilesEx($path)`
- `OnGetFileSRC($arFile)`
- `MoveFile($arFile, $obTargetBucket)`
- `OnFileSave(&$arFile, ...)`
- `OnAfterFileSave($arFile)`
- `CleanUp()`
- `ResizeImageFileGet(...)`
- `ResizeImageFileDelay(...)`

### Выбор bucket-а

`FindBucketForFile(...)` выбирает bucket по:

- активности bucket-а;
- `READ_ONLY`;
- правилам `MODULE`;
- правилам расширения;
- правилам размера файла.

Практическое правило:

- если файл “не ушёл в облако”, первым делом смотри file rules и writable bucket-ы, а не только код сохранения.

### `OnFileSave`

Из ядра подтверждено:

- если bucket найден, файл получает `HANDLER_ID`;
- модуль может сохранить файл напрямую в bucket;
- может копировать из уже облачного источника;
- учитывает duplicate-control через hash;
- записывает метаданные операции в `FileSaveTable`.

### `OnGetFileSRC`

Если у файла есть `HANDLER_ID > 0`, `SRC` берётся через bucket и уже не обязан указывать на локальный `/upload`.

### `OnMakeFileArray`

Подтверждены два сценария:

- входом приходит URL/путь, который указывает на cloud file;
- входом приходит массив файла с `HANDLER_ID`.

В обоих случаях модуль скачивает файл во временное место и формирует локальный descriptor для дальнейшей работы.

### Resize hooks

`OnBeforeResizeImage(...)` и `OnAfterResizeImage(...)` подтверждают, что resize может:

- скачать оригинал из bucket-а;
- записать resize cache обратно в cloud;
- работать в delayed mode через `b_clouds_file_resize`.

Если “resize есть в БД/кеше, но файла нет локально”, это нормальный маршрут при активном `clouds`.

## `CCloudStorageBucket`

Это рабочий объект конкретного bucket-а.

Подтверждены ключевые методы:

- `Init()`
- `RenewToken()`
- `getBucketArray()`
- `getService()`
- `CheckSettings(...)`
- `CreateBucket()`
- `GetFileSRC($arFile, $encoded = true)`
- `FileExists($filePath)`
- `DownloadToFile($arFile, $filePath)`
- `SaveFile($filePath, $arFile)`
- `DeleteFile($filePath, $fileSize = null)`
- `FileCopy($arFile, $filePath)`
- `FileRename($sourcePath, $targetPath, $overwrite = true)`
- `ListFiles($filePath = '/', $bRecursive = false, $pageSize = 0, $pageMarker = '')`
- `GetFileInfo($filePath)`
- `GetFileSize($filePath)`
- `GetAllBuckets()`
- `Add(...)`
- `Update(...)`
- `Delete()`
- `SetFileCounter(...)`
- `IncFileCounter(...)`
- `DecFileCounter(...)`

Пример:

```php
$bucket = new CCloudStorageBucket(3);

if ($bucket->Init())
{
    $src = $bucket->GetFileSRC('/iblock/ab/photo.jpg', false);
    $exists = $bucket->FileExists('/iblock/ab/photo.jpg');
}
```

## `CCloudStorageUpload`

Это отдельный маршрут multipart upload.

Подтверждены:

- `Start(...)`
- `Next(...)`
- `Part(...)`
- `Finish(...)`
- `Delete()`
- `DeleteOld()`
- `CleanUp()`

Это не просто helper: состояние upload-а живёт в `b_clouds_file_upload`.

## `CCloudStorageService`

Подтверждён абстрактный контракт провайдера:

- `GetID()`
- `GetName()`
- `GetLocationList()`
- `GetSettingsHTML(...)`
- `CheckSettings(...)`
- `CreateBucket(...)`
- `DeleteBucket(...)`
- `IsEmptyBucket(...)`
- `FileExists(...)`
- `FileCopy(...)`
- `DeleteFile(...)`
- `SaveFile(...)`
- `ListFiles(...)`
- `InitiateMultipartUpload(...)`
- `GetMinUploadPartSize()`
- `UploadPart(...)`
- `CompleteMultipartUpload(...)`

И провайдеры, зарегистрированные через `OnGetStorageService`:

- `CCloudStorageService_S3`
- `CCloudStorageService_AmazonS3`
- `CCloudStorageService_Yandex`
- `CCloudStorageService_GoogleStorage`
- `CCloudStorageService_OpenStackStorage`
- `CCloudStorageService_RackSpaceCloudFiles`
- `CCloudStorageService_ClodoRU`
- `CCloudStorageService_Selectel`
- `CCloudStorageService_Selectel_S3`
- `CCloudStorageService_HotBox`

## ORM-таблицы и состояния

Подтверждены:

- `\Bitrix\Clouds\FileBucketTable` — bucket-ы, settings, rules, failover
- `\Bitrix\Clouds\FileSaveTable` — текущие операции сохранения файла
- `\Bitrix\Clouds\FileUploadTable` — multipart upload progress
- `\Bitrix\Clouds\FileResizeTable` — delayed/remote resize tasks
- `\Bitrix\Clouds\CopyQueueTable` — copy/rename/sync queue
- `\Bitrix\Clouds\DeleteQueueTable` — delete queue
- `\Bitrix\Clouds\FileHashTable` — hash/dedup/sync inventory

Особенно полезны:

- `FileSaveTable::startFileOperation(...)`
- `FileSaveTable::setFileSize(...)`
- `FileSaveTable::endFileOperation(...)`
- `FileHashTable::syncList(...)`
- `FileHashTable::syncEnd(...)`
- `FileHashTable::duplicateList(...)`
- `FileHashTable::getDuplicatesStat(...)`
- `FileHashTable::copyToFileHash(...)`

### `CopyQueueTable`

Подтверждены операции:

- `OP_COPY = 'C'`
- `OP_RENAME = 'R'`
- `OP_SYNC = 'S'`

Это означает, что cloud copy/rename/sync в модуле имеет собственный очередной контур, а не только мгновенные вызовы API.

## Права и задачи модуля

Инсталлятор подтверждает модульные задачи:

- `clouds_denied`
- `clouds_browse`
- `clouds_upload`
- `clouds_full_access`

И операции:

- `clouds_browse`
- `clouds_upload`
- `clouds_config`

## Что важно помнить

- У `clouds` нет стандартных install-components: это не компонентный, а инфраструктурный и hook-based модуль.
- Если у файла есть `HANDLER_ID > 0`, не предполагай, что физический файл лежит локально в `/upload`.
- `OnMakeFileArray(...)` может реально скачивать файл из bucket-а во временный путь.
- При `READ_ONLY='Y'` bucket может читаться, но не использоваться как целевой для записи.
- Resize может жить в отложенном облачном сценарии через `b_clouds_file_resize`, поэтому локальный cache-file не всегда источник истины.
- Для диагностики “почему файл не туда ушёл” смотри три слоя: file rules bucket-а, `FindBucketForFile(...)`, и состояние в `FileSaveTable` / `FileUploadTable`.

---

## Source: `bitrixcloud.md`

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

---

## Source: `mobileapp.md`

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

---

## Source: `b24connector.md`

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

---

## Source: `translate.md`

# Локализация, языковые файлы и переводческий UI (модуль translate)

> Audit note: ниже сверено с текущим `www/bitrix/modules/translate` версии `25.0.0`. Подтверждены `\Bitrix\Translate\File`, `Filter`, `Settings`, `Permission`, UI-панель `\Bitrix\Translate\Ui\Panel`, CLI-команда `translate:index`, controller-слой `Index\Collector`, `Editor\File`, `Import\Csv`, `Export\Csv`, а также стандартные компоненты `bitrix:translate.list` и `bitrix:translate.edit`.

## Зачем модуль нужен в этом core

`translate` здесь нужен не только для “редактирования lang-файлов в админке”. Это отдельный рабочий контур для:

- индексации языковых файлов и фраз;
- поиска по переводам;
- импорта и экспорта переводов в CSV;
- UI-редактирования lang-файлов;
- контроля прав на просмотр, запись и редактирование исходников;
- работы с `.settings.php` внутри `lang/`-деревьев;
- построения публичной translate-панели.

Если задача звучит как:

- “почему перевод не находится в translate UI”
- “как переиндексировать lang-файлы”
- “как импортировать/выгрузить переводы CSV”
- “как править lang-файлы безопасно”

то первым маршрутом должен быть именно `translate`, а не только `Loc::getMessage()` и ручное редактирование PHP-файлов.

## Базовые классы

### `\Bitrix\Translate\File`

Это главный объект для lang-файла. Подтверждены фабрики:

- `instantiateByPath(string $path)`
- `instantiateByIndex(Index\FileIndex $fileIndex)`
- `instantiateByIoFile(Main\IO\File $fileIn)`

Подтверждены важные методы:

- `getLangId()`
- `setLangId(string $languageId)`
- `getSourceEncoding()`
- `setSourceEncoding(string $encoding)`
- `getOperatingEncoding()`
- `setOperatingEncoding(string $encoding)`
- `lint(...)`
- `load()`
- `loadTokens()`
- `save()`
- `removeEmptyParents()`
- `backup()`
- `getFileIndex()`
- `updatePhraseIndex()`
- `deletePhraseIndex()`
- `getPhraseIndexCollection()`
- `sortPhrases()`
- `getPhrases()`
- `getCodes()`
- `getEnclosure(string $phraseId)`
- `countExcess(self $ethalon)`
- `countDeficiency(self $ethalon)`

Пример:

```php
use Bitrix\Main\Loader;
use Bitrix\Translate\File;

Loader::includeModule('translate');

$file = File::instantiateByPath(
    $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/lang/ru/lib/application.php'
);

if ($file->load())
{
    $value = $file['MAIN_SOME_CODE'] ?? null;
    $file['MAIN_SOME_CODE'] = 'Новое значение';

    if ($file->lint())
    {
        $file->save();
        $file->updatePhraseIndex();
    }
}
```

### `\Bitrix\Translate\Settings`

Это работа с `.settings.php` в `lang/`.

Подтверждены:

- `Settings::FILE_NAME = '.settings.php'`
- `Settings::OPTION_LANGUAGES = 'languages'`
- `instantiateByPath(string $fullPath)`
- `getOption(string $langPath, string $optionType)`
- `getOptions(string $langPath = '')`
- `load()`
- `save()`

### `\Bitrix\Translate\Filter`

Это transport/storage-объект для процессов модуля. Подтверждены параметры:

- `langId`
- `pathId`
- `nextPathId`
- `nextLangPathId`
- `fileId`
- `nextFileId`
- `path`
- `tabId`
- `recursively`

Подтверждены методы:

- `__construct($param = null)`
- `store()`
- `restore(int $id)`
- `getTabId(bool $increment = true)`

Вывод: translate-процессы реально держат прогресс и фильтры в `$_SESSION`, а не в каком-то скрытом хранилище.

## Права

Подтверждён `\Bitrix\Translate\Permission` со значениями:

- `SOURCE = 'X'`
- `WRITE = 'W'`
- `READ = 'R'`
- `DENY = 'D'`

И методами:

- `isAllowPath(string $path)`
- `canEditSource($checkUser)`
- `isAdmin($checkUser)`
- `canView($checkUser)`
- `canEdit($checkUser)`

Если пользователь “видит translate, но не может сохранить”, первым делом смотри этот класс и модульные права `translate`.

## UI и стандартные компоненты

Подтверждены стандартные компоненты:

- `bitrix:translate.list`
- `bitrix:translate.edit`

Подтверждена UI-панель:

- `\Bitrix\Translate\Ui\Panel::onPanelCreate()`
- `\Bitrix\Translate\Ui\Panel::showLoadedFiles()`

В инсталляторе модуль реально вешает:

- `main:OnPanelCreate` -> `\Bitrix\Translate\Ui\Panel::onPanelCreate`

## Controller-слой и фоновые процессы

### Индексация

Подтверждён `\Bitrix\Translate\Controller\Index\Collector` с action-константами:

- `collectLangPath`
- `collectPath`
- `collectFile`
- `collectPhrase`
- `purge`
- `cancel`

И методом:

- `cancelAction()`

### Редактор файлов

Подтверждён `\Bitrix\Translate\Controller\Editor\File` с action-ами:

- `save`
- `saveSource`
- `cleanEthalon`
- `wipeEmpty`
- `cancel`

И важный нюанс:

- `saveSource` требует не только `WRITE`, но и `SOURCE` permission;
- для `save` и `saveSource` отдельно навешан `HttpMethod(POST)`.

### CSV import/export

Подтверждён `\Bitrix\Translate\Controller\Import\Csv`:

- `uploadAction()`
- `importAction()`
- `indexAction()`
- `cancelAction($tabId)`
- `purgeAction($tabId)`
- `finalizeAction()`

Подтверждены режимы update:

- `METHOD_ADD_UPDATE`
- `METHOD_UPDATE_ONLY`
- `METHOD_ADD_ONLY`

Подтверждён `\Bitrix\Translate\Controller\Export\Csv`:

- `exportAction($tabId, $path = '')`
- `clearAction($tabId)`
- `purgeAction($tabId)`
- `cancelAction($tabId)`
- `downloadAction(int $tabId, string $type)`

И важный нюанс:

- у `downloadAction(...)` в конфигурации снимается стандартный `Csrf` prefilter;
- многие операции в import/export опираются на `tabId` и сохранённый `Filter`.

## CLI

Подтверждена команда:

- `translate:index`

Из `\Bitrix\Translate\Cli\IndexCommand`.

Поддерживается опция:

- `--path` / `-p`

По умолчанию индексируется:

- `/bitrix/modules`

Имя команды подтверждено как `translate:index`, но конкретный CLI entrypoint зависит от того, как в проекте поднята консоль `main`. Поэтому безопасный шаблон вызова такой:

```bash
php <console-entrypoint> translate:index --path=/local/modules
```

Команда проходит по:

- `PathLangCollection`
- `PathIndexCollection`
- `FileIndexCollection`
- `PhraseIndexCollection`

## События и служебный контур

В инсталляторе подтверждены:

- агент `\Bitrix\Translate\Index\Internals\PhraseFts::checkTables();`
- `perfmon:OnGetTableSchema`
- `main:OnAfterLanguageAdd`
- `main:\Bitrix\Main\Localization\Language::OnAfterAdd`
- `main:\Bitrix\Main\Localization\Language::OnAfterDelete`
- `main:OnLanguageDelete`

## Что это меняет для скилла

Если задача про локализацию, сначала различай три уровня:

1. обычный `Loc::getMessage()` и lang-файлы;
2. модуль `translate` как UI/индекс/import-export слой;
3. проектные локализационные соглашения в `local/`.

Правильный маршрут обычно такой:

- проверка lang-файла через `\Bitrix\Translate\File`;
- если нужен поиск/массовая операция — translate index;
- если нужна выгрузка/загрузка — `Import\Csv` / `Export\Csv`;
- если задача права/панель/доступ — `Permission` и `Ui\Panel`.

## Gotchas

- `translate` не равен просто `Loc::getMessage()`: UI, CSV и индекс фраз живут отдельным модулем.
- Многие процессы держат прогресс в `$_SESSION` через `Filter`, поэтому проблемы “процесс не продолжился” нужно искать не только в JS, но и в session state.
- После программного изменения lang-файла не забывай про `updatePhraseIndex()`, если задача затрагивает поиск/translate UI.
- `saveSource` и обычное `save` — не одно и то же: у них разные permission-level.
- Если панель/редактор “есть у админа, но нет у редактора”, смотри `Permission` и модульные права `translate`, а не только компонент.

---
