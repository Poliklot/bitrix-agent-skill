# Shop marketing/analytics — sender, mail, SMS, subscribe, ads, A/B, conversion, reports, statistic

> Reference для Bitrix-скилла. Загружай, когда задача связана с маркетингом интернет-магазина: рассылки, подписки, сегменты покупателей, follow-up, email/SMS sender, consent, opens/clicks, UTM, баннеры, A/B тесты, conversion counters, отчёты, legacy statistic или когда пользователь спрашивает, покрыты ли marketing/analytics modules shop-core.

## Audit note

Проверено по shop-core:

- `www/bitrix/modules/sender` — `26.0.0`
- `www/bitrix/modules/mail` — `26.100.200`
- `www/bitrix/modules/messageservice` — `25.200.100`
- `www/bitrix/modules/subscribe` — `25.0.0`
- `www/bitrix/modules/advertising` — `24.200.0`
- `www/bitrix/modules/abtest` — `26.0.0`
- `www/bitrix/modules/conversion` — `25.0.0`
- `www/bitrix/modules/report` — `25.100.0`
- `www/bitrix/modules/statistic` — `26.0.0`
- eShop wizard/public/template calls in `bitrix.eshop`
- sale-side marketing connectors: `sale/lib/senderconnector.php`, `sale/lib/bigdata/targetsalemailconnector.php`, sale statistic events

Ниже только подтверждённый routing/contract layer. Для корзины/заказов читай `sale.md`; для catalog product subscription — `catalog.md`; для стандартных shop components — `shop-standard-components.md`; для email/SMS общих уведомлений — `mail-notifications.md` и `messageservice.md`; для REST — `rest.md`.

## Главный вывод

Marketing/analytics в shop-core — это не один модуль.

Рабочий стек:

1. `sender` — современный marketing hub: contacts, segments, campaigns/letters, triggers, posting queue, opens/clicks, consent, UTM, stats.
2. `mail` — mailbox/client/sync/log layer и mail event read tracking side-channel.
3. `messageservice` — SMS/WA/message providers, queue, limits/restrictions, REST providers.
4. `subscribe` — legacy subscriptions/postings/rubrics; также отдаёт connector в `sender`.
5. `advertising` — banners/contracts, show/click dynamics, conversion counters.
6. `abtest` — site template/page rewrite A/B tests + conversion context attributes.
7. `conversion` — generic counters/attributes/rates/day context.
8. `report` — report builder/visual constructor and sharing.
9. `statistic` — legacy traffic/session/hit/event/advertising statistics; heavy runtime hooks.

Критично:
- `sender.subscribe` и `subscribe.*` — разные подсистемы;
- catalog product subscription (`b_catalog_subscribe`, option `sale.subscribe_prod`) не равно email marketing subscription;
- conversion/statistic/report не заменяют друг друга;
- для клиентского проекта каждый модуль подтверждай отдельно в `www/bitrix/modules/<module>`.

## Fast routing

| Запрос | Сначала читать | Затем |
|---|---|---|
| “Рассылка не отправляется” | `sender` section ниже | `mail-notifications.md`, agents/cron, `mail` logs |
| “Подписка с формы не работает” | `sender.subscribe` или `subscribe.form/edit` ниже | `userconsent.md`, `mail-notifications.md` |
| “Нужен сегмент покупателей” | `sender` + sale connectors below | `sale.md`, `shop-task-matrix.md` |
| “SMS не ушла / лимиты SMS” | `messageservice` section | `messageservice.md`, REST/provider config |
| “Баннер не показался / клики не считаются” | `advertising` section | `conversion`, cache/template, eShop public includes |
| “A/B тест не переключает шаблон/страницу” | `abtest` section | `conversion`, `templates.md`, `sef-urls.md` |
| “Конверсия пустая” | `conversion` section | `advertising`, `sender`, `abtest`, `sale/statistic` |
| “Отчёт не строится / пустой” | `report` section | helper class, rights, `sale_report_helper` |
| “Статистика тормозит сайт” | `statistic` section | agents cleanup, options, skip groups/IP |

## Component inventory

### `sender` components — 65

Families:

- campaigns/letters: `sender.campaign*`, `sender.letter*`, `sender.template*`;
- contacts/segments: `sender.contact*`, `sender.segment*`, `sender.connector.result.list`;
- triggers/return customer: `sender.trigger*`, `sender.rc*`;
- subscription/public: `sender.subscribe`, `sender.consent`;
- message editors/senders: `sender.mail.*`, `sender.sms.*`, `sender.im.message`, `sender.message.*`, `sender.call.*`;
- ads/toloka/yandex: `sender.ads*`, `sender.master.yandex`, `sender.yandex.toloka*`;
- config/UI/stat: `sender.config.*`, `sender.stats`, `sender.ui.*`, `sender.abuse.*`, `sender.blacklist.*`.

Exhaustive list confirmed:

`sender.abuse.list`, `sender.ads`, `sender.ads.list`, `sender.blacklist`, `sender.blacklist.list`, `sender.call.number`, `sender.call.text.editor`, `sender.campaign`, `sender.campaign.edit`, `sender.campaign.list`, `sender.campaign.selector`, `sender.campaign.stat`, `sender.config.limits`, `sender.config.role`, `sender.config.role.edit`, `sender.config.role.list`, `sender.connector.result.list`, `sender.consent`, `sender.contact`, `sender.contact.edit`, `sender.contact.import`, `sender.contact.list`, `sender.contact.recipient`, `sender.contact.set.list`, `sender.contact.set.selector`, `sender.im.message`, `sender.letter`, `sender.letter.edit`, `sender.letter.list`, `sender.letter.stat`, `sender.letter.time`, `sender.mail.editor`, `sender.mail.link.editor`, `sender.mail.sender`, `sender.master.yandex`, `sender.message.audio`, `sender.message.editor`, `sender.message.tester`, `sender.rc`, `sender.rc.list`, `sender.segment`, `sender.segment.edit`, `sender.segment.list`, `sender.segment.selector`, `sender.sms.sender`, `sender.sms.text.editor`, `sender.start`, `sender.stats`, `sender.subscribe`, `sender.template`, `sender.template.edit`, `sender.template.list`, `sender.template.selector`, `sender.trigger`, `sender.trigger.chain`, `sender.trigger.edit`, `sender.trigger.list`, `sender.trigger.stat`, `sender.ui.button.panel`, `sender.ui.panel.title`, `sender.ui.tile.selector`, `sender.ui.user.selector`, `sender.yandex.toloka`, `sender.yandex.toloka.edit`, `sender.yandex.toloka.list`.

### `mail` components — 18

`mail.addressbook`, `mail.blacklist.list`, `mail.client`, `mail.client.config`, `mail.client.config.dirs`, `mail.client.config.permissions`, `mail.client.home`, `mail.client.massconnect`, `mail.client.message.list`, `mail.client.message.new`, `mail.client.message.view`, `mail.client.sidepanel`, `mail.contact.avatar`, `mail.mailbox.list`, `mail.message.actions`, `mail.uf.message`, `mail.usersignature.edit`, `mail.usersignature.list`.

### `messageservice` components — 2

`messageservice.config.sender.limits`, `messageservice.config.sender.sms`.

### `subscribe` components — 5

`subscribe.edit`, `subscribe.form`, `subscribe.index`, `subscribe.news`, `subscribe.simple`.

### `advertising` components — 2

`advertising.banner`, `advertising.banner.view`.

### `report` components — 19

`report.analytics.base`, `report.analytics.config.control`, `report.analytics.empty`, `report.analytics.feedback`, `report.construct`, `report.filter.field.selector`, `report.list`, `report.view`, `report.visualconstructor.board.base`, `report.visualconstructor.board.controls`, `report.visualconstructor.board.filter`, `report.visualconstructor.board.header`, `report.visualconstructor.config.fields`, `report.visualconstructor.widget.content.grid`, `report.visualconstructor.widget.content.groupeddatagrid`, `report.visualconstructor.widget.content.number`, `report.visualconstructor.widget.content.numberblock`, `report.visualconstructor.widget.form`, `report.visualconstructor.widget.pseudoconfig`.

### No public components

`abtest` and `conversion` have no `install/components/bitrix/*` in this core; they work through admin pages, tables, event handlers and shared counters.

`statistic` has one public component: `statistic.table`.

## DB/table layer

### `sender`

Confirmed table families:

- contacts/lists/segments: `b_sender_contact`, `b_sender_contact_list`, `b_sender_list`, `b_sender_group`, `b_sender_group_connector`, `b_sender_group_data`, `b_sender_group_state`, `b_sender_group_queue`, `b_sender_group_thread`, `b_sender_group_counter`;
- campaigns/letters/messages: `b_sender_mailing`, `b_sender_mailing_chain`, `b_sender_mailing_chain_group`, `b_sender_mailing_group`, `b_sender_mailing_subscription`, `b_sender_mailing_trigger`, `b_sender_message`, `b_sender_message_field`, `b_sender_message_utm`;
- posting/runtime: `b_sender_posting`, `b_sender_posting_recipient`, `b_sender_posting_click`, `b_sender_posting_read`, `b_sender_posting_unsub`, `b_sender_posting_thread`, `b_sender_queue`, `b_sender_timeline_queue`;
- counters/abuse/consent/roles: `b_sender_counter`, `b_sender_counter_daily`, `b_sender_abuse`, `b_sender_agreement`, `b_sender_role*`, `b_sender_permission`;
- files/call log: `b_sender_file`, `b_sender_file_info`, `b_sender_call_log`.

Key DataManager classes confirmed: `ContactTable`, `ListTable`, `GroupTable`, `MailingTable`, `MailingChainTable`, `PostingTable`, `RecipientTable`, `ClickTable`, `ReadTable`, `UnsubTable`, `MessageTable`, `MessageUtmTable`, `TemplateTable`, `CounterTable`, `DailyCounterTable`, access role/permission tables.

### `mail`

Confirmed table families:

- mailboxes/messages: `b_mail_mailbox`, `b_mail_message`, `b_mail_message_uid`, `b_mail_msg_attachment`, `b_mail_mailbox_dir`, `b_mail_mailbox_list_search_index`;
- access/roles: `b_mail_access_role`, `b_mail_access_permission`, `b_mail_access_role_relation`, `b_mail_mailbox_access`, `b_mail_message_access`;
- sync/queues/logs: `b_mail_log`, `b_mail_message_delete_queue`, `b_mail_message_upload_queue`, `b_mail_counter`;
- contacts/settings: `b_mail_contact`, `b_mail_blacklist`, `b_mail_mailservices`, `b_mail_oauth`, `b_mail_user_signature`, `b_mail_user_message`, `b_mail_user_relations`, `b_mail_domain_email`, `b_mail_mass_connect`.

### `messageservice`

Tables: `b_messageservice_channel`, `b_messageservice_message`, `b_messageservice_incoming_message`, `b_messageservice_restriction`, `b_messageservice_template`, `b_messageservice_rest_app`, `b_messageservice_rest_app_lang`.

Options: `clean_up_period` default `14`, `queue_limit` default `5`. Install also sets `disable_international=Y` outside RU/BY regions.

### `subscribe`

Tables: `b_subscription`, `b_subscription_rubric`, `b_list_rubric`, `b_posting`, `b_posting_email`, `b_posting_file`, `b_posting_group`, `b_posting_rubric`.

DataManagers confirmed: `Bitrix\Subscribe\RubricTable`, `SubscriptionTable`. Legacy write path remains `CSubscription`, `CRubric`, `CPosting`, `CPostingTemplate`.

### `advertising`

Core tables include `b_adv_banner`, `b_adv_contract`, `b_adv_type`, plus relation/dynamics tables for sites/pages/country/day/weekday/stat advertising. Core fields on `b_adv_banner` include active/status, type, contract, weight, show/click/visitor limits and counters, date windows, image/code/url, stat event fields, user group and page restrictions.

### `abtest`

Table: `b_abtest`.

It stores test definition/state; switching is event-driven through main site template and file rewrite/page-start hooks.

### `conversion`

Tables: `b_conv_context`, `b_conv_context_attribute`, `b_conv_context_counter_day`, `b_conv_context_entity_item`.

This module stores day counters by context snapshot and attributes. Other modules register counter/rate/attribute handlers into it.

### `report`

Tables: `b_report`, `b_report_sharing`, `b_report_visual_report_dashboard`, `b_report_visual_report_dashboard_row`, `b_report_visual_report_widget`, `b_report_visual_report_widget_config`, `b_report_visual_report_entity`, `b_report_visual_report_entity_config`, `b_report_visual_report_configuration`.

`Bitrix\Report\ReportTable` maps `ID`, `OWNER_ID`, `TITLE`, `DESCRIPTION`, `CREATED_DATE`, `CREATED_BY`, `SETTINGS`, `MARK_DEFAULT`.

### `statistic`

Legacy `b_stat_*` layer: sessions, hits, guests, paths, events, adv, searchers, referers, phrases, city/country, stoplist and dynamic/day tables. This module is runtime-heavy and has many cleanup/optimization options.

## Event handlers and agents

### `sender` events/agents

Install registers:

- main mail tracking: `main.OnMailEventMailRead` → `postingmanager::onMailEventMailRead`, `main.OnMailEventMailClick` → `postingmanager::onMailEventMailClick`;
- subscription mail events: `OnMailEventSubscriptionDisable`, `OnMailEventSubscriptionEnable`, `OnMailEventSubscriptionList` → `Bitrix\Sender\Subscription`;
- sender extension points: `sender.OnConnectorList`, `sender.OnPresetTemplateList`, `sender.OnPresetMailBlockList`, `sender.OnTriggerList`;
- recipient/conversion: `sender.OnAfterRecipientUnsub`, `sender.OnAfterRecipientClick`, `conversion.OnSetDayContextAttributes`, `conversion.OnGetAttributeTypes`, `main.OnBeforeProlog` via `Bitrix\Sender\Internals\ConversionHandler`;
- optional integrations: `voximplant.OnInfoCallResult`, `pull.OnGetDependentModule`, `im.OnGetNotifySchema`, `main.OnAfterFileSave`.

Agents/stepper:

- `Bitrix\Sender\Access\Install\AccessInstaller::installAgent();`
- `Bitrix\Sender\Runtime\Job::actualizeAll();`
- `Bitrix\Sender\Trigger\Manager::activateAllHandlers();`
- `Bitrix\Sender\Install\SetFileInfoStepper`.

Key options:

- `auto_method`: `agent` / `cron`;
- `max_emails_per_hit`, `max_emails_per_cron` default `500`;
- `auto_agent_interval` default `0`;
- `track_mails` default depends on Bitrix24 region;
- `mail_consent`, `~mail_max_consent_requests`.

### `mail` events/agents

Install registers:

- `main.OnMailEventMailRead` → `Bitrix\Mail\Helper\MessageEventManager::onMailEventMailRead`;
- `mail.onMailMessageNew` → calendar ICal manager;
- `calendar.OnAfterCalendarEventDelete` → unbind event;
- `pull.OnGetDependentModule` → `MailPullSchema`;
- `tasks.OnTaskDelete` → secretary cleanup.

Agents:

- `CMailbox::CleanUp();` daily;
- `Bitrix\Mail\Access\Install\AccessInstaller::install();` after install.

Options include `save_src`, `save_attachments`, `sync_old_limit2`, `php_path` and SMTPD manager actions.

### `messageservice` events/agents

Install registers:

- `main.OnAfterEpilog` → `Bitrix\MessageService\Queue::run`;
- REST service descriptors/app lifecycle: `rest.OnRestServiceBuildDescription`, `OnRestAppDelete`, `OnRestAppUpdate`;
- `imconnector` delivery/read statuses for Wazzup.

Agents:

- `Bitrix\MessageService\Queue::cleanUpAgent();`
- `Bitrix\MessageService\IncomingMessage::cleanUpAgent();`

### `subscribe` events/agents

Install registers:

- `main.OnBeforeLangDelete` → `CRubric::OnBeforeLangDelete`;
- `main.OnUserDelete`, `main.OnUserLogout` → `CSubscription`;
- `main.OnGroupDelete` → `CPosting`;
- `sender.OnConnectorList` → `Bitrix\Subscribe\SenderEventHandler::onConnectorListSubscriber`;
- `perfmon.OnGetTableSchema`.

Options:

- `subscribe_section` default `#SITE_DIR#about/`;
- `subscribe_confirm_period` default `60`;
- `subscribe_auto_method`: `agent` / `cron`;
- `subscribe_max_emails_per_hit` default `5`;
- `subscribe_template_method`: `agent` / `cron`;
- `subscribe_template_interval` default `60`;
- `mail_additional_parameters`.

