# Shop-core tail modules

Compact code-first route for `calendar`, `idea`, `learning`, `support`, `wiki`, `b24connector`, `landing`, `mobileapp`. Это соседние модули shop-core: они могут влиять на витрину, заявки, поддержку, обучение, лендинги, мобильный слой и виджеты, но не заменяют `catalog`/`sale`/`currency`.

## Quick map

| Module | Version | Route | Do not promise |
|---|---:|---|---|
| `calendar` | `25.170.0` | calendar/events/resource booking/sharing/sync/livefeed | checkout/order flow без локальной интеграции |
| `idea` | `25.0.0` | ideas/feedback/comments/subscribe/socialnetwork log | CRM/lead/order engine |
| `learning` | `25.0.0` | courses/lessons/tests/gradebook/SCORM/import-export | commerce course sale без кастомной связки |
| `support` | `26.0.0` | tickets/SLA/dictionaries/coupons/mail filter/reminders | sale order support API |
| `wiki` | `25.0.0` | wiki/history/diff/social discussion/search | shop knowledge base без route |
| `b24connector` | `25.0.0` | widgets/openlines/CRM forms/recall/chat/telephony binding | local CRM/sale integration engine |
| `landing` | `26.200.0` | landing pages/blocks/domains/roles/catalog blocks/forms/cookies | source of products/prices/stocks |
| `mobileapp` | `25.0.100` | mobile shell/designer/JN/native/push settings | sale mobile components ownership |

## Module checks

```bash
for m in calendar idea learning support wiki b24connector landing mobileapp; do
  test -f "www/bitrix/modules/$m/install/version.php" \
    && echo "FOUND $m" && sed -n '1,60p' "www/bitrix/modules/$m/install/version.php" \
    || echo "MISSING $m"
done
```

## Routes

- `calendar`: components `calendar.grid/events.list/view.slider/edit.slider/pub.sharing`; classes `CCalendar*`; tables `b_calendar_*`; events with `pull`, `im`, `rest`, `socialnetwork`, `mail`, `dav`, `iblock`; agents for sync/queue/sharing. Diagnose sync/mail/agents/logs, not `sale`.
- `idea`: `idea.*` components, `CIdeaManagment*`, table `b_idea_email_subscribe`, `socialnetwork` log event. Feedback layer only.
- `learning`: `learning.course/test/student.*`, admin course/test/gradebook/import/export, `CCourse`, `CLearnLesson`, `CTest`, `CGradeBook`, `b_learn_*`, search/ratings/user/site delete events. Not CommerceML.
- `support`: `support.ticket*`, ticket/SLA/dictionary/coupon/admin reports, `CTicket*`, `CSupportEMail`, `b_ticket*`, mail filter and reminder/autoclose agents. Ticket layer only unless project links orders.
- `wiki`: `wiki.*`, `CWiki*`, diff/security/socnet, ratings/search/IM/socialnetwork events. Content/social layer.
- `b24connector`: button/openline components, admin widgets/forms/openlines/chat/recall/telephony, `ButtonTable`, `ButtonSiteTable`, `Connection`, `OnBuildGlobalMenu`, `OnBeforeProlog`.
- `landing`: `landing.*` and `landing.blocks.*`, catalog/filter blocks, `Landing`, `Block`, `Site`, `Domain`, `Hook`, `Connector\Iblock`, `Sanitizer`, `b_landing*`. Product truth remains iblock/catalog.
- `mobileapp`: `mobileapp.*`, mobile designer, `CMobile`, `CAdminMobilePush`, `Janative\Manager`, `b_mobileapp_*`, `pull` dependency. Sale mobile order components live in `sale`.

## Symptom routing

| Symptom | Check first |
|---|---|
| B24 widget missing | connection, button-site binding, `OnBeforeProlog`, cache |
| Product absent on landing | landing block connector/filter, iblock/catalog, rights/site/cache |
| Support ticket from email missing | mail filter, `CSupportEMail`, dictionary, agents |
| Calendar invite/sync broken | iCal/mail/sync agents, queue, connection tables |
| Mobile push broken | `mobileapp` + `pull`, token component, app config |
| Learning grade/test broken | attempt/result/gradebook tables, learning rights |
| Wiki page not searchable | search/socialnetwork events, reindex |
| Idea subscribe broken | `b_idea_email_subscribe`, component params, social notify |

Related: `core-routing.md`, `version-impact.md`, `site-cloud-mobile.md`, `commerce-shop.md`, runtime smoke section in `core-routing.md`.
