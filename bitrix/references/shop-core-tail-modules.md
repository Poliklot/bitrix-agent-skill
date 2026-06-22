# Shop-core tail modules: calendar, idea, learning, support, wiki, b24connector, landing, mobileapp

Открывай, когда задача касается оставшихся/смежных модулей shop-core или пользователь спрашивает “все ли модули интернет-магазина и 1С покрыты”. Этот файл закрывает code-first routing для модулей, которые не являются основным `catalog`/`sale`/`currency` runtime, но могут влиять на витрину, заявки, поддержку, обучение, лендинги, мобильный слой и внешние виджеты.

Граница: это **code-first audit**, не runtime pass. Для production-доказательств всё равно нужен [runtime-smoke-verification.md](runtime-smoke-verification.md).

## Быстрый вывод

| Модуль | Версия в shop-core | Роль | Статус после аудита | Что не обещать |
|---|---:|---|---|---|
| `calendar` | `25.170.0` | календарь, ресурсное бронирование, sharing, livefeed, sync | covered code-first | не считать частью checkout/order flow без локальной интеграции |
| `idea` | `25.0.0` | идеи/feedback, comments, subscribe, socialnetwork log | covered code-first | не считать CRM/lead/order engine |
| `learning` | `25.0.0` | курсы, уроки, тесты, gradebook, SCORM/import/export | covered code-first | не связывать с магазином без кастомного проекта |
| `support` | `26.0.0` | тикеты, SLA, словари, купоны, mail filter, reminder agents | covered code-first | не считать sale order support API |
| `wiki` | `25.0.0` | wiki/content/social discussion, diff, ratings/search | covered code-first | не считать knowledge base магазина без локального route |
| `b24connector` | `25.0.0` | виджеты, openlines, CRM forms, recall/chat/telephony binding | covered code-first | не считать локальным CRM или sale integration engine |
| `landing` | `26.200.0` | лендинги, blocks, domains, roles, catalog blocks, forms/cookies | covered code-first | не считать источником товаров/цен/остатков |
| `mobileapp` | `25.0.100` | mobile shell, designer, JN/native, push settings | covered code-first | не переносить sale mobile components из `sale` в `mobileapp` |

## Общий маршрут ответа

1. Проверить наличие модуля и версию.
2. Если задача про магазин — сначала понять, это реально shop flow или соседний UI/support/content layer.
3. Открыть локальные component/admin/lib/classes files по конкретной задаче.
4. Проверить зависимые модули: `socialnetwork`, `mail`, `pull`, `rest`, `iblock`, `catalog`, `sale`, `crm`, `im` — только если они есть локально.
5. Не переносить контракты из этих модулей на `sale/catalog` и наоборот.

```bash
for m in calendar idea learning support wiki b24connector landing mobileapp; do
  if test -f "www/bitrix/modules/$m/install/version.php"; then
    echo "--- $m ---"
    sed -n '1,60p' "www/bitrix/modules/$m/install/version.php"
    find "www/bitrix/modules/$m/install/components/bitrix" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sed 's#.*/##' | sort | head -80
  else
    echo "--- $m missing ---"
  fi
done
```

## `calendar` 25.170.0

### Surface

- Компоненты: `calendar.grid`, `calendar.events.list`, `calendar.view.slider`, `calendar.edit.slider`, `calendar.event.preview`, `calendar.event.simple.add`, `calendar.ical.mail`, `calendar.open-events`, `calendar.pub.event`, `calendar.pub.sharing`, `calendar.sharing.mail`, settings/sliders/grid variants.
- Admin: `calendar_convert.php`, task/operation descriptions.
- Legacy classes: `CCalendar`, `CCalendarEvent`, `CCalendarSect`, `CCalendarType`, `CCalendarPlanner`, `CCalendarNotify`, `CCalendarSync`, `CCalendarRestService`, `CCalendarWebservice`.
- D7/lib слой: `Bitrix\Calendar\Internals\EventTable`, `SectionTable`, `TypeTable`, `AccessTable`, `ResourceTable`, `LocationTable`, queue/sharing/open-event tables, controllers and services.
- Tables: `b_calendar_type`, `b_calendar_section`, `b_calendar_event`, `b_calendar_event_sect`, `b_calendar_access`, `b_calendar_resource`, `b_calendar_location`, `b_calendar_log`, sync/sharing/queue/open-event tables.

