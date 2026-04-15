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
