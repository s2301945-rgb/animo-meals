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
            <strong>{item.name}</strong>
            <span>
              {item.shop_name} · {item.location}
            </span>
          </div>
          <b>{money(item.price)}</b>
        </li>
      ))}
    </ul>
  );
}

function SavedBox({ plan, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(plan.title);
  const [expanded, setExpanded] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function mutate(method) {
    setBusy(true);
    setError("");
    try {
      const updated = await request(`/api/plans/${plan.id}`, {
        owned: true,
        method,
        ...(method === "PUT" ? { body: { title: title.trim() } } : {}),
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
        <form onSubmit={(event) => { event.preventDefault(); mutate("PUT"); }}>
          <label htmlFor={`box-name-${plan.id}`}>
            Meal box name
            <input
              id={`box-name-${plan.id}`}
              autoFocus
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              maxLength={100}
              required
              disabled={busy}
            />
          </label>
          <div className="planner-actions">
            <button className="primary-button" disabled={busy || !title.trim()}>
              {busy ? "Saving…" : "Save name"}
            </button>
            <button type="button" className="secondary-button" disabled={busy}
              onClick={() => { setEditing(false); setTitle(plan.title); setError(""); }}>
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <h3>{plan.title}</h3>
      )}
      <p className="box-summary">
        {plan.items.length} {plan.items.length === 1 ? "item" : "items"} · Budget {money(plan.budget)}
      </p>
      <div className="meal-total">
        <strong>{money(plan.total)} total</strong>
        <span>{money(plan.remaining)} left</span>
      </div>
      {expanded && (
        <div id={`box-details-${plan.id}`}>
          <MealLines items={plan.items} />
          <p className="planner-small">
            Prices saved with this box. Confirm current prices at the shop.
          </p>
        </div>
      )}
      {error && <p className="planner-error" role="alert">{error}</p>}
      {!editing && (
        <div className="planner-actions">
          <button className="secondary-button"
            aria-expanded={expanded} aria-controls={`box-details-${plan.id}`}
            onClick={() => setExpanded(!expanded)}>
            {expanded ? "Hide details" : "View meals"}
          </button>
          <button className="secondary-button" disabled={busy || confirming}
            onClick={() => { setTitle(plan.title); setEditing(true); setError(""); }}>
            Rename
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

export default function MealPlanner({ budget, onBudgetChange, highlights, children }) {
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
      setNotice("Your meal box is saved. You can view, rename, or delete it below.");
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
              My Meal Boxes <span>View, rename, or delete your saved meals</span>
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
          Your food plans, ready for later. Open a box to view its meals, give it a
          name, or delete it when you’re done.
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
              onUpdate={(updated) => {
                setPlans((current) => current.map((entry) => entry.id === updated.id ? updated : entry));
                setBoxNotice("Meal box renamed.");
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