`options.php` manages `CPostingTemplate::Execute();` agent depending on template method.

### `advertising` events/agents

Install registers:

- `main.OnBeforeProlog` → module-level advertising init;
- `main.OnEndBufferContent` → `CAdvBanner::FixShowAll`;
- `main.OnBeforeRestartBuffer` → `CAdvBanner::BeforeRestartBuffer`;
- `conversion.OnGetCounterTypes`, `conversion.OnGetRateTypes` → `Bitrix\Advertising\Internals\ConversionHandlers`;
- `advertising.onBannerClick` → conversion handler.

Agents:

- `CAdvContract::SendInfo();` every 7200 seconds;
- `CAdvBanner::CleanUpDynamics();` daily.

Options: `BANNER_DAYS` default `360`, `COOKIE_DAYS` default `7`, upload subdir and cleanup callbacks.

### `abtest` events

Install registers:

- `main.OnGetCurrentSiteTemplate` → `Bitrix\ABTest\EventHandler::onGetCurrentSiteTemplate`;
- `main.OnFileRewrite` → `onFileRewrite`;
- `main.OnPageStart` → `onPageStart`;
- `main.OnPanelCreate` → `onPanelCreate`;
- `conversion.OnGetAttributeTypes` → `onGetAttributeTypes`;
- `conversion.OnSetDayContextAttributes` → `onConversionSetContextAttributes`.

No public components confirmed.

### `conversion` events

Install registers:

- self events: `OnGetCounterTypes`, `OnGetAttributeTypes`, `OnGetAttributeGroupTypes`, `OnSetDayContextAttributes`;
- `main.OnProlog` → `Bitrix\Conversion\Internals\Handlers::onProlog`.

Other modules (`sender`, `advertising`, `abtest`) plug into these events.

### `report` events

Install registers:

- `report.OnReportDelete` → `Bitrix\Report\Sharing::OnReportDelete`.

### `statistic` events/agents

Install registers:

- `main.OnPageStart` → `CStopList::Check`;
- `main.OnBeforeProlog` → `CStatistics::Keep` and `CStatistics::StartBuffer`;
- `main.OnLocalRedirect` → `CStatistics::Keep`;
- `main.OnEpilog` → `CStatistics::Set404`;
- `main.OnEndBufferContent` → `CStatistics::EndBuffer`;
- `main.OnEventLogGetAuditTypes` → audit types;
- `statistic.OnCityLookup` chain;
- `cluster.OnGetTableList`.

Agents:

- `CStatistics::SetNewDay();`
- `CStatistics::CleanUpStatistics_1();`
- `CStatistics::CleanUpStatistics_2();`
- `CStatistics::CleanUpSessionData();`
- `CStatistics::CleanUpPathCache();`
- optional `SendDailyStatistics();`.

Storage options include retention days for hits/sessions/guests/events/adv/searchers/referers/phrases/cities/countries, skip groups/IP ranges, defence thresholds and auto optimize.

## Standard component contracts

### `sender.subscribe`

Confirmed params:

- `AJAX_MODE`
- `USER_CONSENT`
- `USE_PERSONALIZATION` default `Y`
- `USE_CONFIRMATION` default `Y`
- `SET_TITLE` default `Y`
- `HIDE_MAILINGS` default `N`
- `SHOW_HIDDEN` default `N`
- `CACHE_TIME` default `3600`

Confirmed request/state:

- form action appends/removes `sender_subscription` query param;
- POST fields include `SENDER_SUBSCRIBE_EMAIL`, `SENDER_SUBSCRIBE_RUB_ID`;
- session key `SENDER_SUBSCRIBE_LIST` caches current subscription list;
- cookie `SENDER_SUBSCR_EMAIL` stores email;
- calls `Bitrix\Sender\Subscription::sendEventConfirm()` when confirmation is enabled and `Subscription::add()` when adding immediately;
- result message codes include security/email/success/confirm states.

Gotchas:

- `sender.subscribe` is not `subscribe.form`; it writes to sender contacts/mailings.
- `USER_CONSENT` can block form submission before sender code.
- If `HIDE_MAILINGS=Y`, user may not see selectable mailings but backend still needs active mailing list.
- Cache key is site/component-path dependent; stale rubrics/mailings can be cache, not DB.

