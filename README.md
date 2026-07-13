# ai-plugins

Cloud-Xero's personal catalog of Claude Code plugins (skills). Skills and agents are split into three plugins by domain.

| Plugin | Domain | Contents |
|--------|--------|----------|
| [xero-biz](./plugins/xero-biz/) | Strategy & decisions | Business strategy, finance, service design, decision review, contract review, market research |
| [xero-marketing](./plugins/xero-marketing/) | Marketing & growth | Marketing strategy, CS design, ad operations, SEO content, SNS operations |
| [xero-work](./plugins/xero-work/) | Client work & dev | Excel analysis, proposals, effort estimation, QA, AI news |

## Dashboard

A public dashboard lists every skill and agent at a glance.

**https://cloud-xero.github.io/ai-plugins/**

It is generated from the frontmatter under `plugins/`, and every push to `main` triggers a GitHub Actions rebuild and redeploy. It supports search, type/domain filters, grid/table views, and a detail modal (copy the full file contents). See [`dashboard/`](./dashboard/) for the implementation.

## Setup

```bash
git clone https://github.com/Cloud-Xero/ai-plugins.git
cd ai-plugins

# Register the marketplace and install the plugins (install only the ones you need).
claude plugin marketplace add "$(pwd)"
claude plugin install xero-biz@cloud-xero-plugins
claude plugin install xero-marketing@cloud-xero-plugins
claude plugin install xero-work@cloud-xero-plugins
```

## Updating

```bash
git pull
claude plugin install xero-biz@cloud-xero-plugins
claude plugin install xero-marketing@cloud-xero-plugins
claude plugin install xero-work@cloud-xero-plugins
```

> Claude Code manages skills by copying them into a cache, so `git pull` alone does not apply changes.

## Invoking a skill

```
/<plugin-name>:<skill-name>
```

Examples: `/xero-work:excel-analyze`, `/xero-biz:biz-strategy`

## Adding a skill

Pick the domain plugin to add it to, and create two files under `plugins/<plugin-name>/skills/<skill-name>/` (the two-layer structure inherited from apsis).

- `SKILL.md` — frontmatter (`name` = directory name / `description` = a concrete "when to use it") plus a single reference line to `INSTRUCTIONS.md`
- `INSTRUCTIONS.md` — the actual steps and knowledge

Copy [example-skill](./plugins/xero-work/skills/example-skill/) as a template.

Agents delegated from a skill go in the `agents/` of the **same plugin** as that skill.

## Structure

```
ai-plugins/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace definition
├── plugins/
│   ├── xero-biz/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/<skill-name>/
│   │   │   ├── SKILL.md          # frontmatter + reference to INSTRUCTIONS.md
│   │   │   └── INSTRUCTIONS.md   # actual steps and knowledge
│   │   └── agents/<agent-name>.md
│   ├── xero-marketing/           # same as above
│   └── xero-work/                # same as above
├── CLAUDE.md
└── README.md
```

For the full list of skills/agents per plugin, see each plugin's README.
