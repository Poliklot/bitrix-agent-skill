# Shop integrations/webservice — webservice, REST, sale/catalog app hooks

> Reference для Bitrix-скилла. Загружай, когда задача связана с `webservice.sale`, `webservice.statistic`, SOAP/WSDL, REST webhooks/apps/placements, sale/catalog REST API, внешними платежными/доставочными/кассовыми app handlers или когда нужно закрыть integration extras shop-core. Не используй этот файл как замену `commerce-1c-integration.md`: CommerceML/1С живёт в `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`.

## Audit note

Проверено по shop-core:

- `www/bitrix/modules/webservice` — `26.0.0`, `VERSION_DATE` `2026-03-18 18:00:00`, 5 components, 0 admin pages, 1 `lib` file, 12 legacy class files, no DB tables.
- `www/bitrix/modules/rest` — `26.0.0`, `VERSION_DATE` `2026-01-28 16:35:48`, 42 components, 2 admin pages, 510 `lib` files, REST DB layer present.
- Adjacent confirmed modules: `sale` `26.0.0`, `catalog` `25.550.0`, `statistic` `26.0.0`.
- `webservice.sale` and `webservice.statistic` are **components inside module `webservice`**, not separate modules `webservice.sale` / `webservice.statistic`.

Use this as confirmed routing/contract layer. For order lifecycle read `sale.md`; for product/price/store data read `catalog.md`; for generic REST patterns read `rest.md`; for traffic/statistic internals read `shop-marketing-analytics.md`; for 1С/CommerceML read `commerce-1c-integration.md`.

## Главный вывод

`webservice` in this core is legacy SOAP/WSDL infrastructure plus two dashboard/gadget services:

1. `webservice.server` — generic SOAP endpoint wrapper around `IWebService` implementors.
2. `webservice.checkauth` — SOAP auth helper.
3. `webservice.sale` — sale **statistics/livefeed** SOAP service over order counters, not order CRUD and not 1С exchange.
4. `webservice.statistic` — legacy traffic/statistic SOAP service, not sales analytics by itself.
5. `stssync.server` — SharePoint/Outlook sync endpoint layer with application-password auth.

Modern external integrations in this shop-core mostly use `rest` + module controllers/events:

- `sale` exposes Engine REST controllers for order/payment/shipment/basket/status/properties and explicit REST scopes for pay systems, deliveries, cashboxes and sale events.
- `catalog` exposes Engine REST controllers for products, prices, price types, measures, stores, store products, documents, sections and event bindings for selected catalog entities.
- `rest` owns apps, incoming/outgoing webhooks, event bindings, placements, auth, batch, method discovery and usage/stat tables.

Критично:

- `webservice.sale` ≠ `sale.export.1c` and ≠ order API. It returns aggregate counters and a link to `/bitrix/admin/sale_stat.php`.
- `webservice.statistic` requires module `statistic` and reads legacy traffic tables. It can be empty even when orders exist.
- REST controller method names must be confirmed at runtime with `methods`, `method.get` or the Engine route map before hardcoding; controller/action summaries below are routing hints.
- Do not expose SOAP helpers or test endpoints publicly without access review: `webservice.checkauth` accepts login/password and returns user fields; `webservice.server?test` can execute component test code.

## Fast routing

| Запрос | Сначала читать | Затем |
|---|---|---|
| “`webservice.sale` не работает” | `webservice.sale` section below | `sale.md`, order rights/status/date filters |
| “`webservice.statistic` пустой” | `webservice.statistic` section below | `shop-marketing-analytics.md`, `statistic` tables/options |
| “Нужен WSDL/SOAP endpoint” | `webservice.server` + SOAP classes | `http.md`, access/auth review |
| “REST событие заказа не прилетело” | sale REST events section | `rest.md`, `b_rest_event`, `event.offline.*` |
| “Внешняя доставка/ПС/касса через приложение” | sale explicit REST scopes | handler tables and `onRestAppDelete` cleanup |
| “REST товар/цена/склад” | catalog REST controllers | `catalog.md`, `rest.md`, permissions, pagination |
| “Placement для внешнего товара” | catalog placement section | `placement.*`, `b_rest_placement` |
| “Это 1С?” | usually `commerce-1c-integration.md` | only use this file if task is SOAP/REST, not CommerceML |