### `sender.letter.list`, `sender.contact.list`, `sender.segment.list`, `sender.trigger.list`

These admin/list components are class-based and use `CommonSenderComponent`, `main.ui.grid`, `main.ui.filter`, `GridOptions`, `FilterOptions`, `PageNavigation`, AJAX endpoints and action rights from `Bitrix\Sender\Access\ActionDictionary`.

Confirmed list/action patterns:

- `sender.letter.list/ajax.php` can `send`, `pause`, `resume`, `stop`, `remove` letters through `Bitrix\Sender\Entity\Letter`;
- `sender.contact.list` exposes columns such as email/phone code, type, name, subscribed/unsubscribed, contact set, statistics, consent status;
- filters support subscribed/unsubscribed presets and contact set filtering;
- `sender.stats` uses `Bitrix\Sender\Statistics` for chain list, counters, dynamic counters and efficiency.

Gotchas:

- Do not patch only grid templates for delivery bugs; delivery state lives in posting/recipient queues and letter entity state.
- Pagination state can reset through component AJAX, e.g. letter removal resets `PageNavigation("page-sender-letters")` session var.

### `sender.config.limits`

Confirmed reads:

- `Option::get('sender', 'track_mails')`
- `Option::get('sender', 'mail_consent')`
- `Option::get('sender', 'sending_time')`
- `Option::get('sender', 'sending_start', '09:00')`
- `Option::get('sender', 'sending_end', '18:00')`

Use this component/config layer for send window and tracking/consent UI checks.

### `subscribe.form`

Confirmed params:

- `USE_PERSONALIZATION` default `Y`
- `PAGE` default `COption::GetOptionString('subscribe', 'subscribe_section') . 'subscr_edit.php'`
- `SHOW_HIDDEN` default `N`
- `CACHE_TIME` default `3600`

Confirmed behavior:

- checks `IsModuleInstalled('subscribe')` and includes `subscribe`;
- reads user's existing categories;
- builds `FORM_ACTION` from `PAGE`;
- request email field is `sf_EMAIL`;
- result has `EMAIL` and `RUBRICS`.

### `subscribe.edit`

Confirmed params:

- `AJAX_MODE`
- `SHOW_HIDDEN`
- `ALLOW_ANONYMOUS` from subscribe option;
- `SHOW_AUTH_LINKS` from subscribe option;
- `CACHE_TIME` default `3600`.

Confirmed behavior:

- works with `PostAction` `Add`/`Update`, `ID`, `EMAIL`, `FORMAT`, rubrics and `CONFIRM_CODE`;
- supports `action=unsubscribe` path;
- checks `CSubscription::IsAuthorized($ID)` for editing existing subscription.

### `advertising.banner`

Confirmed params:

- `TYPE` from advertising type list;
- `NOINDEX`;
- `QUANTITY` default `1`;
- `CACHE_TIME` default `0`;
- `DEFAULT_TEMPLATE` from component templates.

`advertising.banner.view` renders concrete banner payload with templates such as `bootstrap`, `bootstrap_v4`, `jssor`, `nivo`, `parallax`; templates check `PROPS.LINK_URL`, `CASUAL_PROPERTIES.URL`, preview mode and media fields.

### `statistic.table`

Confirmed params:

- `CACHE_TIME` default `20`;
- `CACHE_FOR_ADMIN` default `N`.

Confirmed behavior:

- disables cache for admin unless `CACHE_FOR_ADMIN=Y`;
- calls `CTraffic::GetCommonValues([], true)`;
- exposes `STATISTIC`, `TODAY`, `NOW`, `IS_ADMIN`.

### `report.list` / `report.view` / `report.construct`

Confirmed report list behavior:

- requires module `report`;
- expects `REPORT_HELPER_CLASS` (or POST `HELPER_CLASS`);
- calls helper `getOwnerId`;
- exports/imports report rows through `Bitrix\Report\ReportTable`;
- checks rights via `Bitrix\Report\RightsManager`;
- supports sharing through AJAX and `Bitrix\Report\Sharing`.

`report.construct` is a builder UI around selected columns, calculated columns, filters, sort, grouping, result limits, mobile settings and chart config. It is helper-class dependent; never assume a shop report helper exists until checking the caller.

