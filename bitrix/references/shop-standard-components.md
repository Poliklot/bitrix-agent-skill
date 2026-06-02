# Shop standard components — витрина, корзина, checkout, личный кабинет

> Reference для Bitrix-скилла. Загружай, когда задача связана со стандартными компонентами интернет-магазина: `bitrix:catalog`, `catalog.section`, `catalog.element`, `catalog.smart.filter`, compare, basket, checkout/order, personal order pages, admin productcard/store components, viewed/recommended/gifts или когда нужно понять, где реально лежит компонент.

## Audit note

Проверено по shop-core:
- `www/bitrix/modules/iblock/install/components/bitrix/catalog*`
- `www/bitrix/modules/catalog/install/components/bitrix/catalog*`
- `www/bitrix/modules/sale/install/components/bitrix/sale*`
- `www/bitrix/modules/bitrix.eshop/install/components/bitrix/*`
- `www/bitrix/modules/bitrix.eshop/install/wizards/bitrix/eshop/site/*`
- `catalog.section` / `catalog.element` class + ajax + stock templates
- `catalog.smart.filter` component/class/templates
- `sale.basket.basket`, `sale.order.ajax`, `sale.order.checkout`, `sale.personal.order*`
- `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c` component parameters

Ниже только layer map и подтверждённые контракты из этого core. Для deep API товаров/цен/остатков читай `catalog.md`; для basket/order/payment/delivery — `sale.md`; для 1С — `commerce-1c-integration.md`; для pagination/lazy load — `pagination.md`.

## Главный вывод

Витринные `catalog.*` компоненты в этом core находятся в модуле `iblock`.

Это критично:
- наличие `www/bitrix/modules/iblock/install/components/bitrix/catalog.section` **не доказывает** установленный модуль `catalog`;
- полноценная торговая логика всё равно требует `catalog`, `sale`, `currency`;
- для чужого проекта сначала проверяй `www/bitrix/modules/catalog`, `www/bitrix/modules/sale`, `www/bitrix/modules/currency`.

## Component inventory

### `iblock` public catalog components

Подтверждены 18 shop-facing components:

| Component | Files | Templates | Роль |
|---|---|---:|---|
| `catalog` | `.parameters.php`, `component.php` | 3 | комплексный catalog router |
| `catalog.section` | `.parameters.php`, `class.php`, `ajax.php` | 6 | список товаров раздела |
| `catalog.element` | `.parameters.php`, `class.php`, `ajax.php` | 4 | детальная карточка товара |
| `catalog.smart.filter` | `.parameters.php`, `component.php`, `class.php` | 2 | умный фильтр/facet |
| `catalog.compare.list` | `.parameters.php`, `component.php` | 2 | список сравнения |
| `catalog.compare.result` | `.parameters.php`, `component.php` | 2 | таблица сравнения |
| `catalog.filter` | `.parameters.php`, `component.php` | 3 | legacy filter |
| `catalog.search` | `.parameters.php`, `component.php` | 2 | поиск по каталогу |
| `catalog.section.list` | `.parameters.php`, `component.php` | 5 | список разделов |
| `catalog.sections.top` | `.parameters.php`, `component.php` | 1 | top-разделы |
| `catalog.top` | `.parameters.php`, `class.php` | 3 | top products |
| `catalog.item` | `class.php`, `ajax.php` | 3 | item renderer/helper |
| `catalog.main` | `.parameters.php`, `component.php` | 1 | catalog main helper |
| `catalog.brandblock` | `.parameters.php`, `component.php` | 2 | brand block |
| `catalog.comments` | `.parameters.php`, `component.php` | 1 | comments bridge |
| `catalog.link.list` | `.parameters.php`, `component.php` | 1 | linked elements |
| `catalog.socnets.buttons` | `.parameters.php`, `component.php` | 1 | social buttons |
| `catalog.tabs` | `component.php` | 1 | tabs helper |

### `catalog` module components

`catalog` module components в основном отвечают за admin/productcard/store/report/1С/service UI:

- 1С/import/export: `catalog.import.1c`, `catalog.export.1c`, `catalog.import.hl`;
- product grid/card: `catalog.product.grid`, `catalog.productcard.*`, `catalog.grid.product.field`, `catalog.product.search`;
- stores/documents: `catalog.store*`, `catalog.store.document.*`, `catalog.store.entity.*`;
- reports: `catalog.report.store_*`;
- public-ish recommendations/viewed: `catalog.bigdata.products`, `catalog.products.viewed`, `catalog.viewed.products`, `catalog.recommended.products`;
- subscription: `catalog.product.subscribe*`;
- config/admin helpers: `catalog.config.*`, `catalog.seo.detail`, `catalog.set.constructor`.

Exhaustive component directory list in this core:

`catalog.agent.contract.controller`, `catalog.agent.contract.detail`, `catalog.agent.contract.list`, `catalog.bigdata.products`, `catalog.catalog.controller`, `catalog.compilation`, `catalog.config.permissions`, `catalog.config.settings`, `catalog.contractor.list`, `catalog.discsave.info`, `catalog.export.1c`, `catalog.feedback`, `catalog.grid.product.field`, `catalog.image.input`, `catalog.import.1c`, `catalog.import.hl`, `catalog.notfounderror`, `catalog.product.grid`, `catalog.product.search`, `catalog.product.subscribe`, `catalog.product.subscribe.list`, `catalog.productcard.controller`, `catalog.productcard.details`, `catalog.productcard.iblocksectionfield`, `catalog.productcard.reserved.deal.list`, `catalog.productcard.service.grid`, `catalog.productcard.store.amount`, `catalog.productcard.store.amount.details`, `catalog.productcard.store.amount.details.slider`, `catalog.productcard.variation.details`, `catalog.productcard.variation.grid`, `catalog.products.viewed`, `catalog.property.creation.form`, `catalog.recommended.products`, `catalog.report.store_profit.grid`, `catalog.report.store_profit.products.grid`, `catalog.report.store_sale.chart`, `catalog.report.store_sale.chart.stores.grid`, `catalog.report.store_sale.grid`, `catalog.report.store_sale.products.grid`, `catalog.report.store_stock.grid`, `catalog.report.store_stock.products.grid`, `catalog.report.store_stock.salechart`, `catalog.report.store_stock.salechart.stores.grid`, `catalog.seo.detail`, `catalog.set.constructor`, `catalog.show.products.mail`, `catalog.store`, `catalog.store.admin_list`, `catalog.store.amount`, `catalog.store.detail`, `catalog.store.document.control_panel`, `catalog.store.document.controller`, `catalog.store.document.detail`, `catalog.store.document.list`, `catalog.store.document.product.list`, `catalog.store.enablewizard`, `catalog.store.entity.controller`, `catalog.store.entity.details`, `catalog.store.field.config.list`, `catalog.store.list`, `catalog.viewed.products`.

### `sale` module components

Подтверждены ключевые families:

- basket: `sale.basket.basket`, `sale.basket.basket.line`, `sale.basket.basket.small`, `sale.basket.order.ajax`;
- checkout/order: `sale.order.ajax`, `sale.order.checkout`, `sale.order.payment*`, `sale.order.full`;
- personal cabinet: `sale.personal.order*`, `sale.personal.profile*`, `sale.personal.account`, `sale.personal.section`, `sale.personal.subscribe*`;
- delivery/location: `sale.ajax.delivery.calculator`, `sale.delivery.request*`, `sale.location.*`, `sale.store.choose`;
- gifts/recommendations: `sale.gift.*`, `sale.products.gift*`, `sale.recommended.products`, `sale.bestsellers`;
- 1С: `sale.export.1c`;
- mail/bigdata: `sale.bigdata.followup.mail`, `sale.bigdata.personal.mail`, `sale.discount.coupon.mail`;
- mobile admin/order: `sale.mobile.order.*`, `sale.mobile.orders.*`, `sale.mobile.product.list`.

Exhaustive component directory list in this core:

`sale.account.pay`, `sale.admin.page.stub`, `sale.affiliate.account`, `sale.affiliate.instructions`, `sale.affiliate.plans`, `sale.affiliate.register`, `sale.affiliate.report`, `sale.ajax.delivery.calculator`, `sale.basket.basket`, `sale.basket.basket.line`, `sale.basket.basket.small`, `sale.basket.basket.small.mail`, `sale.basket.order.ajax`, `sale.bestsellers`, `sale.bigdata.followup.mail`, `sale.bigdata.personal.mail`, `sale.bsm.site.master`, `sale.bsm.site.master.button`, `sale.business.value.mail`, `sale.crm.site.master`, `sale.delivery.request`, `sale.delivery.request.processed`, `sale.delivery.ruspost.reliability`, `sale.discount.coupon.mail`, `sale.domain.verification.form`, `sale.ebay.categories`, `sale.export.1c`, `sale.facebook.conversion`, `sale.gift.basket`, `sale.gift.main.products`, `sale.gift.product`, `sale.gift.section`, `sale.location.import`, `sale.location.map`, `sale.location.reindex`, `sale.location.selector.search`, `sale.location.selector.steps`, `sale.location.selector.system`, `sale.mobile.order.barcodes`, `sale.mobile.order.deduction`, `sale.mobile.order.detail`, `sale.mobile.order.history`, `sale.mobile.order.stores`, `sale.mobile.order.transact`, `sale.mobile.orders.list`, `sale.mobile.orders.push`, `sale.mobile.product.list`, `sale.notice.product`, `sale.order.ajax`, `sale.order.checkout`, `sale.order.full`, `sale.order.payment`, `sale.order.payment.change`, `sale.order.payment.receive`, `sale.paysystem.registration.robokassa`, `sale.paysystem.settings.robokassa`, `sale.personal.account`, `sale.personal.cc`, `sale.personal.cc.detail`, `sale.personal.cc.list`, `sale.personal.order`, `sale.personal.order.cancel`, `sale.personal.order.detail`, `sale.personal.order.detail.mail`, `sale.personal.order.list`, `sale.personal.profile`, `sale.personal.profile.detail`, `sale.personal.profile.list`, `sale.personal.section`, `sale.personal.subscribe`, `sale.personal.subscribe.cancel`, `sale.personal.subscribe.list`, `sale.prediction.product.detail`, `sale.products.gift`, `sale.products.gift.basket`, `sale.products.gift.section`, `sale.recommended.products`, `sale.store.choose`.

### `bitrix.eshop` solution layer

`bitrix.eshop` 25.0.0 in this core is a solution/wizard layer, not a separate commerce engine.

Confirmed own components:
- `eshop.banner`
- `eshop.facebook.plugin`
- `eshop.socnet.links`

Confirmed wizard/templates reference these components:

`advertising.banner`, `breadcrumb`, `catalog`, `catalog.section`, `catalog.section.list`, `catalog.store`, `catalog.viewed.products`, `eshop.banner`, `eshop.facebook.plugin`, `eshop.socnet.links`, `idea.popup`, `main.feedback`, `main.include`, `main.map`, `menu`, `menu.sections`, `news`, `news.list`, `sale.basket.basket`, `sale.basket.basket.line`, `sale.order.ajax`, `sale.order.payment`, `sale.order.payment.receive`, `sale.personal.order`, `sale.personal.section`, `search.page`, `search.title`, `sender.subscribe`, `socserv.auth.split`, `system.field.edit`.

Gotchas:
- `bitrix.eshop` creates/ships site skeleton, templates, wizard services and demo/public files; runtime commerce behavior still goes through `iblock`, `catalog`, `sale`, `currency`, `sender`, `advertising`, `search` and template code.
- If a project was bootstrapped from eShop wizard, inspect `bitrix/templates/*`, `local/templates/*`, copied public pages and component templates before changing standard component code.
- `eshop_templates_rename.php` is an admin helper for templates; do not treat it as shop runtime.

## Комплексный `bitrix:catalog`

`iblock/install/components/bitrix/catalog` — complex component/router.

Подтверждённые группы параметров:
- `SECTIONS_SETTINGS`
- `LIST_SETTINGS`
- `DETAIL_SETTINGS`
- `FILTER_SETTINGS`
- `COMPARE_SETTINGS`
- `OFFERS_SETTINGS`
- `PRICES`
- `BASKET`
- `GIFTS_SETTINGS`
- `ALSO_BUY_SETTINGS`
- `BIG_DATA_SETTINGS`
- `ANALYTICS_SETTINGS`
- `REVIEW_SETTINGS`
- `SEARCH_SETTINGS`

