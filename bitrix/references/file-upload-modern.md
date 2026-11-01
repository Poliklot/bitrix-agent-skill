# Bitrix File Uploader — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с загрузкой файлов через `Bitrix\Main\FileUploader\FieldFileUploaderController`, `Bitrix\UI\FileUploader\UploaderController`, `Configuration`, `UploadedFilesRegistry` и `UploaderFileSigner`.

## Audit note

Проверено по текущему core:
- `www/bitrix/modules/main/lib/fileuploader/FieldFileUploaderController.php`
- `www/bitrix/modules/ui/lib/fileuploader/UploaderController.php`
- `www/bitrix/modules/ui/lib/fileuploader/Configuration.php`
- `www/bitrix/modules/main/lib/userfield/file/uploadedfilesregistry.php`
- `www/bitrix/modules/main/lib/userfield/file/uploaderfilesigner.php`
- `www/bitrix/modules/main/lib/userfield/file/uploadercontextgenerator.php`

В этой установке не найден стандартный компонент `bitrix:ui.file.input` внутри `modules/*/install/components`, поэтому не обещай его как гарантированную точку входа. Для фронта ориентируйся на реальный проектный код и на контекст, который собирает core вокруг userfield/file utilities.

## Что реально есть в core

### `FieldFileUploaderController`

Это готовый контроллер для UF-файлов. Он:
- наследует `Bitrix\UI\FileUploader\UploaderController`;
- валидирует `id`, `cid`, `entityId`, `fieldName`, `multiple`, `signedFileId`;
- берёт ограничения поля через `$USER_FIELD_MANAGER->GetUserFields(...)`;
- в `getConfiguration()` настраивает `Configuration`;
- в `onUploadComplete()` регистрирует файл во внутренних utility/registry механизмах.

Подтверждённые опции конструктора:

```php
[
    'id' => 0,
    'cid' => '',
    'entityId' => '',
    'fieldName' => '',
    'multiple' => false,
    'signedFileId' => '',
]
```

`cid` в текущем core проходит regex-проверку на 32 hex-символа.

### `UploaderController`

В `ui` это абстрактный базовый класс. Он требует реализовать:
- `isAvailable(): bool`
- `getConfiguration(): Configuration`
- `canUpload(): bool|CanUploadResult`
- `canView(): bool`
- `verifyFileOwner(FileOwnershipCollection $files): void`
- `canRemove(): bool`

Есть стандартные lifecycle hooks:
- `onUploadStart(...)`
- `onUploadComplete(...)`
- `onUploadError(...)`

### `UploadedFilesRegistry`

В текущем core это не сервис `confirm()`. Реально он умеет:
- `registerFile(int $fileId, string $controlId, string $cid, string $tempFileToken)`
- `getTokenByFileId(...)`
- `getCidByFileId(...)`
- `unregisterFile(...)`

То есть это session-backed registry временных связей `fileId <-> controlId/cid/token`, а не универсальный confirm-API.

### `UploaderFileSigner`

Сигнатура в текущем core:

```php
new UploaderFileSigner(string $entityId, string $fieldName)
```

Подтверждённые методы:
- `sign(int $fileId): string`
- `verify(string $signedString, int $fileId): bool`

Это важно: `verify()` требует и signed string, и реальный `fileId`.

## Конфигурация загрузчика

В `Bitrix\UI\FileUploader\Configuration` подтверждены методы:
- `setMaxFileSize(?int $bytes)`
- `setMinFileSize(int $bytes)`
- `setAcceptedFileTypes(array $extensions)`
- `setAcceptOnlyImages(bool $flag = true)`
- `acceptOnlyImages()`
- `setImageMinWidth(...)`
- `setImageMinHeight(...)`
- `setImageMaxWidth(...)`
- `setImageMaxHeight(...)`
- `setImageMaxFileSize(...)`
- `setImageMinFileSize(...)`
- `setTreatOversizeImageAsFile(bool)`
- `setIgnoreUnknownImageTypes(bool)`
- `toArray()`

