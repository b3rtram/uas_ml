// app.js — FRONTEND BEHAVIOR (runs in the browser).
//
// Three jobs, all done by hand:
//   1. Catch user events (form submit, button clicks)
//   2. Talk to the backend over HTTP (fetch)
//   3. Update the page (DOM manipulation, Chart.js)
//
// Every line of code in this file is wiring you have to write when frontend
// and backend are separated. In the Streamlit version, none of this exists.

// ----------------------------------------------------------------
// DOM references
// ----------------------------------------------------------------

const addForm        = document.getElementById("add-form");
const tickerInput    = document.getElementById("ticker-input");
const addError       = document.getElementById("add-error");
const portfolioList  = document.getElementById("portfolio-list");
const emptyMessage   = document.getElementById("empty-message");

const forecastSection = document.getElementById("forecast-section");
const forecastTitle   = document.getElementById("forecast-title");
const forecastStatus  = document.getElementById("forecast-status");
const forecastStats   = document.getElementById("forecast-stats");
const chartWrap       = document.getElementById("chart-wrap");
const chartCanvas     = document.getElementById("forecast-chart");

const statLatest      = document.getElementById("stat-latest");
const statPredicted   = document.getElementById("stat-predicted");
const statChange      = document.getElementById("stat-change");
const statRange       = document.getElementById("stat-range");

let currentChart = null;  // Chart.js instance — kept so we can destroy() it before redrawing


// ----------------------------------------------------------------
// 1) API calls — every interaction with the backend goes through fetch()
// ----------------------------------------------------------------

async function apiListPortfolio() {
  const r = await fetch("/api/portfolio");
  if (!r.ok) throw new Error("Failed to load portfolio");
  return r.json();
}

async function apiAddStock(ticker) {
  const r = await fetch("/api/portfolio", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker }),
  });
  if (!r.ok) {
    const err = await r.json();
    throw new Error(err.detail || "Add failed");
  }
  return r.json();
}

async function apiDeleteStock(id) {
  const r = await fetch(`/api/portfolio/${id}`, { method: "DELETE" });
  if (!r.ok) throw new Error("Delete failed");
}

async function apiGetForecast(ticker, horizon = 30) {
  const r = await fetch(`/api/forecast/${ticker}?horizon=${horizon}`);
  if (!r.ok) {
    const err = await r.json();
    throw new Error(err.detail || "Forecast failed");
  }
  return r.json();
}


// ----------------------------------------------------------------
// 2) Render the portfolio list (called after every mutation)
// ----------------------------------------------------------------

async function renderPortfolio() {
  let items;
  try {
    items = await apiListPortfolio();
  } catch (err) {
    showAddError(err.message);
    return;
  }

  portfolioList.innerHTML = "";

  if (items.length === 0) {
    emptyMessage.classList.remove("hidden");
    return;
  }
  emptyMessage.classList.add("hidden");

  for (const item of items) {
    const li = document.createElement("li");
    li.style.cursor = "pointer";
    li.title = `Click to forecast ${item.ticker}`;

    // The whole row is clickable — much harder to miss than a small button.
    li.addEventListener("click", (event) => {
      // Ignore clicks that came from inside the delete button
      if (event.target.closest(".delete-button")) return;

      console.log("[stocks-demo] forecasting", item.ticker);
      Promise.resolve(showForecast(item.ticker)).catch((err) => {
        console.error("[stocks-demo] showForecast failed:", err);
        alert("Forecast error: " + (err && err.message ? err.message : err));
      });
    });

    // Ticker label — just a span, the row above handles the click
    const tickerLabel = document.createElement("span");
    tickerLabel.className = "ticker-button";
    tickerLabel.textContent = item.ticker;

    // Delete button — stops the click from bubbling to the row above
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-button";
    deleteButton.textContent = "✕";
    deleteButton.title = "Remove";
    deleteButton.addEventListener("click", async (event) => {
      event.stopPropagation();
      console.log("[stocks-demo] deleting", item.ticker);
      try {
        await apiDeleteStock(item.id);
        await renderPortfolio();
      } catch (err) {
        showAddError(err.message);
      }
    });

    li.appendChild(tickerLabel);
    li.appendChild(deleteButton);
    portfolioList.appendChild(li);
  }
}


// ----------------------------------------------------------------
// 3) Run a forecast and render the chart
// ----------------------------------------------------------------

