---
name: bitrix
description: Core-first 1C-Bitrix CMS skill for MCP Market. Use for Bitrix projects, installed core inspection, modules, standard components, iblocks, highloadblocks, catalog, sale, currency, shop-core module inventory, StoreAssist, standard shop components, internet shop workflows, shop marketing/analytics, sender, mail, messageservice, subscribe, advertising, abtest, conversion, report, statistic, shop automation/bizproc, bizprocdesigner, workflow, lists, pull, shop integrations/webservice, webservice.sale, webservice.statistic, sale/catalog REST, external app hooks, 1C/CommerceML exchange, basket, orders, payments, delivery, discounts, SEO, pagination, cache/index diagnostics, operations, and PHP-heavy work. Always inspect the local `www/bitrix` core before relying on memory.
metadata:
  author: poliklot
  version: "1.24.0"
compatibility: MCP Market compact read-only import; full lifecycle edition lives in `bitrix/`
---

# Bitrix Expert Skill — MCP Market Edition

Эксперт по 1C-Bitrix CMS. Работаешь **core-first**: сначала проверяешь установленное ядро, стандартные компоненты, stock templates и проектные `local/*`-оверрайды, потом предлагаешь решение.

Эта папка — компактная версия для MCP Market. Она намеренно не содержит `update.sh`, `install.sh`, `uninstall.sh` и 74 отдельных reference-файла, потому что MCP Market ограничивает импортируемую skill-папку 50 файлами. Полная lifecycle-версия находится в `bitrix/` основного репозитория.

## Текущая фаза

Активным маршрутом считай только то, что подтверждается реально установленным ядром проекта. Для non-commerce core рабочий слой: `main`, `iblock`, `highloadblock`, `photogallery`, `blog`, `forum`, `vote`, `form`, `landing`, `bitrix.sitecorporate`, `socialservices`, `b24connector`, `mobileapp`, `clouds`, `bitrixcloud`, `security`, `fileman`, `location`, `messageservice`, `translate`, `rest`, `search`, `seo`, `subscribe`, `ui`, `perfmon`, проектные `local/*`-оверрайды.

Если в локальном проекте подтверждены `catalog`, `sale` и `currency`, активируй shop route: товары, SKU/offers, цены, остатки, склады, корзина, checkout, заказы, оплаты, доставки, скидки, marketing/analytics, automation/bizproc, webservice/REST integration extras и 1С/CommerceML. Если модулей нет — не выдумывай commerce API.

## Источник истины

1. `www/bitrix/modules/<module>/install/version.php`
2. `www/bitrix/modules/<module>/lib/`
3. `www/bitrix/modules/<module>/install/components/bitrix/<component>/`
4. `local/components`, `local/templates`, `bitrix/templates`
5. `local/php_interface`, `local/modules`, `urlrewrite.php`

Для `main` допускай `www/bitrix/modules/main/classes/general/version.php`, если `install/version.php` отсутствует.

## Быстрые проверки ядра

```bash
find www/bitrix/modules -maxdepth 1 -mindepth 1 -type d | sort
for m in main iblock currency catalog sale; do
  test -f "www/bitrix/modules/$m/install/version.php" && sed -n '1,40p' "www/bitrix/modules/$m/install/version.php"
done
```

```php
use Bitrix\Main\Loader;

foreach (['iblock'] as $module) {
    if (!Loader::includeModule($module)) {
        throw new \RuntimeException("Module {$module} is not installed");
    }
}
```

## Рабочий алгоритм

1. Определи домен задачи: content, component, PHP-heavy, search/SEO/cache, ops, shop или 1С.
2. Проверь наличие нужных модулей и стандартных компонентов в конкретном ядре.
3. Посмотри project overrides и glue-code в `local/`.
4. Загрузи минимальный релевантный compact bundle из `references/`.
5. Выбери слой изменения: migration, service, event handler, component, template, agent, CLI.
6. Проговори side effects: cache, indexes, rights, SEF, background processes, sale/order/exchange effects.
7. Если меняются реальные данные, сначала сделай изменение воспроизводимым и обратимым.

## Подтверждение перед изменением данных

Подтверждение обязательно перед прямыми изменениями в БД, контенте, правах, файловом хранилище или админке, если это не просто подготовка кода в репозитории.

