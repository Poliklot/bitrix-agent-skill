# Bitrix Модули, Loader, Application — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с созданием модуля, Loader, PSR-4 автозагрузкой, Application, ServiceLocator, Config\Option или локализацией.

## Содержание
- Application и ServiceLocator
- Config\Option — настройки модуля
- Локализация (Loc)
- Структура модуля: include.php, install/index.php, version.php, .settings.php
- Инсталлятор: CModule, InstallDB/UnInstallDB
- Loader: requireModule, registerNamespace, local/ vs bitrix/

---

## Application и сервис-локатор

`Application::getInstance()` — синглтон, точка входа во всё приложение. Через него получаешь соединение с БД, кеш, контекст запроса. `ServiceLocator` — DI-контейнер Bitrix: регистрируешь сервисы один раз (обычно в `include.php` модуля), получаешь их везде по имени. Это позволяет избежать `new MyService()` разбросанных по коду и упрощает замену реализаций.

```php
$app = \Bitrix\Main\Application::getInstance();

// ServiceLocator — регистрируй в include.php модуля
$serviceLocator = \Bitrix\Main\DI\ServiceLocator::getInstance();
$serviceLocator->addInstanceLazy('myVendor.orderService', [
    'constructor' => fn() => new \MyVendor\MyModule\OrderService(),
]);
// Получай где угодно
$service = $serviceLocator->get('myVendor.orderService');

// Запрос и ответ — безопасный способ получить параметры
$request = $app->getContext()->getRequest();
$id      = (int)$request->getQuery('id');    // GET-параметр
$title   = (string)$request->getPost('title'); // POST-параметр
// Никогда не используй $_GET/$_POST напрямую в D7-коде
```

---

## Config\Option — настройки модуля

Хранятся в таблице `b_option`. Используй для конфигурационных значений модуля — API-ключи, лимиты, флаги. Не используй для пользовательских данных или данных, которые меняются часто (для этого есть ORM-таблицы).

```php
use Bitrix\Main\Config\Option;

$value = Option::get('my.module', 'API_KEY', '');          // третий аргумент — дефолт
Option::set('my.module', 'API_KEY', $newKey);
Option::delete('my.module', ['name' => 'API_KEY']);
```

---

## Локализация

`Loc::getMessage()` ищет ключ в lang-файле рядом с текущим PHP-файлом. `loadMessages(__FILE__)` говорит системе: "загрузи lang-файл для этого файла". Без вызова `loadMessages` ключи будут пустыми.

```php
use Bitrix\Main\Localization\Loc;

Loc::loadMessages(__FILE__); // вызывай в начале каждого файла где нужны переводы

echo Loc::getMessage('MY_MODULE_GREETING', ['#NAME#' => 'Иван']);
// lang/ru/my_file.php: $MESS['MY_MODULE_GREETING'] = 'Привет, #NAME#!';
// lang/en/my_file.php: $MESS['MY_MODULE_GREETING'] = 'Hello, #NAME#!';
```

---


---
## Модули

### Архитектурный смысл

Модуль в Bitrix — это изолированная библиотека функциональности с собственной схемой БД, правами, событиями и PSR-4 namespace. Каждый модуль регистрируется в системе через инсталлятор. `Loader::includeModule()` — единственная точка входа; без этого вызова классы модуля **не появятся** в автозагрузчике, даже если файлы физически присутствуют.

**Поиск модуля** — сначала `local/modules/`, потом `bitrix/modules/`. Это позволяет переопределять стандартные модули в `local/`.

**PSR-4 автозагрузка** регистрируется автоматически:
- Bitrix-модуль `iblock` → namespace `Bitrix\Iblock` → `/bitrix/modules/iblock/lib`
- Партнёрский модуль `vendor.mymodule` → namespace `Vendor\Mymodule` → `/bitrix/modules/vendor.mymodule/lib`
- Файл `lib/service/ordermanager.php` → класс `Vendor\Mymodule\Service\OrderManager`

### Структура модуля

```
local/modules/vendor.mymodule/
├── include.php              ← точка входа, подключается Loader-ом
├── .settings.php            ← конфигурация ServiceLocator, роутов, REST
├── lib/                     ← PSR-4 корень
│   ├── service/
│   │   └── ordermanager.php ← Vendor\Mymodule\Service\OrderManager
│   └── model/
│       └── ordertable.php   ← Vendor\Mymodule\Model\OrderTable
└── install/
    ├── index.php            ← класс-инсталлятор, extends CModule
    ├── version.php          ← VERSION, VERSION_DATE
    └── db/
        ├── mysql/
        │   ├── install.sql
        │   └── uninstall.sql
        └── pgsql/
```

