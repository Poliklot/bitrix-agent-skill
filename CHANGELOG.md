# Changelog

Формат: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), версионирование: [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.24.0] — 2026-06-03

### Added
- `bitrix/references/shop-integrations-webservice.md` — отдельный core-first reference по integration extras интернет-магазина: `webservice` 26.0.0, `webservice.sale`, `webservice.statistic`, SOAP/WSDL, `stssync`, REST apps/webhooks/events/placements, sale REST controllers/events и catalog REST controllers/events/placement.

### Changed
- `shop-core-module-inventory.md` теперь считает webservice/integration extras покрытыми и сдвигает ordered roadmap к Docker/runtime smoke.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с webservice/REST baseline `1.24.0`.

## [1.23.0] — 2026-06-03

### Added
- `bitrix/references/shop-automation-bizproc.md` — отдельный core-first reference по automation/bizproc слою интернет-магазина: `bizproc`, `bizprocdesigner`, legacy `workflow`, `lists`, `pull`, workflow templates/states/tasks, robots/triggers, list processes, REST surface и realtime diagnostics.

### Changed
- `shop-core-module-inventory.md` теперь считает automation/bizproc покрытыми и сдвигает ordered roadmap к `shop-integrations-webservice.md` и Docker/runtime smoke.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с automation/bizproc baseline `1.23.0`.

## [1.22.0] — 2026-06-03

### Added
- `bitrix/references/shop-marketing-analytics.md` — отдельный core-first reference по маркетингово-аналитическому слою интернет-магазина: `sender`, `mail`, `messageservice`, `subscribe`, `advertising`, `abtest`, `conversion`, `report`, `statistic`, eShop hooks и sale-side sender/statistic connectors.

### Changed
- `shop-core-module-inventory.md` теперь считает marketing/analytics покрытыми и сдвигает ordered roadmap к automation/bizproc и webservice/integration extras.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с marketing/analytics baseline `1.22.0`.

## [1.21.0] — 2026-06-02

### Added
- `bitrix/references/shop-standard-components.md` — отдельный core-first reference по стандартным компонентам интернет-магазина: `bitrix:catalog`, `catalog.section`, `catalog.element`, `catalog.smart.filter`, compare, basket, `sale.order.ajax`, `sale.order.checkout`, personal order pages, catalog productcard/store/report components, `bitrix.eshop` wizard layer и quick map параметров 1С components.

### Changed
- `shop-core-module-inventory.md` теперь считает standard shop components покрытыми и сдвигает ordered roadmap к marketing/analytics, automation и webservice.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы со standard-components baseline `1.21.0`.
- Windows `update.ps1` больше не передаёт `-Claude`/`-Codex` в installer как версию; `install.ps1` также умеет восстановиться после старого broken forwarding из уже установленных updater-копий.

## [1.20.0] — 2026-06-02

### Added
- `bitrix/references/storeassist.md` — отдельный core-first reference по `storeassist` 24.0.0: мастер магазина, `storeassist_1c_*` onboarding pages, admin toolbar, task whitelist, options `storeassist_settings`/`progress_percent`/`num_orders`, AJAX endpoint `/bitrix/tools/storeassist.php`, menu hooks и daily order-progress agent.

### Changed
- `shop-core-module-inventory.md` теперь считает `storeassist` покрытым и сдвигает ordered roadmap к `shop-standard-components.md`, marketing/analytics, automation и webservice.
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы со StoreAssist baseline `1.20.0`.

## [1.19.0] — 2026-06-02

### Added
- `bitrix/references/shop-core-module-inventory.md` — полный inventory 49 модулей shop-core: версии, counts по components/admin/lib/classes, shop/1С relevance, coverage status и ordered roadmap для `storeassist`, shop standard components, marketing/analytics, automation и webservice.

