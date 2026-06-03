# Shop automation/bizproc — bizproc, bizprocdesigner, workflow, lists, pull

> Reference для Bitrix-скилла. Загружай, когда задача связана с автоматизацией интернет-магазина/контента: бизнес-процессы, роботы, шаблоны workflow, задания БП, запуск/остановка workflows, процессы в списках, legacy `workflow`, realtime/pull, designer/editor, REST automation или когда пользователь спрашивает, покрыты ли automation modules shop-core.

## Audit note

Проверено по shop-core:

- `www/bitrix/modules/bizproc` — `26.200.0`, `VERSION_DATE` `2026-01-16 16:33:00`
- `www/bitrix/modules/bizprocdesigner` — `26.0.0`, `VERSION_DATE` `2025-12-05 12:00:00`
- `www/bitrix/modules/workflow` — `26.0.0`, `VERSION_DATE` `2026-03-18 14:30:00`
- `www/bitrix/modules/lists` — `25.600.100`, `VERSION_DATE` `2026-02-27 11:09:11`
- `www/bitrix/modules/pull` — `25.300.0`, `VERSION_DATE` `2025-06-25 09:30:00`
- adjacent facts checked in `iblock`, `catalog`, `sale` only for routing/side effects.

Ниже — подтверждённый routing/contract layer. Для корзины/заказов читай `sale.md`; для товарных данных — `catalog.md`; для стандартных shop components — `shop-standard-components.md`; для REST — `rest.md`; для realtime общих деталей — `push-pull.md`.

## Главный вывод

Automation в текущем shop-core — это несколько разных подсистем:

1. `bizproc` — современный workflow engine: templates, states/instances, tasks, tracking, history, automation robots/triggers, scripts, debugger, globals, REST activities/providers.
2. `bizprocdesigner` — UI/editor layer для редактирования workflow templates и роботов; сам runtime не заменяет.
3. `workflow` — legacy документооборот файлов/страниц со статусами, lock/history/preview, admin UI и cleanup agent.
4. `lists` — процессы и списки поверх `iblock` + `bizproc`: list elements, process catalog, livefeed/user processes, rights, REST list CRUD.
5. `pull` — realtime/push transport: channels, stack, watches, push queue, REST and JS client; используется как зависимость UI/notifications, а не как workflow engine.

Критично:

- `workflow` и `bizproc` — разные механизмы; `iblock` запрещает одновременно `WORKFLOW=Y` и `BIZPROC=Y`.
- `bizprocdesigner` нужен для редактора, но не исполняет процессы сам.
- `lists` запускает БП через `BizprocDocument*` над iblock/list element, а не через `sale` order API.
- В проверенном `sale` модуле нет отдельного sale-order business-process document provider уровня `CBPDocument` для заказов; не обещай “роботов заказа” без проверки CRM/проектного модуля.
- `pull` не чинит бизнес-логику БП; он чинит доставку realtime-событий, counters, watches и push.

## Fast routing

| Запрос | Сначала читать | Затем |
|---|---|---|
| “Бизнес-процесс не стартует” | `bizproc` sections below | `iblocks.md`, `lists` section, permissions |
| “Робот/automation не срабатывает” | `bizproc.automation` below | template status, triggers, `b_bp_automation_trigger`, logs |
| “Задание БП висит / нельзя выполнить” | `bizproc.task*` below | `b_bp_task`, `b_bp_task_user`, permissions/delegation |
| “Шаблон не сохраняется в дизайнере” | `bizprocdesigner` below | `bizproc.workflow.edit`, sessid, rights, template table |
| “Процессы в списках не работают” | `lists` below | `iblock` BIZPROC flag, `CLists::isBpFeatureEnabled`, list rights |
| “Legacy workflow страницы/файлы” | `workflow` below | `fileman`, status/group rights, cleanup/history options |
| “Realtime не пришёл / счетчик не обновился” | `pull` below | `push-pull.md`, pull server config, watches/channels |
| “Нужна автоматизация заказа” | сначала `sale.md`, затем этот файл | не обещать sale robots без локального provider-а |

## Component inventory

### `bizproc` components — 49

Families:

- automation/debugger: `bizproc.automation`, `bizproc.automation.robot.button`, `bizproc.automation.scheme`, `bizproc.debugger*`;
- documents/history/log: `bizproc.document`, `bizproc.document.history`, `bizproc.log`, `bizproc.workflow.timeline.slider`;
- workflow start/list/instances/faces/info: `bizproc.workflow.*`;
- tasks: `bizproc.task`, `bizproc.task.list`;
- scripts: `bizproc.script.*`;
- storage/global fields: `bizproc.storage.*`, `bizproc.globalfield.*`;
- process wizard/user processes: `bizproc.template.processes`, `bizproc.user.processes*`, `bizproc.wizards*`;
- UI helpers: `bizproc.interface.filter`, `bizproc.interface.grid`.

Exhaustive list confirmed:

`bizproc.ai.agents`, `bizproc.automation`, `bizproc.automation.robot.button`, `bizproc.automation.scheme`, `bizproc.debugger`, `bizproc.debugger.log`, `bizproc.debugger.session.list`, `bizproc.debugger.start`, `bizproc.document`, `bizproc.document.history`, `bizproc.globalfield.edit`, `bizproc.globalfield.list`, `bizproc.interface.filter`, `bizproc.interface.grid`, `bizproc.log`, `bizproc.script.edit`, `bizproc.script.list`, `bizproc.script.placement`, `bizproc.script.queue.document.list`, `bizproc.script.queue.list`, `bizproc.storage.edit`, `bizproc.storage.field.edit`, `bizproc.storage.field.list`, `bizproc.storage.item.list`, `bizproc.task`, `bizproc.task.list`, `bizproc.template.processes`, `bizproc.user.processes`, `bizproc.user.processes.start`, `bizproc.wizards`, `bizproc.wizards.index`, `bizproc.wizards.list`, `bizproc.wizards.log`, `bizproc.wizards.new`, `bizproc.wizards.setvar`, `bizproc.wizards.start`, `bizproc.wizards.task`, `bizproc.wizards.view`, `bizproc.workflow.faces`, `bizproc.workflow.info`, `bizproc.workflow.instances`, `bizproc.workflow.list`, `bizproc.workflow.livefeed`, `bizproc.workflow.setconstants`, `bizproc.workflow.setparameters`, `bizproc.workflow.setvar`, `bizproc.workflow.start`, `bizproc.workflow.start.list`, `bizproc.workflow.timeline.slider`.

### `bizprocdesigner` components — 2

- `bizproc.workflow.edit` — legacy/compatible workflow template editor wrapper.
- `bizprocdesigner.editor` — modern designer/editor component.

### `lists` components — 19

`lists`, `lists.catalog.processes`, `lists.element.attached.crm`, `lists.element.creation_guide`, `lists.element.edit`, `lists.element.navchain`, `lists.element.preview`, `lists.export.excel`, `lists.field.edit`, `lists.fields`, `lists.file`, `lists.list`, `lists.list.edit`, `lists.lists`, `lists.live.feed`, `lists.lock.status.widget`, `lists.menu`, `lists.sections`, `lists.user.processes`.

### `workflow` components — 0

Legacy module exposes admin pages and `CWorkflow*` API, not public components.

### `pull` components — 1

`pull.request` — AJAX/long-poll request component/init endpoint.

## DB/table layer

### `bizproc`

Core workflow tables:

- templates: `b_bp_workflow_template`, `b_bp_workflow_template_settings`, `b_bp_workflow_template_user_option`, `b_bp_document_type_user_option`, `b_bp_workflow_template_draft`, `b_bp_workflow_template_trigger`, `b_bp_workflow_template_section`, `b_bp_workflow_template_file`;
- runtime state/instances: `b_bp_workflow_state`, `b_bp_workflow_instance`, `b_bp_workflow_state_identify`, `b_bp_workflow_meta`, `b_bp_workflow_filter`, `b_bp_workflow_duration_stat`, `b_bp_workflow_user`, `b_bp_workflow_user_comment`, `b_bp_workflow_result`;
- tasks/search/archive: `b_bp_task`, `b_bp_task_user`, `b_bp_task_search_content`, `b_bp_task_archive`, `b_bp_task_archive_tasks`;
- tracking/history: `b_bp_tracking`, `b_bp_history`;
- REST and scheduler: `b_bp_rest_activity`, `b_bp_rest_provider`, `b_bp_scheduler_event`;
- automation/scripts/storage/debugger/globals: `b_bp_automation_trigger`, `b_bp_script`, `b_bp_script_queue`, `b_bp_script_queue_document`, `b_bp_storage_activity`, `b_bp_storage_type`, `b_bp_storage_field`, `b_bp_storage_record_data`, `b_bp_global_const`, `b_bp_global_var`, `b_bp_debugger_session*`, `b_bp_robot_version_index`, `b_bp_messenger_workflow_start_message`.

