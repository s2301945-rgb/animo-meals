import { useEffect, useMemo, useState } from "react";
import Photo from "./Photo.jsx";
import FoodCover from "./FoodCover.jsx";
import MealPlanner from "./MealPlanner.jsx";
import StagingBanner, { verifyStagingEnvironment } from "./Staging.jsx";

const API = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");
const pesos = new Intl.NumberFormat("en-PH", {
  style: "currency",
  currency: "PHP",
});
const categories = ["All items", "Main dish", "Drink", "Snack", "Side"];
const cleanName = (name) => name.replace(/^Demo\s*[•·]\s*/i, "");
const isDemoName = (name) => /^Demo\s*[•·]/i.test(name);

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

function MenuCarousel({ items, budget, onSelect }) {
  const amount = Number(budget);
  const limit = amount > 0 && amount <= 10000 ? amount : 75;
  const eligible = useMemo(
    () =>
      items.filter(
        (item) =>
          item.is_listed &&
          ["Main dish", "Snack"].includes(item.category) &&
          Number(item.price) <= limit,
      ),
    [items, limit],
  );
  const [frame, setFrame] = useState({
    current: null,
    previous: null,
    cycle: 0,
  });
  const [paused, setPaused] = useState(false);
  const [hovered, setHovered] = useState(false);
  const [focused, setFocused] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [hidden, setHidden] = useState(() => document.hidden);
  const current =
    eligible.find((item) => item.id === frame.current) || eligible[0];
  const previous = eligible.find((item) => item.id === frame.previous);

  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updateMotion = () => setReducedMotion(preference.matches);
    const updateVisibility = () => setHidden(document.hidden);
    updateMotion();
    preference.addEventListener("change", updateMotion);
    document.addEventListener("visibilitychange", updateVisibility);
    return () => {
      preference.removeEventListener("change", updateMotion);
      document.removeEventListener("visibilitychange", updateVisibility);
    };
  }, []);

  useEffect(() => {
    if (
      eligible.length < 2 ||
      paused ||
      hovered ||
      focused ||
      reducedMotion ||
      hidden
    )
      return;
    const timer = setInterval(() => {
      setFrame((old) => {
        const active =
          eligible.find((item) => item.id === old.current) || eligible[0];
        const choices = eligible.filter((item) => item.id !== active.id);
        const next = choices[Math.floor(Math.random() * choices.length)];
        return { current: next.id, previous: active.id, cycle: old.cycle + 1 };
      });
    }, 7000);
    return () => clearInterval(timer);
  }, [eligible, paused, hovered, focused, reducedMotion, hidden]);

  function changeItem(direction) {
    if (eligible.length < 2) return;
    const index = eligible.findIndex((item) => item.id === current.id);
    const next =
      eligible[(index + direction + eligible.length) % eligible.length];
    setFrame((old) => ({
      current: next.id,
      previous: current.id,
      cycle: old.cycle + 1,
    }));
  }

  function slide(item, outgoing) {
    const content = (
      <>
        <span className="featured-icon">
          <Icon name="shop" />
        </span>
        <span>
          <small>
            {item.category.toUpperCase()}
            {isDemoName(item.stall_name) ? " · DEMO MENU" : " · LISTED MENU"}
          </small>
          <strong>{item.name}</strong>
          <span>{cleanName(item.stall_name)}</span>
        </span>
        <b>{pesos.format(item.price)}</b>
      </>
    );
    return (
      <div
        key={`${item.id}-${outgoing ? "out" : frame.cycle}`}
        className={`carousel-slide ${outgoing ? "slide-out" : "slide-in"}`}
        aria-hidden={outgoing || undefined}
      >
        <div className="hero-plate">
          <FoodCover item={item} />
        </div>
        {outgoing ? (
          <div className="featured-label">{content}</div>
        ) : (
          <a
            href="#menu"
            className="featured-label"
            onClick={() => onSelect(item)}
            aria-label={`View ${item.name}, ${pesos.format(item.price)} at ${cleanName(item.stall_name)}`}
          >
            {content}
          </a>
        )}
      </div>
    );
  }

  return (
    <section
      className="hero-stage menu-carousel"
      aria-label="Recorded budget menu highlights"
      aria-roledescription="carousel"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onFocusCapture={() => setFocused(true)}
      onBlurCapture={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget))
          setFocused(false);
      }}
    >
      <div className="hero-arc" />
      <div className="stage-top">
        <strong>Menu picks up to {pesos.format(limit)}</strong>
      </div>
      <div
        className="carousel-window"
        aria-live={paused || focused ? "polite" : "off"}
        aria-atomic="true"
      >
        {current ? (
          <>
            {previous && previous.id !== current.id && slide(previous, true)}
            {slide(current, false)}
          </>
        ) : (
          <div className="carousel-empty">
            <Icon name="shop" width="40" height="40" />
            <h3>
              {items.length
                ? "No picks in this budget just yet."
                : "Your next food find is on its way."}
            </h3>
            <p>
              {items.length
                ? "Try a larger budget or browse the full menu below."
                : "Recorded meal and snack listings will appear here."}
            </p>
          </div>
        )}
      </div>
      {current && (
        <div className="carousel-controls">
          <button
            className="carousel-arrow previous-arrow"
            aria-label="Previous menu highlight"
            onClick={() => changeItem(-1)}
            disabled={eligible.length < 2}
          >
            <Icon name="arrow" />
          </button>
          <span className="carousel-count">
            {eligible.findIndex((item) => item.id === current.id) + 1}{" "}
            <span>/ {eligible.length}</span>
          </span>
          <button
            className="carousel-arrow"
            aria-label="Next menu highlight"
            onClick={() => changeItem(1)}
            disabled={eligible.length < 2}
          >
            <Icon name="arrow" />
          </button>
          <button
            className="carousel-pause"
            onClick={() => setPaused((value) => !value)}
            aria-pressed={paused}
            disabled={reducedMotion || eligible.length < 2}
          >
            {reducedMotion
              ? "Autoplay off"
              : paused
                ? "▶ Resume"
                : "Ⅱ Pause"}
          </button>
        </div>
      )}
      <span className="illustration-label">
        Illustrations are not actual food photos
      </span>
    </section>
  );
}

