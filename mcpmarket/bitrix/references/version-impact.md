# Version impact layer

Открывай, когда локальная версия модуля отличается от reference, модуль отсутствует/обновлён или после обновления сломался component/REST/checkout/1С/admin route.

Правило: версия в reference означает “контракт проверен на этом core”, а не гарантию совместимости всех релизов. При mismatch агент должен сверить локальные файлы и отвечать по ним.

## Version check

```bash
for m in main iblock highloadblock catalog sale currency rest webservice sender mail messageservice bizproc lists pull; do
  if test -f "www/bitrix/modules/$m/install/version.php"; then
    echo "--- $m ---" && sed -n '1,60p' "www/bitrix/modules/$m/install/version.php"
  elif test -f "www/bitrix/modules/$m/classes/general/version.php"; then
    echo "--- $m fallback ---" && sed -n '1,40p' "www/bitrix/modules/$m/classes/general/version.php"
  else
    echo "--- $m missing ---"
  fi
done
```

## Checked baseline

| Module | Baseline | Notes |
|---|---:|---|
| `main` | `26.150.0` | fallback version path may be `classes/general/version.php` |
| `catalog` | `25.550.0` | products/SKU/prices/stocks/stores/import/export/catalog REST |
| `sale` | `26.0.0` | basket/order/payment/shipment/delivery/discounts/export/sale REST |
| `currency` | `26.0.0` | rates/formatting/price and order sums |
| `rest` | `26.0.0` | apps/webhooks/scopes/events/placements |
| `webservice` | `26.0.0` | SOAP/WSDL, `webservice.sale`, `webservice.statistic` |
| `sender` | `26.0.0` | contacts/segments/posting/events |
| `bizproc` | `26.200.0` | templates/states/tasks/robots/triggers |
| `pull` | `25.300.0` | realtime channels/watches/push queue |

## Version-sensitive contracts

- standard component `.parameters.php`, `component.php`, `class.php`, templates;
- D7 `*Table::getMap()`, validators, relations, install DB;
- REST controllers, scopes, events, placements;
- sale/catalog write paths with side effects;
- CommerceML `checkauth/init/file/import`, zip/chunk/temp options;
- admin list/grid/filter/action files;
- agents/stepper/cache/composite behavior.

## Workflow

1. Capture local module version.
2. Compare with checked baseline.
3. Open only relevant contract files.
4. If contract matches — say local version was checked and apply route.
5. If contract differs — build answer from local core.
6. If local core unavailable — state compatibility is not confirmed.

Answer pattern:

```text
Контракт в скилле проверен на `[module]` X. В проекте `[module]` Y. Я сверил/не смог сверить [paths], поэтому [route / limitation].
```

Связанные bundles: `project-intake.md`, `core-grep-cookbook.md`, `reference-map.md`, `core-routing.md`, `runtime-smoke-verification.md` section inside `core-routing.md`.
