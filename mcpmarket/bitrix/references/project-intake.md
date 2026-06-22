# Project intake

Открывай, когда задача относится к конкретному repo: “у нас”, “в этом проекте”, “найди где”, “почему не работает”, “почини”, “сделай патч”.

## Persistent project context

Если в корне проекта есть `BITRIX_PROJECT_CONTEXT.md`, прочитай его после `AGENTS.md`, но до широкого intake. Это snapshot, не абсолютная истина: для рискованных задач и shop/1С/integration изменений перепроверяй код.

Если файла нет и проведён полный project audit, создай/обнови `BITRIX_PROJECT_CONTEXT.md` в корне клиентского проекта по шаблону [../assets/BITRIX_PROJECT_CONTEXT.template.md](../assets/BITRIX_PROJECT_CONTEXT.template.md). Не записывать secrets, tokens, cookies, license keys, production XML/дампы и персональные данные.

## Quick scan

```bash
find . -maxdepth 5 -type d -path '*/bitrix/modules/main' -print
find . -maxdepth 4 -type d \( -name local -o -name bitrix \) -print
find www/bitrix/modules -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sed 's#^www/bitrix/modules/##' | sort | head -n 80
find local/templates bitrix/templates www/bitrix/templates -maxdepth 3 \( -name header.php -o -name footer.php -o -name '.section.php' \) -type f 2>/dev/null | sort
rg -n 'ShowHead|ShowTitle|ShowBodyScripts|ShowPanel|IncludeComponent\(' local bitrix/templates www/bitrix/templates --glob '*.php' 2>/dev/null
```

If public root is not `www/`, replace prefix with detected root.

## Capture facts

| Fact | Why |
|---|---|
| public root | Bitrix paths depend on it. |
| `local/`, `local/modules`, `local/components`, `local/templates` | Customization layer. |
| active template/header/footer | Meta/assets/layout/panel. |
| `ShowHead`, `ShowTitle`, `ShowBodyScripts` | Everyday head/assets answers. |
| `IncludeComponent` calls and local component templates | Where output/params live. |
| module inventory | Do not promise missing APIs. |
| `404.php`, `urlrewrite.php`, `SEF_*` | Routing/status diagnostics. |
| cache/composite markers | “Changes not visible” diagnostics. |
| composer/phpunit/phpstan/psalm/rector | Project tooling first. |
| events/agents | Custom logic/background jobs. |

## Module check

```bash
for m in iblock highloadblock form search seo catalog sale currency rest bizproc workflow pull socialnet; do
  test -f "www/bitrix/modules/$m/install/version.php" && echo "FOUND $m" || echo "MISSING $m"
done
```

## Report format

```text
Нашёл по проекту:
- context file: BITRIX_PROJECT_CONTEXT.md found/missing/updated
- public root: [path]
- project layer: [local/local modules/components/templates]
- template/head: [header path, ShowHead yes/no, ShowTitle yes/no]
- modules: [relevant found/missing]
- target layer: [page/component/template/local module]

Дальше делаю: [next action].
```

For a simple question, show only relevant facts.

## Project context file

Create/update `BITRIX_PROJECT_CONTEXT.md` after full project study, multi-step work, handoff, or discovery of important module/template/shop/1C/integration facts. If template asset is unavailable, create the same sections manually: project passport, public root, modules/versions, templates/head, components, shop, 1С, REST/webservice, events/agents, tooling, cache/SEO/routing, risks, open questions, sources.

## Stop

Stop intake when target file/layer, module presence, next check/patch, and side effects are clear. Then use the narrow bundle or implement the patch.