export default function App() {
  const [items, setItems] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [shopRecords, setShopRecords] = useState([]);
  const [status, setStatus] = useState("loading");
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All items");
  const [shop, setShop] = useState("");
  const [sort, setSort] = useState("default");
  const [listedOnly, setListedOnly] = useState(false);
  const [budget, setBudget] = useState("");
  const [draftBudget, setDraftBudget] = useState("");
  const [menuBudget, setMenuBudget] = useState("");
  const [budgetError, setBudgetError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;
    const timeout = setTimeout(() => controller.abort(), 75000);
    setStatus("loading");
    async function readList(path) {
      const response = await fetch(`${API}${path}`, {
        signal: controller.signal,
      });
      if (!response.ok) throw new Error("Menu request failed");
      const data = await response.json();
      if (!Array.isArray(data)) throw new Error("Unexpected menu response");
      return data;
    }
    // Read shop records directly: a shop exists even before its first menu item.
    // Always refresh the full catalog so shop summaries do not depend on budget.
    const isolationCheck = verifyStagingEnvironment(API, controller.signal);
    const fullCatalogRequest = isolationCheck.then(() =>
      readList("/api/menu-items"),
    );
    Promise.all([
      budget
        ? isolationCheck.then(() =>
            readList(`/api/menu-items?budget=${encodeURIComponent(budget)}`),
          )
        : fullCatalogRequest,
      fullCatalogRequest,
      isolationCheck.then(() => readList("/api/stalls")),
    ])
      .then(([data, fullCatalog, stalls]) => {
        if (!cancelled) {
          setItems(data);
          setCatalog(fullCatalog);
          setShopRecords(stalls);
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
    setListedOnly(false);
    setBudget("");
    setMenuBudget("");
    setBudgetError("");
    setSort("default");
  }
  function scrollToMenu() {
    document.getElementById("menu").scrollIntoView({
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
      setBudgetError(
        "Enter ₱0.01–₱10,000, with up to two decimal places.",
      );
      return;
    }
    setBudgetError("");
    setBudget(amount);
    setMenuBudget(amount);
    setAttempt((current) => current + 1);
    scrollToMenu();
  }
  const shops = shopRecords.map((record) => {
    const menu = catalog.filter((item) => item.stall_id === record.id);
    return {
      ...record,
      count: menu.length,
      min: menu.length
        ? Math.min(...menu.map((item) => Number(item.price)))
        : null,
    };
  });
  const selectedShop = shops.find((entry) => String(entry.id) === shop);
  const hasDemoShops = shops.some((entry) => isDemoName(entry.name));
  const visible = items
    .filter(
      (item) =>
        (category === "All items" || item.category === category) &&
        (!shop || String(item.stall_id) === shop) &&
        (!listedOnly || item.is_listed) &&
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
  const filtered =
    budget || query || shop || category !== "All items" || listedOnly;

  return (
    <>
      <a href="#recommendations" className="skip-link">
        Skip to meal finder
      </a>
      <StagingBanner />
      <header className="header" id="top">
        <Brand />
        <nav aria-label="Main navigation">
          <a href="#recommendations">Meal finder</a>
          <a href="#shops">Browse menus</a>
          <a className="nav-collection" href="#meal-boxes">My Meal Boxes</a>
        </nav>
      </header>
      <main>
        <MealPlanner
          budget={draftBudget}
          catalog={catalog}
          onBudgetChange={setDraftBudget}
          highlights={
            <MenuCarousel
              items={catalog}
              budget={draftBudget}
              onSelect={(item) => {
                clearFilters();
                setQuery(item.name);
                setShop(String(item.stall_id));
                setListedOnly(true);
              }}
            />
          }
        >
          <section
            id="shops"
            className="shops-section"
            aria-labelledby="shops-title"
          >
            <div className="section-heading">
              <h2 id="shops-title">Browse shops</h2>
              <a className="text-link" href="#menu">
                See menu <Icon name="arrow" />
              </a>
            </div>
            {shops.length > 0 ? (
              <div className="shop-grid">
                {shops.map((entry, index) => (
                  <article className="shop-card" key={entry.id}>
                    <div className={`shop-symbol shop-${index % 3}`}>
                      <Photo
                        src={entry.image_url}
                        alt={entry.name}
                        className="shop-photo"
                        fallback={<Icon name="shop" width="27" height="27" />}
                      />
                    </div>
                    <div className="shop-info">
                      <h3>{cleanName(entry.name)}</h3>
                      <p>
                        <Icon name="pin" width="14" height="14" />
                        {entry.location}
                      </p>
                      <span>
                        {entry.count
                          ? `${entry.count} listed ${entry.count === 1 ? "item" : "items"} · From ${pesos.format(entry.min)}`
                          : "Menu not added yet"}
                      </span>
                    </div>
                    <button
                      className="shop-link"
                      aria-label={`View ${cleanName(entry.name)} menu`}
                      onClick={() => {
                        clearFilters();
                        setShop(String(entry.id));
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
                  : status === "ready"
                    ? "No shops listed yet. Check back soon."
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
                <h2 id="menu-title">
                  {selectedShop ? cleanName(selectedShop.name) : "All menu items"}
                </h2>
                {selectedShop && (
                  <p className="section-caption menu-location">
                    <Icon name="pin" width="16" height="16" /> {selectedShop.location}
                  </p>
                )}
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
            <p className="section-caption menu-guidance">
              {hasDemoShops && "Demo listings use fictional data. "}
              Prices are recorded. Confirm current prices and availability at the shop.
            </p>
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
            <form
              className="menu-budget"
              onSubmit={(event) => {
                event.preventDefault();
                findFood(menuBudget);
              }}
            >
              <label htmlFor="budget">Maximum price (₱)</label>
              <input
                id="budget"
                inputMode="decimal"
                value={menuBudget}
                onChange={(event) => setMenuBudget(event.target.value)}
                placeholder="Any price"
                aria-describedby={budgetError ? "budget-error" : undefined}
                aria-invalid={!!budgetError}
              />
              <button className="clear-button" type="submit">Apply</button>
              {budgetError && (
                <p className="validation" id="budget-error" role="alert">
                  {budgetError}
                </p>
              )}
            </form>
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
                        at{" "}
                        <strong>
                          {cleanName(selectedShop?.name || "selected shop")}
                        </strong>
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
                    checked={listedOnly}
                    onChange={(event) => setListedOnly(event.target.checked)}
                  />{" "}
                  Listed items only
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
                  We couldn’t retrieve the listings. Check your connection and
                  try again in a moment.
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
                <h3>
                  {selectedShop?.count === 0 || !catalog.length
                    ? "This shop’s menu is on its way."
                    : "No matches on the menu just yet."}
                </h3>
                <p>
                  {selectedShop?.count === 0 || !catalog.length
                    ? "No meals or prices have been listed for this shop yet. Browse another shop while its menu is being added."
                    : "Try a bigger budget, another category, or a different search."}
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
                      <FoodCover item={item} />
                      {!item.is_listed && (
                        <span className="availability unavailable"><span /> Unlisted</span>
                      )}
                      <span className="category-label">{item.category}</span>
                    </div>
                    <div className="card-content">
                      <button
                        className="stall-name"
                        onClick={() => setShop(String(item.stall_id))}
                      >
                        {cleanName(item.stall_name)}{" "}
                        <span aria-hidden="true">↗</span>
                      </button>
                      <h3>{item.name}</h3>
                      {item.description && <p className="description">{item.description}</p>}
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
                          Recorded{" "}
                          {new Date(item.updated_at).toLocaleDateString("en-PH", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          })}{" "}
                          {isDemoName(item.stall_name) && " · Demo"}
                        </small>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </MealPlanner>
        <details id="how" className="how-guide">
          <summary>How AnimoMeals works</summary>
          <p>
            AI reads your food preferences. AnimoMeals checks recorded menu prices
            against your budget. Save the combinations you want to try in My Meal
            Boxes.
          </p>
        </details>
        <footer>
          <div>
            <Brand />
          </div>
          <div className="footer-links">
            <a href="#meal-boxes">My Meal Boxes</a>
            <a href="#recommendations">Meal finder</a>
            <a href="#shops">Browse shops</a>
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
