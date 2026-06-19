# Project intake для Bitrix-проекта

Открывай, когда задача относится к конкретному репозиторию: “у нас”, “в этом проекте”, “найди где”, “почему не работает”, “почини”, “сделай патч”. Цель — за 1–3 минуты понять структуру Bitrix-проекта и отвечать по фактам, а не по памяти.

Не запускай этот intake для чисто теоретического вопроса без доступа к проекту.

## Быстрый intake

Запускать из корня репозитория. Если команда падает из-за отсутствующей папки — это факт проекта, не ошибка.

```bash
find . -maxdepth 5 -type d -path '*/bitrix/modules/main' -print
find . -maxdepth 4 -type d \( -name local -o -name bitrix \) -print
```

```bash
find www/bitrix/modules -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sed 's#^www/bitrix/modules/##' | sort | head -n 80
```

```bash
find local/templates bitrix/templates www/bitrix/templates -maxdepth 3 \
  \( -name header.php -o -name footer.php -o -name '.section.php' \) -type f 2>/dev/null | sort
```

```bash
rg -n 'ShowHead|ShowTitle|ShowBodyScripts|ShowPanel|IncludeComponent\(' \
  local bitrix/templates www/bitrix/templates --glob '*.php' 2>/dev/null
```

## Что зафиксировать

| Факт | Как искать | Почему важно |
|---|---|---|
| Public root | `*/bitrix/modules/main` | Все Bitrix paths зависят от public root. |
| Project layer | `local/`, `local/modules`, `local/components`, `local/templates` | Постоянные правки должны идти сюда, не в core. |
| Active template | `header.php`, `footer.php`, `SITE_TEMPLATE_PATH`, calls on pages | Для meta/assets/panel/layout. |
| Head contract | `ShowHead`, `ShowTitle`, `ShowBodyScripts` | Решает бытовые meta/CSS/JS вопросы. |
| Components | `IncludeComponent(` and `local/templates/*/components` | Где править вывод и параметры. |
| Module inventory | `www/bitrix/modules/*/install/version.php` | Нельзя обещать API отсутствующего module. |
| 404/routing | `404.php`, `urlrewrite.php`, `SEF_MODE`, `SET_STATUS_404` | Для status/SEO/SEF diagnostics. |
| Cache/composite | `CACHE_TYPE`, `CACHE_GROUPS`, `StartResultCache`, `Composite`, `Frame` | Для “изменения не видны” и персонализации. |
| Tooling | `composer.json`, `phpunit.xml*`, `phpstan*`, `psalm*`, `rector.php` | Не тащить новый PHP-stack, если проектный уже есть. |
| Events/agents | `EventManager`, `addEventHandler`, `CAgent`, `Stepper` | Для кастомной логики и фоновых задач. |

## Module check

Для optional modules:

```bash
for m in iblock highloadblock form search seo catalog sale currency rest bizproc workflow pull socialnet; do
  if test -f "www/bitrix/modules/$m/install/version.php"; then
    echo "FOUND $m"
    sed -n '1,40p' "www/bitrix/modules/$m/install/version.php"
  else
    echo "MISSING $m"
  fi
done
```

Если public root не `www/`, заменить prefix на найденный root.

## Tooling check

```bash
find . -maxdepth 3 \( -name composer.json -o -name 'phpunit.xml*' -o -name 'phpstan*' -o -name 'psalm*' -o -name 'rector.php' -o -name '.php-cs-fixer*' \) -print
```

Не считать `www/bitrix/modules/*/vendor/composer.json` project tooling.

## Intake report format

После intake отвечай кратко:

```text
Нашёл по проекту:
- public root: [path]
- project layer: [local yes/no, local/modules yes/no, local/components yes/no]
- template/head: [header.php path, ShowHead yes/no, ShowTitle yes/no]
- modules: [relevant found/missing]
- target layer: [page/component/template/local module]

Дальше делаю: [next action].
```

Для простого вопроса не показывай весь отчёт, только релевантные факты:

```text
Проверил: в `local/templates/main/header.php` уже есть `ShowHead()` и `ShowTitle()`.
Значит meta руками вставлять не надо; меняем [page property/component SEO param].
```

## Intake для частых задач

### Meta/title/CSS/JS

Проверить:

```bash
rg -n 'ShowHead|ShowTitle|SetTitle|SetPageProperty|AddHeadString|Asset::getInstance|ShowBodyScripts' \
  local bitrix/templates www/bitrix/templates --glob '*.php'
```

Выводить только найденный `header.php`/page/component fact.

### Где править компонент

```bash
rg -n 'IncludeComponent\(' . --glob '*.php' --glob '!upload/**' --glob '!bitrix/cache/**' --glob '!www/bitrix/cache/**'
find local/templates bitrix/templates -path '*components/bitrix*' -type f 2>/dev/null | sort
```

Сначала project template, затем stock component contract.

### “В админке есть, на сайте нет”

Проверить:

1. Module and source entity.
2. Component params (`IBLOCK_ID`, `PROPERTY_CODE`, filters).
3. Rights/site binding/activity/date.
4. `result_modifier.php` / template.
5. Cache/index/composite.

### Shop/1C

Сначала:

```bash
for m in catalog sale currency; do test -f "www/bitrix/modules/$m/install/version.php" && echo "FOUND $m" || echo "MISSING $m"; done
```

Без `catalog`/`sale`/`currency` не вести задачу как полноценный shop-route.

## Когда остановиться

Intake не должен превращаться в аудит всего проекта. Остановиться, когда есть:

- найденный target file/layer;
- подтверждённый или отсутствующий module;
- понятная следующая проверка/patch;
- риски side effects.

Дальше переходить к узкому reference или патчу.
