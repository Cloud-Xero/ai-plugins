import { loadCatalog } from "../lib/catalog";
import Catalog from "../components/Catalog";

// 静的エクスポート時（next build）にビルド時点で plugins/ を読み込む。
export default function Page() {
  const { domains, items } = loadCatalog();
  return <Catalog domains={domains} items={items} />;
}
