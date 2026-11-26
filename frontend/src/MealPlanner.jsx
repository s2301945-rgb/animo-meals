import { useEffect, useState } from "react";
import { verifyStagingEnvironment } from "./Staging.jsx";
import "./planner.css";

const API = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");
const TOKEN_KEY = `animomeals.meal-box-key.${API}`;
const money = (value) =>
  new Intl.NumberFormat("en-PH", { style: "currency", currency: "PHP" }).format(
    value,
  );

function browserKey(create = false) {
  try {
    let key = localStorage.getItem(TOKEN_KEY);
    if (key && !/^[a-f0-9]{64}$/.test(key))
      throw new Error("Invalid browser key.");
    if (!key && create) {
      key = Array.from(crypto.getRandomValues(new Uint8Array(32)), (n) =>
        n.toString(16).padStart(2, "0"),
      ).join("");
      localStorage.setItem(TOKEN_KEY, key);
    }
    return key;
  } catch {
    throw new Error(
      "This browser cannot access saved meal boxes. Enable site storage or use menu browsing instead.",
    );
  }
}

async function request(path, { method = "GET", body, owned = false } = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 75000);
  try {
    await verifyStagingEnvironment(API, controller.signal);
    const headers = { "Content-Type": "application/json" };
    if (owned) {
      const key = browserKey(method === "POST");
      if (!key && method === "GET") return [];
      if (!key)
        throw new Error("This browser no longer has access to that meal box.");
      headers.Authorization = `Bearer ${key}`;
    }
    const response = await fetch(`${API}${path}`, {
      method,
      headers,
      signal: controller.signal,
      cache: "no-store",
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    if (response.status === 204) return null;
    const data = await response.json().catch(() => null);
    if (!response.ok)
      throw new Error(
        typeof data?.detail === "string"
          ? data.detail
          : response.status >= 500
            ? "The meal service is temporarily unavailable. Please try again."
            : "Check your budget and meal details, then try again.",
      );
    if (data === null)
      throw new Error("The meal service sent an unreadable response. Please try again.");
    return data;
  } catch (error) {
    if (error.name === "AbortError")
      throw new Error("The meal service took too long. Please try again.");
    if (error instanceof TypeError)
      throw new Error(
        "We couldn’t connect to the meal service. Check your connection and try again.",
      );
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

function MealLines({ items }) {
  return (
    <ul className="meal-lines">
      {items.map((item, index) => (
        <li key={`${item.name}-${index}`}>
          <div>
            <strong>{item.quantity > 1 ? `${item.quantity} × ` : ""}{item.name}</strong>
            <span>
              {item.shop_name} · {item.location}
            </span>
          </div>
          <b>{money(item.line_total ?? item.price)}</b>
        </li>
      ))}
    </ul>
  );
}

function MealBoxEditor({ plan, catalog, busy, onSave, onCancel }) {
  const [title, setTitle] = useState(plan.title);
  const [budget, setBudget] = useState(String(plan.budget));
  const [items, setItems] = useState(() =>
    plan.items.map((item) => ({ ...item, quantity: String(item.quantity ?? 1) })),
  );
  const [query, setQuery] = useState("");
  const validBudget = /^\d+(\.\d{1,2})?$/.test(budget) &&
    Number(budget) > 0 && Number(budget) <= 10000;
  const validQuantities = items.every((item) =>
    /^\d+$/.test(item.quantity) && Number(item.quantity) >= 1 && Number(item.quantity) <= 20,
  );
  const totalCents = items.reduce((total, item) =>
    total + Math.round(Number(item.price) * 100) * (Number(item.quantity) || 0), 0);
  const remainingCents = Math.round(Number(budget) * 100) - totalCents;
  const canSave = title.trim() && validBudget && validQuantities &&
    items.length > 0 && remainingCents >= 0;
  const choices = catalog.filter((item) => item.is_listed && Number(item.price) > 0 &&
    `${item.name} ${item.stall_name}`.toLowerCase().includes(query.trim().toLowerCase()));

  function addMeal(meal) {
    const index = items.findIndex((item) => item.menu_item_id === meal.id ||
      (!item.menu_item_id && item.name === meal.name &&
        item.shop_name === meal.stall_name && item.location === meal.location));
    if (index >= 0) {
      setItems(items.map((item, position) => position === index
        ? { ...item, quantity: String(Math.min(20, (Number(item.quantity) || 0) + 1)) }
        : item));
    } else {
      setItems([...items, { menu_item_id: meal.id, name: meal.name,
        shop_name: meal.stall_name, location: meal.location, price: meal.price, quantity: "1" }]);
    }
  }

  return (
    <form className="box-editor" onSubmit={(event) => {
      event.preventDefault();
      if (!canSave || busy) return;
      onSave({
        title: title.trim(), budget, expected_version: plan.version,
        items: items.map((item) => ({
          ...(item.id ? { saved_item_id: item.id } : { menu_item_id: item.menu_item_id }),
          quantity: Number(item.quantity),
        })),
      });
    }}>
      <fieldset disabled={busy}>
        <legend>Edit meal box</legend>
        <label htmlFor={`box-name-${plan.id}`}>Meal box name
          <input id={`box-name-${plan.id}`} value={title}
            onChange={(event) => setTitle(event.target.value)} maxLength={100} required autoFocus />
        </label>
        <label htmlFor={`box-budget-${plan.id}`}>Meal box budget (₱)
          <input id={`box-budget-${plan.id}`} inputMode="decimal" value={budget}
            onChange={(event) => setBudget(event.target.value)} required aria-invalid={!validBudget}
            aria-describedby={`box-budget-help-${plan.id}`} />
        </label>
        <p className="planner-small" id={`box-budget-help-${plan.id}`}>
          {validBudget ? "Set how much you want to spend on this box." : "Enter ₱0.01–₱10,000 with up to two decimal places."}
        </p>
        <ul className="editable-meals" aria-label="Meals in this box">
          {items.map((item, index) => (
            <li key={item.id ? `saved-${item.id}` : `menu-${item.menu_item_id}`}>
              <div className="editable-meal-info">
                <strong>{item.name}</strong>
                <span>{item.shop_name} · {money(item.price)} each</span>
              </div>
              <div className="editable-meal-controls">
                <label htmlFor={`quantity-${plan.id}-${index}`}>Quantity
                  <input id={`quantity-${plan.id}-${index}`} type="number" min="1" max="20" step="1"
                    value={item.quantity} required
                    aria-label={`Quantity for ${item.name}`}
                    onChange={(event) => setItems(items.map((row, position) =>
                      position === index ? { ...row, quantity: event.target.value } : row))} />
                </label>
                <button type="button" className="delete-button" aria-label={`Remove ${item.name}`}
                  onClick={() => setItems(items.filter((_, position) => position !== index))}>
                  Remove
                </button>
              </div>
            </li>
          ))}
        </ul>
        {!items.length && <p className="planner-small">Add at least one meal before saving.</p>}
        {!validQuantities && <p className="planner-small">Use whole quantities from 1 to 20.</p>}
        <details className="meal-picker">
          <summary>Add a meal</summary>
          <label htmlFor={`meal-search-${plan.id}`}>Search meals or shops
            <input id={`meal-search-${plan.id}`} type="search" value={query}
              onChange={(event) => setQuery(event.target.value)} placeholder="Try rice, chicken, or BAMSOYS" />
          </label>
          <ul className="meal-picker-list">
            {choices.map((meal) => {
              const existing = items.find((item) => item.menu_item_id === meal.id ||
                (!item.menu_item_id && item.name === meal.name &&
                  item.shop_name === meal.stall_name && item.location === meal.location));
              const atLimit = existing ? Number(existing.quantity) >= 20 : items.length >= 20;
              return (
                <li key={meal.id}>
                  <div><strong>{meal.name}</strong><span>{meal.stall_name} · {money(meal.price)} each</span></div>
                  <button type="button" className="secondary-button" disabled={atLimit}
                    aria-label={`Add ${meal.name} from ${meal.stall_name}`} onClick={() => addMeal(meal)}>
                    {atLimit ? "Limit reached" : "Add"}
                  </button>
                </li>
              );
            })}
          </ul>
          {!choices.length && <p className="planner-small">No listed meals found. Try another search or refresh the menu.</p>}
          <p className="planner-small">Up to 20 different meals, with 1–20 portions each.</p>
        </details>
        <div className={`meal-total ${validBudget && remainingCents < 0 ? "over-budget" : ""}`} role="status">
          <strong>{money(totalCents / 100)} total</strong>
          <span>{validBudget
            ? `${money(Math.abs(remainingCents) / 100)} ${remainingCents < 0 ? "over budget" : "left"}`
            : "Enter a valid budget"}</span>
        </div>
        {validBudget && remainingCents < 0 && <p className="planner-small">Increase your budget or reduce the meals before saving.</p>}
        <p className="planner-small">Existing meals keep their saved unit prices. Added meals use the current recorded menu price.</p>
        <div className="planner-actions">
          <button className="primary-button" disabled={busy || !canSave}>
            {busy ? "Saving…" : "Save changes"}
          </button>
          <button type="button" className="secondary-button" onClick={onCancel}>Cancel</button>
        </div>
      </fieldset>
    </form>
  );
}

function SavedBox({ plan, catalog, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function mutate(method, body) {
    setBusy(true);
    setError("");
    try {
      const updated = await request(`/api/plans/${plan.id}`, {
        owned: true,
        method,
        ...(body ? { body } : {}),
      });
      if (method === "DELETE") {
        onDelete(plan.id);
      } else {
        onUpdate(updated);
        setEditing(false);
      }
    } catch (failure) {
      setError(failure.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className="meal-box saved-meal-box" aria-label={plan.title}>
      <p className="saved-date">
        Saved {new Date(plan.created_at).toLocaleDateString("en-PH", {
          month: "short", day: "numeric", year: "numeric",
        })}
      </p>
      {editing ? (
        <MealBoxEditor plan={plan} catalog={catalog} busy={busy}
          onSave={(body) => mutate("PUT", body)}
          onCancel={() => { setEditing(false); setError(""); }} />
      ) : (
        <>
          <h3>{plan.title}</h3>
          <p className="box-summary">
            {plan.items.reduce((count, item) => count + (item.quantity ?? 1), 0)} portions · Budget {money(plan.budget)}
          </p>
          <div className="meal-total">
            <strong>{money(plan.total)} total</strong>
            <span>{money(plan.remaining)} left</span>
          </div>
          {expanded && (
            <div id={`box-details-${plan.id}`}>
              <MealLines items={plan.items} />
              <p className="planner-small">Prices saved with this box. Confirm current prices at the shop.</p>
            </div>
          )}
        </>
      )}
      {error && (
        <div className="planner-error" role="alert">
          <p>{error}</p>
          {editing && <button type="button" className="secondary-button" disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                const current = await request(`/api/plans/${plan.id}`, { owned: true });
                onUpdate(current);
                setEditing(false);
                setError("");
              } catch (failure) { setError(failure.message); }
              finally { setBusy(false); }
            }}>Discard edits and reload box</button>}
        </div>
      )}
      {!editing && (
        <div className="planner-actions">
          <button className="secondary-button"
            aria-expanded={expanded} aria-controls={`box-details-${plan.id}`}
            onClick={() => setExpanded(!expanded)}>
            {expanded ? "Hide details" : "View meals"}
          </button>
          <button className="secondary-button" disabled={busy || confirming || !plan.version}
            onClick={() => { setEditing(true); setError(""); }}>
            Edit meal box
          </button>
          <button className="delete-button" disabled={busy || confirming}
            onClick={() => { setConfirming(true); setError(""); }}>
            Delete
          </button>
        </div>
      )}
      {confirming && (
        <div className="delete-confirmation" role="group" aria-label="Confirm deletion">
          <p>Delete “{plan.title}”? This permanently removes the saved box.</p>
          <div className="planner-actions">
            <button className="delete-button" disabled={busy} onClick={() => mutate("DELETE")}>
              {busy ? "Deleting…" : "Yes, delete"}
            </button>
            <button className="secondary-button" disabled={busy}
              onClick={() => { setConfirming(false); setError(""); }}>
              Keep meal box
            </button>
          </div>
        </div>
      )}
    </article>
  );
}

export default function MealPlanner({ budget, onBudgetChange, highlights, catalog = [], children }) {
  const [preferences, setPreferences] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [savedError, setSavedError] = useState("");
  const [notice, setNotice] = useState("");
  const [plans, setPlans] = useState([]);
  const [saving, setSaving] = useState(null);
  const [savedSuggestions, setSavedSuggestions] = useState([]);
  const [boxNotice, setBoxNotice] = useState("");
  const [savedLoading, setSavedLoading] = useState(true);
  async function loadPlans() {
    const data = await request("/api/plans", { owned: true });
    if (!Array.isArray(data))
      throw new Error("Saved meal boxes could not be read. Please try again.");
    setPlans(data);
  }
  useEffect(() => {
    let active = true;
    request("/api/plans", { owned: true })
      .then((data) => {
        if (!Array.isArray(data))
          throw new Error("Saved meal boxes could not be read. Please try again.");
        if (active) setPlans(data);
      })
      .catch((failure) => {
        if (active) setSavedError(failure.message);
      })
      .finally(() => {
        if (active) setSavedLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  async function recommend(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setResult(null);
    setSavedSuggestions([]);
    if (
      !/^\d+(\.\d{1,2})?$/.test(budget) ||
      Number(budget) <= 0 ||
      Number(budget) > 10000
    ) {
      setError(
        "Enter a budget from ₱0.01 to ₱10,000, with up to two decimal places.",
      );
      return;
    }
    setBusy(true);
    try {
      const data = await request("/api/recommendations", {
        method: "POST",
        body: { budget, preferences },
      });
      if (!Array.isArray(data.suggestions))
        throw new Error("Suggestions could not be read. Please try again.");
      setResult({ ...data, budget });
    } catch (failure) {
      setError(failure.message);
    } finally {
      setBusy(false);
    }
  }
  async function saveBox(suggestion, index) {
    if (saving !== null || savedSuggestions.includes(index)) return;
    setSaving(index);
    setError("");
    setNotice("");
    try {
      const created = await request("/api/plans", {
        method: "POST",
        owned: true,
        body: {
          title: `My ${money(result.budget)} meal box`,
          budget: result.budget,
          item_ids: suggestion.items.map((item) => item.id),
        },
      });
      setPlans((current) => [created, ...current.filter((plan) => plan.id !== created.id)]);
      setSavedError("");
      setSavedSuggestions((current) => [...current, index]);
      setNotice("Your meal box is saved. You can view, edit, or delete it below.");
    } catch (failure) {
      setError(failure.message);
    } finally {
      setSaving(null);
    }
  }
  return (
    <>
      <section
        id="recommendations"
        className="planner-section meal-finder"
        aria-labelledby="planner-title"
      >
        <div className="hero">
          <div className="hero-copy">
            <h1 id="planner-title">
              Find food that <em>fits your budget.</em>
            </h1>
            <p className="intro">
              Get AI meal ideas from shops in and around La Salle.
              Save your favorites in My Meal Boxes for your next food trip.
            </p>
            <a className="box-shortcut" href="#meal-boxes">
              My Meal Boxes <span>View, edit, or delete your saved meals</span>
            </a>
            <form className="planner-form" onSubmit={recommend}>
                <label htmlFor="planner-budget">
                  Your budget (₱)
                  <input
                    id="planner-budget"
                    inputMode="decimal"
                    placeholder="100.00"
                    value={budget}
                    onChange={(event) => onBudgetChange(event.target.value)}
                    disabled={busy}
                    required
                  />
                </label>
                <div className="quick-budgets" aria-label="Suggested budgets" role="group">
                  {[50, 75, 100].map((value) => (
                    <button
                      key={value}
                      type="button"
                      disabled={busy}
                      aria-pressed={Number(budget) === value}
                      onClick={() => onBudgetChange(String(value))}
                    >
                      ₱{value}
                    </button>
                  ))}
                </div>
                <label htmlFor="preferences">
                <span>
                  What sounds good? <span className="planner-small">(optional)</span>
                </span>
                  <textarea
                    id="preferences"
                    aria-label="Food preferences"
                    aria-describedby="preference-help"
                    value={preferences}
                    onChange={(event) => setPreferences(event.target.value)}
                    maxLength={1000}
                    rows={2}
                    disabled={busy}
                    placeholder="Chicken with rice, or manok kag kan-on…"
                  />
                  <span className="planner-small" id="preference-help">
                    English, Tagalog, Hiligaynon, and Bisaya are welcome. Common
                  typos are okay.
                  </span>
                </label>
                <button className="primary-button" disabled={busy || saving !== null}>
                  {busy ? "Finding meal ideas…" : "Suggest my meals"}
                </button>
            </form>
          </div>
          {(busy || error || notice || result) && (
            <div className="finder-feedback">
              {busy && (
                <p role="status">
                  Finding options within your budget. The first visit may take about a
                  minute.
                </p>
              )}
              {error && (
                <p className="planner-error" role="alert">
                  {error}
                </p>
              )}
              {notice && (
                <p className="planner-success" role="status">
                  {notice}{" "}
                  <a className="text-link" href="#meal-boxes">
                    View meal boxes
                  </a>
                </p>
              )}
              {result && (
                <div aria-live="polite">
                  <h3 className="planner-result-title">{result.message}</h3>
                  {result.preferences && (
                    <p className="planner-small">
                      Budget: {money(result.budget)} · Food:{" "}
                      {result.preferences.preferred_food || "Any listed meal"} ·{" "}
                      {result.preferences.include_drink
                        ? "With a drink"
                        : "No drink required"}{" "}
                      ·{" "}
                      {result.preferences.prefer_same_stall === false
                        ? "Multiple shops allowed"
                        : "One shop per suggestion"}
                      {result.preferences.avoid_spicy
                        ? " · Explicitly non-spicy listings only"
                        : ""}
                      {result.preferences.exclusions.length > 0
                        ? ` · Avoid listed mentions of: ${result.preferences.exclusions.join(", ")}`
                        : ""}
                    </p>
                  )}
                  {result.suggestions.length > 0 && (
                    <p className="planner-small">
                      Choose a meal idea and save it to your collection.
                      {plans.length >= 20 && <> <a className="text-link" href="#meal-boxes">Manage your saved boxes to make room</a>.</>}
                    </p>
                  )}
                  <div className="meal-box-grid">
                    {result.suggestions.map((suggestion, index) => (
                      <article
                        className="meal-box"
                        key={suggestion.items.map((item) => item.id).join("-")}
                      >
                        <h3>{suggestion.items.map((item) => item.name).join(" + ")}</h3>
                        <MealLines items={suggestion.items} />
                        <div className="meal-total">
                          <strong>{money(suggestion.total)} total</strong>
                          <span>{money(suggestion.remaining)} left</span>
                        </div>
                        <p className="planner-small">{suggestion.reason}</p>
                        <button
                          className="primary-button"
                          disabled={saving !== null || savedSuggestions.includes(index) || plans.length >= 20}
                          onClick={() => saveBox(suggestion, index)}
                        >
                          {savedSuggestions.includes(index)
                            ? "Saved to My Meal Boxes"
                            : saving === index ? "Saving…" : plans.length >= 20
                              ? "20 boxes saved · collection full" : "Save meal box"}
                        </button>
                      </article>
                    ))}
                  </div>
                  <p className="planner-small">{result.notice}</p>
                </div>
              )}
            </div>
          )}
          {highlights}
        </div>
      </section>
      <section
        id="meal-boxes"
        className="planner-section saved-boxes"
        aria-labelledby="boxes-title"
      >
        <div className="section-heading">
          <h2 id="boxes-title">My Meal Boxes</h2>
          <a className="primary-button" href="#recommendations">Find a meal to save</a>
        </div>
        <p className="collection-intro">
          Your food plans, ready for later. Add or remove meals, change quantities,
          and adjust your budget inside each saved box.
        </p>
        <div className="collection-toolbar">
          <span aria-live="polite">{savedLoading ? "Loading collection…" : `${plans.length} of 20 boxes saved`}</span>
          <details className="storage-help">
            <summary>Will my boxes stay saved?</summary>
            <p>They stay saved when you return using this browser and profile.
              Anyone using this browser can access them. Clearing site data
              removes access. Other browsers and devices have separate collections.</p>
          </details>
        </div>
        {boxNotice && <p className="planner-success" role="status">{boxNotice}</p>}
        {savedError && (
          <div className="planner-error" role="alert">
            <p>{savedError}</p>
            <button
              className="clear-button"
              onClick={() => {
                setSavedError("");
                loadPlans().catch((failure) => setSavedError(failure.message));
              }}
            >
              Retry meal boxes
            </button>
          </div>
        )}
        {savedLoading ? (
          <p role="status">Opening your meal boxes…</p>
        ) : (
          !savedError && !plans.length && (
            <div className="planner-empty">
              <h3>Your first meal box starts here.</h3>
              <p>Enter a budget, choose an AI meal idea, then select Save meal box.</p>
              <a className="text-link" href="#recommendations">Create my first meal box</a>
            </div>
          )
        )}
        <div className="meal-box-grid">
          {plans.map((plan) => (
            <SavedBox
              key={plan.id}
              plan={plan}
              catalog={catalog}
              onUpdate={(updated) => {
                setPlans((current) => current.map((entry) => entry.id === updated.id ? updated : entry));
                setBoxNotice("Meal box updated.");
              }}
              onDelete={(id) => {
                setPlans((current) => current.filter((entry) => entry.id !== id));
                setBoxNotice("Meal box deleted.");
              }}
            />
          ))}
        </div>
      </section>
      {children}
    </>
  );
}
