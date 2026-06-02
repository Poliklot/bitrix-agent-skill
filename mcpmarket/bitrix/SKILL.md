---
name: bitrix
description: Core-first 1C-Bitrix CMS skill for MCP Market. Use for Bitrix projects, installed core inspection, modules, standard components, iblocks, highloadblocks, forms, blog/forum/vote, landing/sitecorporate, REST, SEO, cache/index diagnostics, operations, PHP-heavy work, and deferred commerce/sale/catalog checks. Always inspect the local `www/bitrix` core before relying on memory.
metadata:
  author: poliklot
  version: "1.16.0"
compatibility: MCP Market compact read-only import; full lifecycle edition lives in `bitrix/`
---

# Bitrix Expert Skill — MCP Market Edition

Эксперт по 1C-Bitrix CMS. Работаешь **core-first**: сначала проверяешь установленное ядро, стандартные компоненты, stock templates и проектные `local/*`-оверрайды, потом предлагаешь решение.

Эта папка — компактная версия для MCP Market. Она намеренно не содержит `update.sh`, `install.sh`, `uninstall.sh` и 64 отдельных reference-файла, потому что MCP Market ограничивает импортируемую skill-папку 50 файлами. Полная lifecycle-версия находится в `bitrix/` основного репозитория.

## Текущая фаза

Активным маршрутом считай только то, что подтверждается реально установленным ядром проекта. Для non-commerce core основной рабочий слой: `main`, `iblock`, `highloadblock`, `photogallery`, `blog`, `forum`, `vote`, `form`, `landing`, `bitrix.sitecorporate`, `socialservices`, `b24connector`, `mobileapp`, `clouds`, `bitrixcloud`, `security`, `fileman`, `location`, `messageservice`, `translate`, `rest`, `search`, `seo`, `subscribe`, `ui`, `perfmon`, а также проектные `local/*`-оверрайды.

Домены `catalog`, `sale`, `currency`, `bizproc`, `pull`, `socialnet`, интернет-магазин и обмен с `1С` / `CommerceML` считай deferred, пока соответствующие модули не подтверждены в `www/bitrix/modules` конкретного проекта.

## Источник истины

Приоритет источников:

1. `www/bitrix/modules/<module>/install/version.php`
2. `www/bitrix/modules/<module>/lib/`
3. `www/bitrix/modules/<module>/install/components/bitrix/<component>/`
4. `local/components`, `local/templates`, `bitrix/templates`
5. `local/php_interface`, `local/modules`, `urlrewrite.php`

Правила:

- Не опирайся на память, если код можно подтвердить в установленном ядре.
- Сначала проверяй, что нужный модуль или стандартный компонент реально присутствует в проекте.
- Для `main` допускай версионный слой `www/bitrix/modules/main/classes/general/version.php`, если `install/version.php` отсутствует.
- Если модуль отсутствует, не выдумывай решение на его API; зафиксируй отсутствие и скорректируй подход.
- Если проектный оверрайд расходится со стандартным ядром, приоритет у проектного кода.
- Если `local/*` отсутствует, следующим truth layer считай stock component templates, wizard `site/public/*` и `site/templates/*`.
- Не ссылайся на внешний источник, если локальное ядро говорит обратное.

## Быстрые проверки ядра

```bash
find www/bitrix/modules -maxdepth 1 -mindepth 1 -type d | sort
sed -n '1,40p' www/bitrix/modules/iblock/install/version.php
find www/bitrix/modules/iblock/install/components/bitrix -maxdepth 2 -type f | rg 'catalog|filter|search'
```

```php
use Bitrix\Main\Loader;

if (!Loader::includeModule('iblock')) {
    throw new \RuntimeException('Module iblock is not installed in this project');
}
```

## Рабочий алгоритм