## `webservice` module structure

### Components — 5

- `webservice.server` — generic SOAP server component.
- `webservice.checkauth` — auth SOAP service wrapper.
- `webservice.sale` — order statistics livefeed SOAP service.
- `webservice.statistic` — traffic/statistics SOAP service and Windows gadget assets.
- `stssync.server` — SharePoint/Outlook list sync server.

### Legacy classes

Autoloaded from `include.php`:

- XML: `CXMLCreator`.
- SOAP structures: `CSOAPHeader`, `CSOAPBody`, `CSOAPEnvelope`, `CSOAPParameter`, `CSOAPFault`.
- SOAP runtime: `CSOAPCodec`, `CSOAPRequest`, `CSOAPResponse`, `CSOAPClient`, `CSOAPServerResponser`, `CWSSOAPResponser`, `CSOAPServer`.
- WSDL: `CWSDLCreator`.
- Web service wrapper: `CWebServiceDesc`, `IWebService`, `CWebService`.
- SharePoint client: `CSPListsClient`.

Constants registered by `include.php` include SharePoint service path/namespace and SOAP namespace constants such as `BX_SOAP_ENV`, `BX_SOAP_ENC`, `BX_SOAP_SCHEMA_INSTANCE`, `BX_SOAP_SCHEMA_DATA`.

### Install files/endpoints

Install copies:

- components to `/bitrix/components/bitrix/*`;
- tools to `/bitrix/tools/`: `sale_gadget.php`, `stat_gadget.php`, `stssync.php`;
- JS extension `stssync` to `/bitrix/js/webservice/stssync.js`;
- sample `/bitrix/ws/wscauth.php`, `/bitrix/ws/wsadvert.php`, with `.access.php` denying folder by default except those files for group 2 read.

Options: `webservice` default option `DENYALL=N`; options page mainly links the statistic gadget package.

## SOAP core contract

### `webservice.server`

Parameters:

- `WEBSERVICE_NAME` — SOAP service name, e.g. `bitrix.webservice.sale`.
- `WEBSERVICE_MODULE` — module to include before class lookup; can be empty when class is defined by current component.
- `WEBSERVICE_CLASS` — `IWebService` implementor class.
- optional `SOAPSERVER_RESPONSER` array — raw SOAP responders.

Runtime behavior:

1. Design mode shows include areas/template for admin.
2. If `SOAPSERVER_RESPONSER` is passed and request is POST without `directcall`, it creates `CSOAPServer` and processes raw SOAP.
3. Otherwise it includes `WEBSERVICE_MODULE` if class is missing.
4. Calls `CWebService::SetComponentContext($arParams)` and `CWebService::RegisterWebService($WEBSERVICE_CLASS)`.
5. `?wsdl` returns XML WSDL from `CWebService::GetWSDL($WEBSERVICE_NAME)`.
6. `?test` runs `CWebService::TestComponent($WEBSERVICE_NAME)`.
7. POST without `directcall` runs `CWebService::SOAPServerProcessRequest($WEBSERVICE_NAME)`.
8. Other requests render component template/service description.

`IWebService` implementors must provide `GetWebServiceDesc()` returning `CWebServiceDesc` with:

- `wsname`;
- `wsclassname`;
- `wsdlauto`;
- `wsendpoint`;
- `wstargetns`;
- `classes` method descriptors;
- `structTypes` and `classTypes` complex type descriptors.

`CWebService::RegisterWebService()` rejects missing service name/class/namespace/endpoint/classes/struct/class type arrays, builds WSDL through `CWSDLCreator`, registers functions in `CWSSOAPResponser`, and stores descriptors in `$GLOBALS['wsdescs']` / `$GLOBALS['wswraps']`.

## `webservice.checkauth`

Class: `CCheckAuthWS`.

Methods:

- `CheckAuthorization($user, $password)` — calls `CUser::Login($user, $password)` and returns fetched user fields or `CSOAPFault`.
- `GetHTTPUserInfo()` — requires current user to be admin; otherwise calls `$USER->RequiredHTTPAuthBasic()` and returns fault.

Descriptor:

- `wsname`: `bitrix.webservice.checkauth`;
- struct type `CUser` includes fields such as `ID`, `NAME`, `LOGIN`, `EMAIL`, `ACTIVE`, `PASSWORD`, `CHECKWORD`.

Safety notes:

- Treat this as highly sensitive. Do not expose it to anonymous/public networks casually.
- Do not log SOAP request bodies containing passwords.
- The stock test uses hardcoded `admin` / `123456` in sample code; never copy this into production docs or code.

## `webservice.sale`

Class: `CSaleWS`; requires modules `webservice` and `sale`.

This is **order statistics livefeed**, not order CRUD.

Method:

- `GetLiveFeedData($site_id = "", $lang = "en")`.

Auth:

- `CheckAuth()` reads `$APPLICATION->GetGroupRight('sale')`.
- If sale right is `D`, it triggers HTTP Basic auth and returns SOAP fault.
- If sale right is not `W`, it adds status permission filter by current user groups:
  - `STATUS_PERMS_GROUP_ID` = `$USER->GetUserGroupArray()`;
  - `>=STATUS_PERMS_PERM_VIEW` = `Y`.

Data:

- Aggregates `CSaleOrder::GetList()` by periods:
  - before last week;
  - last week;
  - this week;
  - before yesterday;
  - yesterday;
  - today.
- Status buckets:
  - `CREATED` by `DATE`;
  - `PAID` by `DATE_PAYED`;
  - `CANCELED` by `DATE_UPDATE` + `CANCELED=Y`;
  - `ALLOW_DELIVERY` by `DATE_UPDATE` + `ALLOW_DELIVERY=Y`.
- Sums use aggregate `SUM => PRICE`, `COUNT => ID`.
- Currency is `CSaleLang::GetLangCurrency($site_id)` when site is passed; otherwise `CCurrency::GetBaseCurrency()`.

Output struct `LiveFeedData`:

- `TITLE`;
- `MESSAGE` — HTML table string;
- `TEXT_MESSAGE` — text with `#BR#` separators;
- `URL` — admin URL `/bitrix/admin/sale_stat.php?lang=<lang>`.

Observed gotcha in current core:

- In the `site_id` branch the code calls `CSite::GetByID($arFields['SITE_ID'])` while `$arFields` is not defined in this component. Treat site filtering/server-name behavior as suspect until runtime-tested; verify actual output with a real site id.

Diagnostics:

1. Confirm `webservice` and `sale` modules exist.
2. Confirm endpoint includes `bitrix:webservice.sale`, not `sale.export.1c`.
3. Request `?wsdl` first; then POST SOAP.
4. Check sale group rights and order status permissions.
5. Check date fields: created vs paid vs canceled/delivery are different filters.
6. Check site id/currency branch and current `server_name` option.
7. For actual order CRUD use sale REST controllers or Sale API, not `webservice.sale`.

## `webservice.statistic`

Class: `CStatisticWS`; requires modules `webservice` and `statistic`.

Methods:

- `UsersOnline()` — `CUserOnline::GetList()` sessions and guest count.
- `GetCommonValues()` — `CTraffic::GetCommonValues()` plus `ONLINE_LIST`.
- `GetAdv()` — top advertising/adv records through `CAdv::GetList()`.
- `GetEvents()` — event counters through `CStatEventType::GetList()`.
- `GetPhrases()` — search phrases through `CTraffic::GetPhraseList()`.
- `GetRefSites()` — referer sites through `CTraffic::GetRefererList()`.
- `GetSearchers()` — searchers through `CSearcher::GetList()`.
- `GetLiveFeedData($site_id = "", $lang = "en")` — HTML/text dashboard data.