### include.php

```php
<?php
// include.php — вызывается при Loader::includeModule()
// Обычно пустой или подключает legacy-файлы
// PSR-4 регистрируется автоматически, include.php не обязан ничего делать

use Bitrix\Main\Localization\Loc;
Loc::loadMessages(__FILE__);
```

### install/index.php — инсталлятор

Класс ОБЯЗАТЕЛЬНО должен называться по MODULE_ID (без точки, только первая буква?). Нет — имя класса = MODULE_ID с заменой `.` на `_` или первая часть. Фактически в Bitrix имя класса инсталлятора = MODULE_ID.

```php
<?php
use Bitrix\Main\Localization\Loc;
use Bitrix\Main\ModuleManager;
use Bitrix\Main\EventManager;
use Bitrix\Main\Application;

Loc::loadMessages(__FILE__);

class vendor_mymodule extends CModule
{
    public $MODULE_ID = 'vendor.mymodule';
    public $MODULE_VERSION;
    public $MODULE_VERSION_DATE;
    public $MODULE_NAME;
    public $MODULE_DESCRIPTION;

    public function __construct()
    {
        $version = [];
        include __DIR__ . '/version.php';
        $this->MODULE_VERSION      = $version['VERSION'];
        $this->MODULE_VERSION_DATE = $version['VERSION_DATE'];
        $this->MODULE_NAME         = Loc::getMessage('VENDOR_MYMODULE_NAME');
        $this->MODULE_DESCRIPTION  = Loc::getMessage('VENDOR_MYMODULE_DESCRIPTION');
    }

    public function InstallDB(): bool
    {
        $connection = Application::getConnection();
        $connection->queryExecute(
            file_get_contents(__DIR__ . '/db/' . $connection->getType() . '/install.sql')
        );

        ModuleManager::registerModule($this->MODULE_ID);

        // Регистрация обработчиков событий (хранится в БД)
        $em = EventManager::getInstance();
        $em->registerEventHandler('main', 'OnBeforeUserAdd', $this->MODULE_ID,
            \Vendor\Mymodule\EventHandler::class, 'onBeforeUserAdd'
        );

        return true;
    }

    public function UnInstallDB(array $params = []): bool
    {
        $em = EventManager::getInstance();
        $em->unRegisterEventHandler('main', 'OnBeforeUserAdd', $this->MODULE_ID,
            \Vendor\Mymodule\EventHandler::class, 'onBeforeUserAdd'
        );

        ModuleManager::unRegisterModule($this->MODULE_ID);
        return true;
    }

    public function InstallFiles(): bool { return true; }
    public function UnInstallFiles(): bool { return true; }

    public function DoInstall(): void
    {
        $this->InstallDB();
        $this->InstallFiles();
    }

    public function DoUninstall(): void
    {
        $this->UnInstallDB();
        $this->UnInstallFiles();
    }
}
```

### .settings.php — конфигурация модуля

```php
<?php
// .settings.php читается ServiceLocator при загрузке модуля
return [
    // Конфигурация Engine\Controller (D7 MVC)
    'controllers' => [
        'value' => [
            'defaultNamespace' => '\Vendor\Mymodule\Controller',
            'namespaces' => [
                '\Vendor\Mymodule\Controller' => 'api',  // /vendor.mymodule/api/...
            ],
            'restIntegration' => [
                'enabled' => true,  // методы контроллеров доступны через REST
            ],
        ],
        'readonly' => true,
    ],
];
```

### Loader — тонкости

```php
use Bitrix\Main\Loader;

// Возвращает bool, кешируется — второй вызов бесплатный
if (!Loader::includeModule('vendor.mymodule')) {
    // модуль не установлен или не найден
    return;
}

// requireModule() — то же самое, но бросает LoaderException при неудаче
Loader::requireModule('vendor.mymodule');

// Ручная регистрация namespace (редко нужно, обычно автоматически)
Loader::registerNamespace('Vendor\\Extra', '/absolute/path/to/lib');

// Регистрация классов вручную (legacy-классы без PSR-4)
Loader::registerAutoLoadClasses('vendor.mymodule', [
    '\COldClass' => 'classes/oldclass.php',
]);
```

**Gotcha:** `local/modules/` имеет приоритет над `bitrix/modules/`. Если в `local/` есть модуль с тем же ID, он загрузится вместо стандартного — это механизм кастомизации.

---