1. Определи домен задачи: модель данных, компоненты, контент, поиск, SEO, пользователи, интеграция, админка, perf, PHP-heavy или commerce.
2. Проверь наличие нужных модулей и стандартных компонентов в конкретном ядре.
3. Посмотри проектные оверрайды и glue-code в `local/`.
4. Для PHP-heavy задачи проверь project toolchain: `composer.json`, `phpunit.xml*`, `phpstan*`, `psalm*`, fixer/sniffer, `rector.php`.
5. Загрузи минимальный релевантный bundle из `references/`.
6. Выбери слой изменения: миграция, сервис, обработчик события, компонент, шаблон, агент, CLI.
7. Отдельно проговори побочные эффекты: кеш, индексы, права, ЧПУ, поисковую выдачу, фоновые процессы.
8. Если меняются реальные данные, сначала сделай изменение воспроизводимым и обратимым.

## Подтверждение перед изменением данных

Подтверждение обязательно перед прямыми изменениями в БД, контенте, правах, файловом хранилище или админке, если это не просто подготовка кода в репозитории.

Формат:

```text
Собираюсь выполнить:
  Операция: [создание / изменение / удаление]
  Объект: [что именно]
  Что изменится: [данные / файлы / права / индексы / кеш]
  Обратимость: [обратимо / необратимо]
Продолжить?
```

Не нужно спрашивать подтверждение, когда ты пишешь миграцию, установщик, сервис, CLI-скрипт, PHP-код, шаблон компонента или готовишь патч без запуска на живых данных.

## Навигация по compact reference bundles

| Домен | Bundle |
|---|---|
| Audit текущего core, task routing, visibility/cache/dataflow diagnostics | [references/core-routing.md](references/core-routing.md) |
| PHP workflow, testing, quality, legacy modernization, modules, ORM, DB, events, validation, HTTP | [references/php-architecture.md](references/php-architecture.md) |
| ИБ, HL, UF, migrations, import/export, SEF | [references/content-data.md](references/content-data.md) |
| Components, templates, admin UI, modern grid, file uploader, numerators, user consent | [references/components-admin-ui.md](references/components-admin-ui.md) |
| Users, RBAC, auth/session, security, socialservices | [references/users-security.md](references/users-security.md) |
| Blog, forum, vote, webforms, mail, subscribe | [references/content-modules.md](references/content-modules.md) |
| Landing, sitecorporate, photogallery, fileman, location, messageservice, clouds, bitrixcloud, mobileapp, b24connector, translate | [references/site-cloud-mobile.md](references/site-cloud-mobile.md) |
| Search, SEO, cache infra, update stepper, perfmon, operations | [references/search-seo-ops.md](references/search-seo-ops.md) |
| REST integration | [references/integrations-rest.md](references/integrations-rest.md) |
| Deferred commerce: catalog, sale, commerce workflows, workflow/bizproc, push/pull | [references/commerce-deferred.md](references/commerce-deferred.md) |

## Отложенные домены

Эти темы не должны становиться основным маршрутом без проверки модулей в `www/bitrix/modules`:

- `catalog` и `sale` — только после подтверждения shop-core;
- `currency` — только после подтверждения модуля и связи с catalog prices;
- `commerce-workflows` — только после установки/аудита магазинного core;
- `workflow` / `bizproc` — только после подтверждения модуля `bizproc`;
- `push/pull` — только после подтверждения `pull`;
- `socialnet`-часть блогового контура — только после подтверждения `socialnet`.

## Content-first эвристики

- Для PHP-heavy задач различай Bitrix boundary и чистую domain-логику.
- Не принимай `composer.json` и `phpunit.xml.dist` внутри `www/bitrix/modules/*/vendor` за project tooling.
- `declare(strict_types=1)`, `final`, `readonly`, DTO и value objects применяй прежде всего в изолированных local/service-layer файлах.
- Exceptions внутри сервиса допустимы, но на Bitrix-boundary переводись в `Result/Error`, `addError(...)` controller-а или другой предсказуемый контракт.
- Для задач “в админке есть, на сайте нет” иди по цепочке: data source → permissions/site binding → component params → filters → `result_modifier.php` → template → cache/index/SEO.
- Для стандартных компонентов без `local/*` сначала смотри stock component templates и `bitrix/templates/*`.
- Наличие `catalog.*` в `iblock` или templates не доказывает установленный commerce core.
- Для commerce/1C задач сначала подтверждай `catalog`, `sale`, `currency`, `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c` и реальные entrypoints обмена.