### Changed
- `bitrix/SKILL.md`, `shop-task-matrix.md`, `core-audit-matrix.md`, `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с module-inventory baseline `1.19.0`.
- Shop-route теперь явно не обещает глубокое покрытие `storeassist`, `sender`, `report`, `statistic`, `conversion`, `abtest`, `advertising`, `bizproc`, `webservice` без отдельного deep-reference.

## [1.18.0] — 2026-06-02

### Added
- `bitrix/references/pagination.md` — отдельный core-first reference по пагинации из `main` 26.150.0: `CDBResult::NavStart`, `GetNavPrint`, `PAGEN_N`/`SIZEN_N`/`SHOWALL_N`, `system.pagenavigation`, D7 `PageNavigation`, `AdminPageNavigation`, `ReversePageNavigation`, `main.pagenavigation`, admin/grid navigation и ajax/lazy load.

### Changed
- `bitrix/SKILL.md` теперь явно маршрутизирует задачи про пустые/дублирующие страницы, `PAGEN_N`, lazy load, admin/grid navigation и `PageNavigation` в отдельный pagination-layer.
- `README.md`, `PLAN.md`, `bitrix/VERSION` и MCP Market compact bundles синхронизированы с pagination baseline `1.18.0`.

## [1.17.0] — 2026-06-02

### Added
- `bitrix/references/currency.md` — отдельный core-first reference по модулю `currency` 26.0.0: валюты, курсы, форматирование денег, `CurrencyManager`, `CurrencyTable`, `CurrencyRateTable`, связь с catalog prices и sale sums.
- `bitrix/references/commerce-1c-integration.md` — отдельный reference по 1С / CommerceML: `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`, `checkauth/init/file/import`, `BX_CML2_IMPORT`, `BX_CML2_EXPORT`, temp files, zip/chunks, `secure_1c_exchange`, exchange logs.
- `bitrix/references/shop-task-matrix.md` — быстрый routing интернет-магазина: товары, SKU, цены, остатки, корзина, checkout, оплата, доставка, скидки, заказы и 1С diagnostics.
- `mcpmarket/bitrix/` — компактная read-only версия навыка для импорта через MCP Market: reference-файлы сгруппированы в bundles, чтобы skill folder оставался ниже лимита 50 файлов.

### Changed
- `bitrix/references/catalog.md` переаудирован по shop-core с `catalog` 25.550.0: product/SKU/price/store/store document/measure/VAT/admin component/1C import layers.
- `bitrix/references/sale.md` переаудирован по shop-core с `sale` 26.0.0: basket/order/payment/shipment/discount/location/cashbox/exchange side effects.
- `bitrix/references/commerce-workflows.md` переведён из deferred в подтверждённый shop-route после локальной проверки `catalog`, `sale`, `currency` и 1С components.
- `bitrix/references/core-audit-matrix.md` теперь описывает фазовую матрицу: active non-commerce route, active shop-core route и deferred zones per project.
- `bitrix/SKILL.md`, `README.md`, `PLAN.md` и `bitrix/VERSION` синхронизированы с commerce/1С baseline `1.17.0`.

## [1.16.0] — 2026-04-24

### Added
- `bitrix/references/core-audit-matrix.md` — матрица текущего non-commerce core: активные модули, deferred-домены и ловушки вроде `catalog.*` компонентов внутри `iblock` без установленного модуля `catalog`
- `bitrix/references/noncommerce-task-matrix.md` — быстрый routing типовых и нетиповых задач без интернет-магазина в правильные reference-файлы
- `bitrix/references/diagnostic-visibility.md` — диагностика “в админке есть, на сайте нет”: права, site binding, component params, filters, templates, cache/index/SEO chain
- `bitrix/references/index-cache-diagnostics.md` — отдельный слой по component/tagged/managed/composite cache, search index и SEO artifacts
- `bitrix/references/component-dataflow-debugging.md` — трассировка standard component flow от `.parameters.php` до `component_epilog.php` и AJAX
- `bitrix/references/php-quality.md` — PHP quality gates для Bitrix-проектов: phpstan/psalm/fixer/sniffer/rector без навязывания нового toolchain
- `bitrix/references/php-legacy-modernization.md` — безопасная legacy modernization: boundary extraction, D7 vs `C*` write paths, selective modern PHP
- `bitrix/references/standard-components-noncommerce.md` — standard components без магазина и stock template truth layer
- `bitrix/references/operations-runbook.md` — эксплуатационный runbook без магазина: переносы, agents/cron/stepper, импорты, backup/monitoring, perf diagnostics, обновления core

### Changed
- `bitrix/SKILL.md` теперь маршрутизирует весь non-commerce контур по audit matrix, diagnostic layers, PHP quality/legacy modernization, standard components и operations runbook
- `bitrix/references/php-workflow.md` и `bitrix/references/php-testing.md` связаны с новыми PHP quality и legacy modernization слоями
- `README.md` синхронизирован с новым non-commerce покрытием и полной матрицей новых reference-файлов

## [1.15.0] — 2026-04-24

### Added
- `bitrix/references/php-testing.md` — отдельный reference по PHP testing и verification в Bitrix-проекте: unit/integration, smoke без готового PHPUnit-контура, test seams, fixtures и разведение project contour от vendor noise внутри core

### Changed
- `bitrix/references/php-workflow.md` теперь явно исключает vendor noise внутри `www/bitrix/modules/*/vendor` при диагностике project tooling и ссылается на новый testing-layer
- `bitrix/SKILL.md` теперь маршрутизирует PHP testing/verification в новый `php-testing.md`, различает project contour и vendor noise и фиксирует safe-подход к проверке boundary-кода
- `README.md` синхронизирован с новым testing-покрытием PHP-слоя и дополнен `php-testing.md` в матрице reference-файлов

## [1.14.0] — 2026-04-24

### Added
- `bitrix/references/php-workflow.md` — отдельный reference по PHP-heavy задачам в Bitrix-проекте: service-layer, DTO/value-object границы, exceptions vs `Result/Error`, project toolchain (`composer`, `phpunit`, `phpstan`/`psalm`, fixer/sniffer, `rector`) и минимальные quality gates без конфликта с Bitrix-нормами

### Changed
- `bitrix/SKILL.md` теперь явно маршрутизирует PHP-heavy Bitrix-задачи в новый `php-workflow.md`, учитывает project-tooling-first подход и фиксирует границы для `strict_types`, exceptions и foreign framework patterns
- `README.md` синхронизирован с новым PHP-покрытием и дополнен `php-workflow.md` в матрице reference-файлов

## [1.13.0] — 2026-04-15

### Changed
- `bitrix/references/sitecorporate.md` дополнен реальным wizard template/public слоем и зафиксированным фактом, что `corp_furniture` skeleton местами тянет `bitrix:catalog`, не доказывая наличие магазинного core
- `bitrix/references/blog-socialnet.md` дополнен stock template layer для случая без `www/local`: `micro`, `old_version`, `socialnetwork`, `result_modifier.php`, JS и upload hooks
- `bitrix/references/webforms.md` дополнен stock component/template layer для случая без `www/local`: `intranet`-templates, cache/tags/error-style слой и component-level развилки `form.result.new`
- `bitrix/SKILL.md` теперь явно учитывает checkout без `local/*` и ведёт аудит в stock templates и wizard assets текущего core
- `README.md` синхронизирован с новым покрытием template/public слоя поверх уже проверенного core

## [1.12.0] — 2026-04-15

### Added
- `bitrix/references/sitecorporate.md` — отдельный core-first справочник по модулю `bitrix.sitecorporate`, wizard-решениям `corp_services` / `corp_furniture` и stock `furniture.*` компонентам

### Changed
- `bitrix/references/blog-socialnet.md` переписан под реально установленный `blog`: D7 read-only таблицы, `CBlog*`, mail reply handlers, search reindex и условный `socialnet`-контур
- `bitrix/references/webforms.md` расширен до реального `form`-workflow: статусы, handlers, validators, CRM link, secure file access и стандартные `form.*` компоненты
- `bitrix/SKILL.md` теперь явно маршрутизирует задачи в `sitecorporate.md` и фиксирует core-first ограничения для `blog` и `form`
- `README.md` синхронизирован с новым покрытием текущего core и обновлёнными описаниями `sitecorporate`, `blog` и `form`

## [1.11.0] — 2026-04-15

### Added
- `bitrix/references/mobileapp.md` — отдельный core-first справочник по модулю `mobileapp`
- `bitrix/references/b24connector.md` — отдельный core-first справочник по модулю `b24connector`

### Changed
- `bitrix/SKILL.md` теперь явно считает `mobileapp` и `b24connector` активными модулями текущего core и маршрутизирует задачи в правильные reference-файлы
- `README.md` синхронизирован с новым покрытием текущего core и дополнен `mobileapp.md` и `b24connector.md`

## [1.10.0] — 2026-04-15

### Added
- `bitrix/references/bitrixcloud.md` — отдельный core-first справочник по модулю `bitrixcloud`

### Changed
- `bitrix/references/security.md` расширен до реально установленного модуля `security`: WAF, redirect/IP rules, session hardening, OTP/MFA, recovery codes, antivirus, site checker и xscan
- `bitrix/SKILL.md` теперь явно считает `security` и `bitrixcloud` активными модулями текущего core и маршрутизирует задачи в правильные reference-файлы
- `README.md` синхронизирован с новым покрытием текущего core и дополнен `bitrixcloud.md`

## [1.9.0] — 2026-04-15

### Added
- `bitrix/references/photogallery.md` — отдельный core-first справочник по модулю `photogallery`

### Changed
- `bitrix/SKILL.md` расширен на подтверждённый активный модуль `photogallery` и теперь ведёт gallery/upload/comment-задачи в отдельный маршрут
- `README.md` синхронизирован с новым покрытием текущего core и дополнен новым reference-файлом

## [1.8.0] — 2026-04-15

### Added
- `bitrix/references/highloadblock.md` — отдельный core-first справочник по модулю `highloadblock`
- `bitrix/references/clouds.md` — отдельный core-first справочник по модулю `clouds`

### Changed
- `bitrix/SKILL.md` расширен на подтверждённый активный модуль `clouds`, получил отдельные маршруты для `highloadblock` и `clouds`, а также новые core-first эвристики для HL и внешнего файлового хранения
- `bitrix/references/iblock-hl-relations.md` явно разведён с новым `highloadblock.md`
- `bitrix/references/import-export.md` явно разведён с новым `clouds.md`, чтобы задачи по `HANDLER_ID` и cloud-storage не ехали в общий `CFile`-маршрут
- `README.md` синхронизирован с новым покрытием текущего core и дополнен новыми reference-файлами

## [1.7.0] — 2026-04-15

### Added
- `bitrix/references/location.md` — отдельный core-first справочник по модулю `location`
- `bitrix/references/messageservice.md` — отдельный core-first справочник по модулю `messageservice`
- `bitrix/references/fileman.md` — отдельный core-first справочник по модулю `fileman`
- `bitrix/references/translate.md` — отдельный core-first справочник по модулю `translate`

### Changed
- `bitrix/SKILL.md` расширен на подтверждённые активные модули `fileman`, `location`, `messageservice`, `translate` и теперь маршрутизирует задачи в новые reference-файлы
- `bitrix/references/mail-notifications.md` явно разведён с `messageservice`, чтобы SMS-задачи шли в правильный модульный слой
- `README.md` синхронизирован с новым покрытием текущего core и дополнен новыми reference-файлами

## [1.6.0] — 2026-04-10

### Added
- `bitrix/versions.sh` и `bitrix/versions.ps1` — просмотр доступных release-версий навыка
- `bitrix/uninstall.sh` и `bitrix/uninstall.ps1` — удаление установленной копии навыка для `Claude` и `Codex`
- поддержка установки и обновления конкретной версии через `--version` и `-Version`

### Changed
- `install.sh` и `install.ps1` теперь в первую очередь ставят навык из release/tag-архива, а не из branch tarball
- `bitrix/update.sh` и `bitrix/update.ps1` теперь умеют обновлять и откатывать навык на конкретную release-версию
- `README.md` дополнен полноценным lifecycle: установка, обновление, просмотр версий, удаление и пути с учётом `$CODEX_HOME`

## [1.5.1] — 2026-04-10

### Changed
- `README.md` переведён на новый bootstrap URL репозитория `bitrix-agent-skill`
- changelog compare/release links переведены на новый GitHub slug
- репозиторий после rename зафиксирован как основной, при этом legacy fallback в install/update-скриптах сохранён для мягкой миграции старых установок

## [1.5.0] — 2026-04-10

### Added
- dual-target install/update flow для `Claude Code` и `Codex`
- автоматическое определение текущего и legacy slug репозитория: сначала `bitrix-agent-skill`, затем `claude-bitrix-skill`
- флаги таргетинга installer-ов: `--claude/--codex/--both` и `-Claude/-Codex/-Both`

### Changed
- `README.md` переведён из Claude-only документации в общий формат `Bitrix Agent Skill` для двух агентов
- `bitrix/SKILL.md` обновлён под совместимость с `Claude Code` и `Codex`
- `install.sh`, `install.ps1`, `bitrix/update.sh`, `bitrix/update.ps1` отвязаны от жёсткой привязки к старому slug и готовы к rename репозитория
- PowerShell installer больше не зависит от шаблона архива `claude-bitrix-skill-*`
- `PLAN.md` синхронизирован с текущей версией и rename-safe install/update слоем

## [1.4.1] — 2026-04-10

### Added
- `bitrix/references/forum.md` — отдельный core-first справочник по модулю `forum`
- `bitrix/references/vote.md` — отдельный core-first справочник по модулю `vote`
- `bitrix/references/landing.md` — отдельный core-first справочник по модулю `landing`
- `bitrix/references/socialservices.md` — отдельный core-first справочник по модулю `socialservices`
- `bitrix/references/perfmon.md` — отдельный core-first справочник по модулю `perfmon`

### Changed
- `bitrix/SKILL.md` расширен на подтверждённые модули `forum`, `vote`, `landing`, `socialservices`, `perfmon`
- `bitrix/references/search.md` дополнен подтверждённым fast-search маршрутом через `CSearchTitle` и `bitrix:search.suggest.input`
- `bitrix/references/seo-cache-access.md` дополнен подтверждённым путём для `OpenGraph` и `JSON-LD` через `$APPLICATION->AddHeadString(...)`
- `README.md` синхронизирован с новым покрытием текущего core без partial-зон в блоговом и стандартном контуре

## [1.4.0] — 2026-04-10

### Added
- `install.ps1` — нативная установка навыка на Windows через PowerShell
- `bitrix/update.ps1` — нативное обновление и `-Check` для Windows через PowerShell
- `bitrix/allow-update.ps1` — helper для глобального разрешения автообновления на Windows

### Changed
- `README.md` переписан под три платформы: macOS, Linux и Windows
- `bitrix/allow-update.sh` теперь добавляет разрешения и для bash-, и для PowerShell-апдейтера
- `SKILL.md` учитывает Windows/PowerShell при проверке новой версии навыка

## [1.3.11] — 2026-04-08

### Added
- `bitrix/allow-update.sh` — helper-скрипт, который одной командой добавляет глобальное разрешение на запуск `update.sh` в `~/.claude/settings.json`

### Changed
- `README.md` больше не предлагает руками редактировать проектный `.claude/settings.local.json` для автообновления навыка
- Инструкция по постоянному разрешению на `update.sh` упрощена до одной команды и переведена на глобальный `~/.claude/settings.json`

## [1.3.10] — 2026-04-08

### Added
- GitHub Actions workflow, который на push в `master` автоматически публикует tag и GitHub Release для текущей версии из `bitrix/VERSION`, если их ещё нет

### Changed
- `README.md` дополнен описанием fully-automatic release flow без ручного создания тега и release в GitHub UI
- В README добавлен шаг с постоянным разрешением на запуск `update.sh`, чтобы агент мог держать навык свежим без повторных запросов

## [1.3.9] — 2026-04-08

### Changed
- Выпущен повторный тестовый релиз для проверки предложения обновить навык при появлении новой версии

## [1.3.8] — 2026-04-08

### Changed
- Выпущен тестовый релиз для проверки сценария с предложением обновить навык при появлении новой версии

## [1.3.7] — 2026-04-08

### Added
- `bitrix/update.sh --check` — явная проверка новой версии без немедленного обновления
- Правило в `SKILL.md`: при первом `/bitrix` сначала проверить версию навыка и при наличии новой версии предложить обновление в явной форме

### Changed
- `README.md` дополнен сценарием проверки новой версии без апдейта

## [1.3.6] — 2026-04-08

### Changed
- Завершена полная core-first ревизия всех `bitrix/references/*.md` по реально установленному ядру
- `README.md` и `PLAN.md` синхронизированы с текущим состоянием скилла и его deferred-доменов
- Маршруты `catalog`, `sale`, `commerce-workflows`, `bizproc`, `pull` и `socialnet` зафиксированы как условные до появления соответствующих модулей в core

### Fixed
- Убраны неподтверждённые API и устаревшие формулировки в reference-файлах по `blog`, `search`, `seo`, `session`, `access`, `subscribe`, `grid`, `file uploader`, `validation`, `templates`, `import/export`, `stepper`, `numerator` и связанным подсистемам
- Исправлены описания покрытия в `README.md`, чтобы они соответствовали реальным контрактам текущего ядра

## [1.1.0] — 2026-03-19

### Added
- `bitrix/VERSION` — файл версии, единый источник истины
- `install.sh` — идемпотентный скрипт установки и обновления (bash + curl)
- `bitrix/update.sh` — встроенный обновлятор: один вызов для обновления навыка
- `CHANGELOG.md` — этот файл
- 35 reference-файлов по всем подсистемам Bitrix

### Changed
- Версия в `SKILL.md` frontmatter обновлена до `"1.1"`
- `README.md` — добавлена секция "Обновление", упрощена установка

## [1.0.0] — 2026-02-XX

### Added
- Первый публичный релиз: `SKILL.md`, progressive disclosure архитектура

[Unreleased]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.24.0...HEAD
[1.24.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.23.0...v1.24.0
[1.23.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.22.0...v1.23.0
[1.22.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.21.0...v1.22.0
[1.21.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.20.0...v1.21.0
[1.20.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.19.0...v1.20.0
[1.19.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.18.0...v1.19.0
[1.18.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.17.0...v1.18.0
[1.17.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.16.0...v1.17.0
[1.16.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.15.0...v1.16.0
[1.15.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.14.0...v1.15.0
[1.14.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.13.0...v1.14.0
[1.13.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.12.0...v1.13.0
[1.12.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.11.0...v1.12.0
[1.11.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.10.0...v1.11.0
[1.10.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.9.0...v1.10.0
[1.9.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.11...v1.4.0
[1.3.11]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.10...v1.3.11
[1.3.10]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.9...v1.3.10
[1.3.9]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.8...v1.3.9
[1.3.8]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.7...v1.3.8
[1.3.7]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.3.6...v1.3.7
[1.3.6]: https://github.com/Poliklot/bitrix-agent-skill/compare/v1.1.0...v1.3.6
[1.1.0]: https://github.com/Poliklot/bitrix-agent-skill/releases/tag/v1.1.0
[1.0.0]: https://github.com/Poliklot/bitrix-agent-skill/releases/tag/v1.0.0