Confirmed DataManagers include:

- `WorkflowTemplateTable`, `WorkflowTemplateDraftTable`, `WorkflowTemplateTriggerTable`, `WorkflowTemplateSettingsTable`, `WorkflowTemplateUserOptionTable`, `WorkflowTemplateSectionTable`, `WorkflowTemplateFileTable`;
- `WorkflowStateTable`, `WorkflowInstanceTable`, `WorkflowMetadataTable`, `WorkflowFilterTable`, `WorkflowDurationStatTable`, `WorkflowUserTable`, `WorkflowUserCommentTable`, `ResultTable`;
- `TaskTable`, `TaskUserTable`, `TaskSearchContentTable`, `TaskArchiveTable`, `TaskArchiveTasksTable`;
- `TrackingTable`, `SchedulerEventTable`, `RestActivityTable`, `RestProviderTable`, `TriggerTable`;
- `ScriptTable`, `ScriptQueueTable`, `ScriptQueueDocumentTable`;
- `GlobalConstTable`, `GlobalVarTable`, `ActivityStorageTable`, `StorageTypeTable`, `StorageFieldTable`, `StorageRecordTable`;
- debugger session tables and `RobotVersionIndexTable`.

### `workflow`

Tables:

- `b_workflow_document` — document path/status/lock/body metadata;
- `b_workflow_file` — attached/temp files;
- `b_workflow_log` — document logs;
- `b_workflow_move` — move records;
- `b_workflow_preview` — preview files;
- `b_workflow_status` — statuses;
- `b_workflow_status2group` — status permissions by group.

Legacy APIs confirmed: `CWorkflow`, `CWorkflowStatus`.

### `lists`

Tables:

- `b_lists_permission` — iblock type permissions;
- `b_lists_field` — field settings per iblock/field;
- `b_lists_socnet_group` — socialnetwork group permissions;
- `b_lists_url` — livefeed/list URL config.

The actual list data is still `iblock` data: iblocks, sections, elements, properties and rights. `lists` adds process/list wrappers, permissions, field settings and integrations.

### `pull`

Tables:

- `b_pull_stack` — queued events by channel;
- `b_pull_channel` — user/public channels;
- `b_pull_push` — device tokens/push registration;
- `b_pull_push_queue` — push queue;
- `b_pull_watch` — tag watches/subscriptions.

Confirmed DataManagers: `ChannelTable`, `PushTable`, `WatchTable`.

## Events, agents and options

### `bizproc`

Install registers:

- `iblock.OnAfterIBlockElementDelete` → `CBPVirtualDocument::OnAfterIBlockElementDelete`;
- `main.OnAdminInformerInsertItems` → `CBPAllTaskService::OnAdminInformerInsertItems`;
- REST: `OnRestServiceBuildDescription`, `OnRestAppDelete`, `OnRestAppUpdate` → `Bitrix\Bizproc\RestService`;
- `timeman.OnAfterTMDayStart` → `CBPDocument::onAfterTMDayStart`;
- REST app configuration handlers: import/export/clear/entity through `Bitrix\Bizproc\Integration\Rest\AppConfiguration`;
- `im.OnGetNotifySchema` → `Bitrix\Bizproc\Integration\NotifySchema`;
- forum/socialnetwork comment listeners for workflow comments/views;
- intranet settings provider, CRM category delete guards, AI context messages.

Agents:

- `Bitrix\Bizproc\Infrastructure\Agent\StorageCleanupAgent::runAgent();` daily;
- `Bitrix\Bizproc\Install\Agent\CreateRobotVersionIndex::run();` after install, interval 60;
- options UI can add/remove `CBPTrackingService::ClearOldAgent();`, `Bitrix\Bizproc\Worker\Workflow\ClearFilterAgent::getName()`, `Bitrix\Bizproc\Worker\Task\ClearSearchContentAgent::getName()`.

