(async function () {
  const app = document.getElementById("app");
  const updatedEl = document.getElementById("updated");

  function showMessage(text) {
    app.innerHTML = `<div class="state-msg">${text}</div>`;
  }

  function fmtSigned(n, digits = 1) {
    if (n === null || n === undefined || isNaN(n)) return "n/a";
    const sign = n > 0 ? "+" : "";
    return `${sign}${n.toFixed(digits)}%`;
  }

  function fmtPct(n, digits = 1) {
    if (n === null || n === undefined || isNaN(n)) return "n/a";
    return `${n.toFixed(digits)}%`;
  }

  function fmtUpdated(iso) {
    if (!iso) return "";
    try {
      return new Date(iso).toLocaleString("th-TH", {
        timeZone: "Asia/Bangkok",
        dateStyle: "medium",
        timeStyle: "short",
      });
    } catch {
      return iso;
    }
  }

  function render(data) {
    const pl = data.unrealized_pl_pct;
    const plClass = pl > 0 ? "up" : pl < 0 ? "down" : "";
    const xirr = data.xirr_pct;
    const alloc = data.allocation || {};
    const holdings = data.holdings || [];
    const rebalance = data.rebalance_alert || {};

    updatedEl.textContent = data.updated_at ? `อัปเดต ${fmtUpdated(data.updated_at)}` : "";

    const rebalanceHtml = rebalance.triggered
      ? `<div class="rebalance-banner">
          <span>⚠️</span>
          <span>สัดส่วนพอร์ตคลาดเคลื่อนจากเป้าหมาย — ${rebalance.message || "ตรวจสอบ rebalance"}</span>
        </div>`
      : "";

    const holdingsHtml = holdings.length
      ? holdings
          .map(
            (h) => `
        <div class="holding-row">
          <span class="holding-ticker">${h.ticker}</span>
          ${h.market ? `<span class="holding-market">${h.market}</span>` : ""}
          <span class="holding-leader"></span>
          <span class="holding-pct">${fmtPct(h.allocation_pct)}</span>
        </div>`
          )
          .join("")
      : `<div class="state-msg">ยังไม่มีรายการถือครอง</div>`;

    const corePct = alloc.core_pct || 0;
    const satellitePct = alloc.satellite_pct || 0;

    app.innerHTML = `
      <div class="hero">
        <div class="hero-pl ${plClass}">${fmtSigned(pl)}</div>
        <div class="hero-label">กำไร/ขาดทุน รวม (Unrealized)</div>
        <div class="hero-badge">XIRR ${fmtSigned(xirr)}</div>
      </div>

      <div class="metrics">
        <div class="metric-card">
          <div class="metric-value ${plClass}">${fmtSigned(pl)}</div>
          <div class="metric-label">Unrealized P/L</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${fmtSigned(xirr)}</div>
          <div class="metric-label">XIRR</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="font-size:.78rem">${fmtUpdated(data.updated_at) || "n/a"}</div>
          <div class="metric-label">อัปเดตล่าสุด</div>
        </div>
      </div>

      ${rebalanceHtml}

      <div class="section">
        <div class="section-title">สัดส่วนพอร์ต</div>
        <div class="alloc-bar">
          <div class="alloc-seg core" style="width:${corePct}%"></div>
          <div class="alloc-seg satellite" style="width:${satellitePct}%"></div>
        </div>
        <div class="alloc-legend">
          <span class="alloc-legend-item"><span class="alloc-dot core"></span>Core ${corePct.toFixed(1)}%</span>
          <span class="alloc-legend-item"><span class="alloc-dot satellite"></span>Satellite ${satellitePct.toFixed(1)}%</span>
        </div>
      </div>

      <div class="section">
        <div class="section-title">รายการถือครอง</div>
        ${holdingsHtml}
      </div>
    `;
  }

  try {
    const res = await fetch("./dca.json?t=" + Date.now());
    if (!res.ok) throw new Error("not found");
    const data = await res.json();
    render(data);
  } catch {
    showMessage("ข้อมูลกำลังอัปเดต ลองใหม่ภายหลัง");
  }
})();