Auth:

- `CheckAuth()` reads `$APPLICATION->GetGroupRight('statistic')` and triggers HTTP Basic auth/fault if right is `D`.

Limits/options:

- Top lists stop at `COption::GetOptionInt('statistic', 'STAT_LIST_TOP_SIZE', 10)`.

Output:

- `GetLiveFeedData()` returns `LiveFeedData` struct with title, HTML table, text and `/bitrix/admin/stat_list.php?lang=<lang>` URL.
- Generic methods return complex structs: `Session`, `Top`, `UsersOnlineList`, `CommonValues`.

Diagnostics:

1. Confirm module `statistic` exists and actually records traffic/events.
2. Confirm statistic right is not `D` for current user/auth context.
3. Check `STAT_LIST_TOP_SIZE` for unexpectedly short lists.
4. If livefeed is empty but orders exist, this is expected: orders are in `webservice.sale`, not `webservice.statistic`.
5. If statistic is heavy/slow, open `shop-marketing-analytics.md`; `statistic` has runtime hit/session hooks and cleanup/optimization options.

## `stssync.server` and `/bitrix/tools/stssync.php`

`stssync.server` supports only SEF mode. Default templates:

- endpoint: `#user_id#/#ap#/_vti_bin/lists.asmx`;
- item redirect: `#user_id#/#ap#/#path#/DispForm.aspx`;
- index redirect: `#user_id#/#ap#/#path#/`.

Endpoint flow:

1. Parse `user_id`, `ap`, `path`.
2. Include module `webservice`.
3. Call `Bitrix\WebService\StsSync::checkAuth($userId, $ap)`.
4. Include `bitrix:webservice.server` with target service params.
5. Final actions and die.

`Bitrix\WebService\StsSync`:

- `getUrl()` builds JS call `BX.StsSync.sync(...)` and loads JS extension `stssync`.
- `checkAuth($userId, $ap)` uses `ApplicationPasswordTable::findPassword()` and accepts only application password with `OutlookApplication::ID` and valid scope; then updates login date/IP and authorizes user.
- `getAuth($type)` generates application password through intranet `OutlookApplication`.

`/bitrix/tools/stssync.php`:

- defines `NOT_CHECK_PERMISSIONS`;
- responds JSON;
- action `stssync_auth` requires authorized user, POST, `check_bitrix_sessid()` and module `webservice`;
- returns generated application password `ap` when available.

Safety:

- Treat `ap` as a credential.
- Do not bypass POST + sessid for `stssync_auth`.
- Do not expose arbitrary service class through `stssync.server` without checking `WEBSERVICE_CLASS` and auth.

## Generic REST module layer

### Components — 42

Important families:

- endpoint/auth: `rest.server`, `rest.authorize`, `rest.token`;
- webhooks/integrations: `rest.hook*`, `rest.integration.*`;
- marketplace/apps: `rest.marketplace*`, `app.layout`, `app.placement`, `rest.app.settings`;
- configuration import/export/install: `rest.configuration*`;
- provider/stat: `rest.provider`, `rest.statistic`;
- tooling: `rest.devops`, `rest.apconnect`, `rest.einvoice.installer`.

### Core REST methods

From `CRestProvider` and API handlers:

- `batch`;
- `scope`, `methods`, `method.get`;
- `server.time`;
- `profile`;
- `app.info`, `feature.get`;
- `app.option.get`, `app.option.set`;
- `user.option.get`, `user.option.set`;
- `events`, `event.bind`, `event.unbind`, `event.get`;
- `event.offline.get`, `event.offline.clear`, `event.offline.error`, `event.offline.list`;
- `event.test`;
- `placement.list`, `placement.bind`, `placement.unbind`, `placement.get`;
- user/userfield type methods through `Bitrix\Rest\Api\User` and `UserFieldType`.

### REST auth and handlers

Install registers:

- `main.OnBeforeProlog` → `CRestEventHandlers::OnBeforeProlog`;
- `rest.OnRestServiceBuildDescription` → base entity/user/placement/event/userfieldtype handlers;
- `rest.onFindMethodDescription` → `Bitrix\Rest\Engine\RestManager::onFindMethodDescription`;
- `rest.onRestCheckAuth` → OAuth fallback when `oauth` module is missing, APAuth, SessionAuth;
- configuration import/export/clear/entity/manifest handlers;
- application/module change hooks for scope manager and marketplace tags;
- IM notify schema and subscription hooks.

### REST DB layer

Core tables confirmed:

- app/auth: `b_rest_app`, `b_rest_app_lang`, `b_rest_ap`, `b_rest_ap_permission`;
- event delivery: `b_rest_event`, `b_rest_event_offline`;
- logs/stat: `b_rest_log`, `b_rest_app_log`, `b_rest_stat_method`, `b_rest_stat_app`, `b_rest_stat`;
- placements: `b_rest_placement`, `b_rest_placement_lang`;
- usage/owner/integration/config: `b_rest_usage_entity`, `b_rest_usage_stat`, `b_rest_owner_entity`, `b_rest_integration`, `b_rest_configuration_storage`, `b_rest_free_app`.

Diagnostics for REST:

1. Check method exists with `methods` or `method.get` before assuming name/signature.
2. Check token scopes via `scope` and app permissions.
3. For outgoing events check `b_rest_event` binding and handler URL.
4. For offline/SQS delivery check `b_rest_event_offline` and `event.offline.*` methods.
5. For placements check `placement.list` + `b_rest_placement`.
6. For batch issues check `batch` length/allowed methods and per-method errors.

## Sale REST surface

### Engine controllers

`sale/.settings.php` enables REST integration:

- default namespace: `\Bitrix\Sale\Controller`;
- additional namespace: `\Bitrix\Sale\Exchange\Integration\Controller` under `integration`;
- `restIntegration.enabled = true`.

Controller/action families confirmed:

- `order`: `getFields`, `get`, `tryModify`, `modify`, `tryAdd`, `add`, `tryUpdate`, `update`, `list`, `delete`, order subresource getters, `import`, `importDelete`.
- `basketitem`: fields, catalog product fields, modify/add/update/delete/list, price/quantity/vat/weight getters.
- `payment`: fields, modify/add/update/delete/get/list, paid/return/account/pay system methods.
- `shipment`: fields, modify/add/update/delete/get/list, shipped/allow-delivery/base-price methods.
- `property`, `propertyvalue`, `propertygroup`, `propertyvariant`, `propertyrelation`.
- `persontype`, `status`, `statuslang`, `profile`, `profilevalue`.
- `paymentitembasket`, `paymentitemshipment`, `shipmentitem`, `shipmentpropertyvalue`.
- `deliveryrequest`, `deliveryservices`, `tracking`, `tradebinding`, `tradeplatform`, `businessvaluepersondomain`, `barcode`, `facebookconversion`, `synchronizer`.

Naming is Engine/REST-controller based; confirm concrete public method names in runtime through REST discovery. Typical pattern is `<module>.<controller>.<action>`, e.g. order controller actions map into sale order methods, but do not hardcode without checking current `method.get`.

Sale controller base has important behavior:

- `processBeforeAction()` checks permission and internalizes request fields through `Bitrix\Sale\Rest\Internalizer` or CRM order internalizer when CRM is installed.
- `processAfterAction()` externalizes output through Sale/CRM externalizer.
- `getNavData()` uses `IRestService::LIST_LIMIT` and `start` offset.
- Order builder defaults can create anonymous user and delete missing client/trade/payment/shipment/property structures in REST import-style operations.

### Explicit sale REST scopes/methods

Install registers `rest.OnRestServiceBuildDescription` handlers:

#### Pay systems — scope `pay_system`

