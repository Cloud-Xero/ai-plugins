# dashboard

A public dashboard (Next.js static site) that reads the frontmatter of the skills and agents under `plugins/` and lists them. Deployed automatically to GitHub Pages via GitHub Actions.

Public URL: https://cloud-xero.github.io/ai-plugins/

## What it shows

- Scans `plugins/*/skills/*/SKILL.md` and `plugins/*/agents/*.md` in the repo
- Extracts frontmatter (`name` / `description` / `model` / `tools` / `argument-hint` / `delegates`)
- The detail modal shows the full file contents (for skills, `SKILL.md` + `INSTRUCTIONS.md`) and lets you copy them
- Organized by domain (xero-biz / xero-marketing / xero-work) × category (Skills / Agents / Hooks / MCP)
- Search, type filter, domain filter, grid/table view toggle, and light/dark toggle

A category is shown only when it has at least one item. Hooks / MCP are currently empty, so they do not appear (they show up automatically once added to a plugin — see the comments in `lib/catalog.ts` for the loader's extension point).

## Local development

The package manager is fixed to **pnpm** and the dev port to **3011**.

```bash
cd dashboard
pnpm install
pnpm dev          # http://localhost:3011
```

## Build (static export)

```bash
pnpm build        # generates static files into out/
```

`next.config.mjs` sets `output: "export"`. Only production builds get `basePath: "/ai-plugins"` (for GitHub Pages project-page hosting). Local `pnpm dev` has no basePath.

## Deploy

`.github/workflows/deploy-dashboard.yml` fires on push to `main` (when `plugins/**` or `dashboard/**` change), builds, and publishes to Pages. Manual runs (workflow_dispatch) are also supported.

The first time only, you must set the repository's **Settings → Pages → Build and deployment → Source** to **GitHub Actions**.

## Structure

```
dashboard/
├── app/
│   ├── globals.css     # Design tokens + all styles
│   ├── layout.tsx      # Theme init (anti-flash script)
│   └── page.tsx        # Runs loadCatalog() at build time and injects the data
├── components/
│   └── Catalog.tsx     # List / filters / modal / theme toggle (client)
├── lib/
│   ├── config.ts       # Domain/category display meta (color, label, order)
│   └── catalog.ts      # Scans plugins/ and reads frontmatter + full file contents
└── next.config.mjs
```

## When you add a new domain (plugin)

Add an entry to `DOMAIN_META` and `DOMAIN_ORDER` in `lib/config.ts` (short id, label, color token). Unregistered plugins are still shown with the default color, but add them here to get the intended color and order. To add a new color token, add `--<color>` / `--<color>-tint` and `.dot.<color>` in `app/globals.css`.
