/*
JS mínimo (sin SPA)

Solo para:
- Toggle de sidebar (estado persistente)
- Pequeños hooks post-HTMX (ej: re-marcar activo)
*/

(function () {
  const storageKey = "ds.sidebar.collapsed";
  const charts = new WeakMap();

  function setCollapsed(isCollapsed) {
    document.body.classList.toggle("sidebar-collapsed", isCollapsed);
    localStorage.setItem(storageKey, isCollapsed ? "1" : "0");
  }

  function initSidebarState() {
    const saved = localStorage.getItem(storageKey);
    if (saved === "1") setCollapsed(true);
  }

  function bindToggles() {
    document.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-action='toggle-sidebar']");
      if (!btn) return;

      // En desktop: colapsa. En móvil: abre overlay.
      if (window.matchMedia("(max-width: 992px)").matches) {
        document.body.classList.toggle("sidebar-open");
        return;
      }

      setCollapsed(!document.body.classList.contains("sidebar-collapsed"));
    });

    // Cerrar overlay al navegar (móvil)
    document.addEventListener("click", (e) => {
      const link = e.target.closest(".app-sidebar a");
      if (!link) return;
      document.body.classList.remove("sidebar-open");
    });
  }

  function setActiveNav(pathname) {
    const current = normalizeUrl(pathname);

    document.querySelectorAll(".app-sidebar .nav-link").forEach((a) => {
      const rawHref = a.getAttribute("href") || "";
      const href = normalizeUrl(rawHref);
      a.classList.toggle("is-active", href === current);
    });
  }

  function normalizeUrl(raw) {
    // Acepta pathname ("/dashboard/") o href relativo/absoluto.
    // Compara pathname+search para soportar tabs (?tab=...) en el menú.
    try {
      const url = new URL(raw, window.location.origin);
      // Normaliza barra final (consistente con Django).
      const path = url.pathname.endsWith("/") ? url.pathname : `${url.pathname}/`;
      return `${path}${url.search}`;
    } catch (_) {
      return raw;
    }
  }

  function initDemoCharts(root) {
    // Server-driven: el servidor envía data-*; el cliente solo pinta.
    if (!window.Chart) return;
    root.querySelectorAll("canvas[data-chart='demo']").forEach((canvas) => {
      // Re-init seguro tras HTMX swaps.
      const existing = charts.get(canvas);
      if (existing) {
        existing.destroy();
        charts.delete(canvas);
      }

      let labels = [];
      let values = [];
      try {
        labels = JSON.parse(canvas.getAttribute("data-labels") || "[]");
        values = JSON.parse(canvas.getAttribute("data-values") || "[]");
      } catch (_) {
        // Si el JSON es inválido, no pintamos el chart.
        return;
      }

      const chart = new window.Chart(canvas, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Eventos",
              data: values,
              borderWidth: 2,
              tension: 0.35,
              pointRadius: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: { grid: { display: false } },
            y: { grid: { color: "rgba(16, 24, 40, 0.06)" } },
          },
        },
      });

      charts.set(canvas, chart);
    });
  }

  // Hooks HTMX
  function bindHtmx() {
    document.body.addEventListener("htmx:pushedIntoHistory", (evt) => {
      // evt.detail.path puede incluir querystring.
      setActiveNav(evt.detail.path);
    });

    document.body.addEventListener("htmx:afterSwap", () => {
      setActiveNav(`${window.location.pathname}${window.location.search}`);
      initDemoCharts(document);
    });
  }

  initSidebarState();
  bindToggles();
  bindHtmx();
  setActiveNav(`${window.location.pathname}${window.location.search}`);
  initDemoCharts(document);
})();