### Events/agents

- Интеграции: `pull` dependent module, `im` notifications/callbacks, `rest` service description, `socialnetwork` livefeed/comments, `search` indexing, `main` userfield/resource booking, `mail` iCal replies, `dav` sync, `iblock` department membership, `forum` comments.
- Agents: data sync, connection cleanup, Office365 sections, push watch renewal, exchange import, event queues, room cleanup, attendee updates, expired sharing links, email notification sender, log cleanup.

### Guardrails

- Для задач “в календаре не синхронизируется/не приходит приглашение” идти в sync/mail/agents/logs, а не в `sale`.
- Для resource booking проверять userfield registration и access controller, а не только component template.
- Для shop-задач считать `calendar` соседним модулем; checkout appointment/booking возможен только если проект явно связал это с заказом.

## `idea` 25.0.0

### Surface

- Компоненты: `idea`, `idea.list`, `idea.detail`, `idea.edit`, `idea.category.list`, `idea.comment.list`, `idea.filter`, `idea.popup`, `idea.rss`, `idea.search`, `idea.statistic`, `idea.subscribe`, `idea.tags`.
- Legacy classes: `CIdeaManagment`, `CIdeaManagmentEmailNotify`, `CIdeaManagmentIdea`, `CIdeaManagmentIdeaComment`, `CIdeaManagmentNotify`, `CIdeaManagmentSonetNotify`.
- D7/lib: `notifyemail.php`.
- Table: `b_idea_email_subscribe`.
- Event: `socialnetwork` → `OnFillSocNetLogEvents`.

### Guardrails

- Это feedback/idea layer, а не CRM/sale lead engine.
- Если “идея не видна/не ищется/не подписывает” — проверять component params, socialnetwork integration, email subscription table и search/rss layer.
- Не обещать связь с заказами или покупателями без локального проекта.

## `learning` 25.0.0

### Surface

- Компоненты: `learning.course`, `learning.course.list`, `learning.course.detail`, `learning.course.contents`, `learning.course.tree`, `learning.chapter.detail`, `learning.lesson.detail`, `learning.search`, `learning.test`, `learning.test.list`, `learning.test.self`, `learning.student.*`.
- Admin: course/lesson/question/test/attempt/gradebook/certification/group/import/export pages.
- Legacy classes: `CCourse`, `CLearnLesson`, `CLearnLessonTree`, `CLQuestion`, `CTest`, `CTestResult`, `CGradeBook`, `CCertification`, `CStudent`, `CLearningGroup*`, `CLearnAccess`, `CLearnHelper`, `CExport`, `CImport`, `CScorm`.
- Tables: `b_learn_course`, `b_learn_lesson`, `b_learn_question`, `b_learn_answer`, `b_learn_test`, `b_learn_attempt`, `b_learn_test_result`, `b_learn_gradebook`, `b_learn_student`, `b_learn_certification`, groups/rights/site path tables.
- Events: main group/user/site/lang delete, search reindex, ratings, audit types/handlers, learning group cleanup.

### Guardrails

- Это education/content module. Для продажи курсов через интернет-магазин нужна локальная связка с `sale/catalog`; по умолчанию её нет.
- Для импорта/экспорта курсов использовать learning admin/import-export layer, не CommerceML.
- Для прав смотреть `CLearnAccess`/rights tables, а не только группы пользователей.

## `support` 26.0.0

### Surface

