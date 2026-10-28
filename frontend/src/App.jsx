import { useEffect, useState } from "react";

const API = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");
const pesos = new Intl.NumberFormat("en-PH", {
  style: "currency",
  currency: "PHP",
});
const categories = ["All items", "Main dish", "Drink", "Snack", "Side"];
const cleanName = (name) => name.replace(/^Demo\s*[•·]\s*/i, "");

function Icon({ name, ...props }) {
  const paths = {
    arrow: "M5 12h14m-6-6 6 6-6 6",
    pin: "M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0ZM12 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6",
    search: "m21 21-5-5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0",
    check: "m5 12 4 4L19 6",
    shop: "M3 10h18l-2-6H5l-2 6Zm1 0v11h16V10M9 21v-7h6v7M2 10c0 4 5 4 5 0 0 4 5 4 5 0 0 4 5 4 5 0 0 4 5 4 5 0",
    close: "m6 6 12 12M6 18 18 6",
  };
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      <path d={paths[name] || paths.arrow} />
    </svg>
  );
}

function Brand() {
  return (
    <a className="brand" href="#top" aria-label="AnimoMeals home">
      <img src="/animo-mark.png" alt="" width="45" height="45" />
      <span>
        Animo<span>Meals</span>
      </span>
    </a>
  );
}

// Illustrations intentionally avoid implying photos of demonstration listings.
function FoodArt({ item }) {
  const name = item.name.toLowerCase();
  const vegetables = /tofu|vegetable/.test(name);
  return (
    <svg viewBox="0 0 300 220" className="food-art" aria-hidden="true">
      <ellipse cx="150" cy="190" rx="86" ry="9" fill="#173f2812" />
      {item.category === "Drink" ? (
        /water/.test(name) ? (
          <g>
            <rect x="127" y="29" width="46" height="23" rx="6" fill="#286947" />
            <path
              d="M128 53h44v21l13 19v80q0 16-16 16h-38q-16 0-16-16V93l13-19Z"
              fill="#d1e7de"
              stroke="#649b87"
              strokeWidth="2"
            />
            <path
              d="M120 128h60v42q0 12-12 12h-36q-12 0-12-12Z"
              fill="#a4d0be"
            />
            <rect
              x="114"
              y="106"
              width="72"
              height="35"
              rx="3"
              fill="#fffdf5"
            />
            <path
              d="m142 116 8 15 8-15"
              fill="none"
              stroke="#397553"
              strokeWidth="3"
            />
          </g>
        ) : (
          <g>
            <path
              d="m102 65 13 116q1 10 12 10h46q11 0 12-10l13-116Z"
              fill="#fffdf3"
              stroke="#dad8c1"
              strokeWidth="2"
            />
            <path
              d="m109 88 11 89q1 8 10 8h40q9 0 10-8l11-89Z"
              fill={/tea/.test(name) ? "#bd853c" : "#c7d466"}
            />
            <path
              d="m164 103 15-73h22"
              fill="none"
              stroke="#367b56"
              strokeWidth="7"
            />
            <rect
              x="121"
              y="92"
              width="24"
              height="26"
              rx="4"
              fill="#fff9dd"
              opacity=".6"
              transform="rotate(-12 130 100)"
            />
            <rect
              x="152"
              y="119"
              width="26"
              height="26"
              rx="4"
              fill="#fff9dd"
              opacity=".4"
              transform="rotate(15 160 130)"
            />
            <circle cx="106" cy="83" r="24" fill="#e9d06b" />
            <circle cx="106" cy="83" r="18" fill="#f7e9aa" />
            <path d="m106 66 0 34m-16-17h32" stroke="#e0c467" strokeWidth="2" />
          </g>
        )
      ) : item.category === "Snack" ? (
        /bread/.test(name) ? (
          <g>
            <path
              d="M91 99q-9-31 20-39 37-18 77 0 31 9 21 39v76H91Z"
              fill="#ae713b"
            />
            <path
              d="M99 102q-8-30 20-35 34-13 61 0 27 6 21 35v65H99Z"
              fill="#e4bf7d"
            />
            <path
              d="m119 104 9 4m37-21 9 4m-29 39 9 4m20 13 9 4m-67-4 9 4"
              stroke="#a97539"
              strokeWidth="5"
              strokeLinecap="round"
            />
          </g>
        ) : (
          <g>
            <path d="m78 152 76-100 74 100Z" fill="#c78c47" />
            <path d="m85 146 69-85 64 85Z" fill="#f4e4b5" />
            <path d="m82 151 73-14 69 14-9 12H92Z" fill="#6e9854" />
            <path d="m84 164 71-9 68 9-10 9H96Z" fill="#e5bc57" />
            <path d="m88 174 66-13 65 13-9 14H99Z" fill="#f2d69a" />
          </g>
        )
      ) : (
        <g>
          <ellipse
            cx="150"
            cy="115"
            rx="99"
            ry="75"
            fill="#fcfcf7"
            stroke="#e0e3d6"
            strokeWidth="3"
          />
          <ellipse cx="150" cy="115" rx="81" ry="60" fill="#f0f1e7" />
          <ellipse cx="120" cy="109" rx="39" ry="42" fill="#fffef9" />
          {[0, 1, 2, 3].map((row) => (
            <path
              key={row}
              d={`m${98 + row * 3} ${87 + row * 12} 8 3m9-4 8 3m9-3 7 2`}
              stroke="#dedfca"
              strokeWidth="2"
              strokeLinecap="round"
            />
          ))}
          {item.category !== "Side" && (
            <>
              <path
                d="M161 76q25-10 38 9 7 18-9 24-28 11-37-7-5-16 8-26Z"
                fill={vegetables ? "#cfa963" : "#ad6734"}
              />
              <path
                d="M173 112q26-12 35 6 12 22-13 28-22 8-30-9-6-15 8-25Z"
                fill={vegetables ? "#e0bd78" : "#be7b3f"}
              />
              <path
                d="m158 88 20 8m3 25 16 7"
                stroke={vegetables ? "#b98b43" : "#8e512c"}
                strokeWidth="3"
                strokeLinecap="round"
              />
              <path
                d="M130 147q7-27 28-17-1 23-28 17Zm17 4q12-24 28-10-7 21-28 10Z"
                fill="#548b49"
              />
              <circle cx="109" cy="147" r="10" fill="#cb7050" />
              <circle cx="109" cy="147" r="5" fill="#ebaa74" />
            </>
          )}
        </g>
      )}
    </svg>
  );
}

