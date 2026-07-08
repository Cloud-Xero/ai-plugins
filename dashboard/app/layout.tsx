import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "xero plugin catalog",
  description:
    "Cloud-Xero 個人用 Claude Code プラグインカタログ。スキル・エージェントを frontmatter から一覧化。",
};

// ハイドレーション前にテーマを確定させてチラつきを防ぐ。
const themeScript = `(function(){try{var t=localStorage.getItem('theme');if(t!=='light'&&t!=='dark'){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}document.documentElement.setAttribute('data-theme',t);}catch(e){}})();`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
