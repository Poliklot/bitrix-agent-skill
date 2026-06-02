# Commerce + 1С / CommerceML integration

> Truth layer: shop-core `/Users/igormajorov/Downloads/Telegram Desktop/bitrix-shop-core`. Подтверждены модули `catalog` 25.550.0, `sale` 26.0.0, `currency` 26.0.0, компоненты `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`, admin entrypoints `/bitrix/admin/1c_import.php`, `/bitrix/admin/1c_exchange.php`, `/bitrix/admin/1c_admin.php`, `/bitrix/admin/sale_exchange_log.php`.

Используй этот файл для задач обмена с 1С, CommerceML, выгрузки каталога, импорта товаров/цен/остатков, экспорта/импорта заказов, диагностики `mode=checkauth/init/file/import`.

## 1. Проверка наличия exchange слоя

```bash
for p in \
  www/bitrix/modules/catalog/install/components/bitrix/catalog.import.1c/component.php \
  www/bitrix/modules/catalog/install/components/bitrix/catalog.export.1c/component.php \
  www/bitrix/modules/sale/install/components/bitrix/sale.export.1c/component.php \
  www/bitrix/admin/1c_import.php \
  www/bitrix/admin/1c_exchange.php \
  www/bitrix/admin/sale_exchange_log.php
  do test -f "$p" && echo "OK $p" || echo "MISS $p"; done
```

```bash
find www/bitrix/modules/sale/lib/exchange -maxdepth 3 -type f | sort
rg "BX_CML2_IMPORT|BX_CML2_EXPORT|mode.*checkauth|mode.*init|mode.*file|mode.*import|secure_1c_exchange" www/bitrix/modules/{catalog,sale}
```

## 2. Entry points

| Поток | Entry point / component | Назначение |
|---|---|---|
| Импорт каталога из 1С | `catalog.import.1c` / `/bitrix/admin/1c_import.php` | товары, разделы, свойства, картинки, SKU, цены, остатки по CommerceML |
| Экспорт каталога | `catalog.export.1c` | выгрузка catalog data наружу |
| Обмен заказами | `sale.export.1c` / `/bitrix/admin/1c_exchange.php` | экспорт заказов в 1С и импорт обратных документов/статусов |
| Админка обмена | `/bitrix/admin/1c_admin.php` | настройки/страницы 1С exchange |
| Логи заказов | `/bitrix/admin/sale_exchange_log.php`, `b_sale_exchange_log` | диагностика обмена sale |

`/bitrix/admin/1c_import.php` просто требует `catalog/admin/1c_import.php`; `/bitrix/admin/1c_exchange.php` требует `sale/admin/1c_exchange.php`. Всегда переходи в модульный файл, а не анализируй wrapper как контракт.

## 3. Протокол режимов

Catalog import (`catalog.import.1c/component.php`) подтверждает режимы:

- `mode=checkauth` — авторизация, выдача cookie/session и `sessid`;
- `mode=init` — инициализация, ответ `zip=yes/no`, file limits, подготовка `$_SESSION['BX_CML2_IMPORT']`;
- `mode=file` — приём файла/chunk, запись во временный каталог;
- `mode=import` — распаковка zip или пошаговая обработка XML;
- session state: `BX_CML2_IMPORT`, `TEMP_DIR`, `zip`, `last_zip_entry`, `NS`, maps.

Sale exchange (`sale.export.1c/component.php`) подтверждает режимы:

- `mode=checkauth` — авторизация и `sessid`;
- `mode=init` — `zip=yes/no`, версия, `cmlVersion`, `BX_CML2_EXPORT`;
- `mode=file` — старый и новый формат загрузки;
- `mode=import` — unzip и обработка XML обратных документов;
- session state: `BX_CML2_EXPORT`, `last_zip_entry`, `last_xml_entry`, order prefix;
- option: `sale.secure_1c_exchange` и `check_bitrix_sessid()`.

## 4. Security и access

Проверяй:

1. группа пользователя, под которым ходит 1С;
2. права на catalog/sale exchange;
3. `secure_1c_exchange` и передачу `sessid`;
4. cookies/session: 1С должна сохранять cookie между `checkauth`, `init`, `file`, `import`;
5. `BX_SESSION_ID_CHANGE`, если компонент ругается на смену session ID;
6. `SKIP_SOURCE_CHECK` / source check в catalog import;
7. HTTPS/basic auth/proxy, если exchange идёт через внешний контур.

Никогда не советуй отключить security навсегда. Для диагностики можно временно подтвердить изменение с пользователем, но фиксируй rollback.

## 5. Временные файлы и zip/chunks

Типовые места:

- `upload/1c_exchange/` для sale export/import files;
- temp dir через `CTempFile::GetDirectoryName(...)`;
- `$_SESSION['BX_CML2_IMPORT']['TEMP_DIR']` / `BX_CML2_EXPORT['TEMP_DIR']`;
- zip state: `zip`, `last_zip_entry`;
- XML continuation: `last_xml_entry`.

Для больших файлов проверяй:

- `upload_max_filesize`, `post_max_size`, `max_execution_time`, `max_input_time`, memory;
- права на `upload/`, temp, `bitrix/tmp`;
- повторный chunk и идемпотентность;
- cleanup старых временных файлов;
- zip support (`zip_open`).

## 6. Catalog import: товары, SKU, цены, остатки

Диагностический порядок:

1. Найди XML/CommerceML файл и убедись, что 1С реально отправила нужный узел.
2. Проверь mapping по `XML_ID`: раздел, товар, offer, цена, склад.
3. Для товара проверь `CIBlockElement`, `b_catalog_product`.
4. Для SKU проверь offers-ИБ через `CCatalogSKU::GetInfoByProductIBlock()` и связь `CML2_LINK`/`SKU_PROPERTY_ID`.
5. Для цены проверь `b_catalog_price`, `CATALOG_GROUP_ID`, `CURRENCY`, quantity range.
6. Для остатков проверь `b_catalog_product.QUANTITY` и `b_catalog_store_product.AMOUNT`.
7. Проверь post-import side effects: facet/search index, managed/tagged/component cache.

## 7. Sale exchange: заказы и обратные документы

В shop-core есть `sale/lib/exchange/*`, `sale/lib/exchange/onec/*`, autoload для `Bitrix\Sale\Exchange\OneC\*` и `Bitrix\Sale\Exchange\Entity\*` loaders.

Проверяй:

- `b_sale_order.DATE_UPDATE`, status, paid/deducted/canceled;
- критерии выгрузки и order prefix в `BX_CML2_EXPORT`;
- `b_sale_exchange_log` и `sale_exchange_log.php`;
- `b_sale_synchronizer_log`, если участвует synchronizer;
- business values / `b_sale_bizval_code_1c`;
- import collision classes: order/shipment/payment/profile;
- обратные документы: payment/shipment/status updates.

## 8. Типовые проблемы

### `failure\nSession ID change is active`

Проверь файл включения компонента и рекомендацию компонента: `BX_SESSION_ID_CHANGE` должен быть определён до prolog, если это требуется конкретным exchange route. Не меняй глобально без понимания security impact.

### `checkauth` проходит, `file` или `import` падает

1. 1С не сохраняет cookie/session.
2. Потерян `sessid` при `secure_1c_exchange=Y`.
3. Temp/upload dir недоступен на запись.
4. File size/time limits.
5. Source check/CSRF/proxy режет запрос.

### Товар загружен, но не виден на витрине

1. `ACTIVE`, даты, section/site binding, права.
2. Товар vs offer: цена/остаток могут быть на offer.
3. `b_catalog_product` отсутствует или неверный `TYPE`.
4. Нет доступной цены для группы пользователя.
5. Остаток/availability запрещает покупку.
6. Не обновлён facet/search index или component cache.

### Цена/остаток не обновились

1. Неверный external ID / XML_ID.
2. Обновлён parent product вместо offer.
3. Неверный price type / currency.
4. Складской остаток обновился, общий quantity не пересчитан.
5. Сработал кастомный event handler и откатил/перезаписал значения.

### Заказы не уходят в 1С

1. Неверный exchange user или права.
2. Заказ не попадает в критерии выгрузки.
3. `DATE_UPDATE`/status не меняются ожидаемо.
4. Ошибка в `b_sale_exchange_log`.
5. `secure_1c_exchange` / `sessid` / cookies.
6. Кастомизация `sale.export.1c` или local override.

## 9. Safe verification flow

Перед любым тестом с обменом:

1. Используй sandbox, не production 1С.
2. Сохрани исходные options и настройки компонента.
3. Подготовь маленький CommerceML fixture: один раздел, один товар, один offer, одна цена, один остаток, один заказ.
4. Включи диагностические логи только на время теста.
5. После теста проверь таблицы, файлы, кеши, индексы.
6. Зафиксируй rollback: удалить тестовый товар/заказ/файлы, вернуть options.

## 10. Что не делать

- Не подключать реальную production 1С без подтверждения.
- Не отключать `secure_1c_exchange` как постоянное решение.
- Не удалять `CML2_LINK` и XML_ID-связи.
- Не чистить все товары перед импортом без backup и подтверждения.
- Не считать XML успешным только потому, что `file` вернул success: проверяй `import` и таблицы.