async function showForecast(ticker) {
  // Show section, reset state
  forecastSection.classList.remove("hidden");
  forecastTitle.textContent = `${ticker} forecast`;
  forecastStatus.textContent = `Fetching data and running Prophet for ${ticker}…`;
  forecastStatus.classList.remove("hidden");
  forecastStats.classList.add("hidden");
  chartWrap.classList.add("hidden");

  // Scroll the forecast into view (nice touch for desktop)
  forecastSection.scrollIntoView({ behavior: "smooth", block: "nearest" });

  let result;
  try {
    result = await apiGetForecast(ticker, 30);
  } catch (err) {
    forecastStatus.textContent = `Error: ${err.message}`;
    return;
  }

  forecastStatus.classList.add("hidden");
  forecastStats.classList.remove("hidden");
  chartWrap.classList.remove("hidden");

  // Stats row
  const latest = result.latest_price;
  const lastForecast = result.forecast[result.forecast.length - 1];
  const predicted = lastForecast.yhat;
  const lower = lastForecast.yhat_lower;
  const upper = lastForecast.yhat_upper;
  const changePct = ((predicted - latest) / latest) * 100;

  statLatest.textContent = formatPrice(latest);
  statPredicted.textContent = formatPrice(predicted);
  statRange.textContent = `${formatPrice(lower)} – ${formatPrice(upper)}`;
  statChange.textContent = `${changePct >= 0 ? "+" : ""}${changePct.toFixed(1)}%`;
  statChange.className = "stat-change " + (changePct >= 0 ? "up" : "down");

  drawChart(result.historical, result.forecast);
}


function formatPrice(p) {
  return "$" + p.toFixed(2);
}


function drawChart(historical, forecast) {
  // Destroy the previous chart, if any — Chart.js keeps state otherwise
  if (currentChart) {
    currentChart.destroy();
  }

  // Build labels (dates) and datasets
  const histDates = historical.map(p => p.date);
  const histValues = historical.map(p => p.value);

  const fcDates = forecast.map(p => p.date);
  const fcValues = forecast.map(p => p.yhat);
  const fcUpper  = forecast.map(p => p.yhat_upper);
  const fcLower  = forecast.map(p => p.yhat_lower);

  // For a continuous x-axis, we concatenate dates and pad each series with nulls
  // so they line up on the right indices.
  const allDates = [...histDates, ...fcDates];
  const histSeries = [...histValues, ...new Array(fcDates.length).fill(null)];
  const fcSeries    = [...new Array(histDates.length).fill(null), ...fcValues];
  const upperSeries = [...new Array(histDates.length).fill(null), ...fcUpper];
  const lowerSeries = [...new Array(histDates.length).fill(null), ...fcLower];

  currentChart = new Chart(chartCanvas.getContext("2d"), {
    type: "line",
    data: {
      labels: allDates,
      datasets: [
        {
          label: "Confidence band (upper)",
          data: upperSeries,
          borderColor: "transparent",
          backgroundColor: "rgba(15, 118, 110, 0.12)",
          fill: "+1",  // fill down to the next dataset (lower band)
          pointRadius: 0,
        },
        {
          label: "Confidence band (lower)",
          data: lowerSeries,
          borderColor: "transparent",
          backgroundColor: "rgba(15, 118, 110, 0.12)",
          fill: false,
          pointRadius: 0,
        },
        {
          label: "Historical",
          data: histSeries,
          borderColor: "#1E293B",
          backgroundColor: "#1E293B",
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.1,
        },
        {
          label: "Forecast",
          data: fcSeries,
          borderColor: "#0F766E",
          backgroundColor: "#0F766E",
          borderWidth: 2,
          borderDash: [6, 4],
          pointRadius: 0,
          tension: 0.1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: {
          ticks: { maxTicksLimit: 8, color: "#64748B" },
          grid: { color: "#F1F5F9" },
        },
        y: {
          ticks: {
            color: "#64748B",
            callback: (v) => "$" + v,
          },
          grid: { color: "#F1F5F9" },
        },
      },
      plugins: {
        legend: {
          // Hide the two confidence-band series from the legend — they're cosmetic
          labels: { filter: (item) => !item.text.startsWith("Confidence") },
        },
        tooltip: {
          callbacks: {
            label: (ctx) =>
              ctx.dataset.label.startsWith("Confidence")
                ? null
                : `${ctx.dataset.label}: $${ctx.parsed.y.toFixed(2)}`,
          },
        },
      },
    },
  });
}


// ----------------------------------------------------------------
// 4) Helpers
// ----------------------------------------------------------------

function showAddError(message) {
  addError.textContent = message;
  addError.classList.remove("hidden");
  setTimeout(() => addError.classList.add("hidden"), 4000);
}


// ----------------------------------------------------------------
// 5) Wire up event listeners
// ----------------------------------------------------------------

// Form submission — add a ticker
addForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const ticker = tickerInput.value.trim().toUpperCase();
  if (!ticker) return;

  try {
    await apiAddStock(ticker);
    tickerInput.value = "";
    addError.classList.add("hidden");
    await renderPortfolio();
  } catch (err) {
    showAddError(err.message);
  }
});

// Delete and ticker-click handlers are attached directly in renderPortfolio()
// when each button is created — no delegation needed.


// ----------------------------------------------------------------
// 6) Initial load — fetch the portfolio when the page opens
// ----------------------------------------------------------------

renderPortfolio();