- Компоненты: `support.ticket`, `support.ticket.edit`, `support.ticket.list`, `support.wizard`, `iblock.wizard`.
- Admin: ticket list/edit/message/file, dictionary, SLA, timetable, holidays, groups, coupons, reports/graphs, online/desktop, messages reindex.
- Legacy classes: `CTicket`, `CTicketDictionary`, `CSupportEMail`, `CTicketReminder`, `CTicketSLA`, `CTicketTimetable`, `CSupportTimetableCache`, `CTicketCoupons`, `CTicketUserGroup`.
- Tables: `b_ticket`, `b_ticket_message`, `b_ticket_message_2_file`, `b_ticket_dictionary`, `b_ticket_online`, `b_ticket_sla*`, `b_ticket_ugroups`, `b_ticket_supercoupons*`, `b_ticket_timetable*`, `b_ticket_holidays`, `b_ticket_search`.
- Event/agents: `mail` `OnGetFilterList`, reminder agent, online cleanup, auto-close, timetable cache.

### Guardrails

- `support` может содержать словари “Оплата заказа”/“Доставка заказа”, но это не делает его `sale` API.
- Для тикета по заказу сначала ищи локальную связку ticket ↔ order; стандартный module сам по себе хранит support entities.
- Для email-to-ticket проверять mail filter, source dictionary, SLA and agents.
- Для вложений проверять secure file access через support file endpoint/admin route, не отдавать прямой `/upload` без прав.

## `wiki` 25.0.0

### Surface

- Компоненты: `wiki`, `wiki.show`, `wiki.edit`, `wiki.history`, `wiki.history.diff`, `wiki.categories`, `wiki.category`, `wiki.discussion`, `wiki.menu`.
- Legacy classes: `CWiki`, `CWikiDocument`, `CWikiParser`, `CWikiDiff`, `CWikiSecurity`, `CWikiSocnet`, `CWikiUserTypeWiki`, notify/rating classes.
- D7/lib: `diff.php`, update livefeed index classes, socialnetwork integration.
- Events: ratings vote/cancel, search `BeforeIndex`, socialnetwork indexing/menu/routes, IM notify schema, `onLogIndexGetContent`.

### Guardrails

- Wiki — content/social module. Для public knowledge base магазина нужна локальная маршрутизация, шаблон и права.
- Если “страница не ищется/не попала в livefeed” — смотреть search/socialnetwork events and reindex, а не SEO компонента каталога.
- Для diff/history работать через wiki classes/components, не вручную по таблицам.

## `b24connector` 25.0.0

### Surface

- Компоненты: `b24connector.button.list`, `b24connector.openline.info`.
- Admin: `b24connector.php`, `buttons.php`, `crm_forms.php`, `open_lines.php`, `recall.php`, `chat.php`, `telefonia.php`, `prolog_before.php`.
- Lib: `Button`, `ButtonTable`, `ButtonSiteTable`, `Connection`, `Helper`, `Cache`.
- Tables: `b_b24connector_buttons`, `b_b24connector_button_site`.
- Events: `main` `OnBuildGlobalMenu`, `OnBeforeProlog`.

### Guardrails

- Это connector/widgets layer, а не локальный CRM или заказной API.
- Для “виджет не появился” проверять active connection, site binding, admin settings, component/template placement, cache and `OnBeforeProlog`.
- Для лидов/форм/openlines не обещать локальные CRM entities без установленного CRM/Bitrix24-side контекста.

## `landing` 26.200.0

### Surface