`component.php` оперирует:
- `FOLDER`
- `URL_TEMPLATES`
- `VARIABLES`
- `ALIASES`

Практика: при задаче по URL/SEF комплексного каталога открывай `sef-urls.md`, `components.md`, `pagination.md` и конкретный child component (`catalog.section`, `catalog.element`, `catalog.smart.filter`).

## `catalog.section`

Файлы:
- `.parameters.php`
- `class.php`
- `ajax.php`
- stock templates: 6

Подтверждённые важные параметры:

| Группа | Параметры |
|---|---|
| Data source | `IBLOCK_TYPE`, `IBLOCK_ID`, `SECTION_ID`, `SECTION_CODE`, `SECTION_CODE_PATH`, `SECTION_ID_VARIABLE`, `INCLUDE_SUBSECTIONS`, `SHOW_ALL_WO_SECTION` |
| Sort/page | `ELEMENT_SORT_FIELD`, `ELEMENT_SORT_ORDER`, `ELEMENT_SORT_FIELD2`, `ELEMENT_SORT_ORDER2`, `PAGE_ELEMENT_COUNT`, `LINE_ELEMENT_COUNT` |
| Select | `PROPERTY_CODE`, `PROPERTY_CODE_MOBILE`, `SECTION_USER_FIELDS`, `BACKGROUND_IMAGE` |
| Prices | `PRICE_CODE`, `USE_PRICE_COUNT`, `SHOW_PRICE_COUNT`, `PRICE_VAT_INCLUDE` |
| Offers | `OFFERS_FIELD_CODE`, `OFFERS_PROPERTY_CODE`, `OFFERS_SORT_FIELD`, `OFFERS_SORT_ORDER`, `OFFERS_LIMIT` |
| Basket action | `BASKET_URL`, `ACTION_VARIABLE`, `PRODUCT_ID_VARIABLE`, `PRODUCT_QUANTITY_VARIABLE`, `PRODUCT_PROPS_VARIABLE`, `USE_PRODUCT_QUANTITY`, `ADD_PROPERTIES_TO_BASKET`, `PRODUCT_PROPERTIES`, `PARTIAL_PRODUCT_PROPERTIES` |
| Filter/compare | `FILTER_NAME`, `COMPARE` |
| SEO/meta | `SET_TITLE`, `SET_BROWSER_TITLE`, `SET_META_KEYWORDS`, `SET_META_DESCRIPTION`, `SET_LAST_MODIFIED`, `BROWSER_TITLE`, `META_KEYWORDS`, `META_DESCRIPTION` |
| JS/runtime | `DISABLE_INIT_JS_IN_COMPONENT`, `COMPATIBLE_MODE`, `AJAX_MODE` |

Core facts:
- `class.php` checks iblock/catalog-related fields and edit links;
- `ajax.php` exists;
- stock templates contain lazy/show-more logic in shop-core templates;
- pagination and lazy load use `PAGEN_<NavNum>` — смотри `pagination.md`.

Gotchas:
- `nTopCount` is not pagination; for page bugs open `pagination.md`.
- Use stable sort with `ID` to avoid duplicates/skips.
- `FILTER_NAME` must point to an actual global filter array; do not pass user input raw.
- Parent product vs offer matters: price/stock/basket often resolve on offer.
- `SHOW_ALL_WO_SECTION` changes visibility when section is missing.

## `catalog.element`

Файлы:
- `.parameters.php`
- `class.php`
- `ajax.php`
- stock templates: 4

Подтверждённые важные параметры:

| Группа | Параметры |
|---|---|
| Element identity | `ELEMENT_ID`, `ELEMENT_CODE`, `SECTION_ID`, `SECTION_CODE`, `SECTION_CODE_PATH`, `CHECK_SECTION_ID_VARIABLE`, `STRICT_SECTION_CHECK` |
| Properties | `PROPERTY_CODE`, `LINK_IBLOCK_TYPE`, `LINK_IBLOCK_ID`, `LINK_PROPERTY_SID`, `LINK_ELEMENTS_URL` |
| Offers | `OFFERS_FIELD_CODE`, `OFFERS_PROPERTY_CODE`, `OFFERS_SORT_FIELD`, `OFFERS_SORT_ORDER`, `OFFERS_LIMIT`, `SHOW_SKU_DESCRIPTION` |
| Prices | `PRICE_CODE`, `USE_PRICE_COUNT`, `SHOW_PRICE_COUNT`, `PRICE_VAT_INCLUDE`, `PRICE_VAT_SHOW_VALUE` |
| Basket action | `BASKET_URL`, `ACTION_VARIABLE`, `PRODUCT_ID_VARIABLE`, `PRODUCT_QUANTITY_VARIABLE`, `PRODUCT_PROPS_VARIABLE`, `USE_PRODUCT_QUANTITY`, `ADD_PROPERTIES_TO_BASKET`, `PRODUCT_PROPERTIES`, `PARTIAL_PRODUCT_PROPERTIES` |
| SEO/meta | `SET_TITLE`, `SET_CANONICAL_URL`, `SET_BROWSER_TITLE`, `SET_META_KEYWORDS`, `SET_META_DESCRIPTION`, `SET_LAST_MODIFIED`, `ADD_ELEMENT_CHAIN`, `ADD_SECTIONS_CHAIN` |
| Gifts/analytics | `USE_GIFTS_DETAIL`, `USE_GIFTS_MAIN_PR_SECTION_LIST`, `ANALYTICS_SETTINGS` |

Core facts:
- `ajax.php` returns status/text style response keys;
- class code references `PRODUCT_ID`, `OFFER_ID`, `CATALOG_GROUP_ID`, `GROUP_ID`, `IBLOCK_ID`, `LID`;
- SKU/offer selection is template+JS-sensitive.

Gotchas:
- If product visible but cannot buy, check offer ID, price group, quantity, catalog provider and basket events in `catalog.md` / `sale.md`.
- If SEO/canonical wrong, check both component params and template overrides.
- If AJAX add-to-basket fails, inspect template JS, `ACTION_VARIABLE`, `PRODUCT_ID_VARIABLE`, `sessid`, and basket response.

## `catalog.smart.filter`

Файлы:
- `.parameters.php`
- `component.php`
- `class.php`
- stock templates: 2

Подтверждённые параметры:
- `IBLOCK_TYPE`
- `IBLOCK_ID`
- `SECTION_ID`
- `SECTION_CODE`
- `SECTION_CODE_PATH`
- `FILTER_NAME`
- `PREFILTER_NAME`
- `PRICE_CODE`
- `CACHE_GROUPS`
- `SAVE_IN_SESSION`
- `XML_EXPORT`
- `SECTION_TITLE`
- `SECTION_DESCRIPTION`
- `SMART_FILTER_PATH`
- `SEF_MODE`
- `SEF_RULE`
- `PAGER_PARAMS_NAME`

Class/component confirmed fields include:
- `CONTROL_ID`
- `CONTROL_NAME`
- `CONTROL_NAME_ALT`
- `HTML_VALUE`
- `HTML_VALUE_ALT`
- `DISPLAY_TYPE`
- `DISPLAY_EXPANDED`
- `FILTER_HINT`
- `PRICE`
- `PROPERTY_TYPE`
- `USER_TYPE`
- `USER_TYPE_SETTINGS`
- `MIN`, `MAX`
- `URL_ID`

Gotchas:
- Smart filter is tightly coupled with section scope and facet/filter indexes. If products disappear after filter, read `diagnostic-visibility.md`, `index-cache-diagnostics.md`, `pagination.md`.
- `SAVE_IN_SESSION` can preserve old filter state.
- `PREFILTER_NAME` is separate from `FILTER_NAME`.
- SEF filter URL issues go to `sef-urls.md`.

## Compare components

### `catalog.compare.list`

Parameters:
- `IBLOCK_TYPE`, `IBLOCK_ID`
- `DETAIL_URL`
- `COMPARE_URL`
- `ACTION_VARIABLE`
- `PRODUCT_ID_VARIABLE`
- `AJAX_MODE`

Component fields include `DELETE_URL`, `DETAIL_PAGE_URL`, `SECTIONS_LIST`, `COUNT`, `STATUS`.

### `catalog.compare.result`

