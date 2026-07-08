// ドメイン（プラグイン）とカテゴリの表示メタデータ。
// 項目そのものは frontmatter から生成されるが、色・日本語ラベル・並び順はここで定義する。

export type DomainMeta = {
  /** フィルタや URL で使う短い ID */
  id: string;
  /** 表示名（プラグインディレクトリ名と一致） */
  label: string;
  /** ドメインの説明 */
  desc: string;
  /** CSS カラートークン兼ドットクラス名（biz / mkt / work） */
  color: string;
};

/** プラグインディレクトリ名 → 表示メタ */
export const DOMAIN_META: Record<string, DomainMeta> = {
  "xero-biz": { id: "biz", label: "xero-biz", desc: "Strategy & decisions", color: "biz" },
  "xero-marketing": { id: "marketing", label: "xero-marketing", desc: "Marketing & growth", color: "mkt" },
  "xero-work": { id: "work", label: "xero-work", desc: "Client work & dev", color: "work" },
};

/** ドメインの表示順（DOMAIN_META に無いプラグインは後ろに続ける） */
export const DOMAIN_ORDER = ["xero-biz", "xero-marketing", "xero-work"];

/** DOMAIN_META に無いプラグインへ割り当てる既定色トークン */
export const DEFAULT_COLOR = "work";

export type CategoryMeta = {
  kind: "skill" | "agent" | "hook" | "mcp";
  label: string;
  head: string;
  statLabel: string;
  tag: string;
};

// カテゴリ = セクションの単位。0件のカテゴリは UI 側でセクションごと非表示にする。
export const CATEGORIES: CategoryMeta[] = [
  { kind: "skill", label: "Skills", head: "Skills", statLabel: "skills", tag: "SKILL" },
  { kind: "agent", label: "Agents", head: "Agents", statLabel: "agents", tag: "AGENT" },
  { kind: "hook", label: "Hooks", head: "Hooks", statLabel: "hooks", tag: "HOOK" },
  { kind: "mcp", label: "MCP", head: "MCP", statLabel: "mcp", tag: "MCP" },
];
