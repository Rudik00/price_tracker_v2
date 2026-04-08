const stateEl = document.getElementById("state");
const gridEl = document.getElementById("grid");
const subtitleEl = document.getElementById("subtitle");
const countBadgeEl = document.getElementById("countBadge");
const refreshBtn = document.getElementById("refreshBtn");
const debugPanel = document.getElementById("debugPanel");
const debugLoadBtn = document.getElementById("debugLoadBtn");
const initDataInput = document.getElementById("initDataInput");

const tg = window.Telegram?.WebApp;

function setState(text) {
  stateEl.textContent = text;
}

function toPrice(value, currency) {
  if (value === null || value === undefined) {
    return "-";
  }
  const cur = currency || "";
  return `${value} ${cur}`.trim();
}

function renderProducts(products) {
  gridEl.innerHTML = "";
  countBadgeEl.textContent = `${products.length} товаров`;

  if (!products.length) {
    setState("Список пуст. Добавь товар в основном боте.");
    return;
  }

  setState("");
  for (const item of products) {
    const card = document.createElement("article");
    card.className = "card";
    const imageBlock = item.img
      ? `<img class="product-image" src="${item.img}" alt="Товар ID ${item.local_id}" loading="lazy" />`
      : `<div class="product-image product-image-empty">Нет фото</div>`;
    card.innerHTML = `
      ${imageBlock}
      <h3>ID ${item.local_id}</h3>
      <div class="row"><span class="label">Текущая</span><span class="value">${toPrice(item.price_now, item.currency)}</span></div>
      <div class="row"><span class="label">Старт</span><span class="value">${toPrice(item.price_start, item.currency)}</span></div>
      <div class="row"><span class="label">Максимум</span><span class="value">${toPrice(item.price_max, item.currency)}</span></div>
      <div class="row"><span class="label">Минимум</span><span class="value">${toPrice(item.price_min, item.currency)}</span></div>
      <a class="url" href="${item.url}" target="_blank" rel="noopener noreferrer">${item.url}</a>
    `;
    gridEl.appendChild(card);
  }
}

async function loadProducts(initData) {
  if (!initData) {
    setState("initData не найден. Открой страницу внутри Telegram Mini App.");
    return;
  }

  setState("Загружаем товары...");
  try {
    const response = await fetch("/api/products", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ init_data: initData }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Ошибка загрузки");
    }

    subtitleEl.textContent = `Пользователь Telegram ID: ${payload.telegram_id}`;
    renderProducts(payload.products || []);
  } catch (error) {
    setState(`Ошибка: ${error.message}`);
  }
}

function setupTelegramWebApp() {
  if (!tg) {
    debugPanel.classList.remove("hidden");
    setState("Режим вне Telegram: вставь initData вручную.");
    return;
  }

  tg.ready();
  tg.expand();
  tg.MainButton.hide();

  if (tg.colorScheme === "dark") {
    document.documentElement.style.setProperty("--bg-1", "#071114");
    document.documentElement.style.setProperty("--bg-2", "#102228");
  }
}

setupTelegramWebApp();
loadProducts(tg?.initData || "");

refreshBtn.addEventListener("click", () => {
  loadProducts(tg?.initData || initDataInput.value.trim());
});

debugLoadBtn.addEventListener("click", () => {
  loadProducts(initDataInput.value.trim());
});