## Shop/eShop integration points

### eShop wizard/public/templates

Confirmed in `bitrix.eshop`:

- public include `include/sender.php` uses `bitrix:sender.subscribe`;
- `sect_sidebar.php`, personal sidebar and template footers include `sender.php`;
- home/bottom public pages use `bitrix:advertising.banner` if `advertising` is installed;
- wizard services create advertising data through `site/services/advertising/index.php`;
- wizard temporarily reads/toggles statistic option `DEFENCE_ON`;
- wizard configures sale product subscription option `sale.subscribe_prod` and subscribe section `#SITE_DIR#personal/subscribe/`;
- subscribe templates are copied from `subscribe/install/php_interface/subscribe/templates/news` when `subscribe` is installed.

### Sale connectors into sender/statistic

Confirmed sale → sender:

- `Bitrix\Sale\SenderConnectorBuyer` extends `Bitrix\Sender\Connector`;
- connector code is `buyer`;
- filters buyers by site `LID`, order count range, paid sum range and last order date range;
- source data uses `BuyerStatistic::getList()` and returns user email/name/user id;
- `Bitrix\Sale\Bigdata\TargetSaleMailConnector` extends sender connector, code `target_sale`, selects products and potential consumers via sale bigdata cloud.

Confirmed sale → statistic:

- paid orders call `CStatEvent::AddByEvents("eStore", "order_paid", ...)`;
- chargeback/cancel flows call statistic events when `statistic` is installed;
- sale product search references `$_SESSION['SESS_SEARCHER_ID']` when statistic exists.

### Catalog/product subscription is separate

Catalog has `b_catalog_subscribe` / `b_catalog_subscribe_access` and product subscribe notifications (`CATALOG_PRODUCT_SUBSCRIBE_NOTIFY*`). Do not merge this with `sender.subscribe` or `subscribe.form`: it is product availability notification, not marketing mailing membership.

## Diagnostics by symptom

### Sender mailing does not send

Check in order:

1. Module exists and options: `auto_method`, `max_emails_per_hit`, `max_emails_per_cron`, `auto_agent_interval`.
2. If `auto_method=agent`, sender agents/runtime jobs exist and agents are executed.
3. If `auto_method=cron`, cron route is configured; do not expect per-hit sending.
4. Letter state in `b_sender_mailing_chain` / `Bitrix\Sender\Entity\Letter`.
5. Posting and recipients in `b_sender_posting`, `b_sender_posting_recipient`.
6. Consent/tracking options: `mail_consent`, `track_mails`, send window.
7. Main mail subsystem and mail event logs.
8. User/contact email validity and blacklist/abuse tables.

### Opens/clicks not tracked

Check:

- `sender.track_mails` option;
- main event handlers `OnMailEventMailRead`, `OnMailEventMailClick`;
- `b_sender_posting_read`, `b_sender_posting_click`;
- mail link editor/UTM settings (`b_sender_message_utm`);
- email clients/proxies can suppress or prefetch opens/clicks;
- consent option can disable tracking in some regions.

### Subscribe form submits but user not subscribed

First identify component:

- `bitrix:sender.subscribe` → sender contacts/mailings;
- `bitrix:subscribe.form` / `subscribe.edit` → legacy subscribe module;
- catalog product subscription → catalog/sale product availability.

For `sender.subscribe`:

1. `check_bitrix_sessid()` and `USER_CONSENT`;
2. valid `SENDER_SUBSCRIBE_EMAIL`;
3. selected/hidden mailing IDs in `SENDER_SUBSCRIBE_RUB_ID`;
4. `USE_CONFIRMATION`: user may be pending confirmation, not absent;
5. session `SENDER_SUBSCRIBE_LIST` and cache;
6. cookie `SENDER_SUBSCR_EMAIL` can prefill stale email.

For `subscribe.edit`:

1. `ALLOW_ANONYMOUS`, `SHOW_AUTH_LINKS`;
2. `CONFIRM_CODE` and `CSubscription::IsAuthorized()`;
3. `action=unsubscribe` or `PostAction=Add/Update`;
4. rubrics in `b_list_rubric` and `b_subscription_rubric`.

### SMS/message not sent

Check:

1. `messageservice` installed;
2. provider configured in `messageservice.config.sender.sms`;
3. queue runs on `main.OnAfterEpilog` (`Bitrix\MessageService\Queue::run`);
4. `queue_limit` option;
5. restrictions: per IP/user/phone limits in `b_messageservice_restriction`;
6. region option `disable_international`;
7. REST app/provider lifecycle if using REST provider;
8. cleanup agents should not remove fresh messages, but verify `clean_up_period`.

### Banner not shown

Check:

1. `advertising` module and `advertising.banner` component are present.
2. Component `TYPE` matches `b_adv_type.SID`.
3. Banner active/status, contract active, site/page/day/country/user group restrictions.
4. Date window and show/click/visitor limits.
5. Weight and `QUANTITY`.
6. Template selection and banner view template.
7. Cache: component default cache is `0`, but page/composite/template can still cache output.
8. Runtime hooks `OnBeforeProlog`, `OnEndBufferContent`, `OnBeforeRestartBuffer` are registered.

### Banner clicks/conversions not counted

Check:

- `FIX_CLICK`, `FIX_SHOW` flags on banner;
- advertising relation to statistic advertising if used;
- `advertising.onBannerClick` event;
- conversion handlers registered for counter/rate types;
- click URL/template does not bypass Bitrix banner click route.

### A/B test does not switch

Check:

1. `abtest` module and `b_abtest` test row.
2. Test enabled/state/site/template/page condition.
3. Event handlers: `OnGetCurrentSiteTemplate`, `OnFileRewrite`, `OnPageStart`.
4. Admin panel handler `OnPanelCreate` if UI state differs from runtime.
5. Conversion handlers for test attribution.
6. Template/page cache and SEF rewrite can hide switching.

### Conversion report empty

Check:

- `conversion` module exists and `main.OnProlog` handler runs;
- context attributes exist in `b_conv_context*`;
- module-specific handlers registered: advertising, sender, abtest;
- correct base currency if money rates matter;
- date range/day context;
- user/session/cookie context can be different in CLI/admin/public.

### Report list/view empty

Check:

1. `REPORT_HELPER_CLASS` passed and class exists.
2. Helper returns correct `OWNER_ID`.
3. `Bitrix\Report\ReportTable` rows in `b_report`.
4. Rights via `RightsManager`.
5. Sharing rows in `b_report_sharing`.
6. Visual constructor tables for dashboards/widgets.
7. Default reports may be created by helper/user option logic; do not assume static fixtures.

### Statistic slows site or writes too much

Check:

- `statistic` event handlers at `OnPageStart`, `OnBeforeProlog`, `OnEndBufferContent`;
- skip groups/IP ranges and `SKIP_STATISTIC_WHAT`;
- defence settings (`DEFENCE_ON`, `DEFENCE_MAX_STACK_HITS`, delays/log);
- retention days and cleanup agents;
- MySQL optimize/index options;
- stoplist and city lookup handlers;
- whether the project really needs legacy statistic instead of lighter analytics.

## Safe implementation rules

- Do not send real mail/SMS/calls in smoke tests without explicit user approval and sandbox recipients.
- Do not directly update `b_sender_*`, `b_subscription*`, `b_messageservice_*`, `b_adv_*`, `b_conv_*`, `b_report*`, `b_stat_*` unless there is no API and the user approved data mutation.
- For new shop segments, prefer sender connectors/services and sale APIs over SQL.
- For forms, keep `sessid`, consent and confirmation flow intact.
- For unsubscribe, never remove only UI state; update the real subscription/unsub tables through module API.
- For reports, do not invent helper classes: inspect existing helper/caller first.
- For statistic, be conservative: it has early runtime hooks and cleanup agents; changes can affect every public hit.

## What not to do

- Do not confuse `sender.subscribe`, `subscribe.form/edit` and catalog product subscription.
- Do not claim `conversion` is a full analytics system; it is a counter/context layer fed by modules.
- Do not claim `statistic` is harmless: it hooks into public request lifecycle and stores many hit/session tables.
- Do not debug sender delivery from template only; check letter/posting/recipient queue, agents/cron, consent and mail logs.
- Do not debug SMS only from sender UI; `messageservice` queue/providers/restrictions are a separate layer.
- Do not activate marketing/analytics route in another project until each target module exists locally.
