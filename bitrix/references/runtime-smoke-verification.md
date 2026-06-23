# Runtime Smoke Verification — Bitrix/shop-core проверка на живом маршруте

> Reference для Bitrix-скилла. Загружай, когда задача требует доказать, что решение работает в runtime: Docker/sandbox, fixtures, ручные smoke-сценарии, release verification, “можно ли считать покрытым”. Этот файл фиксирует проверочный слой; он не подменяет code-first audit и не разрешает использовать production secrets/data без подтверждения.

## Статус

Текущий reference-слой даёт сильное **code-first** покрытие. Runtime smoke — отдельная фаза. До её выполнения нельзя говорить:

- “весь core полностью проверен в runtime”;
- “checkout/exchange/REST точно работает в этом проекте”;
- “можно подключать production 1С/платежи/доставки”.

Правильная формулировка: “контракт подтверждён по core; runtime нужно проверить на sandbox/fixtures”.

## Sandbox safety

Нельзя использовать без явного подтверждения:

- production DB dump с персональными данными;
- реальные 1С credentials;
- реальные платежные/кассовые/доставочные credentials;
- реальные SMS/email рассылки;
- production webhooks/tokens;
- публичное открытие SOAP/checkauth/test endpoints.

Для smoke нужны:

- isolated Docker/VM/local sandbox;
- test DB or sanitized dump;
- test site id and admin user;
- test catalog/offers/prices/stores;
- fake/test payment, delivery, SMS/email adapters;
- CommerceML fixtures;
- logs and rollback/reset plan.

## Docker execution plan

Этот reference не должен распространять proprietary Bitrix core, license keys, DB dumps, `upload/` или клиентские secrets. Docker-слой — это **harness**, а не поставка ядра. Core кладётся оператором локально и не коммитится в skill/repo.

Минимальная структура sandbox-проекта:

```text
bitrix-runtime-smoke/
├── docker-compose.yml          # php-fpm/apache or nginx, db, optional mailhog
├── .env.example                # безопасные placeholders, без secrets
├── www/                        # локально положенное ядро Bitrix, не коммитить
├── fixtures/                   # синтетические catalog/sale/CommerceML данные
├── smoke/                      # read-only или idempotent smoke scripts
└── evidence/                   # logs/screenshots/output, не содержит PII/secrets
```

Минимальные сервисы:

| Service | Требование | Зачем |
|---|---|---|
| `php`/`web` | PHP + расширения под версию Bitrix | public/admin/component smoke |
| `db` | MySQL/MariaDB с зафиксированной версией и charset | импорт, ORM, индексы, заказы |
| `mailhog`/stub | локальный перехват email | checkout/sender без реальных писем |
| `sms/payment/delivery` stubs | fake endpoints or disabled adapters | не трогать реальные внешние сервисы |
| optional `browser` | Playwright/CLI browser | list/detail/checkout screenshots |

Перед smoke зафиксировать:

```bash
docker compose ps
docker compose exec php php -v
docker compose exec php php -m | sort
docker compose exec db mysql --version 2>/dev/null || true
find www/bitrix/modules -maxdepth 1 -mindepth 1 -type d | sort
```

Правило evidence: все команды, fixture names, module versions и результаты сохранять в `evidence/`, но не коммитить туда персональные данные, ключи, cookies, session ids и реальные XML выгрузки клиента.

## Порядок запуска smoke-прохода

Используй один и тот же порядок, чтобы результаты можно было сравнивать между проектами:

1. **Preflight**: зафиксировать окружение, public root, modules/versions, site ids, шаблоны, режим агентов, mail/SMS/payment/delivery stubs.
2. **Fixture import**: загрузить только синтетические данные; отдельно записать fixture names и rollback/reset plan.
3. **Read-only smoke**: проверить видимость каталога, компонентные маршруты, REST method discovery, WSDL доступность и отсутствие production endpoints.
4. **Write-mode smoke**: выполнять только в sandbox: basket, checkout/order, CommerceML import/export, test sender/SMS/bizproc.
5. **Second request/cache pass**: повторить ключевые public checks с включённым кешем/composite, чтобы поймать cache-only регрессии.
6. **Evidence pack**: сохранить команды, expected/actual, логи, screenshots/HTML snippets и verdict `pass`, `fail` или `blocked`.
7. **Reference feedback**: перенести подтверждённые runtime findings обратно в профильные references; blocked-зоны описать как ограничения, а не как pass.

