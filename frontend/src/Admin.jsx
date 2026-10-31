import { useEffect, useRef, useState } from "react";
import "./admin.css";

const API = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");
const emptyShop = { name: "", location: "" };
const emptyItem = {
  name: "",
  description: "",
  price: "",
  category: "Main dish",
  stall_id: "",
  is_available: true,
};
const money = new Intl.NumberFormat("en-PH", {
  style: "currency",
  currency: "PHP",
});

export default function Admin() {
  // Access tokens stay in memory. Reloading or closing the page requires sign-in.
  const [token, setToken] = useState("");
  const [config, setConfig] = useState(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [shops, setShops] = useState([]);
  const [items, setItems] = useState([]);
  const [tab, setTab] = useState("menus");
  const [draft, setDraft] = useState(null);
  const [editing, setEditing] = useState(null);
  const [pendingDelete, setPendingDelete] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [search, setSearch] = useState("");
  const [loaded, setLoaded] = useState(false);
  const [configAttempt, setConfigAttempt] = useState(0);
  const [configLoading, setConfigLoading] = useState(true);
  const [shopFilter, setShopFilter] = useState("");
  const [expiresAt, setExpiresAt] = useState(null);
  const lock = useRef(false);
  const formRef = useRef(null);
  const formOpen = Boolean(draft);

  useEffect(() => {
    if (formOpen) {
      formRef.current?.scrollIntoView({ behavior: "instant", block: "start" });
      formRef.current?.querySelector("input")?.focus({ preventScroll: true });
    }
  }, [formOpen, editing]);

  useEffect(() => {
    if (!expiresAt) return;
    const timer = setTimeout(
      () => {
        setToken("");
        setDraft(null);
        setPendingDelete(null);
        setLoaded(false);
        setShops([]);
        setItems([]);
        setExpiresAt(null);
        setError("Your session has expired. Please sign in again.");
      },
      Math.max(0, expiresAt - Date.now()),
    );
    return () => clearTimeout(timer);
  }, [expiresAt]);

  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;
    const timeout = setTimeout(() => controller.abort(), 75000);
    setConfigLoading(true);
    setConfig(null);
    fetch(`${API}/api/admin/auth-config`, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok)
          throw new Error(
            "Administrator sign-in needs configuration. You can still browse the public menu.",
          );
        return response.json();
      })
      .then((data) => {
        if (
          typeof data.url !== "string" ||
          !data.url.startsWith("https://") ||
          typeof data.publishable_key !== "string"
        )
          throw new Error(
            "Sign-in configuration is unavailable. Please contact the administrator.",
          );
        if (!cancelled) {
          setConfig(data);
          setError("");
        }
      })
      .catch((err) => {
        if (!cancelled)
          setError(
            err.name === "AbortError"
              ? "Sign-in service took too long. Please retry."
              : err instanceof TypeError
                ? "Could not reach the sign-in service. Please retry."
                : err.message,
          );
      })
      .finally(() => {
        clearTimeout(timeout);
        if (!cancelled) setConfigLoading(false);
      });
    return () => {
      cancelled = true;
      clearTimeout(timeout);
      controller.abort();
    };
  }, [configAttempt]);

  function clearSession() {
    setToken("");
    setDraft(null);
    setPendingDelete(null);
    setShops([]);
    setItems([]);
    setLoaded(false);
    setPassword("");
    setExpiresAt(null);
    setShopFilter("");
    setSearch("");
  }

  async function api(path, options = {}, accessToken = token) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      signal: AbortSignal.timeout(75000),
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
    });
    if (response.status === 401) {
      clearSession();
      throw new Error("Your session has expired. Please sign in again.");
    }
    if (response.status === 403) {
      clearSession();
      throw new Error("This account does not have administrator access.");
    }
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      const fields = Array.isArray(data.detail)
        ? [
            ...new Set(
              data.detail
                .map((issue) => issue.loc?.slice(1).join("."))
                .filter(Boolean),
            ),
          ]
        : [];
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : fields.length
            ? `Please check: ${fields.join(", ")}. Required fields, prices and categories must be valid.`
            : "Check the fields and try again. Names, shops and prices must be valid.",
      );
    }
    return response.status === 204 ? null : response.json();
  }

  async function load(accessToken = token) {
    const [shopData, menuData] = await Promise.all([
      api("/api/stalls", {}, accessToken),
      api("/api/menu-items", {}, accessToken),
    ]);
    if (!Array.isArray(shopData) || !Array.isArray(menuData))
      throw new Error(
        "The record list could not be read. Please refresh the list.",
      );
    setShops(shopData);
    setItems(menuData);
    setLoaded(true);
  }

  async function run(action) {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
    } catch (err) {
      setError(
        err.name === "TimeoutError"
          ? "The service took too long. Refresh the list before retrying a change."
          : err instanceof TypeError
            ? "Connection lost. Refresh the list before retrying a change."
            : err.message,
      );
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }

  function login(event) {
    event.preventDefault();
    if (!config || busy) return;
    run(async () => {
      let response;
      try {
        response = await fetch(
          `${config.url}/auth/v1/token?grant_type=password`,
          {
            method: "POST",
            headers: {
              apikey: config.publishable_key,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ email: email.trim(), password }),
            signal: AbortSignal.timeout(20000),
          },
        );
      } finally {
        setPassword("");
      }
      if (!response.ok)
        throw new Error(
          response.status === 429
            ? "Too many sign-in attempts. Please wait and try again."
            : "Could not sign in. Check your administrator email and password.",
        );
      const session = await response.json();
      if (typeof session.access_token !== "string")
        throw new Error(
          "Sign-in returned an invalid session. Please try again.",
        );
      await api("/api/admin/me", {}, session.access_token);
      const seconds = Number(session.expires_in);
      if (!Number.isFinite(seconds) || seconds <= 0 || seconds > 86400)
        throw new Error(
          "Sign-in returned an invalid expiry. Please try again.",
        );
      setToken(session.access_token);
      setExpiresAt(Date.now() + seconds * 1000);
      await load(session.access_token);
    });
  }

  function startEdit(record = null) {
    setEditing(record?.id ?? null);
    setPendingDelete(null);
    setError("");
    setNotice("");
    setDraft(
      tab === "shops"
        ? record
          ? { name: record.name, location: record.location }
          : { ...emptyShop }
        : record
          ? {
              name: record.name,
              description: record.description || "",
              price: record.price,
              category: record.category,
              stall_id: String(record.stall_id),
              is_available: record.is_available,
            }
          : {
              ...emptyItem,
              stall_id: shopFilter || String(shops[0]?.id || ""),
            },
    );
  }

  function save(event) {
    event.preventDefault();
    if (!draft.name.trim() || (tab === "shops" && !draft.location.trim())) {
      setError("Name and location cannot contain only spaces.");
      return;
    }
    const path = tab === "shops" ? "/api/stalls" : "/api/menu-items";
    const payload =
      tab === "shops"
        ? draft
        : {
            ...draft,
            stall_id: Number(draft.stall_id),
            description: draft.description.trim() || null,
          };
    run(async () => {
      await api(`${path}${editing ? `/${editing}` : ""}`, {
        method: editing ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      setDraft(null);
      setNotice(
        "Saved successfully. Visitors will see the change when they refresh the menu.",
      );
      try {
        await load();
      } catch {
        setError(
          "Saved, but the list could not refresh. Use Refresh list; do not submit the item again.",
        );
      }
    });
  }

  function remove() {
    run(async () => {
      await api(
        `${tab === "shops" ? "/api/stalls" : "/api/menu-items"}/${pendingDelete.id}`,
        { method: "DELETE" },
      );
      setPendingDelete(null);
      setNotice("Record deleted.");
      try {
        await load();
      } catch {
        setError("Deleted, but the list could not refresh. Use Refresh list.");
      }
    });
  }

  const records = (tab === "shops" ? shops : items).filter(
    (record) =>
      (tab === "shops" ||
        !shopFilter ||
        String(record.stall_id) === shopFilter) &&
      `${record.name} ${record.stall_name || ""}`
        .toLowerCase()
        .includes(search.toLowerCase()),
  );
  return (
    <div className="admin-page">
      <header className="admin-header">
        <a className="brand" href="#top">
          <img src="/animo-mark.png" alt="" width="40" height="40" />
          AnimoMeals
        </a>
        <a href="#menu">Back to public menu</a>
        {token && (
          <button
            onClick={() => {
              clearSession();
              setError("");
              setNotice("Signed out on this device.");
            }}
            disabled={busy}
          >
            Sign out
          </button>
        )}
      </header>
      <main className="admin-main">
        <p className="eyebrow">SHOP & MENU MANAGEMENT</p>
        <h1>Administrator workspace</h1>
        <p>
          Maintain regular meals and listed prices. Stock may change at the
          shop.
        </p>
        {error && (
          <p className="admin-alert error" role="alert">
            {error}
          </p>
        )}
        {notice && (
          <p className="admin-alert" role="status">
            {notice}
          </p>
        )}
        {!token ? (
          <form className="admin-panel login-panel" onSubmit={login}>
            <h2>Sign in</h2>
            <p>
              Use your AnimoMeals administrator account. This is separate from
              your database password.
            </p>
            <label>
              Email
              <input
                type="email"
                autoComplete="username"
                required
                maxLength="254"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={busy}
              />
            </label>
            <label>
              Password
              <input
                type="password"
                autoComplete="current-password"
                required
                maxLength="256"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={busy}
              />
            </label>
            {configLoading && (
              <p role="status">Connecting to the sign-in service…</p>
            )}
            <button className="admin-primary" disabled={!config || busy}>
              {busy ? "Signing in…" : "Sign in"}
            </button>
            {!configLoading && !config && (
              <button
                type="button"
                onClick={() => setConfigAttempt((value) => value + 1)}
              >
                Retry connection
              </button>
            )}
            <small>
              Your session stays in memory and ends when this page reloads.
            </small>
          </form>
        ) : (
          <>
            <div className="admin-summary" aria-label="Catalog summary">
              <div>
                <strong>{shops.length}</strong>
                <span>Shops</span>
              </div>
              <div>
                <strong>{items.length}</strong>
                <span>Menu items</span>
              </div>
              <div>
                <strong>
                  {items.filter((item) => item.is_available).length}
                </strong>
                <span>Listed available</span>
              </div>
            </div>
            <div className="admin-toolbar">
              <div className="admin-tabs" aria-label="Manage records">
                {["menus", "shops"].map((value) => (
                  <button
                    key={value}
                    disabled={busy}
                    aria-pressed={tab === value}
                    onClick={() => {
                      setTab(value);
                      setDraft(null);
                      setPendingDelete(null);
                      setSearch("");
                      setError("");
                    }}
                  >
                    {value === "menus" ? "Menu items" : "Shops"}
                  </button>
                ))}
              </div>
              <button disabled={busy} onClick={() => run(() => load())}>
                Refresh list
              </button>
              <button
                className="admin-primary"
                disabled={busy || (tab === "menus" && !shops.length)}
                onClick={() => startEdit()}
              >
                Add {tab === "shops" ? "shop" : "menu item"}
              </button>
            </div>
            {!loaded && (
              <p role="status">
                Load the list to begin. The hosted service may take a moment to
                wake up.
              </p>
            )}
            {tab === "menus" && loaded && !shops.length && (
              <p>Add a shop first, then add its menu items.</p>
            )}
            {draft && (
              <form className="admin-panel" ref={formRef} onSubmit={save}>
                <h2>
                  {editing ? "Edit" : "Add"}{" "}
                  {tab === "shops" ? "shop" : "menu item"}
                </h2>
                <fieldset disabled={busy} className="admin-fields">
                  <label>
                    Name
                    <input
                      required
                      maxLength={tab === "shops" ? 100 : 120}
                      value={draft.name}
                      onChange={(e) =>
                        setDraft({ ...draft, name: e.target.value })
                      }
                    />
                  </label>
                  {tab === "shops" ? (
                    <label>
                      Location / landmark
                      <input
                        required
                        maxLength="200"
                        placeholder="Use ‘Location to be confirmed’ if unknown"
                        value={draft.location}
                        onChange={(e) =>
                          setDraft({ ...draft, location: e.target.value })
                        }
                      />
                    </label>
                  ) : (
                    <>
                      <label>
                        Shop
                        <select
                          aria-label="Shop"
                          required
                          value={draft.stall_id}
                          onChange={(e) =>
                            setDraft({ ...draft, stall_id: e.target.value })
                          }
                        >
                          {shops.map((shop) => (
                            <option key={shop.id} value={shop.id}>
                              {shop.name}
                            </option>
                          ))}
                        </select>
                      </label>
                      <label>
                        Price (₱)
                        <input
                          type="number"
                          required
                          min="0.01"
                          max="10000"
                          step="0.01"
                          value={draft.price}
                          onChange={(e) =>
                            setDraft({ ...draft, price: e.target.value })
                          }
                        />
                      </label>
                      <label>
                        Category
                        <select
                          aria-label="Category"
                          value={draft.category}
                          onChange={(e) =>
                            setDraft({ ...draft, category: e.target.value })
                          }
                        >
                          {["Main dish", "Drink", "Snack", "Side"].map(
                            (category) => (
                              <option key={category}>{category}</option>
                            ),
                          )}
                        </select>
                      </label>
                      <label className="admin-wide">
                        Description (optional)
                        <textarea
                          maxLength="2000"
                          value={draft.description}
                          onChange={(e) =>
                            setDraft({ ...draft, description: e.target.value })
                          }
                        />
                      </label>
                      <label className="admin-checkbox">
                        <input
                          type="checkbox"
                          checked={draft.is_available}
                          onChange={(e) =>
                            setDraft({
                              ...draft,
                              is_available: e.target.checked,
                            })
                          }
                        />
                        Listed as available
                      </label>
                      <small>
                        Use this to hide sold-out or discontinued meals from
                        available-only results. It does not track live stock.
                      </small>
                    </>
                  )}
                </fieldset>
                <div className="admin-actions">
                  <button className="admin-primary" disabled={busy}>
                    {busy ? "Saving…" : "Save changes"}
                  </button>
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => setDraft(null)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
            {pendingDelete && (
              <section
                className="admin-panel delete-confirm"
                aria-labelledby="delete-title"
              >
                <h2 id="delete-title">Delete {pendingDelete.name}?</h2>
                <p>
                  This permanently removes the record. Shops with menu items
                  cannot be deleted.
                </p>
                <div className="admin-actions">
                  <button
                    className="admin-danger"
                    disabled={busy}
                    onClick={remove}
                  >
                    Confirm delete
                  </button>
                  <button
                    disabled={busy}
                    onClick={() => setPendingDelete(null)}
                  >
                    Keep record
                  </button>
                </div>
              </section>
            )}
            <div className="admin-list-filters">
              <label className="admin-search">
                Search {tab === "shops" ? "shops" : "menu items"}
                <input
                  type="search"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </label>
              {tab === "menus" && (
                <label className="admin-search">
                  Filter by shop
                  <select
                    value={shopFilter}
                    onChange={(e) => setShopFilter(e.target.value)}
                  >
                    <option value="">All shops</option>
                    {shops.map((shop) => (
                      <option key={shop.id} value={shop.id}>
                        {shop.name}
                      </option>
                    ))}
                  </select>
                </label>
              )}
            </div>
            <p role="status">
              {records.length} {tab === "shops" ? "shops" : "menu items"}
              {busy ? " · Working…" : ""}
            </p>
            <div className="admin-records">
              {records.map((record) => (
                <article className="admin-record" key={record.id}>
                  <div>
                    <h3>{record.name}</h3>
                    {tab === "shops" ? (
                      <p>{record.location}</p>
                    ) : (
                      <>
                        <p>
                          {record.stall_name} · {record.category} ·{" "}
                          <strong>{money.format(record.price)}</strong>
                        </p>
                        <p>
                          {record.is_available
                            ? "Listed as available"
                            : "Unavailable"}{" "}
                          · Last updated{" "}
                          {new Date(record.updated_at).toLocaleDateString(
                            "en-PH",
                          )}
                        </p>
                        {record.description && <p>{record.description}</p>}
                      </>
                    )}
                  </div>
                  <div className="admin-actions">
                    <button disabled={busy} onClick={() => startEdit(record)}>
                      Edit<span className="sr-only"> {record.name}</span>
                    </button>
                    <button
                      className="admin-danger-text"
                      disabled={busy}
                      onClick={() => {
                        setDraft(null);
                        setPendingDelete(record);
                        setError("");
                      }}
                    >
                      Delete<span className="sr-only"> {record.name}</span>
                    </button>
                  </div>
                </article>
              ))}
            </div>
            {loaded && !records.length && (
              <p className="admin-panel">
                No records found. Add a record or clear your search.
              </p>
            )}
          </>
        )}
      </main>
    </div>
  );
}