- Компоненты: `landing.sites`, `landing.site_edit`, `landing.landing_edit`, `landing.landing_view`, `landing.pub`, `landing.domain_edit`, `landing.role_edit`, `landing.blocks.*`, `landing.cookies`, `landing.userconsent.selector`, catalog/filter blocks (`landing.blocks.catalog_section_with_carousel`, `landing.blocks.cmpfilter`).
- Admin: `site.php`, `view.php`, menu/task/operation descriptions.
- Lib: `Landing`, `Block`, `Site`, `Domain`, `Folder`, `Hook`, `File`, `Role`, `EntityRights`, `UrlRewrite`, `Connector\Iblock`, `Connector\Crm`, `Connector\Socialnetwork`, `Sanitizer`, `History`, `Metrika`, `Copilot`.
- Tables: `b_landing`, `b_landing_block`, `b_landing_site`, `b_landing_domain`, `b_landing_hook_data`, `b_landing_file`, `b_landing_syspage`, `b_landing_placement`, `b_landing_urlrewrite`, `b_landing_entity_rights`, `b_landing_role`, filter/view/binding/chat/history/copilot tables.

### Guardrails

- Catalog blocks are presentation/connectors. Product truth remains `iblock/catalog`; price/stock truth remains `catalog/sale`.
- For “товар не отображается на лендинге” check: module presence → block code → connector/filter settings → iblock/catalog data → rights/site → cache/search index.
- For landing security/content changes, use sanitizer/hook/domain/right layers; do not patch generated block HTML as the only truth.

## `mobileapp` 25.0.100

### Surface

- Компоненты: `mobileapp.auth`, `mobileapp.menu`, `mobileapp.list`, `mobileapp.jnrouter`, `mobileapp.push`, `mobileapp.push.token`, `mobileapp.edit`, `mobileapp.filter`, UI controls and designer file input.
- Admin: `mobile_designer.php`, mobile admin area.
- Legacy/classes: `CMobile`, `CMobileAppPullSchema`, `CAdminMobilePush`, interface/filter helpers.
- Lib: `Bitrix\MobileApp\Mobile`, `App`, `AppResource`, `Designer\Manager`, `Designer\Config*`, `Designer\Tools`, `Janative\Manager`, JN entity/extension/config utilities.
- Tables: `b_mobileapp_app`, `b_mobileapp_config`.
- Events: `pull` dependent module, buffer/epilog init scripts.

### Guardrails

- Sale mobile order components are in `sale`, not proof that `mobileapp` owns checkout.
- For push/token issues check `mobileapp.push.token`, pull dependency and device/app config.
- For JN/native tasks inspect JN extension/component path and bundle settings; do not solve by public web template assumptions.

## Диагностика по симптомам

| Симптом | Сначала проверить | Не делать первым |
|---|---|---|
| Виджет Bitrix24 не виден | `b24connector` connection, button-site binding, `OnBeforeProlog`, cache | не править `sale`/CRM API |
| Товар на лендинге не появился | landing block connector/filter, `iblock/catalog`, rights/site/cache | не считать landing источником товара |
| Support ticket из email не создаётся | mail filter, `CSupportEMail`, source dictionary, agents | не писать parser вручную |
| Calendar invite не синхронизируется | iCal/mail/sync agents, queue, connection tables | не искать в checkout |
| Mobile push не приходит | `mobileapp` + `pull`, token component, app config | не менять sale order status handlers |
| Learning test/grade не считается | learning test/attempt/result/gradebook tables, rights | не использовать CommerceML |
| Wiki page не ищется | search/socialnetwork events, reindex | не чистить весь кеш сайта первым шагом |
| Idea subscribe не работает | `b_idea_email_subscribe`, component params, socialnetwork notify | не обещать CRM lead |

## С чем читать вместе

- Inventory — [shop-core-module-inventory.md](shop-core-module-inventory.md)
- Version mismatch — [version-impact.md](version-impact.md)
- Landing — [landing.md](landing.md)
- B24 connector — [b24connector.md](b24connector.md)
- Mobile app — [mobileapp.md](mobileapp.md)
- Mail/messages — [mail-notifications.md](mail-notifications.md), [messageservice.md](messageservice.md)
- Search/social — [search.md](search.md), [blog-socialnet.md](blog-socialnet.md)
- Shop task matrix — [shop-task-matrix.md](shop-task-matrix.md)
- Runtime smoke — [runtime-smoke-verification.md](runtime-smoke-verification.md)