Options confirmed:

- `SkipNonPublicCustomTypes=Y` on install;
- `log_cleanup_days` default `90`;
- `search_cleanup_days`;
- `employee_compatible_mode`;
- `limit_simultaneous_processes`;
- `limit_while_iterations` default `1000`;
- `log_skip_types`;
- `automation_no_forced_tracking`;
- `enable_getdocument_select`;
- `storage_items_cleanup_days` default `90`;
- `storage_item_data_limit` default `1`;
- `use_gzip_compression`;
- `locked_wi_path`;
- per-site `name_template`.

### `bizprocdesigner`

Install registers:

- `pull.OnGetDependentModule` → `Bitrix\BizprocDesigner\Internal\Integration\Pull\BizprocDesignerPullManager::OnGetDependentModule`;
- `main.OnAfterRegisterModule` → module/service setup handler.

It copies admin/tools/components/js. It has no DB tables of its own in this core.

### `workflow`

Install registers:

- `main.OnPanelCreate` → `CWorkflow::OnPanelCreate`;
- `main.OnChangeFile` → `CWorkflow::OnChangeFile`.

Agent:

- `CWorkflow::CleanUp();`

Options confirmed:

- `USE_HTML_EDIT` default `Y`;
- `HISTORY_SIMPLE_EDITING` default `N`;
- `MAX_LOCK_TIME` default `60`;
- `DAYS_AFTER_PUBLISHING` default `0`;
- `HISTORY_COPIES` default `10`;
- `HISTORY_DAYS` default `-1`;
- `WORKFLOW_ADMIN_GROUP_ID`.

### `lists`

Install registers:

- `iblock.OnAfterIBlockUpdate`, `OnIBlockDelete`, `OnAfterIBlockDelete` → `CLists` cleanup/sync;
- `iblock.CIBlockDocument_OnGetDocumentAdminPage` → `CList::OnGetDocumentAdminPage`;
- `iblock.OnAfterIBlockElementDelete`, property add/update/delete and before element add/update hooks;
- `intranet.OnSharepointCreateProperty`, `OnSharepointCheckAccess`;
- `perfmon.OnGetTableSchema`;
- `search.OnSearchGetURL`;
- socialnetwork livefeed/comment/mention/group handlers;
- REST: `onRestServiceBuildDescription` → `Bitrix\Lists\Rest\RestService`;
- `main.OnGetRatingContentOwner`;
- `socialnetwork.onLogIndexGetContent`;
- `im.OnGetNotifySchema`.

Install also runs `Bitrix\Lists\Importer::installProcesses($defaultLang)` and sets `lists.livefeed_url=/bizproc/processes/`.

Options/defaults:

- `socnet_iblock_type_id` default empty;
- `livefeed_url` default `/bizproc/processes/`;
- `livefeed_iblock_type_id` default `bitrix_processes`.

### `pull`

Install registers:

- `main.OnBeforeProlog` → `/modules/pull/ajax_hit_before.php`;
- `main.OnProlog` → `/modules/pull/ajax_hit.php` and `CPullOptions::OnProlog`;
- `main.OnEpilog` → `CPullOptions::OnEpilog`;
- `main.OnAfterEpilog` → `Bitrix\Pull\Event::onAfterEpilog` and `CPullWatch::DeferredSql`;
- `perfmon.OnGetTableSchema`;
- `main.OnAfterRegisterModule`, `OnAfterUnRegisterModule` → `CPullOptions::ClearCheckCache`;
- `socialnetwork.OnSonetLogCounterClear` → `Bitrix\Pull\MobileCounter`;
- REST: `OnRestServiceBuildDescription`, `onRestCheckAuth`.

Agent:

- `CPullOptions::ClearAgent();` every 30 seconds.

Default options include listener/websocket/publish URLs, `push=Y`, `guest=Y`, `push_message_per_hit=100`, `websocket=Y`, `server_mode=personal`, signature/config timestamps and shared-server settings. `bitrix/php_interface/pull.php` can override defaults.

## Standard component contracts

### `bizproc.automation`

Confirmed params:

- `DOCUMENT_TYPE` complex document type array;
- `DOCUMENT_ID`;
- `DOCUMENT_CATEGORY_ID`;
- `STATUSES_EDIT_URL`;
- `WORKFLOW_EDIT_URL`;
- `CONSTANTS_EDIT_URL`;
- `PARAMETERS_EDIT_URL`;
- `TITLE_VIEW`, `TITLE_EDIT`;
- `API_MODE=Y`;
- `ONE_TEMPLATE_MODE`;
- `TEMPLATE`;
- `IS_TEMPLATES_SCHEME_SUPPORTED`;
- `ACTION=ROBOT_SETTINGS`, `~ROBOT_DATA`, `~CONTEXT_ROBOTS`, `~CONTEXT`.

Behavior:

- requires `bizproc`;
- signs document type/id/category for AJAX;
- returns document fields/user groups/name/statuses/templates/triggers/global variables/log;
- AJAX requires authorized user, POST and `check_bitrix_sessid()`;
- AJAX actions include robot settings and `UPDATE_TEMPLATES`;
- template save goes through `Bitrix\Bizproc\Automation\Engine\Template::save()`.

Gotcha: UI success does not prove runtime start. For runtime check `b_bp_workflow_template`, `b_bp_automation_trigger`, `b_bp_workflow_instance/state`, tracking log and target document type/status.

### `bizproc.workflow.start`

Confirmed params/request:

- `MODULE_ID`, `ENTITY`, `DOCUMENT_TYPE`, `DOCUMENT_ID`;
- `SIGNED_DOCUMENT_TYPE`, `SIGNED_DOCUMENT_ID`;
- `TEMPLATE_ID` / request `workflow_template_id`;
- `AUTO_EXECUTE_TYPE`;
- `ACTION`;
- `SET_TITLE` default `Y`.

Behavior:

- requires `bizproc`;
- unsigned signed document type/id when provided;
- checks `CBPDocument::CanUserOperateDocument` or `CanUserOperateDocumentType` for start;
- loads templates through `CBPDocument::getTemplatesForStart()` / `CBPWorkflowTemplateLoader`;
- validates parameters via `CBPWorkflowTemplateLoader::CheckWorkflowParameters()` / `CBPDocument::StartWorkflowParametersValidate()`;
- starts through `CBPDocument::StartWorkflow()`;
- AJAX actions include `GET_TEMPLATES`, `START_WORKFLOW`, `CHECK_PARAMETERS` and require `check_bitrix_sessid()`.

### `bizproc.task` and `bizproc.task.list`

`bizproc.task`:

- requires `bizproc` and `iblock`;
- params/request: `TASK_ID`, `task_id`, `WORKFLOW_ID`, `DOCUMENT_ID`, `USER_ID`, `TASK_EDIT_URL`, `SET_TITLE`, `SET_NAV_CHAIN`, `POPUP`;
- loads task via `CBPTaskService::GetList()` with `TASK_ID` + `USER_ID`, or by workflow ID and waiting status;
- supports read-only mode for subordinate/admin views;
- comments AJAX requires authorized user, sessid and `bizproc`.

`bizproc.task.list`:

- params: `USER_ID`, `WORKFLOW_ID`, `TASK_EDIT_URL`, `PAGE_ELEMENTS` default `50`, `PAGE_NAVIGATION_TEMPLATE`, `SHOW_TRACKING`, `SET_TITLE`, `SET_NAV_CHAIN`, `COUNTERS_ONLY`;
- grid IDs: `bizproc_task_list`, filter `bizproc_task_list_filter`;
- uses `CGridOptions`, filter/grid columns and task/tracking arrays.

For task bugs check `b_bp_task`, `b_bp_task_user`, `USER_STATUS`, task member, delegation type, workflow state and comments forum binding.

### `bizproc.log` / `bizproc.workflow.instances`

`bizproc.log`:

- params: `ID`/`WORKFLOW_ID`, `COMPONENT_VERSION=2`, `SET_TITLE`, `INLINE_MODE`, `AJAX_MODE`, `NAME_TEMPLATE`, `SET_ADMIN_MODE`;
- checks `CBPStateService::GetWorkflowState()`;
- checks `CBPDocument::CanUserOperateDocument(ViewWorkflow)`;
- grid id includes workflow template id;
- reads tracking by `WORKFLOW_ID` and can show admin details.

`bizproc.workflow.instances`:

- grid id `bizproc_instances`;
- filters by document type group (`*`, `is_locked`, `processes`, `crm`, `disk`, `iblock`) and module/entity/document id;
- uses `Grid\Options`, `Filter\Options`, D7 `PageNavigation`;
- source is `WorkflowInstanceTable` / workflow state joins.

### `bizproc.workflow.edit` / `bizprocdesigner.editor`

`bizproc.workflow.edit`:

- requires `bizproc` + `bizprocdesigner`;
- params: `MODULE_ID`, `ENTITY`, `DOCUMENT_TYPE`, `ID`, `LIST_PAGE_URL`, `EDIT_PAGE_TEMPLATE`, `BACK_URL`;
- loads template from `WorkflowTemplateTable` by ID;
- checks `CBPDocument::CanUserOperateDocumentType` and document type equality;
- save/import/export actions require `check_bitrix_sessid()`;
- save fields include `AUTO_EXECUTE`, `NAME`, `DESCRIPTION`, `TEMPLATE`, `PARAMETERS`, `VARIABLES`, `CONSTANTS`.

`bizprocdesigner.editor`:

- modern editor component;
- derives complex document type from params or template ID;
- checks limits/access before rendering;
- can fill `START_TRIGGER`;
- uses activity searcher from ServiceLocator.

### `bizproc.script.*` and storage components

`bizproc.script.list`:

- takes `DOCUMENT_TYPE_SIGNED`, unsigns to `DOCUMENT_TYPE`;
- grid lists scripts for module/entity/document type through `Script\Manager` and `ScriptTable`;
- uses D7 `PageNavigation` and checks `Manager::canUserCreateScript()`.

`bizproc.script.edit`:

- params `SCRIPT_ID`, `DOCUMENT_TYPE_SIGNED`, `PLACEMENT`, `SET_TITLE`;
- creates/loads scripts through `Bitrix\Bizproc\Script\Manager`;
- AJAX controller requires `bizproc`.

`bizproc.storage.item.list`:

- param/request `storageId`; optional `gridId`;
- requires `bizproc` and `ui` for filter features;
- uses `Storage\Service`, `PageNavigation`, `main.ui.grid` AJAX options;
- columns include `CODE`, `WORKFLOW_ID`, `DOCUMENT_ID`, `TEMPLATE_ID`, creator/date fields.

### `lists` router and process components

`lists` root component:

- routes SEF pages for list/list edit/sections/element/file plus bizproc pages;
- bizproc URL templates include `bizproc_workflow_start`, `bizproc_task`, `bizproc_workflow_admin`, `bizproc_workflow_edit`, `bizproc_workflow_vars`, `bizproc_workflow_constants`;
- stores livefeed URL option when `IBLOCK_TYPE_ID` matches `lists.livefeed_iblock_type_id`;
- if `document_state_id` is present, resolves element ID from `CBPStateService::GetWorkflowState()`.

`lists.list`:

- checks list rights through `CListPermissions` and `CList`;
- detects `PROCESSES` when iblock type equals `lists.livefeed_iblock_type_id`;
- enables bizproc controls when iblock `BIZPROC=Y`, module `bizproc` exists and `CLists::isBpFeatureEnabled()`;
- grid IDs: `lists_list_elements_<IBLOCK_ID>`, filter same;
- AJAX controller uses `main` Engine Controller and action query param.

`lists.element.edit`:

- uses `ElementRight`/`RightParam` services for access;
- detects bizproc with `Loader::includeModule('bizproc')`, `CLists::isBpFeatureEnabled()`, iblock `BIZPROC != N`;
- AJAX actions check `bizproc` before template/process operations;
- routes task/workflow URLs through params such as `BIZPROC_WORKFLOW_START_URL`, `BIZPROC_TASK_URL`, `BIZPROC_LOG_URL`.

`lists.user.processes`:

- uses `lists.livefeed_iblock_type_id`;
- requires `bizproc` and `CLists::isBpFeatureEnabled()`;
- grid/filter `lists_processes`;
- lists elements created by user and attaches current workflow state/comments counts.

### `pull.request`

