/** @type {import('next').NextConfig} */

// GitHub Pages のプロジェクトページ（https://cloud-xero.github.io/ai-plugins/）配信のため
// 本番ビルド時のみ basePath を付与する。CI からは PAGES_BASE_PATH で上書きできる。
const basePath =
  process.env.PAGES_BASE_PATH ??
  (process.env.NODE_ENV === "production" ? "/ai-plugins" : "");

const nextConfig = {
  output: "export",
  basePath,
  assetPrefix: basePath || undefined,
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