В этом core нет подтверждения для методов вроде:
- `setAllowedFileExtensions(...)`
- `setMultiple(...)`
- `setMaxFileCount(...)`
- `setMaxTotalFileSize(...)`

Не используй их в reference как гарантированный API.

## Как выглядит безопасный базовый паттерн

```php
use Bitrix\Main\FileUploader\FieldFileUploaderController;

$controller = new FieldFileUploaderController([
    'entityId' => 'USER',
    'fieldName' => 'UF_PHOTO',
    'multiple' => false,
    'cid' => $cid,
    'id' => (int)$userId,
]);

if (!$controller->isAvailable())
{
    throw new \RuntimeException('Uploader is not available');
}

$config = $controller->getConfiguration()->toArray();
```

## View mode и edit mode

Внутренний контекст различается так:
- edit mode использует `cid`;
- view mode использует `signedFileId`.

Core-утилита `UploaderContextGenerator` подтверждает оба сценария:

```php
use Bitrix\Main\UserField\File\UploaderContextGenerator;
use Bitrix\Main\UI\FileInputUtility;

$generator = new UploaderContextGenerator(
    FileInputUtility::instance(),
    [
        'ID' => 0,
        'ENTITY_ID' => 'USER',
        'FIELD_NAME' => 'UF_PHOTO',
        'MULTIPLE' => 'N',
    ]
);

$editContext = $generator->getContextInEditMode($cid);
$viewContext = $generator->getContextForFileInViewMode($fileId);
```

## Кастомный контроллер

Если нужен свой upload controller, ориентируйся на реальный контракт `UploaderController`, а не на выдуманные методы вроде `getOwners()`.

```php
namespace Vendor\Module\FileUploader;

use Bitrix\UI\FileUploader\Configuration;
use Bitrix\UI\FileUploader\UploaderController;

// Абстрактный образец конфигурации, не готовый production-контроллер.
// Наследник обязан реализовать все проверки доступа и verifyFileOwner
// по фактической модели владения проекта. Без этого инстанцировать нельзя.
abstract class ItemUploaderController extends UploaderController
{
    public function getConfiguration(): Configuration
    {
        return (new Configuration())
            ->setMaxFileSize(10 * 1024 * 1024)
            ->setAcceptedFileTypes(['.jpg', '.png', '.pdf']);
    }
}
```

## Gotchas

- Не обещай `UploadedFilesRegistry::confirm()`: в текущем core такого метода нет.
- Не вызывай `new UploaderFileSigner()` без аргументов: ему нужны `entityId` и `fieldName`.
- Не подменяй `Configuration::setAcceptedFileTypes()` на `setAllowedFileExtensions()`: это не подтверждено текущим API.
- Не обещай стандартный `bitrix:ui.file.input`, пока не увидел его реально в установленном core или в проектном коде.
- Для `FieldFileUploaderController::canUpload()` мало одной авторизации: там ещё проверяется зарегистрированный `cid` через `FileInputUtility`.

## K69 — Uploader не должен присваивать себе все входящие файлы

Контракт UploaderController разделяет доступность, upload/view/remove и verifyFileOwner. Авторизация пользователя не доказывает право на каждый fileId. Удали разрешающий всё пример: конкретный контроллер должен подтвердить связь файла с объектом/контекстом задания на сервере и только затем markAsOwn. Пока модель владения не задана, оставляй контроллер абстрактным, а не возвращай true ради работоспособности демо.

**Проверка на стенде:** Чужой файл не просматривается/удаляется; свои файлы проходят только разрешённые операции.

[Официальный контракт](https://docs.1c-bitrix.ru/api/classes/Bitrix-UI-FileUploader-UploaderController.html). Сверка документации: 2026-11-01; установленное ядро и runtime этого сценария здесь не проверены.
