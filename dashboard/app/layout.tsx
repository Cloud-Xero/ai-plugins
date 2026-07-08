import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "xero plugin catalog",
  description:
    "Cloud-Xero's personal Claude Code plugin catalog. Skills and agents listed from their frontmatter.",
};

// ハイドレーション前にテーマを確定させてチラつきを防ぐ。
const themeScript = `(function(){try{var t=localStorage.getItem('theme');if(t!=='light'&&t!=='dark'){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}document.documentElement.setAttribute('data-theme',t);}catch(e){}})();`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
