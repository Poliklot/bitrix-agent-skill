# Version impact layer

Открывай, когда задача зависит от версии модуля: пользователь показывает другой core, `install/version.php` отличается от reference, модуль отсутствует/обновлён, после обновления сломался компонент, REST method, checkout, 1С exchange или admin-grid.

Цель файла — не угадывать совместимость по всем релизам Bitrix, а дать агенту порядок проверки: **версия → локальные файлы → contract diff → осторожный ответ**.

## Базовое правило

Версия в reference означает: “этот контракт проверен на таком core”. Она не означает, что все соседние релизы ведут себя одинаково.

Правильная формулировка:

```text
Контракт в скилле проверен на `sale` 26.0.0. В вашем проекте `sale` [версия]. Поэтому сначала сверяю локальные файлы: [paths]. Если они совпадают по контракту, можно применять маршрут; если нет — фиксирую отличие.
```

Не говорить:

```text
У вас версия другая, но должно работать так же.
```

## Как читать версию

```bash
# стандартный путь
sed -n '1,60p' www/bitrix/modules/<module>/install/version.php

# fallback для main в проверенном shop-core
sed -n '1,40p' www/bitrix/modules/main/classes/general/version.php
```

Пакетная проверка:

```bash
for m in main iblock highloadblock catalog sale currency rest webservice sender mail messageservice bizproc lists pull; do
  if test -f "www/bitrix/modules/$m/install/version.php"; then
    echo "--- $m install/version.php ---"
    sed -n '1,60p' "www/bitrix/modules/$m/install/version.php"
  elif test -f "www/bitrix/modules/$m/classes/general/version.php"; then
    echo "--- $m classes/general/version.php ---"
    sed -n '1,40p' "www/bitrix/modules/$m/classes/general/version.php"
  else
    echo "--- $m missing ---"
  fi
done
```

## Проверенный baseline shop-core

| Модуль | Проверенная версия | Что покрыто code-first |
|---|---:|---|
| `main` | `26.150.0` | Loader, события, cache/session/auth, pagination, agents/stepper, admin/grid слой |
| `iblock` | по локальному shop-core | элементы/разделы, свойства, компоненты, фильтры, visibility chain |
| `catalog` | `25.550.0` | product/SKU/offers, prices, stores, store documents, measure/VAT, import/export, catalog REST |
| `sale` | `26.0.0` | basket, order, payment, shipment, delivery, discounts, cashbox, order export, sale REST |
| `currency` | `26.0.0` | валюты, курсы, форматирование, связь с prices/sale sums |
| `rest` | `26.0.0` | webhooks/apps/scopes/events/placements, sale/catalog REST routes |
| `webservice` | `26.0.0` | SOAP/WSDL infrastructure, `webservice.sale`, `webservice.statistic`, `stssync` |
| `sender` | `26.0.0` | contacts, segments, letters, posting queue, opens/clicks/unsub, UTM |
| `bizproc` | `26.200.0` | templates/states/tasks, robots/triggers, scripts, debugger, REST activities |
| `pull` | `25.300.0` | channels/stack/watches/push queue/pull server diagnostics |

Если клиентская версия отличается, baseline остаётся ориентиром, но source of truth — локальный core.

## Что считать version-sensitive

| Слой | Почему чувствителен | Что сверять локально |
|---|---|---|
| Standard component params | параметры и default могут меняться | `.parameters.php`, `component.php`, `class.php`, шаблоны |
| D7 ORM tables | поля, validators, relations, runtime fields | `lib/*table.php`, `getMap()`, migrations/install db |
| REST methods/controllers | routes, scopes, events, placements | `lib/controller/*`, `rest.php`, event bind classes |
| Sale/catalog write paths | side effects, events, recalculation | service classes, `Order::save`, basket refresh, price/stock providers |
| 1С/CommerceML | step names, temp files, zip/chunk, options | `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`, exchange logs |
| Admin UI/grid | filters, actions, nav, ajax endpoints | `admin/*.php`, grid/list classes, UI extensions |
| Agents/stepper | intervals, state storage, cleanup behavior | `CAgent::AddAgent`, stepper classes, options |
| Cache/composite | cache keys, tagged cache, frame behavior | `StartResultCache`, tagged cache calls, composite frames |

## Version mismatch workflow

1. Зафиксировать local module version.
2. Найти reference baseline version.
3. Открыть локальные contract files для конкретной задачи, а не весь module.
4. Сравнить только нужный контракт: метод, component param, event, table map, REST route, admin action.
5. Если контракт совпадает — использовать reference и сказать, что локальная версия сверена.
6. Если контракт отличается — описать отличие и строить решение по локальному core.
7. Если локальный core недоступен — честно сказать, что совместимость не подтверждена.

## Быстрые локальные проверки по типам задач

### Компонент

```bash
find www/bitrix/modules -path '*/install/components/bitrix/<component>' -maxdepth 8 -type f | sort
rg -n 'arParams|PARAMETERS|CACHE|SEF|PAGEN|AJAX|ACTION' www/bitrix/modules/*/install/components/bitrix/<component> 2>/dev/null
```

### Sale/catalog write path

```bash
rg -n 'class .*Order|function save|Basket|Shipment|Payment|Discount|Provider|Price|Store' \
  www/bitrix/modules/sale/lib www/bitrix/modules/catalog/lib 2>/dev/null
```

### REST method/event

```bash
rg -n 'Controller|EventBind|OnRestServiceBuildDescription|SCOPE|PLACEMENT|METHOD' \
  www/bitrix/modules/rest www/bitrix/modules/sale/lib www/bitrix/modules/catalog/lib 2>/dev/null
```

### 1С exchange

```bash
rg -n 'checkauth|mode=init|mode=file|mode=import|CommerceML|CML2|BX_CML2|zip|TEMP' \
  www/bitrix/modules/catalog www/bitrix/modules/sale 2>/dev/null
```

## Как отвечать пользователю

### Если версия совпадает

```text
Проверил: в проекте `catalog` 25.550.0, это совпадает с baseline скилла. Иду по подтверждённому маршруту catalog/SKU/price/stock.
```

### Если версия отличается, но контракт сверен

```text
Версия отличается: reference проверен на `sale` 26.0.0, в проекте `sale` 26.x.x. Я сверил локальный `Order`/basket path и нужный контракт совпадает, поэтому решение применимо.
```

### Если версия отличается и контракт не сверен

```text
По памяти это обещать нельзя: версия модуля отличается, а локальные файлы не проверены. Нужен доступ к `www/bitrix/modules/[module]`, особенно к [paths].
```

### Если модуль отсутствует

```text
Модуль `[module]` не найден в `www/bitrix/modules`, поэтому штатный route этого API в проекте недоступен. Нужно искать fallback/project override или менять постановку задачи.
```

## Связанные references

- Project intake — [project-intake.md](project-intake.md)
- Core grep cookbook — [core-grep-cookbook.md](core-grep-cookbook.md)
- Reference map — [reference-map.md](reference-map.md)
- Core audit matrix — [core-audit-matrix.md](core-audit-matrix.md)
- Shop inventory — [shop-core-module-inventory.md](shop-core-module-inventory.md)
- Runtime smoke — [runtime-smoke-verification.md](runtime-smoke-verification.md)