Не смешивай read-only и write-mode: если безопасного write sandbox нет, smoke фиксируется как `blocked`, а не как “не нужен”.

## Пакет 1: каталог → SKU/цены/остатки → корзина/заказ

Это первый обязательный smoke-пакет для превращения shop-route из code-first в runtime-подтверждённый. Его цель — доказать минимальный пользовательский путь: товар виден, offer выбирается, цена/остаток понятны, товар добавляется в корзину, заказ сохраняется в test mode.

### Prerequisites

- Подтверждены модули `main`, `iblock`, `catalog`, `currency`, `sale`.
- Есть sandbox site id и активный site template.
- Есть тестовый пользователь или понятный guest-only сценарий.
- Есть fake/test доставка и fake/test платёжная система; реальные оплаты, кассы и службы доставки не используются.
- Mail/SMS перехватываются stub/MailHog или отключены безопасно.
- Есть rollback/reset plan для созданных товаров, корзин, заказов и связанных файлов.

### Минимальные fixtures

| Fixture | Требование | Зачем |
|---|---|---|
| `section_active` | активный раздел каталога, привязанный к сайту | public list visibility |
| `product_simple_visible` | активный товар с ценой, валютой и положительным остатком | базовая карточка/list/detail |
| `product_inactive` | неактивный товар | negative visibility |
| `product_no_price` | активный товар без цены для группы пользователя | negative purchaseability |
| `product_zero_stock` | активный товар с ценой и нулевым остатком | проверка настроек `CAN_BUY_ZERO`/availability |
| `product_with_offers` | товар с двумя offers и `CML2_LINK` | SKU selection, offer-vs-product add |
| `store_stock` | минимум один склад/остаток | stock/store behavior |
| `test_user` | пользователь с предсказуемыми группами | auth basket/order path |
| `test_delivery` | stub delivery service | checkout без внешней службы |
| `test_pay_system` | stub pay system | order save без реальной оплаты |

### Сценарии пакета

| ID | Сценарий | Expected evidence | Pass criteria | Blocked if |
|---|---|---|---|---|
| P1-01 | Preflight commerce modules | versions for `main`, `iblock`, `catalog`, `currency`, `sale`; PHP/DB/site/template facts | все обязательные modules найдены, версии зафиксированы | отсутствует любой обязательный module |
| P1-02 | Public catalog list/detail | HTTP/CLI/browser output для list и detail, inactive hidden | активный товар виден в списке и детальной, inactive не виден | нет public route или component/template |
| P1-03 | Price/currency/stock | output по цене, валюте, stock/store, zero-stock behavior | цена и валюта соответствуют fixture, zero-stock поведение объяснено настройками | нет price type/store settings |
| P1-04 | SKU/offer selection | выбранный offer id, price/stock выбранного offer, add target | добавляется offer, а не parent product; неверный target диагностирован | нет offers iblock или `CML2_LINK` |
| P1-05 | Guest basket | add-to-basket response, FUSER/session/site, reload check | товар остаётся в корзине после reload, site/fuser понятны | session/FUSER недоступен в sandbox |
| P1-06 | Auth basket | login/test user, basket refresh, group price behavior | auth user видит корректную цену и корзину | нет безопасного test user |
| P1-07 | Checkout/order save | delivery/payment/order props, `Order::save()` result, order id | заказ создан в test mode, payment/shipment collections есть | нет stub delivery/payment или write sandbox |
| P1-08 | Second request/cache pass | повтор list/detail/basket с кешем/composite | второй запрос не скрывает fixture и не показывает чужую корзину | cache/composite нельзя безопасно включить |

### Evidence pack для пакета 1

Сохраняй отдельный блок или файл evidence для каждого `P1-*`:

```text
Scenario: P1-XX
Sandbox URL/CLI:
Modules/versions:
Fixture names:
User mode: guest/auth user id or group
Steps:
Expected:
Actual:
HTTP status / CLI output:
Cache/composite state:
Logs:
Rollback/reset:
Verdict: pass/fail/blocked
Follow-up reference changes:
```

Рекомендуемая структура evidence для одного прохода:

```text
evidence/
└── YYYY-MM-DD-p1-shop-path/
    ├── 00-preflight.txt
    ├── P1-01-modules.txt
    ├── P1-02-catalog-list-detail.txt
    ├── P1-03-price-stock.txt
    ├── P1-04-offer-selection.txt
    ├── P1-05-guest-basket.txt
    ├── P1-06-auth-basket.txt
    ├── P1-07-order-save.txt
    ├── P1-08-cache-pass.txt
    └── summary.md
```