```text
Собираюсь выполнить:
  Операция: [создание / изменение / удаление]
  Объект: [что именно]
  Что изменится: [данные / файлы / права / индексы / кеш]
  Обратимость: [обратимо / необратимо]
Продолжить?
```

## Навигация по compact reference bundles

| Домен | Bundle |
|---|---|
| Audit текущего core, full shop-core inventory, non-commerce/shop task routing, visibility/cache/dataflow diagnostics | [references/core-routing.md](references/core-routing.md) |
| PHP workflow, testing, quality, legacy modernization, modules, ORM, DB, events, validation, HTTP | [references/php-architecture.md](references/php-architecture.md) |
| ИБ, HL, UF, migrations, import/export, SEF | [references/content-data.md](references/content-data.md) |
| Components, templates, pagination, admin UI, modern grid, file uploader, numerators, user consent | [references/components-admin-ui.md](references/components-admin-ui.md) |
| Users, RBAC, auth/session, security, socialservices | [references/users-security.md](references/users-security.md) |
| Blog, forum, vote, webforms, mail, subscribe | [references/content-modules.md](references/content-modules.md) |
| Landing, sitecorporate, photogallery, fileman, location, messageservice, clouds, bitrixcloud, mobileapp, b24connector, translate | [references/site-cloud-mobile.md](references/site-cloud-mobile.md) |
| Search, SEO, cache infra, update stepper, perfmon, operations | [references/search-seo-ops.md](references/search-seo-ops.md) |
| REST integration | [references/integrations-rest.md](references/integrations-rest.md) |
| Commerce/shop: catalog, sale, currency, standard shop components, StoreAssist, marketing/analytics, automation/bizproc, webservice/SOAP, sale/catalog REST, workflow/lists/pull, 1С/CommerceML | [references/commerce-shop.md](references/commerce-shop.md) |

## Content-first эвристики

- Не опирайся на память, если код можно подтвердить в установленном ядре.
- Не принимай `composer.json` и `phpunit.xml.dist` внутри `www/bitrix/modules/*/vendor` за project tooling.
- Для задач “в админке есть, на сайте нет” иди по цепочке: data source → permissions/site binding → component params → filters → pagination/sort → `result_modifier.php` → template → cache/index/SEO.
- Наличие `catalog.*` в `iblock` или templates не доказывает установленный commerce core; для public shop components открывай commerce bundle с `shop-standard-components.md`.
- Для shop-задач сначала подтверждай `catalog`, `sale`, `currency`; затем разделяй product, offer, price, stock, basket, order, marketing/analytics и exchange side effects.
- Для вопросов полного покрытия shop-core сначала смотри inventory bundle: standard shop components, marketing/analytics, automation и webservice/REST уже покрыты code-first, но не обещай runtime-smoke без Docker/runtime проверки.
- Для задач про рассылки, подписки, SMS, баннеры, A/B, conversion, reports или statistic открывай commerce bundle с `shop-marketing-analytics.md`; не смешивай `sender.subscribe`, `subscribe.*` и `catalog.product.subscribe`.
- Для задач про БП, роботов, задания, процессы в списках или realtime открывай commerce bundle с `shop-automation-bizproc.md`; не обещай sale-order robots без локального provider-а/CRM/custom module.
- Для задач про `webservice.sale`, `webservice.statistic`, SOAP/WSDL, REST sale/catalog events, placements или external app handlers открывай commerce bundle с `shop-integrations-webservice.md`; не смешивай это с 1С CommerceML.
- Для 1С задач проверяй `checkauth → init → file → import`, cookies/session, `sessid`, temp files, XML_ID/CML2_LINK и exchange logs.
- Если задача про StoreAssist или `storeassist_1c_*`, помни: это мастер/чеклист и onboarding, а не exchange engine.
- Для пагинации разводи legacy `PAGEN_N`/`NavStart()` и D7 `PageNavigation`: проверяй unique nav id, count/filter, stable sort, cache key и ajax payload.
- Не меняй order/basket/payment/shipment/catalog price/stock прямым SQL, если есть API и side effects.
- Не подключай production 1С, реальные платежи, доставки или кассы для smoke без явного подтверждения.
