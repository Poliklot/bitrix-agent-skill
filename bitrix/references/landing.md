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