- if request `AJAX_CALL=Y`, component returns early;
- otherwise may define `BX_PULL_SKIP_INIT` and include template unless `TEMPLATE_HIDE=Y`;
- AJAX init defines `PULL_AJAX_INIT`, `PUBLIC_AJAX_MODE`, `NO_AGENT_STATISTIC`, `DisableEventsCheck`;
- returns `BITRIX_SESSID` on auth/session errors;
- requires valid session for normal pull request handling.

## REST surface

### `bizproc` REST

Confirmed REST methods:

- activities/robots/providers: `bizproc.activity.add/update/delete/log/list`, `bizproc.robot.add/update/delete/list`, `bizproc.provider.add/delete/list`;
- events: `bizproc.event.send`;
- tasks: `bizproc.task.list`, `bizproc.task.complete`, `bizproc.task.delegate`;
- workflows: `bizproc.workflow.start`, `bizproc.workflow.terminate`, `bizproc.workflow.kill`, `bizproc.workflow.instance.list`, alias `bizproc.workflow.instances`;
- templates: `bizproc.workflow.template.list/add/update/delete`;
- placement: activity properties dialog.

REST app delete/update cleans `RestActivityTable` / `RestProviderTable` entries for app client id.

### `lists` REST

Confirmed methods:

- `lists.get.iblock.type.id`;
- `lists.add/get/update/delete`;
- `lists.section.add/get/update/delete`;
- `lists.field.add/get/update/delete`, `lists.field.type.get`;
- `lists.element.add/get/update/delete`, `lists.element.get.file.url`.

REST code applies list/section/element rights via `RightParam`, `IblockRight`, `ElementRight` and exposes `ERROR_BIZPROC` for workflow-dependent failures.

### `pull` REST

Confirmed methods:

- app/channel/events: `pull.application.config.get`, `pull.application.event.add`, `pull.application.push.add`, `pull.watch.extend`;
- channels: `pull.config.get`, `pull.channel.public.get`, `pull.channel.public.list`;
- mobile counters/push config/status methods.

REST throws `SERVER_ERROR` when Pull server is not configured and restricts some methods to app authorization/admin.

## Shop/commerce integration notes

### Sale/order automation

In checked `sale` 26.0.0, direct `bizproc` references are mostly module-packaging / CRM site master dependency metadata, not a confirmed order workflow document provider. Therefore:

- for order lifecycle changes use `sale.md` events/API first;
- if user wants “order robots”, verify local modules/project first: CRM, custom module, or provider implementing `IBPWorkflowDocument`/document type for orders;
- do not create “robots for orders” by writing to `b_bp_*` manually.

### Catalog/iblock/list automation

Confirmed adjacent layer:

- `iblock` has `CIBlockDocument implements IBPWorkflowDocument` and `BIZPROC` flag;
- `iblock` prevents `WORKFLOW=Y` and `BIZPROC=Y` together;
- `catalog` product grid uses `Iblock\Grid\Column\BusinessProcessProvider` for BP columns;
- `lists` wraps iblock elements as process documents through `BizprocDocument` and `BizprocDocumentLists`.

For product/content automation, first determine document type:

- plain iblock element: `['iblock', 'CIBlockDocument', 'iblock_<IBLOCK_ID>']` / document id with element;
- lists process: `lists` `BizprocDocument`/`BizprocDocumentLists` generated complex type;
- custom module: inspect provider/entity class.

## Diagnostics by symptom

### Workflow does not start

Check:

1. Module exists: `bizproc`; for editor also `bizprocdesigner`.
2. Correct complex document type: module/entity/document type and document id.
3. Template active and `AUTO_EXECUTE` matches manual/create/update/event/script scenario.
4. `CBPDocument::CanUserOperateDocument(Type)` grants start.
5. Required parameters/constants are set.
6. `CBPWorkflowTemplateLoader::CheckWorkflowParameters()` errors.
7. `b_bp_workflow_template`, `b_bp_workflow_state`, `b_bp_workflow_instance`.
8. Tracking/log through `bizproc.log` / `b_bp_tracking`.
9. Limit options: simultaneous processes, while iterations.

### Robot or trigger does not fire

Check:

1. Target document type/category/status passed to `bizproc.automation`.
2. Template exists for expected `DOCUMENT_STATUS`.
3. Trigger rows in `b_bp_automation_trigger` and `b_bp_workflow_template_trigger`.
4. Runtime target handler supports this document/status.
5. Conditions/delays in robot template.
6. Tracking can be skipped by `automation_no_forced_tracking` / `log_skip_types`.
7. If UI changes were made through AJAX, verify sessid and `UPDATE_TEMPLATES` result.

