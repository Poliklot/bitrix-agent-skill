# Bitrix Skill for Claude Code

Claude Code skill for Bitrix CMS and Bitrix24 development. Covers D7 and legacy APIs — ORM, components, iblocks, HL blocks, caching, events, REST, and more.

## Installation

```bash
cp -r bitrix/ ~/.claude/skills/bitrix
```

Then in any Bitrix project:

```
/bitrix <your task>
```

## How it works

The skill follows the [agentskills.io](https://agentskills.io) progressive disclosure format:

- **`bitrix/SKILL.md`** — entry point loaded on every invocation (~200 lines): role, core rules, quick reference, navigation table
- **`bitrix/references/*.md`** — topic files loaded on demand when the task requires them

The agent reads only the relevant reference file, not the entire context at once.

## Coverage

| Reference file | Topics |
|----------------|--------|
| `orm.md` | DataManager, CRUD, Relations, filters, aggregation, runtime fields, ORM events, Result/Error |
| `events-routing.md` | EventManager, Engine\Controller, AJAX, Routing, CSRF |
| `modules-loader.md` | Module structure, Loader, PSR-4, Application, ServiceLocator, Config\Option, Loc |
| `components.md` | CBitrixComponent, templates, component cache, CComponentEngine |
| `cache-infra.md` | Data\Cache, TaggedCache, CAgent, IO\File/Directory/Path |
| `http.md` | Type\DateTime, HttpClient, HttpRequest, HttpResponse |
| `iblocks.md` | Iblocks legacy + D7 ORM, properties, HL blocks, iblock events |
| `iblock-hl-relations.md` | Iblock ↔ HL relations: directory (UF_XML_ID), hlblock UF, `_REF` in ORM, AbstractOrmRepository |
| `custom-uf-types.md` | Custom UF types (BaseType, onBeforeSave, file upload), ACF patterns via HL (Repeater, Group, Flexible Content, deep nesting) |
| `security.md` | XSS, SQL injection, CSRF, access control, CurrentUser, ActionFilter |
| `rest.md` | REST methods, OnRestServiceBuildDescription, REST events, Webhook, OAuth |
| `admin-ui.md` | Admin pages, CAdminList, CAdminForm, CAdminTabControl, custom UF types in admin |
| `entities-migrations.md` | Creating iblocks/types/properties, groups, users, permissions, SQL migrations |
| `sef-urls.md` | SEF URLs, urlrewrite.php, UrlRewriter D7, SEF_MODE/SEF_RULE, CComponentEngine |
| `seo-cache-access.md` | Cache clearing, noindex, sitemap, robots.txt, page access control |
| `mail-notifications.md` | CEventType, CEventMessage, Mail\Event::send, SMS providers |
| `users.md` | UserTable D7, CUser::Add/Login/Update, user groups, UF fields, password recovery |
| `templates.md` | Site template structure, Asset D7, $APPLICATION in header/footer, composite cache |
| `webforms.md` | CForm, CFormResult, AJAX form via Controller, validation |
| `search.md` | CSearch::Index/DeleteIndex/ReIndexAll, BeforeIndex, OnSearch, module registration |
| `import-export.md` | CSV/URL import, multistep import, CFile::SaveFile/MakeFileArray/ResizeImageGet, streaming export |

## Requirements

- Claude Code
- Bitrix CMS 23+ or Bitrix24 2024+