Parameters:
- `IBLOCK_TYPE`, `IBLOCK_ID`
- `FIELD_CODE`, `PROPERTY_CODE`
- `PRICE_CODE`, `USE_PRICE_COUNT`, `SHOW_PRICE_COUNT`, `PRICE_VAT_INCLUDE`
- `OFFERS_FIELD_CODE`, `OFFERS_PROPERTY_CODE`
- `BASKET_URL`, `ACTION_VARIABLE`, `PRODUCT_ID_VARIABLE`, `SECTION_ID_VARIABLE`
- `DISPLAY_ELEMENT_SELECT_BOX`

Gotchas:
- Compare state is usually user/session/browser-state sensitive. Check component params, AJAX mode and template JS.
- Offers compare requires offer fields/properties, not just parent product properties.

## Basket components

### `sale.basket.basket`

Files:
- `.parameters.php`
- `class.php`
- `ajax.php`
- templates: 2

Important params:
- `PATH_TO_ORDER`
- `HIDE_COUPON`
- `COLUMNS_LIST_EXT`
- `COLUMNS_LIST_MOBILE`
- `OFFERS_PROPS`
- `ACTION_VARIABLE`
- `AUTO_CALCULATION`
- `CORRECT_RATIO`
- `COMPATIBLE_MODE`
- `USE_GIFTS`
- `GIFTS_*`
- `USE_PREPAYMENT`
- `SET_TITLE`

Class fields confirm basket states:
- `BASKET_ITEMS`
- `BASKET_REFRESHED`
- `CHANGED_BASKET_ITEMS`
- `DELETED_BASKET_ITEMS`
- `RESTORED_BASKET_ITEMS`
- `MERGED_BASKET_ITEMS`
- `COUPON_LIST`
- `WARNING_MESSAGE`
- `ERROR_MESSAGE`
- `SALE_BASKET_AVAILABLE_QUANTITY`
- `SALE_BASKET_ITEM_WRONG_AVAILABLE_QUANTITY`
- `SALE_BASKET_ITEM_WRONG_PRICE`

Gotchas:
- Basket can refresh/merge/delete items before rendering; do not debug only template.
- Wrong price/quantity warnings usually point to catalog provider, price access, stock or ratio.
- Coupon issues require sale discount/coupon layer.

### `sale.basket.order.ajax`

Legacy checkout component with `component.php` and one template.

Confirmed fields include:
- `BASKET_ITEMS`
- `DELIVERY_ID`, `DELIVERY_PRICE`
- `PAY_SYSTEM_ID`
- `PERSON_TYPE_ID`
- `ORDER_PROPS_ID`
- `ORDER_PRICE`
- `ORDER_WEIGHT`
- `USER_DESCRIPTION`
- `ORDER_ID`, `ORDER_LIST`

Use it as legacy route. For modern checkout prefer checking `sale.order.ajax` / `sale.order.checkout` if present in project.

## Checkout/order components

### `sale.order.ajax`

Files:
- `.parameters.php`
- `class.php`
- `ajax.php`
- templates: 2

Important params:
- `PATH_TO_BASKET`
- `PATH_TO_PERSONAL`
- `PATH_TO_AUTH`
- `PATH_TO_PAYMENT`
- `ALLOW_AUTO_REGISTER`
- `ALLOW_APPEND_ORDER`
- `DISABLE_BASKET_REDIRECT`
- `ONLY_FULL_PAY_FROM_ACCOUNT`
- `SEND_NEW_USER_NOTIFY`
- `DELIVERY_NO_AJAX`
- `DELIVERY_NO_SESSION`
- `DELIVERY_TO_PAYSYSTEM`
- `SHOW_NOT_CALCULATED_DELIVERIES`
- `SPOT_LOCATION_BY_GEOIP`
- `TEMPLATE_LOCATION`
- `USE_PREPAYMENT`
- `USE_PHONE_NORMALIZATION`
- `USER_CONSENT`, `USER_CONSENT_IDS`
- `SHOW_VAT_PRICE`

Class fields confirm:
- auth/registration fields;
- basket positions and discounts;
- delivery/pay system selection;
- location/zip fields;
- final step/order request;
- `ERROR`, `ERROR_SORTED`;
- `ORDER_TOTAL_LEFT_TO_PAY`.

Gotchas:
- Checkout bugs are usually not template-only. Follow: basket refresh → person type → required order props → location → delivery restrictions → payment restrictions → discounts → `Order::save()`.
- `DELIVERY_NO_SESSION` / `DELIVERY_NO_AJAX` can change user-visible behavior.
- Phone normalization/user consent are parameterized.