export default function App() {
  const [items, setItems] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [status, setStatus] = useState("loading");
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All items");
  const [shop, setShop] = useState("");
  const [sort, setSort] = useState("default");
  const [availableOnly, setAvailableOnly] = useState(false);
  const [budget, setBudget] = useState("");
  const [draftBudget, setDraftBudget] = useState("");
  const [budgetError, setBudgetError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;
    const timeout = setTimeout(() => controller.abort(), 75000);
    setStatus("loading");
    fetch(
      `${API}/api/menu-items${budget ? `?budget=${encodeURIComponent(budget)}` : ""}`,
      { signal: controller.signal },
    )
      .then(async (response) => {
        if (!response.ok) throw new Error("Menu request failed");
        const data = await response.json();
        if (!Array.isArray(data)) throw new Error("Unexpected menu response");
        if (!cancelled) {
          setItems(data);
          if (!budget) setCatalog(data);
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

  function clearFilters() {
    setQuery("");
    setCategory("All items");
    setShop("");
    setAvailableOnly(false);
    setBudget("");
    setDraftBudget("");
    setBudgetError("");
    setSort("default");
  }
  function scrollToMenu() {
    document
      .getElementById("menu")
      .scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "instant"
          : "smooth",
      });
  }
  function findFood(value) {
    const amount = value.trim();
    if (
      amount &&
      (!/^\d+(\.\d{1,2})?$/.test(amount) ||
        Number(amount) <= 0 ||
        Number(amount) > 10000)
    ) {
      setBudgetError("Enter ₱0.01–₱10,000, with up to two decimal places.");
      return;
    }
    setBudgetError("");
    setBudget(amount);
    setDraftBudget(amount);
    setAttempt((current) => current + 1);
    scrollToMenu();
  }
  const shops = [...new Set(catalog.map((item) => item.stall_name))].map(
    (name) => {
      const menu = catalog.filter((item) => item.stall_name === name);
      return {
        name,
        location: menu[0].location,
        count: menu.length,
        min: Math.min(...menu.map((item) => Number(item.price))),
      };
    },
  );
  const visible = items
    .filter(
      (item) =>
        (category === "All items" || item.category === category) &&
        (!shop || item.stall_name === shop) &&
        (!availableOnly || item.is_available) &&
        `${item.name} ${item.stall_name} ${item.description || ""}`
          .toLowerCase()
          .includes(query.toLowerCase().trim()),
    )
    .sort((a, b) =>
      sort === "price"
        ? Number(a.price) - Number(b.price)
        : sort === "name"
          ? a.name.localeCompare(b.name)
          : 0,
    );
  const featured = catalog.find(
    (item) => item.category === "Main dish" && item.is_available,
  );
  const filtered =
    budget || query || shop || category !== "All items" || availableOnly;

  return (
    <>
      <a href="#menu" className="skip-link">
        Skip to menu
      </a>
      <header className="header" id="top">
        <Brand />
        <nav aria-label="Main navigation">
          <a href="#menu">Find food</a>
          <a href="#shops">Browse shops</a>
          <a href="#how">How it works</a>
        </nav>
        <span className="campus">
          <span /> Made for student budgets
        </span>
      </header>
      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">
              <span className="little-star">✦</span> GOOD FOOD. SMARTER
              SPENDING.
            </p>
            <h1 id="hero-title">
              A little budget.
              <br />A <em>good meal.</em>
            </h1>
            <p className="intro">
              Your next lunch starts here. Explore canteen menus, compare
              prices, and find a little more room in your allowance.
            </p>
            <form
              className="budget-form"
              onSubmit={(event) => {
                event.preventDefault();
                findFood(draftBudget);
              }}
            >
              <label htmlFor="budget">How much are you spending?</label>
              <div
                className={`budget-controls ${budgetError ? "invalid" : ""}`}
              >
                <span aria-hidden="true">₱</span>
                <input
                  id="budget"
                  inputMode="decimal"
                  value={draftBudget}
                  onChange={(event) => setDraftBudget(event.target.value)}
                  placeholder="100.00"
                  aria-describedby={
                    budgetError ? "budget-error" : "budget-help"
                  }
                  aria-invalid={!!budgetError}
                />
                <button type="submit">
                  Find food <Icon name="arrow" />
                </button>
              </div>
              <p id="budget-help">
                See individual items within your budget. No account needed.
              </p>
              {budgetError && (
                <p className="validation" id="budget-error" role="alert">
                  {budgetError}
                </p>
              )}
            </form>
            <div className="quick-budgets">
              <span>A quick starting point</span>
              {[50, 75, 100].map((value) => (
                <button key={value} onClick={() => findFood(String(value))}>
                  ₱{value}
                </button>
              ))}
            </div>
            <div className="hero-proof">
              <span>
                <Icon name="check" /> Prices you can compare
              </span>
              <span>
                <Icon name="check" /> Menus in one place
              </span>
            </div>
          </div>
          <div className="hero-stage">
            <div className="hero-arc" />
            <div className="stage-top">
              <span className="stage-star">✦</span>
              <span>
                THE LUNCH BREAK EDIT
                <br />
                <strong>Good finds, every break.</strong>
              </span>
            </div>
            <div className="hero-plate">
              <FoodArt
                item={featured || { name: "rice meal", category: "Main dish" }}
              />
            </div>
            <span className="handwritten">Make lunch a little easier.</span>
            {featured && (
              <a href="#menu" className="featured-label">
                <span className="featured-icon">
                  <Icon name="shop" />
                </span>
                <span>
                  <small>FROM THE DEMO MENU</small>
                  <strong>{featured.name}</strong>
                  <span>{cleanName(featured.stall_name)}</span>
                </span>
                <b>{pesos.format(featured.price)}</b>
              </a>
            )}
            <span className="illustration-label">
              Food illustration · not a product photo
            </span>
          </div>
        </section>
        <aside className="notice">
          <span className="demo-pill">DEMO EDITION</span>
          <p>
            Explore with sample menus. Shop names, locations, prices, and
            availability are fictional. AI meal suggestions are coming in a
            later version.
          </p>
        </aside>
        <section
          id="shops"
          className="shops-section"
          aria-labelledby="shops-title"
        >
          <div className="section-heading">
            <div>
              <p className="eyebrow">A FEW PLACES TO START</p>
              <h2 id="shops-title">Find your lunch spot.</h2>
            </div>
            <p className="section-caption">
              Browse a shop, then explore its menu.
              <br />
              Demonstration listings for now.
            </p>
          </div>
          {shops.length > 0 ? (
            <div className="shop-grid">
              {shops.map((entry, index) => (
                <article className="shop-card" key={entry.name}>
                  <div className={`shop-symbol shop-${index % 3}`}>
                    <Icon name="shop" width="27" height="27" />
                  </div>
                  <div className="shop-info">
                    <h3>{cleanName(entry.name)}</h3>
                    <p>
                      <Icon name="pin" width="14" height="14" />
                      {entry.location}
                    </p>
                    <span>
                      {entry.count} listed items · From{" "}
                      {pesos.format(entry.min)}
                    </span>
                  </div>
                  <button
                    className="shop-link"
                    aria-label={`View ${cleanName(entry.name)} menu`}
                    onClick={() => {
                      clearFilters();
                      setShop(entry.name);
                      scrollToMenu();
                    }}
                  >
                    <Icon name="arrow" />
                  </button>
                </article>
              ))}
            </div>
          ) : (
            <p className="shop-placeholder">
              {status === "error"
                ? "Shop details will appear when the menu connection is restored."
                : "Getting the shops ready…"}
            </p>
          )}
        </section>
        <section
          id="menu"
          className="menu-section"
          aria-labelledby="menu-title"
        >
          <div className="section-heading">
            <div>
              <p className="eyebrow">SOMETHING FOR YOUR APPETITE</p>
              <h2 id="menu-title">What sounds good?</h2>
            </div>
            <label className="search">
              <Icon name="search" />
              <input
                aria-label="Search food or shops"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search food or shops…"
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
            <label className="sort-label">
              Sort by
              <select
                value={sort}
                onChange={(event) => setSort(event.target.value)}
              >
                <option value="default">Shop order</option>
                <option value="price">Lowest price</option>
                <option value="name">Food name</option>
              </select>
            </label>
          </div>
          <div className="results-toolbar">
            <p className="result-count" aria-live="polite">
              {status === "ready" ? (
                <>
                  <strong>{visible.length}</strong>{" "}
                  {visible.length === 1 ? "item" : "items"}
                  {budget && (
                    <>
                      {" "}
                      within <strong>{pesos.format(budget)}</strong>
                    </>
                  )}
                  {shop && (
                    <>
                      {" "}
                      at <strong>{cleanName(shop)}</strong>
                    </>
                  )}
                </>
              ) : (
                "Getting your menu ready"
              )}
            </p>
            <div className="result-options">
              <label>
                <input
                  type="checkbox"
                  checked={availableOnly}
                  onChange={(event) => setAvailableOnly(event.target.checked)}
                />{" "}
                Listed available only
              </label>
              {filtered && (
                <button className="clear-button" onClick={clearFilters}>
                  Clear filters <Icon name="close" width="14" height="14" />
                </button>
              )}
            </div>
          </div>
          {status === "loading" && (
            <div className="loading-state" role="status">
              <div className="loading-dot" />
              <h3>Finding your next food stop…</h3>
              <p>
                The first visit can take about a minute while the menu service
                wakes up.
              </p>
            </div>
          )}
          {status === "error" && (
            <div className="state-box" role="alert">
              <Icon name="shop" width="32" height="32" />
              <h3>The menu is taking a little break.</h3>
              <p>
                We couldn’t retrieve the listings. Check your connection and try
                again in a moment.
              </p>
              <button
                className="primary-button"
                onClick={() => setAttempt((value) => value + 1)}
              >
                Try again <Icon name="arrow" />
              </button>
            </div>
          )}
          {status === "ready" && !visible.length && (
            <div className="state-box">
              <Icon name="search" width="32" height="32" />
              <h3>No matches on the menu just yet.</h3>
              <p>
                Try a bigger budget, another category, or a different search.
              </p>
              <button className="primary-button" onClick={clearFilters}>
                Show all food <Icon name="arrow" />
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
                    <FoodArt item={item} />
                    <span
                      className={`availability ${item.is_available ? "" : "unavailable"}`}
                    >
                      <span />
                      {item.is_available ? "Listed available" : "Unavailable"}
                    </span>
                    <span className="category-label">{item.category}</span>
                  </div>
                  <div className="card-content">
                    <button
                      className="stall-name"
                      onClick={() => setShop(item.stall_name)}
                    >
                      {cleanName(item.stall_name)}{" "}
                      <span aria-hidden="true">↗</span>
                    </button>
                    <h3>{item.name}</h3>
                    <p className="description">
                      {item.description ||
                        "Ask the shop for more details about this item."}
                    </p>
                    <div className="card-bottom">
                      <strong>{pesos.format(item.price)}</strong>
                      {budget && (
                        <span className="remaining">
                          {pesos.format(
                            Math.max(
                              0,
                              Math.round(
                                (Number(budget) - Number(item.price)) * 100,
                              ) / 100,
                            ),
                          )}{" "}
                          left
                        </span>
                      )}
                    </div>
                    <div className="card-meta">
                      <span>
                        <Icon name="pin" width="15" height="15" />
                        {item.location}
                      </span>
                      <small>
                        Updated{" "}
                        {new Date(item.updated_at).toLocaleDateString("en-PH", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}{" "}
                        · Demo
                      </small>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
        <section id="how" className="how-section" aria-labelledby="how-title">
          <div>
            <p className="eyebrow">LESS GUESSWORK. MORE GOOD FOOD.</p>
            <h2 id="how-title">
              A better lunch,
              <br />
              in three little steps.
            </h2>
            <p>
              Start with your budget.
              <br />
              Leave with a little more choice.
            </p>
          </div>
          <div className="steps">
            {[
              [
                "01",
                "Set your budget",
                "Enter what you want to spend. We’ll show the individual items within that amount.",
              ],
              [
                "02",
                "Explore the menus",
                "Browse by shop, search for a favorite, or sort from the lowest price.",
              ],
              [
                "03",
                "Choose your next stop",
                "Compare prices and locations. Confirm the current price and availability at the shop.",
              ],
            ].map(([number, title, text]) => (
              <div className="step" key={number}>
                <span>{number}</span>
                <div>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
        <footer>
          <div>
            <Brand />
            <p>A little planning. A better lunch.</p>
          </div>
          <div className="footer-links">
            <a href="#menu">Find food</a>
            <a href="#shops">Browse shops</a>
            <a href="#how">How it works</a>
          </div>
          <p className="footer-note">
            Independent student project
            <br />
            Not an official university service.
          </p>
        </footer>
      </main>
    </>
  );
}
