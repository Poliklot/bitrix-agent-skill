# Bitrix Agent Skill

<p align="center">
  <strong>Core-first Bitrix expert for Claude Code and Codex.</strong><br />
  It inspects the real `www/bitrix` core, stock components, templates, and `local/*` overrides before giving implementation advice.
</p>

<p align="center">
  <a href="https://github.com/Poliklot/bitrix-agent-skill/releases/latest">Latest release</a>
  · <a href="LICENSE">MIT License</a>
  · <a href="https://github.com/Poliklot/bitrix-agent-skill/tree/master/mcpmarket/bitrix">MCP Market folder</a>
</p>

<p align="center">
  <img src="assets/bitrix-demo-v4.gif" alt="Bitrix Agent Skill terminal demo showing how to make Bitrix customizations survive updates" width="100%" />
</p>

## Why it exists

Bitrix projects are not solved by memory. Module sets, copied component templates, wizard assets, legacy write paths, and `local/*` overrides change the correct answer.

This skill makes the agent work like a senior Bitrix developer:

- checks installed modules and versions first;
- reads stock components/templates before suggesting changes;
- separates D7, legacy API, and side-effect-heavy write paths;
- treats `catalog`, `sale`, `currency`, `bizproc`, `pull`, 1С and shop integrations as project-dependent until confirmed locally;
- keeps code-first audit separate from runtime smoke proof.

## Install

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.ps1 | iex
```

Then restart Claude Code or Codex once if the skill does not appear immediately.

Use it in a Bitrix project:

```text
/bitrix почему товар есть в админке, но не виден на сайте?
```

### MCP Market

MCP Market has a 50-file import limit. Use the compact read-only folder:

```text
https://github.com/Poliklot/bitrix-agent-skill/tree/master/mcpmarket/bitrix
```

The full `bitrix/` skill keeps lifecycle scripts and 77 individual reference files. The `mcpmarket/bitrix/` edition contains the same reference layer grouped into compact bundles.

<details>
<summary>Advanced install options</summary>

Install only one agent contour:

```bash
curl -fsSL https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.sh | bash -s -- --claude
curl -fsSL https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.sh | bash -s -- --codex
curl -fsSL https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.sh | bash -s -- --both
```

Install a specific release:

```bash
curl -fsSL https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.sh | bash -s -- --version 1.25.0 --claude
```

PowerShell equivalents:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.ps1))) -Claude
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.ps1))) -Codex
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.ps1))) -Both
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Poliklot/bitrix-agent-skill/master/install.ps1))) -Version 1.25.0 -Claude
```

</details>

## What it covers

| Area | What the skill helps with |
|---|---|
| Core and modules | `main`, `iblock`, ORM, Loader, events, DB layer, sessions, RBAC, cache, steppers |
| Components and templates | stock component contracts, copied templates, `result_modifier.php`, `component_epilog.php`, AJAX, pagination |
| Content | iblocks, HL blocks, UF, forms, blog, forum, vote, landing, fileman, search, SEO |
| Shop | `catalog`, `sale`, `currency`, SKU/offers, prices, stock, basket, checkout, orders, payments, delivery, discounts |
| 1С / CommerceML | `catalog.import.1c`, `catalog.export.1c`, `sale.export.1c`, XML_ID/CML2_LINK, exchange logs and fixtures |
| Integrations | REST, webhooks, app scopes, `webservice.sale`, `webservice.statistic`, SOAP/WSDL, Bitrix24 connector |
| Production work | update-safe customization, D7 vs legacy decisions, pitfalls matrix, smoke verification plan |
| Operations | migrations, agents/cron, steppers, imports, backup, monitoring, perf diagnostics |

Shop coverage is activated per project only after the relevant modules are present in `www/bitrix/modules`. The separate shop-core baseline documents 49 modules, but the skill must still verify each client project locally.

## Example prompts

```text
/bitrix Проверь по core, почему вторая страница каталога пустая после фильтра
/bitrix Разбери, почему 1С выгрузила товар, но на сайте нет цены и остатка
/bitrix Найди stock template layer для form и объясни intranet-вариант
/bitrix Сформируй production-safe план доработки checkout и перечисли грабли
/bitrix Проверь, можно ли в этом проекте идти в sale/catalog, или commerce deferred
/bitrix Почему REST событие заказа не прилетело во внешний webhook?
```

## How it works

The skill uses progressive disclosure:

```text
bitrix-agent-skill/
├── bitrix/SKILL.md              # entrypoint, routing, safety rules
├── bitrix/references/*.md       # 77 focused references loaded only when needed
├── mcpmarket/bitrix/            # compact read-only MCP Market edition
├── install.sh / install.ps1     # installers for Claude Code and Codex
└── CHANGELOG.md / PLAN.md       # release notes and audit roadmap
```

The agent starts from `bitrix/SKILL.md`, detects the task domain, then loads only the relevant reference files. It should not drag the full Bitrix knowledge base into context for every request.

## Safety model

The skill is intentionally conservative:

- no invented APIs, events, classes, or component params;
- no commerce route without local `catalog` / `sale` / `currency` confirmation;
- no direct SQL mutations for order, basket, payment, shipment, catalog price, or stock when API side effects matter;
- no production 1С, real payments, real delivery/cashbox, SMS, or customer data in smoke tests without explicit confirmation;
- no “runtime pass” claim without sandbox fixtures and captured evidence.

## Update and maintenance

The installed skill can check GitHub releases and update itself.

```bash
bash ~/.claude/skills/bitrix/update.sh --check
bash ~/.claude/skills/bitrix/update.sh

bash "${CODEX_HOME:-$HOME/.codex}/skills/bitrix/update.sh" --check
bash "${CODEX_HOME:-$HOME/.codex}/skills/bitrix/update.sh"
```

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\bitrix\update.ps1" -Check
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\bitrix\update.ps1"

$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
powershell -ExecutionPolicy Bypass -File (Join-Path (Join-Path $CodexHome 'skills') 'bitrix\update.ps1') -Check
powershell -ExecutionPolicy Bypass -File (Join-Path (Join-Path $CodexHome 'skills') 'bitrix\update.ps1')
```

On the first meaningful `/bitrix` request, the skill should silently run `--check`. If a newer release exists, it should say exactly:

```text
Обновилась версия скилла с X до Y. Давай обновим?
```

<details>
<summary>Version list and uninstall commands</summary>

```bash
bash ~/.claude/skills/bitrix/versions.sh
bash "${CODEX_HOME:-$HOME/.codex}/skills/bitrix/versions.sh"

bash ~/.claude/skills/bitrix/uninstall.sh
bash "${CODEX_HOME:-$HOME/.codex}/skills/bitrix/uninstall.sh"
```

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\bitrix\versions.ps1"
powershell -ExecutionPolicy Bypass -File "$HOME\.claude\skills\bitrix\uninstall.ps1"

$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
powershell -ExecutionPolicy Bypass -File (Join-Path (Join-Path $CodexHome 'skills') 'bitrix\versions.ps1')
powershell -ExecutionPolicy Bypass -File (Join-Path (Join-Path $CodexHome 'skills') 'bitrix\uninstall.ps1')
```

</details>

## Requirements

- Claude Code or Codex
- A project based on 1C-Bitrix CMS / Bitrix24 self-hosted core

## Feedback

Issues and PRs are welcome, especially when they bring a new core-first case from a real Bitrix project.

If the skill saved you time, star the repository — it is the clearest signal that Bitrix deserves better agent tooling.

## License

MIT. See [LICENSE](LICENSE).