### `sale.order.checkout`

Files:
- `.parameters.php`
- `class.php`
- `ajax.php`
- templates: 1

Params:
- `SHOW_RETURN_BUTTON`
- `URL_PATH_TO_DETAIL_PRODUCT`

Class/ajax fields confirm a newer checkout flow with:
- `ORDER`, `BASKET`, `PAYMENTS`, `PAY_SYSTEMS`;
- `JSON_DATA`;
- `USER_CONSENT_PROPERTY_DATA`;
- `ACTIONS`, `FIELDS`, `ERRORS` in ajax;
- basket item operations: `DELETE`, `RESTORE`, `QUANTITY`, `NEED_FULL_RECALCULATION`.

Gotchas:
- Treat as separate checkout route, not the same as `sale.order.ajax`.
- AJAX contract matters; inspect template JS before changing server code.

## Personal order components

### `sale.personal.order`

Complex personal orders router.

Params:
- `SEF_MODE`
- `PATH_TO_BASKET`
- `PATH_TO_CATALOG`
- `PATH_TO_PAYMENT`
- `ORDERS_PER_PAGE`
- `NAV_TEMPLATE`
- `DISALLOW_CANCEL`
- `SAVE_IN_SESSION`
- `CACHE_GROUPS`
- `SET_TITLE`

### `sale.personal.order.list`

Params:
- `PATH_TO_DETAIL`
- `PATH_TO_CANCEL`
- `PATH_TO_COPY`
- `PATH_TO_BASKET`
- `PATH_TO_CATALOG`
- `PATH_TO_PAYMENT`
- `ORDERS_PER_PAGE`
- `NAV_TEMPLATE`
- `DISALLOW_CANCEL`
- `SAVE_IN_SESSION`

Fields include `ORDER`, `PAYMENT`, `SHIPMENT`, `BASKET_ITEMS`, `USER_ID`.

### `sale.personal.order.detail`

Params:
- `PATH_TO_LIST`
- `PATH_TO_CANCEL`
- `PATH_TO_COPY`
- `PATH_TO_PAYMENT`
- `PERSON_TYPE_ID`
- `SET_TITLE`

Gotchas:
- Personal cabinet must filter by current user and site; if orders leak/missing, check user binding, permissions and path params.
- `SAVE_IN_SESSION` can affect list state.
- Copy/cancel/payment links must be checked through sale permissions/status restrictions.

## Catalog admin/productcard/store components

These are not public storefront components, but matter for admin tasks.

### Product/card

- `catalog.product.grid` — product grid; confirmed fields: `GRID_ID`, `IBLOCK_ID`, `IBLOCK_SECTION_ID`, `PRODUCT_TYPE`, `SKU_FIELD_NAMES`, `SKU_PRODUCT_MAP`, `NAV_STRING`, `URL_TO_ADD_PRODUCT`.
- `catalog.productcard.details` — card fields; confirmed fields include `ENTITY_ID`, `ENTITY_FIELDS`, `ENTITY_VALUES`, `IBLOCK_ID`, `PRICE`, `PROPERTY_FIELDS`, `SEO`, `SMART_FILTER`, `IS_SIMPLE_PRODUCT`.
- `catalog.productcard.variation.grid/details` — variations/SKU admin UI.

### Store documents

- `catalog.store.document.list` — document grid; fields include `GRID_ID`, `FILTER_ID`, `DOC_TYPE`, `STATUS`, `STORES_FROM`, `STORES_TO`, `WAS_CANCELLED`.
- `catalog.store.document.detail` — document form; fields include `DOCUMENT_ID`, `DOCUMENT_TYPE`, `ELEMENTS`, `PRODUCT_ID`, `STORE_FROM`, `STORE_TO`, `AMOUNT`, `PURCHASING_PRICE`, `BARCODE`, `ERROR_MESSAGE`.

Use `catalog.md` for product/store API and `grid-admin-modern.md` for grid mechanics.

## Viewed/recommended/gifts/bigdata

Confirmed components:
- catalog: `catalog.bigdata.products`, `catalog.products.viewed`, `catalog.viewed.products`, `catalog.recommended.products`;
- sale: `sale.bestsellers`, `sale.gift.*`, `sale.products.gift*`, `sale.recommended.products`, `sale.prediction.product.detail`.