### Task is stuck or user cannot complete it

Check:

1. `b_bp_task` row and `b_bp_task_user` membership.
2. `USER_STATUS` and task status are waiting, not already done.
3. Current user vs `USER_ID`; subordinate/admin view may be read-only.
4. Delegation type and target user.
5. Workflow state exists and is not terminated/locked unexpectedly.
6. Comments/forum integration only affects discussion, not task completion.
7. Use `TaskService::doTask()` / `CBPTaskService` APIs, not direct SQL.

### Designer cannot save template

Check:

1. `bizprocdesigner` installed and component `bizproc.workflow.edit`/`bizprocdesigner.editor` exists.
2. User can operate document type.
3. `MODULE_ID`, `ENTITY`, `DOCUMENT_TYPE` match the template row.
4. POST has valid sessid.
5. Template payload has `TEMPLATE`, `PARAMETERS`, `VARIABLES`, `CONSTANTS` arrays.
6. Check `b_bp_workflow_template`, draft/settings tables and PHP errors from activity validation.
7. If realtime editor state is broken, then check `pull` dependency, but not before access/template errors.

### Lists process is missing or cannot start

Check:

1. `lists` + `iblock` + `bizproc` modules exist.
2. Iblock type and iblock id; list data is still iblock data.
3. Iblock `BIZPROC=Y` and not legacy `WORKFLOW=Y`.
4. `CLists::isBpFeatureEnabled($IBLOCK_TYPE_ID)`.
5. User rights via `CListPermissions`, `ElementRight`, `RightParam`.
6. Component routes for `bizproc_workflow_start`, `bizproc_task`, `bizproc_workflow_admin`, `bizproc_workflow_edit`.
7. Template auto-start on create/update if livefeed/process action expects auto-start.

### Legacy workflow blocks file/page edits

Check:

1. Is module `workflow` really used, not `bizproc`?
2. File path/document row in `b_workflow_document`.
3. Status in `b_workflow_status` and group rights in `b_workflow_status2group`.
4. Lock timeout `MAX_LOCK_TIME` and locked user.
5. Cleanup/history options: copies/days/after publishing.
6. `CWorkflow::OnChangeFile` and admin panel hooks.
7. `fileman` editor behavior if `USE_HTML_EDIT=Y`.

### Pull/realtime updates do not arrive

Check:

1. `pull` module installed and event handlers registered.
2. Pull server status/mode/config URL options.
3. `CPullOptions::ClearAgent();` runs.
4. Channel exists in `b_pull_channel`; events in `b_pull_stack`.
5. Watch tag in `b_pull_watch` if using watches.
6. JS client/template includes `pull.request` or modern pull extension.
7. REST app auth restrictions if events come from REST.
8. For general push/pull patterns also open `push-pull.md`.

## Safe implementation rules

- Do not write `b_bp_*`, `b_workflow_*`, `b_lists_*`, `b_pull_*` directly unless no API exists and user approved data mutation.
- Use `CBPDocument`, `CBPWorkflowTemplateLoader`, `WorkflowService`, `TaskService`, `Script\Manager`, `CList`/`CLists`/rights services before SQL.
- For workflow starts always pass correct complex document type and target user parameters.
- For template edits preserve `PARAMETERS`, `VARIABLES`, `CONSTANTS`, `AUTO_EXECUTE`, document type and system code semantics.
- For list processes keep iblock rights/site/group constraints; list UI is not just a grid template.
- For `pull`, do not expose public channels or app push without auth checks and server config validation.
- For smoke tests do not start real customer/order side effects unless explicitly approved; use sandbox docs/list elements.

## What not to do

- Do not claim all shop order automation exists just because `bizproc` is installed.
- Do not confuse `workflow` legacy status workflow with `bizproc` templates/states/tasks.
- Do not fix automation by patching only component templates; check document type, template, runtime state, tasks and tracking.
- Do not use `pull` as a substitute for workflow state or task completion.
- Do not enable both `WORKFLOW` and `BIZPROC` for the same iblock.
- Do not activate automation route in another project until each target module exists locally.