Минимальные переменные запуска:

```bash
export SMOKE_BASE_URL="http://localhost"
export SMOKE_PUBLIC_ROOT="www"
export SMOKE_EVIDENCE_DIR="evidence/$(date +%F)-p1-shop-path"
mkdir -p "$SMOKE_EVIDENCE_DIR"
```

Read-only часть можно начинать с HTTP/browser checks. Write-mode часть (`P1-05`–`P1-07`) запускай только после явного подтверждения sandbox и reset plan. Если нет проектных URL каталога/корзины/checkout, сначала найти их через `IncludeComponent`, `urlrewrite.php`, шаблоны и shop standard components; не угадывать `/catalog/` или `/personal/cart/` как универсальные пути.

Если сценарий падает, не перепрыгивай сразу к следующему “зелёному” результату: сначала классифицируй причину как missing module, bad fixture, component params, rights/site binding, cache, JS/AJAX, sale provider, delivery/payment restriction или sandbox blocker.

## Пакет 2: 1С / CommerceML

Цель — доказать, что обмен проверяется как управляемый sandbox-flow, а не как “загрузили XML и вроде норм”.

### Prerequisites

- Подтверждены `catalog`, `sale`, `currency`.
- Включены только sandbox endpoints обмена; production 1С credentials не используются.
- Есть синтетические CommerceML XML: catalog import, offers/prices/stocks, broken negative fixture, repeated import fixture, order export case.
- Временная директория обмена очищается до/после сценария; cookies/session ids не попадают в commit.

### Сценарии пакета

| ID | Сценарий | Pass criteria | Blocked if |
|---|---|---|---|
| P2-01 | `checkauth` / session contract | sandbox endpoint выдаёт ожидаемый auth/session ответ без production secrets | endpoint недоступен или требует production credentials |
| P2-02 | `init` settings | понятны zip/file limit/sessid/temp path настройки | настройки не получить безопасно |
| P2-03 | `file` upload | XML fixture загружается/chunk-ится в temp path | нет write sandbox/temp permissions |
| P2-04 | catalog `import` | создаются/обновляются товар, offer, price, stock, XML_ID/CML2_LINK | нет catalog fixture или import падает до данных |
| P2-05 | repeated import idempotency | повторный import не дублирует сущности | idempotency нельзя проверить без reset |
| P2-06 | broken XML negative | ошибка контролируемая, лог понятен, данные не портятся | нет safe negative fixture |
| P2-07 | order export | тестовый eligible order попадает в XML export с payment/shipment fields | нет test order или sale export route |
| P2-08 | non-eligible order exclusion | неподходящий заказ исключён по status/date/site/person type | нет настроек фильтра |

## Пакет 3: REST и webservice

Цель — проверить интеграционный слой без смешивания REST, SOAP/WSDL и CommerceML.

### Prerequisites

- Подтверждены `rest`; для SOAP — `webservice`, при статистике — `statistic`.
- Используются sandbox app/webhook credentials со строго ограниченными scopes.
- Токены не пишутся в evidence; в логах оставляются только masked values.

### Сценарии пакета

| ID | Сценарий | Pass criteria | Blocked if |
|---|---|---|---|
| P3-01 | REST method discovery | `methods`/`method.get` показывает нужные методы и scopes | нет sandbox app/webhook |
| P3-02 | missing scope negative | запрос без scope падает безопасно и понятно | нельзя создать negative auth case |
| P3-03 | sale event binding | test order change создаёт ожидаемое REST event delivery/log | нет `sale` или event delivery недоступна |
| P3-04 | catalog event binding | product/price change создаёт ожидаемый event/log | нет `catalog` или event binding |
| P3-05 | placement registration | placement виден только если нужен задаче | placement не используется в sandbox |
| P3-06 | `webservice.sale` WSDL/SOAP | endpoint доступен в sandbox и не трактуется как order CRUD | нет `webservice.sale` |
| P3-07 | `webservice.statistic` | результат соответствует sandbox statistic data или честно blocked | нет `statistic` data |

## Пакет 4: marketing, analytics, automation, realtime

Цель — проверить побочные shop-маршруты безопасно: без реальных писем, SMS, рекламы, customer data и production realtime.

### Prerequisites

