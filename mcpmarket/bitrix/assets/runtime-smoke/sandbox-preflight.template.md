# Runtime smoke sandbox preflight

> Заполни перед write-mode smoke. Не включай secrets, cookies, tokens, license keys, production XML/дампы, персональные данные и приватные payloads.

## Safety gate

- Production data absent or sanitized: yes/no
- Production 1С credentials absent: yes/no
- Real payment/cashbox/delivery credentials absent: yes/no
- Real SMS/email sending disabled or stubbed: yes/no
- Production webhooks/tokens absent: yes/no
- Rollback/reset plan exists: yes/no
- Write-mode smoke allowed in this sandbox: yes/no

Если любой пункт небезопасен, не запускай write-mode smoke. Отмечай сценарии как `blocked`.

## Команды окружения

```bash
pwd
export SMOKE_BASE_URL="http://localhost"
export SMOKE_PUBLIC_ROOT="www"
export SMOKE_EVIDENCE_DIR="evidence/$(date +%F)-p1-shop-path"
mkdir -p "$SMOKE_EVIDENCE_DIR"

docker compose ps 2>/dev/null || true
docker compose exec php php -v 2>/dev/null || php -v
docker compose exec php php -m 2>/dev/null | sort || php -m | sort
find "$SMOKE_PUBLIC_ROOT/bitrix/modules" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort
```

## Команды проверки версий модулей

```bash
for m in main iblock catalog currency sale rest webservice statistic sender mail messageservice bizproc lists pull; do
  if test -f "$SMOKE_PUBLIC_ROOT/bitrix/modules/$m/install/version.php"; then
    echo "FOUND $m"
    sed -n '1,40p' "$SMOKE_PUBLIC_ROOT/bitrix/modules/$m/install/version.php"
  elif test "$m" = "main" && test -f "$SMOKE_PUBLIC_ROOT/bitrix/modules/main/classes/general/version.php"; then
    echo "FOUND main"
    sed -n '1,40p' "$SMOKE_PUBLIC_ROOT/bitrix/modules/main/classes/general/version.php"
  else
    echo "MISSING $m"
  fi
done
```

## Команды поиска маршрутов

```bash
rg -n 'IncludeComponent\(|catalog\.section|catalog\.element|sale\.basket|sale\.order' \
  local bitrix/templates "$SMOKE_PUBLIC_ROOT/bitrix/templates" "$SMOKE_PUBLIC_ROOT" \
  --glob '*.php' --glob '!bitrix/cache/**' --glob '!upload/**' 2>/dev/null

sed -n '1,220p' "$SMOKE_PUBLIC_ROOT/urlrewrite.php" 2>/dev/null || sed -n '1,220p' urlrewrite.php 2>/dev/null || true
```

## Результат preflight

- Public root:
- Base URL:
- Catalog route:
- Detail route:
- Basket route:
- Checkout route:
- Test user:
- Test delivery:
- Test pay system:
- Mail/SMS stub:
- Verdict: pass/fail/blocked
- Blocker reason:
