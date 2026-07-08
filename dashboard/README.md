# dashboard

`plugins/` 配下のスキル・エージェントの frontmatter を読み込んで一覧表示する、公開用ダッシュボード（Next.js 静的サイト）。GitHub Actions で GitHub Pages に自動デプロイされる。

公開URL: https://cloud-xero.github.io/ai-plugins/

## 何を表示するか

- リポジトリの `plugins/*/skills/*/SKILL.md` と `plugins/*/agents/*.md` を走査
- frontmatter（`name` / `description` / `model` / `tools` / `argument-hint` / `delegates`）を抽出
- 詳細モーダルではファイル全文（スキルは `SKILL.md` + `INSTRUCTIONS.md`）を表示・コピー可能
- ドメイン（xero-biz / xero-marketing / xero-work）× カテゴリ（Skills / Agents / Hooks / MCP）で整理
- 検索・種別フィルタ・ドメインフィルタ、グリッド／テーブルのビュー切替、ライト／ダーク切替

カテゴリは項目が 1 件以上あるときだけ表示される。hooks / MCP は現状 0 件なので出ない（プラグインに追加されれば自動で現れる。ローダーの拡張ポイントは `lib/catalog.ts` のコメント参照）。

## ローカル開発

パッケージマネージャは **pnpm**、開発ポートは **3011** に固定。

```bash
cd dashboard
pnpm install
pnpm dev          # http://localhost:3011
```

## ビルド（静的エクスポート）

```bash
pnpm build        # out/ に静的ファイルを生成
```

`next.config.mjs` で `output: "export"` を指定。本番ビルド時のみ `basePath: "/ai-plugins"` が付く（GitHub Pages のプロジェクトページ配信のため）。ローカルの `pnpm dev` では basePath なし。

## デプロイ

`.github/workflows/deploy-dashboard.yml` が `main` への push（`plugins/**` または `dashboard/**` の変更時）で発火し、ビルドして Pages に公開する。手動実行（workflow_dispatch）も可。

初回のみ、リポジトリの **Settings → Pages → Build and deployment → Source** を **GitHub Actions** に設定する必要がある。

## 構成

```
dashboard/
├── app/
│   ├── globals.css     # デザイントークン + 全スタイル
│   ├── layout.tsx      # テーマ初期化（チラつき防止スクリプト）
│   └── page.tsx        # ビルド時に loadCatalog() を実行しデータを注入
├── components/
│   └── Catalog.tsx     # 一覧・フィルタ・モーダル・テーマ切替（クライアント）
├── lib/
│   ├── config.ts       # ドメイン/カテゴリの表示メタ（色・ラベル・順序）
│   └── catalog.ts      # plugins/ を走査し frontmatter とファイル全文を読む
└── next.config.mjs
```

## 新しいドメイン（プラグイン）を足したとき

`lib/config.ts` の `DOMAIN_META` と `DOMAIN_ORDER` にエントリを追加する（短い id・日本語ラベル・色トークン）。未登録のプラグインも既定色で表示はされるが、色と順番を意図通りにするならここに追記する。色トークンを増やす場合は `app/globals.css` に `--<color>` / `--<color>-tint` と `.dot.<color>` を追加する。
