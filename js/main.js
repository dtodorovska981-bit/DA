/* ===== Mareli — интерактивност (мени, каталог, филтрирање) ===== */

/* Мобилно мени */
function initNav() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => nav.classList.toggle("open"));
  }
}

/* Илустративни приказ-слики (SVG) за фелна и гума */
function visual(type) {
  if (type === "rim") {
    return `
      <svg viewBox="0 0 120 120" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
        <circle cx="60" cy="60" r="50" />
        <circle cx="60" cy="60" r="14" />
        <circle cx="60" cy="60" r="4" fill="currentColor" stroke="none" />
        <g>
          <line x1="60" y1="60" x2="60" y2="12" />
          <line x1="60" y1="60" x2="100" y2="84" />
          <line x1="60" y1="60" x2="20" y2="84" />
          <line x1="60" y1="60" x2="98" y2="38" />
          <line x1="60" y1="60" x2="22" y2="38" />
        </g>
      </svg>`;
  }
  /* tire */
  return `
    <svg viewBox="0 0 120 120" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
      <circle cx="60" cy="60" r="50" />
      <circle cx="60" cy="60" r="28" />
      <g stroke-width="4">
        <line x1="60" y1="10" x2="60" y2="32" />
        <line x1="60" y1="88" x2="60" y2="110" />
        <line x1="10" y1="60" x2="32" y2="60" />
        <line x1="88" y1="60" x2="110" y2="60" />
        <line x1="25" y1="25" x2="40" y2="40" />
        <line x1="95" y1="25" x2="80" y2="40" />
        <line x1="25" y1="95" x2="40" y2="80" />
        <line x1="95" y1="95" x2="80" y2="80" />
      </g>
    </svg>`;
}

/* Иницијализација на каталог страница (rims или tires) */
function initCatalog(category) {
  const grid = document.getElementById("product-grid");
  const filtersEl = document.getElementById("filters");
  const countEl = document.getElementById("result-count");
  const searchEl = document.getElementById("search");
  const clearEl = document.getElementById("clear-filters");
  if (!grid) return;

  const items = PRODUCTS.filter((p) => p.category === category);

  /* Собери ги сите уникатни тагови */
  const allTags = [...new Set(items.flatMap((p) => p.tags))].sort((a, b) =>
    a.localeCompare(b, "mk")
  );

  const activeTags = new Set();
  let searchTerm = "";

  /* Изгради ги копчињата за таговите */
  allTags.forEach((tag) => {
    const chip = document.createElement("button");
    chip.className = "filter-chip";
    chip.type = "button";
    chip.textContent = tag;
    chip.addEventListener("click", () => {
      if (activeTags.has(tag)) {
        activeTags.delete(tag);
        chip.classList.remove("active");
      } else {
        activeTags.add(tag);
        chip.classList.add("active");
      }
      render();
    });
    filtersEl.appendChild(chip);
  });

  if (searchEl) {
    searchEl.addEventListener("input", (e) => {
      searchTerm = e.target.value.trim().toLowerCase();
      render();
    });
  }

  if (clearEl) {
    clearEl.addEventListener("click", () => {
      activeTags.clear();
      searchTerm = "";
      if (searchEl) searchEl.value = "";
      filtersEl
        .querySelectorAll(".filter-chip.active")
        .forEach((c) => c.classList.remove("active"));
      render();
    });
  }

  function matches(p) {
    /* Производот мора да ги содржи СИТЕ избрани тагови */
    const tagOk = [...activeTags].every((t) => p.tags.includes(t));
    const text = (p.name + " " + p.desc + " " + p.tags.join(" ")).toLowerCase();
    const searchOk = !searchTerm || text.includes(searchTerm);
    return tagOk && searchOk;
  }

  function render() {
    const filtered = items.filter(matches);
    if (countEl) {
      countEl.textContent =
        filtered.length + (filtered.length === 1 ? " производ" : " производи");
    }

    if (filtered.length === 0) {
      grid.innerHTML =
        '<div class="empty">Нема резултати за избраните филтри. Обидете се да отстраните некој таг.</div>';
      return;
    }

    grid.innerHTML = filtered
      .map(
        (p) => `
      <article class="product">
        <div class="thumb">${visual(p.type)}</div>
        <div class="body">
          <h3>${p.name}</h3>
          <p class="desc">${p.desc}</p>
          <div class="tags">${p.tags
            .map((t) => `<span class="tag">${t}</span>`)
            .join("")}</div>
          <div class="price-row">
            <span class="price">${p.price}</span>
            <a class="btn btn-ghost" href="contact.html">Прашај</a>
          </div>
        </div>
      </article>`
      )
      .join("");
  }

  render();
}

document.addEventListener("DOMContentLoaded", initNav);