Gotchas:
- Recommendations/gifts depend on catalog + sale + user/basket/order context.
- Cache and personalization can make bugs look non-deterministic.
- For marketing/personalization deep dive, use future `shop-marketing-analytics.md`.

## 1С components quick map

### `catalog.import.1c`

Params confirmed:
- `IBLOCK_TYPE`
- `SITE_LIST`
- `INTERVAL`
- `GROUP_PERMISSIONS`
- `FILE_SIZE_LIMIT`
- `USE_CRC`
- `USE_ZIP`
- `USE_OFFERS`
- `FORCE_OFFERS`
- `SKIP_ROOT_SECTION`
- `SKIP_SOURCE_CHECK`
- `ELEMENT_ACTION`
- `SECTION_ACTION`
- `TRANSLIT`
- `IBLOCK_CACHE_MODE`

Component fields include `STEP`, `TEMP_DIR`, `IBLOCK_ID`, `PRICES_MAP`, `SECTION_MAP`.

### `catalog.export.1c`

Params confirmed:
- `IBLOCK_ID`
- `INTERVAL`
- `GROUP_PERMISSIONS`
- `USE_ZIP`
- `ELEMENTS_PER_STEP`

Component fields include `LAST_ID`, `PROPERTY_MAP`, `PRICES_MAP`, `SECTION_MAP`, `PRODUCT_IBLOCK_ID`.

### `sale.export.1c`

Params confirmed:
- `SITE_LIST`
- `EXPORT_PAYED_ORDERS`
- `EXPORT_ALLOW_DELIVERY_ORDERS`
- `EXPORT_FINAL_ORDERS`
- `FINAL_STATUS_ON_DELIVERY`
- `REPLACE_CURRENCY`
- `GROUP_PERMISSIONS`
- `USE_ZIP`
- `INTERVAL`
- `FILE_SIZE_LIMIT`
- `IMPORT_NEW_ORDERS`
- `CHANGE_STATUS_FROM_1C`

For actual exchange flow, use `commerce-1c-integration.md`.

## Diagnostics by symptom

### Catalog list empty, detail opens

Read in order:
1. `diagnostic-visibility.md` — active/site/permissions/section chain;
2. `catalog.section` params: section/filter/sort/page;
3. `catalog.smart.filter` state and facet/index;
4. `pagination.md` for page/offset/lazy load;
5. `cache-infra.md` / `index-cache-diagnostics.md`.

### Filter changes but products do not

Check:
- `FILTER_NAME` global array;
- `PREFILTER_NAME`;
- `SAVE_IN_SESSION`;
- `SMART_FILTER_PATH` / SEF;
- cache key;
- facet/search index.

### Add to basket fails from list/detail

Check:
- component action variables;
- selected offer ID, not parent ID;
- price group and currency;
- quantity/ratio/stock;
- `ADD_PROPERTIES_TO_BASKET`, `PRODUCT_PROPERTIES`, `PARTIAL_PRODUCT_PROPERTIES`;
- template JS and ajax endpoint;
- sale basket warnings.

### Checkout fails

Check:
1. basket refreshed and not empty;
2. person type;
3. required order properties;
4. location;
5. delivery restrictions;
6. payment restrictions;
7. discounts/coupons;
8. `Order::save()` errors;
9. component AJAX/template.

### Personal order missing

Check:
- current user;
- site `LID`;
- `PATH_TO_*` params;
- `ORDERS_PER_PAGE` and pagination;
- cancel/copy/payment restrictions;
- `SAVE_IN_SESSION`.

## What not to do

- Do not treat `iblock`-hosted `catalog.*` as proof that `catalog` module exists.
- Do not debug every storefront issue from template only; standard components have class/component logic, ajax, cache, sale/catalog side effects.
- Do not mix `sale.order.ajax`, `sale.order.checkout`, and `sale.basket.order.ajax` as one component: they are different flows.
- Do not bypass sale/catalog APIs with SQL for basket/order/price/stock fixes.
- Do not promise exact params for project overrides until checking `local/components` and `local/templates`.
- Do not ignore JS/template variants: many public shop components are template-driven.
