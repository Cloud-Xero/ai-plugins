"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type CSSProperties,
} from "react";
import { CATEGORIES, type DomainMeta } from "../lib/config";
import type { CatalogItem, CatalogFile } from "../lib/catalog";

type Props = { domains: DomainMeta[]; items: CatalogItem[] };

type Enriched = CatalogItem & { i: number; hay: string };

/** ドメイン色を CSS 変数として渡す */
function domVars(color: string): CSSProperties {
  return {
    ["--dc"]: `var(--${color})`,
    ["--dc-tint"]: `var(--${color}-tint)`,
  } as CSSProperties;
}

function NameText({ item }: { item: CatalogItem }) {
  if (item.kind === "skill") {
    return (
      <>
        <span className="sl">/</span>
        {item.name}
      </>
    );
  }
  return <>{item.name}</>;
}

function ModelBadge({ model }: { model: string | null }) {
  if (!model) return null;
  return <span className={`model ${model}`}>{model}</span>;
}

const CopyIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="9" y="9" width="11" height="11" rx="2" />
    <path d="M5 15V5a2 2 0 0 1 2-2h10" />
  </svg>
);

function CopyButton({ text }: { text: string }) {
  const [state, setState] = useState<"idle" | "done" | "fail">("idle");
  const onClick = useCallback(async () => {
    let ok = false;
    try {
      await navigator.clipboard.writeText(text);
      ok = true;
    } catch {
      try {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        ok = document.execCommand("copy");
        document.body.removeChild(ta);
      } catch {
        ok = false;
      }
    }
    setState(ok ? "done" : "fail");
    window.setTimeout(() => setState("idle"), 1600);
  }, [text]);

  return (
    <button className={`copy${state === "done" ? " done" : ""}`} onClick={onClick} type="button">
      <CopyIcon />
      <span>{state === "done" ? "Copied" : state === "fail" ? "Failed" : "Copy"}</span>
    </button>
  );
}

