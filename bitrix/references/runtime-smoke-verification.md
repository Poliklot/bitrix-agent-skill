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