- `sale.paysystem.handler.add/update/delete/list`;
- `sale.paysystem.add/update/delete/list`;
- `sale.paysystem.settings.get/update`;
- `sale.paysystem.settings.invoice.get`;
- `sale.paysystem.settings.payment.get`;
- `sale.paysystem.pay.invoice`;
- `sale.paysystem.pay.payment`.

Cleanup on `rest.onRestAppDelete` deletes pay systems created from app REST handlers and rows in `b_sale_pay_system_rest_handlers` when app is clean-deleted.

#### Delivery — scope `delivery`

- handler: `sale.delivery.handler.add/update/delete/list`;
- service: `sale.delivery.add/update/delete/getList`, `sale.delivery.config.get/update`;
- request: `sale.delivery.request.update/delete/sendmessage`;
- extra services: `sale.delivery.extra.service.add/update/delete/get`.

Handler storage: `b_sale_delivery_rest_handler`. App delete cleanup runs through `Bitrix\Sale\Delivery\Rest\BaseService::onRestAppDelete`.

#### Cashbox — scope `cashbox`

- handlers: `sale.cashbox.handler.add/update/delete/list`;
- cashboxes: `sale.cashbox.add/update/delete/list`;
- settings: `sale.cashbox.settings.get/update`, `sale.cashbox.ofd.settings.get/update`;
- checks: `sale.cashbox.check.apply`;
- OFD: `sale.ofd.list`, `sale.ofd.settings.get`.

Handler storage: `b_sale_cashbox_rest_handler`. App delete cleanup removes matching REST cashboxes and handlers.

### Sale REST events

`Bitrix\Sale\Rest\RestManager::onRestServiceBuildDescription()` registers scope `sale` events:

- `OnSaleOrderSaved` → PHP event `sale.OnSaleOrderSaved`;
- `OnSaleBeforeOrderDelete` → `sale.OnSaleBeforeOrderDelete`;
- `OnPropertyValueEntitySaved` → `sale.OnSalePropertyValueEntitySaved`;
- `OnPaymentEntitySaved` → `sale.OnSalePaymentEntitySaved`;
- `OnShipmentEntitySaved` → `sale.OnSaleShipmentEntitySaved`;
- `OnOrderEntitySaved` → `sale.OnSaleOrderEntitySaved`;
- `OnPropertyValueDeleted` → `sale.OnSalePropertyValueDeleted`;
- `OnPaymentDeleted` → `sale.OnSalePaymentDeleted`;
- `OnShipmentDeleted` → `sale.OnSaleShipmentDeleted`;
- `OnOrderDeleted` → `sale.OnSaleOrderDeleted`.

Event payloads:

- `OnSaleOrderSaved` returns `FIELDS.ID`, `FIELDS.XML_ID`, `FIELDS.ACTION=save` unless import/deleted action or same handler is already executed.
- `OnSaleBeforeOrderDelete` returns `FIELDS.ID`, `FIELDS.XML_ID`, `FIELDS.ACTION=delete` and marks manager action as deleted.
- Entity saved/deleted events return `FIELDS.ID` of entity/order-related entity.
- Unsupported context throws `RestException`.

Diagnostics:

1. Check REST event binding with `event.get` / `b_rest_event`.
2. Check app scope contains `sale` and event is available.
3. If event is suppressed, inspect `Bitrix\Sale\Rest\Synchronization\Manager` action: import/delete and duplicate executed handler can stop event.
4. For delete flow check `OnSaleBeforeOrderDelete` vs post-delete events.
5. For partial entity events check whether event parameters include `ENTITY` or `VALUES.ID`.

## Catalog REST surface

### Engine controllers

`catalog/.settings.php` enables REST integration:

- default namespace: `\Bitrix\Catalog\Controller`;
- `restIntegration.enabled = true`;
- REST event bind classes: `Price`, `Product`, `Measure`, `RoundingRule`, `PriceType`.

Controller/action families confirmed:

- `catalog`: `getFields`, `isOffers`, `list`, `get`, `add`, `update`, `delete`.
- `product`: `configure`, `getFieldsByFilter`, `list`, `get`, `add`, `update`, `delete`, `download`, `addProperty`.
- product subtypes: `product.offer`, `product.service`, `product.sku`.
- `price`, `pricetype`, `pricetypegroup`, `pricetypelang`, `pricetyperights`.
- `measure`, `ratio`, `roundingrule`, `vat`, `extra`.
- `store`, `storeproduct`, `storeselector`.
- `document`, `document.element`, `document.mode`, `documentcontractor`.
- `section`, `productproperty*`, `productimage`, `contractor`, `enum`, `config`, `analytics`.

Catalog controller base:

- uses `Bitrix\Rest\Integration\Controller\Base`;
- creates rest views through `CatalogViewManager`;
- gates operations with `Bitrix\Catalog\Access\AccessController` actions;
- list pagination uses `IRestService::LIST_LIMIT` and `start` offset.

### Catalog REST events and placement

`catalog.install` registers:

- `rest.OnRestServiceBuildDescription` → `Bitrix\Catalog\EventDispatcher\EventDispatcher::onRestServiceBuildDescription`;
- `rest.OnRestAppInstall` → `Bitrix\Catalog\Store\EnableWizard\OnecAppManager::onRestAppInstall`.

Event dispatcher returns scope `catalog`:

- `CRestUtil::EVENTS` from event-bind classes in `.settings.php`;
- placement `CATALOG_EXTERNAL_PRODUCT`.

Confirmed event-bind classes:

- `Bitrix\Catalog\Controller\Product` — maps add/update/delete model events to REST event names like `<module>.<entity>.on.add`, `<module>.<entity>.on.update`, `<module>.<entity>.on.delete`; callback payload includes `FIELDS.ID` and `FIELDS.TYPE`.
- `Bitrix\Catalog\Controller\PriceType` — maps `OnGroupAdd`, `OnGroupUpdate`, `OnGroupDelete` to `catalog.price.type.on.add/update/delete`; payload includes `FIELDS.ID`.
- `Price`, `Measure`, `RoundingRule` also implement `EventBindInterface`; inspect current class `getHandlers()` when exact event name matters.

Placement:

- `CATALOG_EXTERNAL_PRODUCT` is available through `placement.*` APIs and stored in `b_rest_placement`.
- Use this for external product UI/app embedding, not for replacing catalog product storage.

Diagnostics:

1. Confirm app has `catalog` scope and method exists via `method.get`.
2. For list methods check `start`, `IRestService::LIST_LIMIT`, stable order and filters.
3. For product writes check catalog RBAC, iblock rights, price permissions and product type/SKU constraints.
4. For file/download actions check `catalog.product.download` route and file access.
5. For event delivery inspect `b_rest_event` and event-bind class payload.
6. For external product placement inspect `placement.list`, `placement.get`, `b_rest_placement` and user/site constraints.

## B24 sale exchange/integration layer

Do not confuse this with 1С/CommerceML.

In `sale/lib/exchange/integration/*` the core contains B24/CRM integration classes:

- app/oauth/client/token layer;
- controllers under namespace `Bitrix\Sale\Exchange\Integration\Controller` with route prefix `integration`;
- REST remote proxies for CRM activity/company/contact/deal/placement/timeline and sale statistics/statistics provider;
- command/batch services;
- entities/tables: `b_sale_b24integration_bind`, `b_sale_b24integration_relation`, `b_sale_b24integration_token`, `b_sale_b24integration_stat_provider`, `b_sale_b24integration_stat`.

Use it when a task says Bitrix24/CRM app integration, not when it says “1С выгрузка”. For 1С open `commerce-1c-integration.md`.

## Diagnostics by symptom

### WSDL opens but SOAP POST fails

Check:

1. Endpoint includes `bitrix:webservice.server` and correct `WEBSERVICE_NAME`/`WEBSERVICE_CLASS`.
2. Implementor class exists and is subclass of `IWebService`.
3. `GetWebServiceDesc()` returns valid `classes`, `structTypes`, `classTypes` arrays.
4. Request is POST and does not set `directcall`.
5. No unexpected output before SOAP response; component may call `RestartBuffer()`.
6. Auth method does not trigger HTTP Basic challenge for non-browser client unexpectedly.
7. SOAPAction namespace/method matches WSDL.

### `webservice.sale` returns zeros

Check:

1. Orders exist in the date windows used by the component.
2. User has sale rights and status view permissions.
3. Status bucket maps to expected date field (`DATE`, `DATE_PAYED`, `DATE_UPDATE`).
4. Currency/site branch; runtime-test `site_id` because current core has suspicious `$arFields['SITE_ID']` usage.
5. This component is aggregate-only; it will not list orders.

### `webservice.statistic` returns empty data

Check:

1. `statistic` module is installed and traffic/events are collected.
2. Statistic rights are not `D`.
3. `STAT_LIST_TOP_SIZE` is not too small.
4. Filters by `SITE_ID` do not exclude data.
5. Performance: legacy statistic tables can be large; avoid expensive SOAP polling.

### REST app event not delivered

Check:

1. `rest` module installed and event handlers registered.
2. App/token has required scope (`sale`, `catalog`, `pay_system`, `delivery`, `cashbox`).
3. `event.bind` exists in `b_rest_event` for exact event name and handler URL.
4. If offline delivery is used, inspect `b_rest_event_offline`, `event.offline.list/get/error`.
5. For sale events check import/delete duplicate suppression in `RestManager::processEvent()`.
6. For catalog events check the event-bind class actually implements exact event through `getHandlers()`.

### REST delivery/paysystem/cashbox app left stale handlers

Check:

1. `b_sale_pay_system_rest_handlers`, `b_sale_delivery_rest_handler`, `b_sale_cashbox_rest_handler`.
2. `rest.onRestAppDelete` fired with `CLEAN=true`.
3. The app client id matches stored handler `APP_ID`.
4. Existing sale services/cashboxes still reference handler code.
5. Do not delete rows directly unless no cleanup API works and user approved data mutation.

### Catalog REST list misses rows or repeats rows

Check:

1. `start` offset and `IRestService::LIST_LIMIT`.
2. Stable `order` and filter values.
3. Iblock/catalog rights for current REST user/app.
4. Product vs offer vs service type.
5. Price type rights and selected catalog group.
6. For large sync use `batch` carefully and check per-call errors.

## Safe implementation rules

- Prefer REST discovery (`methods`, `method.get`, `scope`) before hardcoding method names/signatures.
- For SOAP services, create explicit `IWebService` implementors and keep descriptors small; do not expose arbitrary classes through `WEBSERVICE_CLASS`.
- Do not put order CRUD into `webservice.sale`; use Sale API or sale REST controllers.
- Do not put 1С/CommerceML logic into `webservice`; use `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`.
- For external payments/deliveries/cashboxes, use REST handler APIs and preserve app cleanup semantics.
- For event handlers, make idempotency explicit; REST events can retry/offline queue and sale import can suppress duplicates.
- For public endpoints, enforce HTTPS, auth, scopes, CSRF/session where applicable, and avoid logging credentials/tokens.
- Avoid direct SQL writes to `b_rest_*`, `b_sale_*_rest_handler`, order/payment/shipment/product/price/store tables unless no API exists and user explicitly approves data mutation.

## What not to do

- Do not claim `webservice.sale` is a separate module or a full sale API.
- Do not claim `webservice.statistic` provides order analytics.
- Do not confuse B24 sale integration with 1С CommerceML exchange.
- Do not expose `webservice.checkauth` or test SOAP endpoints without access/security review.
- Do not assume REST method names from memory; verify in the current core/runtime.
- Do not treat placement binding as data storage; it only embeds app UI/hooks.