function Detail({
  item,
  dm,
  onClose,
}: {
  item: CatalogItem;
  dm: DomainMeta;
  onClose: () => void;
}) {
  const cat = CATEGORIES.find((c) => c.kind === item.kind)!;
  const meta: [string, React.ReactNode][] = [
    ["Plugin", dm.label],
    ["Files", item.files.map((f) => <code key={f.filename}>{f.filename}&nbsp; </code>)],
  ];
  if (item.argHint) meta.push(["Args", <code>{item.argHint}</code>]);
  if (item.model) meta.push(["Model", <ModelBadge model={item.model} />]);
  if (item.tools)
    meta.push([
      "Tools",
      <span className="chips">
        {item.tools.map((t) => (
          <span className="chip" key={t}>{t}</span>
        ))}
      </span>,
    ]);
  if (item.delegates)
    meta.push([
      "Delegates",
      <span className="chips">
        {item.delegates.map((x) => (
          <span className="chip dl" key={x}>{x}</span>
        ))}
      </span>,
    ]);

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={item.name} style={domVars(dm.color)}>
        <div className="modal-body">
          <div className="m-top">
            <div className="m-eyebrow">
              <span className={`dot ${dm.color}`} />
              {dm.label} · {cat.head}
            </div>
            <button className="m-close" aria-label="Close" onClick={onClose} type="button" autoFocus>
              ×
            </button>
          </div>
          <div className="m-name">
            <NameText item={item} />
          </div>
          <p className="m-desc">{item.description}</p>
          <dl className="m-meta">
            {meta.map(([k, v], i) => (
              <div key={i} style={{ display: "contents" }}>
                <dt>{k}</dt>
                <dd>{v}</dd>
              </div>
            ))}
          </dl>
          {item.files.map((f: CatalogFile) => (
            <div className="fileblock" key={f.filename}>
              <div className="raw-head">
                <h4>{f.filename}</h4>
                <CopyButton text={f.content} />
              </div>
              <pre className="raw">{f.content}</pre>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Card({ item, dm, onOpen }: { item: Enriched; dm: DomainMeta; onOpen: () => void }) {
  return (
    <button className="card" style={domVars(dm.color)} onClick={onOpen} type="button">
      <span className="card-top">
        <span className="cmd">
          <NameText item={item} />
        </span>
        <ModelBadge model={item.model} />
      </span>
      <p>{item.description}</p>
      {item.delegates ? (
        <span className="deleg">
          <span className="arw">delegates ↳</span>
          {item.delegates.map((x) => (
            <span className="chip dl" key={x}>{x}</span>
          ))}
        </span>
      ) : item.tools ? (
        <span className="chips">
          {item.tools.map((t) => (
            <span className="chip" key={t}>{t}</span>
          ))}
        </span>
      ) : null}
    </button>
  );
}

export default function Catalog({ domains, items }: Props) {
  const domById = useMemo(
    () => new Map(domains.map((d) => [d.id, d])),
    [domains],
  );

  const enriched: Enriched[] = useMemo(
    () =>
      items.map((it, i) => ({
        ...it,
        i,
        hay: [it.name, it.description, ...(it.tools ?? []), ...(it.delegates ?? [])]
          .join(" ")
          .toLowerCase(),
      })),
    [items],
  );

  const [kind, setKind] = useState("all");
  const [dom, setDom] = useState("all");
  const [q, setQ] = useState("");
  const [view, setView] = useState<"grid" | "table">("grid");
  const [selected, setSelected] = useState<number | null>(null);
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const t = document.documentElement.getAttribute("data-theme");
    if (t === "dark" || t === "light") setTheme(t);
  }, []);

  const toggleTheme = () => {
    const t = theme === "dark" ? "light" : "dark";
    setTheme(t);
    document.documentElement.setAttribute("data-theme", t);
    try {
      localStorage.setItem("theme", t);
    } catch {
      /* ignore */
    }
  };

  const term = q.trim().toLowerCase();
  const matches = useCallback(
    (it: Enriched) =>
      (kind === "all" || it.kind === kind) &&
      (dom === "all" || it.domain === dom) &&
      (!term || it.hay.includes(term)),
    [kind, dom, term],
  );

  const visible = useMemo(() => enriched.filter(matches), [enriched, matches]);

  // モーダル: スクロールロック + Esc で閉じる
  useEffect(() => {
    if (selected === null) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelected(null);
    };
    document.addEventListener("keydown", onKey);
    document.body.classList.add("modal-open");
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.classList.remove("modal-open");
    };
  }, [selected]);

  const presentCats = CATEGORIES.filter((c) => enriched.some((i) => i.kind === c.kind));
  const stats = [
    { n: domains.length, l: "plugins" },
    ...presentCats.map((c) => ({
      n: enriched.filter((i) => i.kind === c.kind).length,
      l: c.statLabel,
    })),
  ];

  const dotClass = (id: string) => domById.get(id)?.color ?? "work";

  return (
    <>
      <header className="wrap">
        <div className="prompt">
          <span className="path">~/ai-plugins</span> <span>❯</span> catalog --list
          <span className="cursor" />
        </div>
        <h1>
          <span className="slash">xero</span> plugin catalog
        </h1>
        <p className="lede">
          Cloud-Xero&apos;s personal Claude Code plugin catalog, with skills and
          agents split across {domains.length} domains. Each card is generated
          from the frontmatter of{" "}
          <span className="nowrap">
            <code>SKILL.md</code> / <code>agents/*.md</code>
          </span>{" "}
          in the repo.
        </p>
        <div className="stats">
          {stats.map((s) => (
            <div className="stat" key={s.l}>
              <span className="n">{s.n}</span>
              <span className="l">{s.l}</span>
            </div>
          ))}
        </div>
      </header>

      <div className="toolbar">
        <div className="wrap toolbar-inner">
          <label className="search">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <circle cx="11" cy="11" r="7" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <input
              type="search"
              placeholder="Search by name, description, or tool…"
              autoComplete="off"
              aria-label="Search"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </label>

          <div className="seg" role="group" aria-label="Filter by type">
            <button aria-pressed={kind === "all"} onClick={() => setKind("all")} type="button">
              All
            </button>
            {presentCats.map((c) => (
              <button key={c.kind} aria-pressed={kind === c.kind} onClick={() => setKind(c.kind)} type="button">
                {c.label}
              </button>
            ))}
          </div>

          <div className="seg" role="group" aria-label="Filter by domain">
            <button aria-pressed={dom === "all"} onClick={() => setDom("all")} type="button">
              All
            </button>
            {domains.map((d) => (
              <button key={d.id} aria-pressed={dom === d.id} onClick={() => setDom(d.id)} type="button">
                <span className={`dot ${d.color}`} />
                {d.id}
              </button>
            ))}
          </div>

          <div className="seg" id="viewseg" role="group" aria-label="Toggle view">
            <button aria-pressed={view === "grid"} onClick={() => setView("grid")} type="button" title="Grid view">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                <rect x="3" y="3" width="8" height="8" rx="1" />
                <rect x="13" y="3" width="8" height="8" rx="1" />
                <rect x="3" y="13" width="8" height="8" rx="1" />
                <rect x="13" y="13" width="8" height="8" rx="1" />
              </svg>
              Grid
            </button>
            <button aria-pressed={view === "table"} onClick={() => setView("table")} type="button" title="Table view">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 5h18M3 12h18M3 19h18" />
              </svg>
              Table
            </button>
          </div>

          <button
            className="iconbtn"
            onClick={toggleTheme}
            type="button"
            aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
            title="Toggle theme"
          >
            {theme === "dark" ? (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="4.2" />
                <path d="M12 2v2.5M12 19.5V22M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2 12h2.5M19.5 12H22M4.2 19.8 6 18M18 6l1.8-1.8" />
              </svg>
            ) : (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
              </svg>
            )}
          </button>
        </div>
      </div>

      <main className="wrap">
        {visible.length === 0 ? (
          <p className="empty" style={{ display: "block" }}>
            no matches — nothing fits the current filters.
          </p>
        ) : view === "grid" ? (
          <div id="view-grid">
            {domains.map((dm) => {
              const inDom = visible.filter((v) => v.domain === dm.id);
              if (!inDom.length) return null;
              const summary = CATEGORIES.map((c) => ({
                c,
                n: inDom.filter((v) => v.kind === c.kind).length,
              }))
                .filter((x) => x.n > 0)
                .map((x) => `${x.n} ${x.c.statLabel}`)
                .join(" · ");
              return (
                <section className="domain" key={dm.id} style={domVars(dm.color)}>
                  <div className="domain-head">
                    <span className="id">{dm.label}</span>
                    <span className="desc">{dm.desc}</span>
                    <span className="count">{summary}</span>
                  </div>
                  {CATEGORIES.map((cat) => {
                    const list = inDom.filter((v) => v.kind === cat.kind);
                    if (!list.length) return null;
                    return (
                      <div className="catgroup" key={cat.kind}>
                        <h3 className="cat-head">
                          {cat.head} <span className="cc">{list.length}</span>
                          <span className="line" />
                        </h3>
                        <div className="grid">
                          {list.map((v) => (
                            <Card key={v.name} item={v} dm={dm} onOpen={() => setSelected(v.i)} />
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </section>
              );
            })}
          </div>
        ) : (
          <div id="view-table" style={{ display: "block" }}>
            <div className="tablewrap">
              <table>
                <colgroup>
                  <col style={{ width: "92px" }} />
                  <col style={{ width: "200px" }} />
                  <col style={{ width: "124px" }} />
                  <col />
                </colgroup>
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Name</th>
                    <th>Domain</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {visible.map((v) => {
                    const dm = domById.get(v.domain);
                    const cat = CATEGORIES.find((c) => c.kind === v.kind)!;
                    return (
                      <tr
                        key={v.name}
                        tabIndex={0}
                        style={{ ["--rc"]: `var(--${dm?.color ?? "work"})` } as CSSProperties}
                        onClick={() => setSelected(v.i)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            setSelected(v.i);
                          }
                        }}
                      >
                        <td>
                          <span className={`kindtag ${v.kind}`}>{cat.tag}</span>
                        </td>
                        <td className="name">
                          <NameText item={v} />
                        </td>
                        <td className="dom">
                          <span className="t">
                            <span className={`dot ${dotClass(v.domain)}`} />
                            {v.domain}
                          </span>
                        </td>
                        <td className="desc">{v.description}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      <footer className="wrap">
        <span>
          <span className="k">source</span>{" "}
          <a href="https://github.com/Cloud-Xero/ai-plugins">github.com/Cloud-Xero/ai-plugins</a>
        </span>
        <span>
          <span className="k">install</span> claude plugin install &lt;name&gt;@cloud-xero-plugins
        </span>
        <span>
          <span className="k">generated</span> from frontmatter
        </span>
      </footer>

      {selected !== null &&
        (() => {
          const item = items[selected];
          const dm = domById.get(item.domain);
          if (!dm) return null;
          return <Detail item={item} dm={dm} onClose={() => setSelected(null)} />;
        })()}
    </>
  );
}
