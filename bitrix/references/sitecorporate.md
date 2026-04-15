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
