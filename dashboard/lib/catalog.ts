import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import {
  DOMAIN_META,
  DOMAIN_ORDER,
  DEFAULT_COLOR,
  type DomainMeta,
} from "./config";

export type CatalogFile = { filename: string; content: string };

export type CatalogItem = {
  name: string;
  kind: "skill" | "agent" | "hook" | "mcp";
  /** ドメイン ID（biz / marketing / work …） */
  domain: string;
  /** frontmatter の model（未指定なら null） */
  model: string | null;
  /** エージェントの tools（未指定なら null） */
  tools: string[] | null;
  /** スキルの argument-hint（未指定なら null） */
  argHint: string | null;
  /** スキルが委譲するエージェント名（frontmatter に delegates があれば。無ければ null） */
  delegates: string[] | null;
  /** frontmatter の description（実データ） */
  description: string;
  /** 表示・コピー用のファイル全文（スキルは SKILL.md + INSTRUCTIONS.md） */
  files: CatalogFile[];
};

export type Catalog = { domains: DomainMeta[]; items: CatalogItem[] };

/** dashboard/ からでもリポジトリルートからでも plugins/ を見つける */
function findPluginsDir(): string {
  const candidates = [
    path.join(process.cwd(), "plugins"),
    path.join(process.cwd(), "..", "plugins"),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  throw new Error(
    `plugins directory not found (looked in: ${candidates.join(", ")})`,
  );
}

/** "Read, Write, Glob" のような文字列 or 配列を string[] に正規化 */
function toolList(v: unknown): string[] | null {
  if (v == null) return null;
  const arr = Array.isArray(v) ? v.map(String) : String(v).split(",");
  const out = arr.map((s) => s.trim()).filter(Boolean);
  return out.length ? out : null;
}

/** ファイル全文を読み、末尾の空白・改行だけ落とす */
function readFull(p: string): string {
  return fs.readFileSync(p, "utf8").replace(/\s+$/, "");
}

export function loadCatalog(): Catalog {
  const pluginsDir = findPluginsDir();

  const pluginNames = fs
    .readdirSync(pluginsDir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name);

  const usedDomains = new Map<string, DomainMeta>();
  const items: CatalogItem[] = [];

  for (const plugin of pluginNames) {
    const meta: DomainMeta =
      DOMAIN_META[plugin] ??
      { id: plugin, label: plugin, desc: "", color: DEFAULT_COLOR };
    const base = path.join(pluginsDir, plugin);

    // ---- skills: <plugin>/skills/<name>/SKILL.md (+ INSTRUCTIONS.md) ----
    const skillsDir = path.join(base, "skills");
    if (fs.existsSync(skillsDir)) {
      for (const d of fs.readdirSync(skillsDir, { withFileTypes: true })) {
        if (!d.isDirectory()) continue;
        const skillMd = path.join(skillsDir, d.name, "SKILL.md");
        if (!fs.existsSync(skillMd)) continue;

        const fm = matter(fs.readFileSync(skillMd, "utf8")).data as Record<
          string,
          unknown
        >;
        const files: CatalogFile[] = [
          { filename: "SKILL.md", content: readFull(skillMd) },
        ];
        const instr = path.join(skillsDir, d.name, "INSTRUCTIONS.md");
        if (fs.existsSync(instr)) {
          files.push({ filename: "INSTRUCTIONS.md", content: readFull(instr) });
        }

        items.push({
          name: (fm.name as string) ?? d.name,
          kind: "skill",
          domain: meta.id,
          model: (fm.model as string) ?? null,
          tools: toolList(fm.tools ?? fm["allowed-tools"]),
          argHint: (fm["argument-hint"] as string) ?? null,
          delegates: toolList(fm.delegates),
          description: (fm.description as string) ?? "",
          files,
        });
        usedDomains.set(plugin, meta);
      }
    }

    // ---- agents: <plugin>/agents/<name>.md ----
    const agentsDir = path.join(base, "agents");
    if (fs.existsSync(agentsDir)) {
      for (const f of fs.readdirSync(agentsDir)) {
        if (!f.endsWith(".md")) continue;
        const p = path.join(agentsDir, f);
        const fm = matter(fs.readFileSync(p, "utf8")).data as Record<
          string,
          unknown
        >;
        items.push({
          name: (fm.name as string) ?? f.replace(/\.md$/, ""),
          kind: "agent",
          domain: meta.id,
          model: (fm.model as string) ?? null,
          tools: toolList(fm.tools),
          argHint: null,
          delegates: null,
          description: (fm.description as string) ?? "",
          files: [{ filename: f, content: readFull(p) }],
        });
        usedDomains.set(plugin, meta);
      }
    }

    // ---- hooks / mcp ----
    // 現状このカタログには存在しないため未実装。プラグインに追加されたら
    // ここで plugin.json の hooks / mcpServers や .mcp.json を読み、
    // kind: "hook" / "mcp" の CatalogItem を push する。
    // UI は 0 件のカテゴリを自動的に隠すので、追加までは何も表示されない。
  }

  const ordered = [
    ...DOMAIN_ORDER,
    ...pluginNames.filter((p) => !DOMAIN_ORDER.includes(p)),
  ];
  const domains = ordered
    .filter((p) => usedDomains.has(p))
    .map((p) => usedDomains.get(p)!);

  return { domains, items };
}
