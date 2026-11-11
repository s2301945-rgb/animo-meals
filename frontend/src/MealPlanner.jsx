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

function SavedBox({ plan, onChange, onError }) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(plan.title);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  async function mutate(method) {
    setBusy(true);
    onError("");
    try {
      await request(`/api/plans/${plan.id}`, {
        owned: true,
        method,
        ...(method === "PUT" ? { body: { title } } : {}),
      });
      setEditing(false);
      await onChange();
    } catch (error) {
      onError(error.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <article className="meal-box">
      <span className="box-kicker">
        MY MEAL BOX · SAVED{" "}
        {new Date(plan.created_at).toLocaleDateString("en-PH")}
      </span>
      {editing ? (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            mutate("PUT");
          }}
        >
          <label>
            Meal box name
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              maxLength={100}
              required
              disabled={busy}
            />
          </label>
          <div className="planner-actions">
            <button className="primary-button" disabled={busy || !title.trim()}>
              Save name
            </button>
            <button
              type="button"
              className="clear-button"
              disabled={busy}
              onClick={() => {
                setEditing(false);
                setTitle(plan.title);
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <h3>{plan.title}</h3>
      )}
      <MealLines items={plan.items} />
      <div className="meal-total">
        <strong>{money(plan.total)} total</strong>
        <span>{money(plan.remaining)} left</span>
      </div>
      <p className="planner-small">
        Saved prices are a snapshot. Confirm at the shop before buying.
      </p>
      {!editing && (
        <div className="planner-actions">
          {confirming ? (
            <>
              <span>Delete this meal box?</span>
              <button
                className="clear-button"
                disabled={busy}
                onClick={() => mutate("DELETE")}
              >
                Yes, delete
              </button>
              <button
                className="clear-button"
                disabled={busy}
                onClick={() => setConfirming(false)}
              >
                Keep it
              </button>
            </>
          ) : (
            <>
              <button className="clear-button" onClick={() => setEditing(true)}>
                Rename
              </button>
              <button
                className="clear-button"
                onClick={() => setConfirming(true)}
              >
                Delete
              </button>
            </>
          )}
        </div>
      )}
    </article>
  );
}

export default function MealPlanner({ budget, onBudgetChange }) {
  const [preferences, setPreferences] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [savedError, setSavedError] = useState("");
  const [notice, setNotice] = useState("");
  const [plans, setPlans] = useState([]);
  const [saving, setSaving] = useState(null);
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
        if (active && Array.isArray(data)) setPlans(data);
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
    setSaving(index);
    setSavedError("");
    setNotice("");
    try {
      await request("/api/plans", {
        method: "POST",
        owned: true,
        body: {
          title: `My ${money(result.budget)} meal box`,
          budget: result.budget,
          item_ids: suggestion.items.map((item) => item.id),
        },
      });
      setNotice("Saved to My Meal Boxes. Give it a fun name below!");
      await loadPlans();
    } catch (failure) {
      setSavedError(failure.message);
    } finally {
      setSaving(null);
    }
  }
  return (
    <>
      <section
        id="recommendations"
        className="planner-section"
        aria-labelledby="planner-title"
      >
        <div className="section-heading">
          <div>
            <p className="eyebrow">YOUR BUDGET. YOUR APPETITE.</p>
            <h2 id="planner-title">Let’s build your meal box.</h2>
          </div>
          <p className="section-caption">
            Meal ideas from recorded local menus. <br />
            No account needed.
          </p>
        </div>
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
          <label htmlFor="preferences">
            What sounds good?
            <textarea
              id="preferences"
              aria-label="Food preferences"
              aria-describedby="preference-help"
              value={preferences}
              onChange={(event) => setPreferences(event.target.value)}
              maxLength={1000}
              rows={3}
              disabled={busy}
              placeholder="Chicken with rice, or manok kag kan-on…"
            />
            <span className="planner-small" id="preference-help">
              Write in English, Tagalog, Hiligaynon (Ilonggo), or Cebuano
              (Bisaya). Common typos are okay. Leave blank to compare recorded
              prices only.
            </span>
          </label>
          <button className="primary-button" disabled={busy}>
            {busy ? "Finding meal ideas…" : "Suggest my meals ✦"}
          </button>
        </form>
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
            {notice}
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
            <div className="meal-box-grid">
              {result.suggestions.map((suggestion, index) => (
                <article
                  className="meal-box"
                  key={suggestion.items.map((item) => item.id).join("-")}
                >
                  <span className="box-kicker">
                    OPTION {String(index + 1).padStart(2, "0")} · WITHIN{" "}
                    {money(result.budget)}
                  </span>
                  <h3>A little more for your allowance.</h3>
                  <MealLines items={suggestion.items} />
                  <div className="meal-total">
                    <strong>{money(suggestion.total)} total</strong>
                    <span>{money(suggestion.remaining)} left</span>
                  </div>
                  <p className="planner-small">{suggestion.reason}</p>
                  <button
                    className="primary-button"
                    disabled={saving !== null}
                    onClick={() => saveBox(suggestion, index)}
                  >
                    {saving === index ? "Saving…" : "Save meal box"}
                  </button>
                </article>
              ))}
            </div>
            <p className="planner-small">{result.notice}</p>
          </div>
        )}
      </section>
      <section
        id="meal-boxes"
        className="planner-section saved-boxes"
        aria-labelledby="boxes-title"
      >
        <div className="section-heading">
          <div>
            <p className="eyebrow">LITTLE PLANS FOR LUNCH</p>
            <h2 id="boxes-title">My Meal Boxes</h2>
          </div>
          <span className="section-caption">{plans.length} / 20 saved</span>
        </div>
        <p>
          Your meal boxes are saved in the database and linked to this browser.
          Anyone using this browser can access them. Clearing site data loses
          access; there is no account recovery or cross-device sync.
        </p>
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
          !plans.length && (
            <p className="planner-empty">
              Your lunch plans start here. Find a suggestion above and save your
              first meal box.
            </p>
          )
        )}
        <div className="meal-box-grid">
          {plans.map((plan) => (
            <SavedBox
              key={plan.id}
              plan={plan}
              onChange={loadPlans}
              onError={setSavedError}
            />
          ))}
        </div>
      </section>
    </>
  );
}