- Подтверждены нужные модули: `sender`, `mail`, `messageservice`, `subscribe`, `advertising`, `abtest`, `conversion`, `report`, `statistic`, `bizproc`, `lists`, `pull` — каждый сценарий запускается только после module check.
- Email/SMS только через stub/MailHog/fake provider.
- Realtime проверяется на sandbox pull config или фиксируется как `blocked`.

### Сценарии пакета

| ID | Сценарий | Pass criteria | Blocked if |
|---|---|---|---|
| P4-01 | sender contact/list/segment | sandbox contact попадает в ожидаемый segment | нет `sender` или safe contact fixture |
| P4-02 | subscribe/unsubscribe | test subscription меняет состояние без реальной рассылки | нет safe mail stub |
| P4-03 | mail capture | письмо уходит в MailHog/stub, не наружу | mail transport нельзя безопасно перехватить |
| P4-04 | SMS provider stub | SMS создаётся в fake provider/log, не отправляется клиенту | нет fake provider |
| P4-05 | advertising/banner click | test banner/click фиксируется в sandbox counters | нет `advertising` или counters |
| P4-06 | conversion/report/statistic | counters/reports строятся на тестовых данных | нет statistic/report data |
| P4-07 | bizproc/list task | workflow/list process стартует, task назначен test user | нет safe BP template |
| P4-08 | pull/realtime | watch/event доходит до sandbox client или fallback documented | нет pull server/client |

## Минимальный preflight

```bash
pwd
find www/bitrix/modules -maxdepth 1 -mindepth 1 -type d | sort
for m in main iblock currency catalog sale rest webservice statistic sender mail messageservice bizproc lists pull; do
  test -f "www/bitrix/modules/$m/install/version.php" && sed -n '1,40p' "www/bitrix/modules/$m/install/version.php"
done
find local bitrix/templates www/bitrix/templates -maxdepth 4 -type f 2>/dev/null | sort | head -200
```

Runtime facts to capture:

| Fact | Why |
|---|---|
| PHP version/extensions | Bitrix/runtime compatibility |
| DB type/version/charset | imports, indexes, ORM behavior |
| Site IDs/languages/templates | component routing and mail/SEO |
| Installed modules/versions | active/deferred route |
| Agent mode hit/cron | background tasks |
| Mail/SMS transport mode | no accidental real sends |
| Payment/delivery/cashbox mode | no real transaction |
| Composite/cache mode | public smoke validity |

## Fixture set

### Catalog fixture

- product iblock;
- offers iblock with `CML2_LINK`;
- product with active section;
- one inactive product;
- one product without price;
- one product with price but zero stock;
- one product with purchasable offer;
- one product with multiple offers;
- price types and currencies;
- at least one store and store stock;
- smart filter properties.

### Sale fixture

- guest basket scenario;
- authorized user basket scenario;
- person type;
- order properties;
- delivery service test/stub;
- pay system test/stub;
- discount/coupon;
- order status lifecycle;
- shipment/payment collections.

### 1С/CommerceML fixture

- `checkauth/init/file/import` catalog import XML;
- offer package with price/stock;
- order export fixture;
- large/chunked XML case if supported by sandbox;
- broken XML negative case;
- repeated import idempotency case.

### REST/webservice fixture

- incoming webhook/app test auth;
- method discovery check;
- sale order event binding;
- catalog product/price event binding;
- placement registration if relevant;
- `webservice.sale` SOAP statistics call;
- `webservice.statistic` call when statistic data exists;
- negative auth/scope case.

### Marketing/automation fixture

- sender contact/list/segment;
- sender subscribe form;
- SMS provider stub;
- advertising banner/click;
- A/B test simple page switch;
- conversion/report/statistic smoke;
- bizproc template/task;
- lists process;
- pull watch/realtime event.

## Smoke сценарии

### 1. Public catalog visibility

Expected evidence:

- product visible in list;
- product visible in detail;
- inactive product hidden;
- guest vs authorized behavior documented;
- component cache verified after first and second request.

Diagnostic chain:

```text
iblock data → section active chain → rights/site binding → component params/filter → pagination/sort → template → cache/composite
```

### 2. Offer/price/stock purchaseability

Expected evidence:

- product without price not purchasable;
- product with zero stock behavior matches settings;
- selected offer adds to basket;
- wrong product-vs-offer add is detected;
- price/currency formatting correct.

### 3. Basket and checkout

Expected evidence:

- add to basket works for guest and authorized user;
- basket persists through page reload/session;
- delivery and payment are shown according to restrictions;
- order properties validate;
- order can be saved in test mode;
- order email/event behavior verified without real sends.

### 4. Order lifecycle

Expected evidence:

- order created;
- payment collection exists;
- shipment collection exists;
- status changes via API path;
- discount/coupon result recorded;
- no direct SQL mutation required;
- events/logs captured.

### 5. CommerceML catalog import

Expected evidence:

- `checkauth` returns expected session/cookie contract;
- `init` returns import settings;
- `file` uploads fixture;
- `import` creates/updates product/offer/price/stock;
- repeated import does not duplicate entities;
- broken fixture produces controlled error.

### 6. CommerceML order export

Expected evidence:

- eligible test order appears in export;
- filters by status/date/site/person type match settings;
- exported XML has expected order/payment/shipment fields;
- non-eligible order is excluded.

### 7. REST event and method smoke

Expected evidence:

- `methods`/`method.get` confirm needed methods;
- app/webhook has required scopes;
- event binding exists;
- sale/catalog entity change triggers expected event;
- delivery retries/offline behavior is understood;
- negative missing-scope case fails safely.

### 8. `webservice.sale` / `webservice.statistic`

Expected evidence:

- WSDL/SOAP endpoint reachable only in allowed sandbox context;
- `webservice.sale` returns statistics/livefeed contract, not order CRUD;
- `webservice.statistic` result matches available statistic data;
- auth/test endpoint exposure is reviewed.

### 9. Marketing/analytics

Expected evidence:

- sender segment resolves contacts;
- posting/subscription flow works in test mode;
- mail/SMS are stubbed or captured;
- banner/click/conversion/report/statistic counters behave as expected;
- no real customer communication sent.

### 10. Automation/realtime

Expected evidence:

- bizproc template starts for controlled entity;
- task appears for expected user;
- lists process route works;
- pull/watch event reaches client or fallback path is documented;
- agents/stepper mode is captured.

## Verification output format

For every scenario capture:

```text
Scenario:
Modules/versions:
Input fixture:
Steps:
Expected:
Actual:
Logs/screenshots:
Cache/index actions:
Rollback/reset:
Verdict: pass/fail/blocked
Follow-up reference changes:
```

## Minimal smoke matrix for release confidence

| Area | Minimum pass condition |
|---|---|
| Core modules | versions captured, required modules installed |
| Component visibility | list/detail visible with cache behavior understood |
| Pagination/lazy | no duplicate/empty page with stable sort |
| Catalog | product/offer/price/stock fixture works |
| Basket | guest/auth add-to-basket works |
| Checkout | test order saved with delivery/payment |
| 1С import | fixture import idempotent |
| 1С export | test order exported when eligible |
| REST | method discovery + one event delivery |
| Webservice | sale/statistic SOAP contract verified or blocked reason captured |
| Marketing | one safe test channel captured/stubbed |
| Automation | one bizproc/list/pull scenario captured |
| Ops | agents/cache/logs/rollback documented |

## When smoke is blocked

Do not fake pass. Record:

- missing module;
- missing DB dump;
- no test credentials;
- no safe email/SMS/payment stub;
- PHP/DB incompatibility;
- endpoint inaccessible;
- legal/privacy blocker;
- missing fixture.

Then update skill answer as “code contract known, runtime verification blocked by X”.

## Common mistakes

- Running smoke on production data.
- Calling real payment/SMS/delivery services.
- Treating one successful import as full 1С coverage.
- Treating order creation as payment/shipment/export coverage.
- Forgetting second request with cache enabled.
- Ignoring guest vs authorized behavior.
- Not saving negative cases.
- Not feeding runtime findings back into reference files.

## С чем читать вместе

- Production best practices — [production-best-practices.md](production-best-practices.md)
- Pitfalls — [pitfalls-matrix.md](pitfalls-matrix.md)
- Shop inventory — [shop-core-module-inventory.md](shop-core-module-inventory.md)
- Shop tasks — [shop-task-matrix.md](shop-task-matrix.md)
- Catalog — [catalog.md](catalog.md)
- Sale — [sale.md](sale.md)
- 1С — [commerce-1c-integration.md](commerce-1c-integration.md)
- REST/webservice — [shop-integrations-webservice.md](shop-integrations-webservice.md)
- Testing — [php-testing.md](php-testing.md)
