import { useEffect, useState } from "react";

const API = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");
const pesos = new Intl.NumberFormat("en-PH", {
  style: "currency",
  currency: "PHP",
  maximumFractionDigits: 2,
});
const categories = ["All items", "Main dish", "Drink", "Snack", "Side"];
const symbols = { "Main dish": "🍚", Drink: "🍋", Snack: "🥪", Side: "🍽️" };

export default function App() {
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("loading");
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All items");
  const [budget, setBudget] = useState("");
  const [draftBudget, setDraftBudget] = useState("");
  const [budgetError, setBudgetError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;
    const timeout = setTimeout(() => controller.abort(), 75000);
    setStatus("loading");
    const suffix = budget ? `?budget=${encodeURIComponent(budget)}` : "";
    fetch(`${API}/api/menu-items${suffix}`, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error("Menu request failed");
        const data = await response.json();
        if (!Array.isArray(data)) throw new Error("Unexpected menu response");
        if (!cancelled) {
          setItems(data);
          setStatus("ready");
        }
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      })
      .finally(() => clearTimeout(timeout));
    return () => {
      cancelled = true;
      clearTimeout(timeout);
      controller.abort();
    };
  }, [attempt, budget]);

  function applyBudget(event) {
    event.preventDefault();
    const value = draftBudget.trim();
    if (
      value &&
      (!/^\d+(\.\d{1,2})?$/.test(value) ||
        Number(value) <= 0 ||
        Number(value) > 10000)
    ) {
      setBudgetError(
        "Enter an amount from ₱0.01 to ₱10,000, with up to two decimal places.",
      );
      return;
    }
    setBudgetError("");
    setBudget(value);
    setAttempt((current) => current + 1);
  }

  const visible = items.filter(
    (item) =>
      (category === "All items" || item.category === category) &&
      `${item.name} ${item.stall_name}`
        .toLowerCase()
        .includes(query.toLowerCase().trim()),
  );

  return (
    <>
      <header className="header">
        <a className="brand" href="#">
          <span className="brand-mark">
            a<span>✳</span>
          </span>
          Animo<span>Meals</span>
        </a>
        <span className="campus">LA SALLE CANTEEN PROJECT</span>
        <a className="header-link" href="#menu">
          Explore the menu <span aria-hidden="true">↗</span>
        </a>
      </header>
      <main>
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">
              <span /> A LITTLE PLANNING. A BETTER LUNCH.
            </p>
            <h1>
              Good food.
              <br />
              Student <em>budget.</em>
            </h1>
            <p className="intro">
              Find your next canteen favorite without stretching your allowance.
              A good meal starts with knowing your options.
            </p>
            <form className="budget-form" onSubmit={applyBudget}>
              <label htmlFor="budget">What’s your budget?</label>
              <div className="budget-controls">
                <span aria-hidden="true">₱</span>
                <input
                  id="budget"
                  inputMode="decimal"
                  value={draftBudget}
                  onChange={(e) => setDraftBudget(e.target.value)}
                  placeholder="100.00"
                  aria-describedby={
                    budgetError ? "budget-error" : "budget-help"
                  }
                  aria-invalid={!!budgetError}
                />
                <button type="submit">
                  Find food <span aria-hidden="true">→</span>
                </button>
              </div>
              <p id="budget-help">
                Find individual items within your budget. Leave blank to see
                all.
              </p>
              {budgetError && (
                <p className="validation" id="budget-error" role="alert">
                  {budgetError}
                </p>
              )}
            </form>
          </div>
          <div className="hero-art" aria-hidden="true">
            <span className="art-note top-note">A little more flavor.</span>
            <div className="plate">
              <div className="meal-rice" />
              <div className="meal-chicken one" />
              <div className="meal-chicken two" />
              <div className="meal-chicken three" />
              <div className="greens g1" />
              <div className="greens g2" />
              <div className="greens g3" />
              <div className="tomato t1" />
              <div className="tomato t2" />
            </div>
            <div className="art-label">
              <span>THE LUNCH BREAK EDIT</span>
              <strong>Make room for a good meal.</strong>
            </div>
            <span className="art-note bottom-note">
              A little less spending.
            </span>
          </div>
        </section>
        <div className="notice">
          <span className="notice-icon" aria-hidden="true">
            i
          </span>
          <p>
            <strong>A preview of what’s cooking.</strong> These stalls, prices,
            and locations are fictional demonstration data. AI meal combinations
            are planned for a later version.
          </p>
          <span className="week-tag">WEEK 01</span>
        </div>
        <section id="menu" className="menu-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">YOUR CANTEEN, AT A GLANCE</p>
              <h2>What sounds good?</h2>
            </div>
            <label className="search">
              <span aria-hidden="true">⌕</span>
              <input
                aria-label="Search food or stalls"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search food or stalls"
              />
            </label>
          </div>
          <div className="filter-row">
            <div className="tabs" aria-label="Food categories">
              {categories.map((value) => (
                <button
                  key={value}
                  onClick={() => setCategory(value)}
                  aria-pressed={category === value}
                  className={category === value ? "active" : ""}
                >
                  {value}
                </button>
              ))}
            </div>
            <p className="result-count">
              {status === "ready"
                ? `${visible.length} ${visible.length === 1 ? "option" : "options"}${budget ? ` · up to ${pesos.format(budget)}` : ""}`
                : "Menu explorer"}
            </p>
          </div>
          {status === "loading" && (
            <div className="state-box" role="status">
              Loading the canteen menu… The first visit may take about a minute while the service wakes up.
            </div>
          )}
          {status === "error" && (
            <div className="state-box" role="alert">
              <h3>The menu couldn’t load.</h3>
              <p>Check that the backend is running, then try again.</p>
              <button
                className="retry"
                onClick={() => setAttempt((value) => value + 1)}
              >
                Try again
              </button>
            </div>
          )}
          {status === "ready" && visible.length === 0 && (
            <div className="state-box">
              <h3>No items match just yet.</h3>
              <p>Try a different search, category, or budget.</p>
              <button
                className="retry"
                onClick={() => {
                  setQuery("");
                  setCategory("All items");
                  setBudget("");
                  setDraftBudget("");
                  setBudgetError("");
                }}
              >
                Clear filters
              </button>
            </div>
          )}
          {status === "ready" && (
            <div className="menu-grid">
              {visible.map((item) => (
                <article className="menu-card" key={item.id}>
                  <div
                    className={`food-visual ${item.category.toLowerCase().replace(" ", "-")}`}
                  >
                    <span aria-hidden="true">
                      {symbols[item.category] || "🍽️"}
                    </span>
                    <span
                      className={`availability ${item.is_available ? "" : "unavailable"}`}
                    >
                      {item.is_available ? "Listed available" : "Unavailable"}
                    </span>
                  </div>
                  <div className="card-content">
                    <p className="stall-name">{item.stall_name}</p>
                    <h3>{item.name}</h3>
                    <p className="description">{item.description}</p>
                    <div className="card-bottom">
                      <strong>{pesos.format(item.price)}</strong>
                      <span>{item.category}</span>
                    </div>
                    <div className="location">{item.location}</div>
                    <small>
                      Updated{" "}
                      {new Date(item.updated_at).toLocaleDateString("en-PH", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}{" "}
                      · Demo listing
                    </small>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
        <footer>
          <a className="brand footer-brand" href="#">
            Animo<span>Meals</span>
          </a>
          <p>Made for student budgets and better lunch breaks.</p>
          <span>Independent student project · Demonstration only</span>
        </footer>
      </main>
    </>
  );
}
