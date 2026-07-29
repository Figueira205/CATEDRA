/* ============================================================
   CÁTEDRA DE LA HISPANIDAD — Comportamiento del sitio
   Vanilla JS, mejora progresiva. Sin dependencias.
   En WordPress: encolar con wp_enqueue_script (defer).
   ============================================================ */
(function () {
  "use strict";
  var d = document;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Utilidades ---------- */
  function $(sel, ctx) { return (ctx || d).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || d).querySelectorAll(sel)); }
  function norm(s) {
    return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  function esc(s) {
    return (s || "").replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function highlight(text, q) {
    if (!q) return esc(text);
    var i = norm(text).indexOf(norm(q));
    if (i < 0) return esc(text);
    return esc(text.slice(0, i)) + "<mark>" + esc(text.slice(i, i + q.length)) + "</mark>" + esc(text.slice(i + q.length));
  }
  var TYPE_LABELS = {
    persona: "Personas", proyecto: "Investigación", area: "Áreas", actividad: "Actividades",
    revista: "Revista", publicacion: "Publicaciones", multimedia: "Multimedia",
    premio: "Premios", convenio: "Convenios", pagina: "Páginas"
  };

  /* ---------- Cabecera: estado scroll ---------- */
  var header = $(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Mega menú (generado desde CH_NAV) ---------- */
  var navRoot = $("#main-nav-list");
  if (navRoot && window.CH_NAV) {
    window.CH_NAV.forEach(function (sec, idx) {
      var li = d.createElement("li");
      li.innerHTML =
        '<button class="nav-link" aria-expanded="false" aria-controls="mega-' + idx + '">' +
        esc(sec.label) + ' <span class="caret" aria-hidden="true"></span></button>';
      navRoot.appendChild(li);

      var mega = d.createElement("div");
      mega.className = "mega";
      mega.id = "mega-" + idx;
      var links = sec.items.map(function (it, i) {
        return '<a href="' + it[1] + '"><span class="n">' + String(i + 1).padStart(2, "0") + "</span>" + esc(it[0]) + "</a>";
      }).join("");
      mega.innerHTML =
        '<div class="container"><div class="mega__inner">' +
        '<div class="mega__label">' + esc(sec.label) + "</div>" +
        '<div class="mega__cols">' + links + "</div>" +
        '<div class="mega__feat"><a href="' + sec.feature.url + '">' +
        '<img src="' + sec.feature.img + '" alt="" width="640" height="426" loading="lazy">' +
        '<span class="mono">' + esc(sec.feature.kicker) + "</span><p>" + esc(sec.feature.title) + "</p></a></div>" +
        "</div></div>";
      header.appendChild(mega);

      var btn = li.querySelector("button");
      function open() {
        closeAllMegas();
        mega.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
      }
      function close() {
        mega.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
      }
      btn.addEventListener("click", function () {
        mega.classList.contains("is-open") ? close() : open();
      });
      li.addEventListener("mouseenter", open);
      mega.addEventListener("keydown", function (e) { if (e.key === "Escape") { close(); btn.focus(); } });
    });
    /* El panel permanece abierto mientras el cursor esté dentro de la cabecera
       (botones, hueco intermedio o el propio desplegable). Solo se cierra al
       salir de toda la cabecera, con un pequeño margen de 250 ms. */
    var headerCloseTimer = null;
    header.addEventListener("mouseleave", function () {
      headerCloseTimer = setTimeout(closeAllMegas, 250);
    });
    header.addEventListener("mouseenter", function () {
      if (headerCloseTimer) { clearTimeout(headerCloseTimer); headerCloseTimer = null; }
    });
  }
  function closeAllMegas() {
    $$(".mega.is-open").forEach(function (m) { m.classList.remove("is-open"); });
    $$(".main-nav [aria-expanded='true']").forEach(function (b) { b.setAttribute("aria-expanded", "false"); });
  }
  d.addEventListener("click", function (e) {
    if (header && !header.contains(e.target)) closeAllMegas();
  });
  d.addEventListener("keydown", function (e) { if (e.key === "Escape") closeAllMegas(); });

  /* ---------- Menú móvil ---------- */
  var mm = $("#mobile-menu");
  var mmOpenBtn = $("#menu-open");
  var mmCloseBtn = $("#menu-close");
  var lastFocus = null;
  if (mm && window.CH_NAV) {
    var mnav = $("#mobile-nav");
    window.CH_NAV.forEach(function (sec) {
      var item = d.createElement("div");
      item.className = "mm-item";
      item.innerHTML =
        '<button class="mm-top" aria-expanded="false">' + esc(sec.label) +
        ' <span aria-hidden="true">+</span></button>' +
        '<div class="mm-sub">' +
        sec.items.map(function (it) { return '<a href="' + it[1] + '">' + esc(it[0]) + "</a>"; }).join("") +
        "</div>";
      mnav.appendChild(item);
      var top = item.querySelector(".mm-top");
      top.addEventListener("click", function () {
        var isOpen = item.classList.toggle("is-open");
        top.setAttribute("aria-expanded", String(isOpen));
        top.querySelector("span").textContent = isOpen ? "−" : "+";
      });
    });
  }
  function openMobile() {
    lastFocus = d.activeElement;
    mm.classList.add("is-open");
    d.body.style.overflow = "hidden";
    mmCloseBtn.focus();
  }
  function closeMobile() {
    mm.classList.remove("is-open");
    d.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  if (mmOpenBtn) mmOpenBtn.addEventListener("click", openMobile);
  if (mmCloseBtn) mmCloseBtn.addEventListener("click", closeMobile);
  if (mm) mm.addEventListener("keydown", function (e) { if (e.key === "Escape") closeMobile(); });

  /* ---------- Command palette / buscador global ---------- */
  var palette = $("#palette");
  var paletteInput = palette ? $("#palette-input") : null;
  var paletteResults = palette ? $("#palette-results") : null;
  var paletteLast = null;

  function searchIndex(q, limit) {
    var nq = norm(q);
    if (!nq) return [];
    var scored = [];
    (window.CH_INDEX || []).forEach(function (item) {
      var nt = norm(item.t), nd = norm(item.d || "");
      var score = -1;
      if (nt.indexOf(nq) === 0) score = 0;
      else if (nt.indexOf(nq) >= 0) score = 1;
      else if (nd.indexOf(nq) >= 0) score = 2;
      else {
        // tolerancia: todas las palabras presentes en título+desc
        var words = nq.split(/\s+/).filter(Boolean);
        if (words.length > 1 && words.every(function (w) { return (nt + " " + nd).indexOf(w) >= 0; })) score = 3;
      }
      if (score >= 0) scored.push({ item: item, score: score });
    });
    scored.sort(function (a, b) { return a.score - b.score; });
    return scored.slice(0, limit || 12).map(function (s) { return s.item; });
  }

  function renderPalette(q) {
    var out = "";
    if (!q) {
      out += '<div class="palette__group">Sugerencias</div>';
      (window.CH_SUGGESTIONS || []).forEach(function (s) {
        out += '<a class="palette__item" href="' + s.url + '"><span class="t">' + esc(s.t) + '</span><span class="k">' + esc(s.k) + "</span></a>";
      });
    } else {
      var res = searchIndex(q, 14);
      if (!res.length) {
        out = '<div class="palette__empty">No hemos encontrado una coincidencia exacta. Prueba con otro término o pulsa Intro para ver áreas relacionadas.</div>';
      } else {
        var groups = {};
        res.forEach(function (r) { (groups[r.type] = groups[r.type] || []).push(r); });
        Object.keys(groups).forEach(function (g) {
          out += '<div class="palette__group">' + (TYPE_LABELS[g] || g) + "</div>";
          groups[g].forEach(function (r) {
            out += '<a class="palette__item" href="' + r.url + '"><span class="t">' + highlight(r.t, q) + '</span><span class="k">Abrir</span></a>';
          });
        });
      }
    }
    paletteResults.innerHTML = out;
  }

  function openPalette() {
    closeAllMegas();
    paletteLast = d.activeElement;
    palette.classList.add("is-open");
    d.body.style.overflow = "hidden";
    paletteInput.value = "";
    renderPalette("");
    paletteInput.focus();
  }
  function closePalette() {
    palette.classList.remove("is-open");
    d.body.style.overflow = "";
    if (paletteLast) paletteLast.focus();
  }
  if (palette) {
    $$("[data-open-search]").forEach(function (b) {
      b.addEventListener("click", function (e) { e.preventDefault(); openPalette(); });
    });
    $("#palette-close").addEventListener("click", closePalette);
    palette.addEventListener("click", function (e) { if (e.target === palette) closePalette(); });
    palette.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closePalette();
      if (e.key === "Enter" && paletteInput.value.trim()) {
        var first = $(".palette__item", paletteResults);
        if (first && e.target === paletteInput) { window.location.href = first.href; }
        else if (!first) { window.location.href = "buscar.html?q=" + encodeURIComponent(paletteInput.value.trim()); }
      }
    });
    paletteInput.addEventListener("input", function () { renderPalette(paletteInput.value.trim()); });
    d.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        palette.classList.contains("is-open") ? closePalette() : openPalette();
      }
    });
  }

  /* Barra de búsqueda del hero → página de resultados */
  $$("form[data-search-form]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var q = f.querySelector("input[name='q']").value.trim();
      window.location.href = q ? "buscar.html?q=" + encodeURIComponent(q) : "buscar.html";
    });
  });

  /* ---------- Página de resultados (buscar.html) ---------- */
  var resultsPage = $("#search-results-page");
  if (resultsPage) {
    var params = new URLSearchParams(window.location.search);
    var q = (params.get("q") || "").trim();
    var input = $("#search-page-input");
    if (input) input.value = q;
    var container = $("#search-results-list");
    var summary = $("#search-summary");
    function runPageSearch(query) {
      var res = query ? searchIndex(query, 50) : [];
      if (!query) {
        summary.textContent = "Escribe un término para buscar personas, proyectos, publicaciones, actividades o recursos.";
        container.innerHTML = "";
        return;
      }
      if (!res.length) {
        summary.textContent = "0 resultados para «" + query + "»";
        container.innerHTML =
          '<div class="empty-state"><h3>No hemos encontrado una coincidencia exacta</h3>' +
          "<p>Prueba con otro término o explora estas áreas relacionadas.</p>" +
          '<p style="margin-top:16px"><a class="tag" href="investigacion.html#areas">Áreas temáticas</a> ' +
          '<a class="tag" href="proyectos.html">Proyectos</a> ' +
          '<a class="tag" href="repositorio.html">Repositorio</a> ' +
          '<a class="tag" href="actividades.html">Agenda</a></p></div>';
        return;
      }
      summary.textContent = res.length + " resultado" + (res.length === 1 ? "" : "s") + " para «" + query + "»";
      container.innerHTML = res.map(function (r) {
        return '<article class="search-result"><span class="type">' + (TYPE_LABELS[r.type] || r.type) + "</span>" +
          '<h3><a href="' + r.url + '">' + highlight(r.t, query) + "</a></h3>" +
          "<p>" + highlight(r.d || "", query) + "</p></article>";
      }).join("");
    }
    runPageSearch(q);
    var pageForm = $("#search-page-form");
    if (pageForm) pageForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var nq = input.value.trim();
      history.replaceState(null, "", nq ? "?q=" + encodeURIComponent(nq) : location.pathname);
      runPageSearch(nq);
    });
  }

  /* ---------- Filtros genéricos ---------- */
  /* Botones [data-filter="valor"] dentro de [data-filter-group="attr"]
     filtran elementos [data-item] por su atributo data-<attr>. */
  /* Un elemento es visible solo si pasa TODOS los grupos de filtros activos
     que apuntan a su mismo contenedor. */
  function refreshFilters(scope) {
    var filters = scope.__chFilters || {};
    var items = $$("[data-item]", scope);
    var visible = 0;
    items.forEach(function (it) {
      var show = Object.keys(filters).every(function (attr) {
        var val = filters[attr];
        if (val === "todos") return true;
        return (it.getAttribute("data-" + attr) || "").split(/\s+/).indexOf(val) >= 0;
      });
      it.hidden = !show;
      if (show) visible++;
    });
    Object.keys(filters).forEach(function (attr) {
      var counter = $("[data-filter-count='" + attr + "']");
      if (counter) counter.textContent = visible;
    });
    var empty = $("[data-filter-empty]", scope.parentElement || d);
    if (empty) empty.hidden = visible > 0;
  }
  $$("[data-filter-group]").forEach(function (group) {
    var attr = group.getAttribute("data-filter-group");
    var scope = $(group.getAttribute("data-filter-target")) || d.body;
    var buttons = $$("[data-filter]", group);
    scope.__chFilters = scope.__chFilters || {};
    function apply(value) {
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-filter") === value)); });
      scope.__chFilters[attr] = value;
      refreshFilters(scope);
    }
    buttons.forEach(function (b) {
      b.addEventListener("click", function () { apply(b.getAttribute("data-filter")); });
    });
    // Estado inicial desde la URL (?estado=activo, ?tipo=seminario…)
    var urlVal = new URLSearchParams(location.search).get(attr);
    apply(urlVal && buttons.some(function (b) { return b.getAttribute("data-filter") === urlVal; }) ? urlVal : "todos");
  });

  /* ---------- Vista rejilla/lista ---------- */
  $$(".view-toggle").forEach(function (vt) {
    var target = $(vt.getAttribute("data-view-target"));
    $$("button", vt).forEach(function (b) {
      b.addEventListener("click", function () {
        $$("button", vt).forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        if (target) target.setAttribute("data-view", b.getAttribute("data-view"));
      });
    });
  });

  /* ---------- Acordeones ---------- */
  $$(".accordion__btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var expanded = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!expanded));
      var panel = d.getElementById(btn.getAttribute("aria-controls"));
      if (panel) panel.classList.toggle("is-open", !expanded);
    });
  });

  /* ---------- Atlas de áreas (acordeón de nodos) ---------- */
  $$(".atlas-item__btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.closest(".atlas-item");
      var isOpen = item.classList.contains("is-open");
      $$(".atlas-item.is-open").forEach(function (i) {
        i.classList.remove("is-open");
        $(".atlas-item__btn", i).setAttribute("aria-expanded", "false");
      });
      if (!isOpen) {
        item.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
        var node = $("#atlas-svg [data-node='" + item.getAttribute("data-area") + "']");
        $$("#atlas-svg [data-node]").forEach(function (n) { n.classList.remove("is-active"); });
        if (node) node.classList.add("is-active");
      }
    });
  });

  /* ---------- Tabs ---------- */
  $$(".tabs").forEach(function (tabs) {
    var list = $(".tabs__list", tabs);
    var btns = $$(".tabs__tab", tabs);
    function select(btn) {
      btns.forEach(function (b) {
        var sel = b === btn;
        b.setAttribute("aria-selected", String(sel));
        b.tabIndex = sel ? 0 : -1;
        var panel = d.getElementById(b.getAttribute("aria-controls"));
        if (panel) panel.hidden = !sel;
      });
      btn.focus();
    }
    btns.forEach(function (b) {
      b.addEventListener("click", function () { select(b); });
    });
    list.addEventListener("keydown", function (e) {
      var i = btns.indexOf(d.activeElement);
      if (i < 0) return;
      if (e.key === "ArrowRight") select(btns[(i + 1) % btns.length]);
      if (e.key === "ArrowLeft") select(btns[(i - 1 + btns.length) % btns.length]);
    });
  });

  /* ---------- Lightbox ---------- */
  var lb = $("#lightbox");
  if (lb) {
    var lbContent = $("#lightbox-media");
    var lbCap = $("#lightbox-caption");
    var lbItems = $$("[data-lightbox]");
    var lbIndex = 0, lbLast = null;
    function showLb(i) {
      lbIndex = (i + lbItems.length) % lbItems.length;
      var el = lbItems[lbIndex];
      var src = el.getAttribute("data-lightbox");
      var isVideo = /\.(mp4|webm)$/i.test(src);
      lbContent.innerHTML = isVideo
        ? '<video src="' + src + '" controls preload="metadata" style="background:#000"></video>'
        : '<img src="' + src + '" alt="' + esc(el.getAttribute("data-caption") || "") + '">';
      lbCap.innerHTML = '<span class="mono">' + esc(el.getAttribute("data-meta") || "") + "</span> " + esc(el.getAttribute("data-caption") || "");
    }
    function openLb(i) {
      lbLast = d.activeElement;
      lb.classList.add("is-open");
      d.body.style.overflow = "hidden";
      showLb(i);
      $(".lightbox__close", lb).focus();
    }
    function closeLb() {
      lb.classList.remove("is-open");
      lbContent.innerHTML = "";
      d.body.style.overflow = "";
      if (lbLast) lbLast.focus();
    }
    lbItems.forEach(function (el, i) {
      el.addEventListener("click", function (e) { e.preventDefault(); openLb(i); });
    });
    $(".lightbox__close", lb).addEventListener("click", closeLb);
    $(".lightbox__prev", lb).addEventListener("click", function () { showLb(lbIndex - 1); });
    $(".lightbox__next", lb).addEventListener("click", function () { showLb(lbIndex + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) closeLb(); });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeLb();
      if (e.key === "ArrowLeft") showLb(lbIndex - 1);
      if (e.key === "ArrowRight") showLb(lbIndex + 1);
      if (e.key === "Tab") { // foco atrapado en el diálogo
        var focusables = $$("button, video", lb).filter(function (x) { return x.offsetParent !== null; });
        var first = focusables[0], last = focusables[focusables.length - 1];
        if (e.shiftKey && d.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }

  /* ---------- Aparición al hacer scroll ---------- */
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-visible"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px" });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal").forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- Nav lateral: sección activa ---------- */
  var sideNav = $(".side-nav");
  if (sideNav && "IntersectionObserver" in window) {
    var links = $$("a[href^='#']", sideNav);
    var map = {};
    links.forEach(function (l) { map[l.getAttribute("href").slice(1)] = l; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          links.forEach(function (l) { l.classList.remove("is-active"); });
          map[en.target.id].classList.add("is-active");
        }
      });
    }, { rootMargin: "-30% 0px -60%" });
    Object.keys(map).forEach(function (id) {
      var sec = d.getElementById(id);
      if (sec) spy.observe(sec);
    });
  }

  /* ---------- Indicador de progreso de lectura ---------- */
  var progress = $(".reading-progress");
  if (progress) {
    window.addEventListener("scroll", function () {
      var h = d.documentElement;
      var pct = (h.scrollTop) / (h.scrollHeight - h.clientHeight) * 100;
      progress.style.width = pct + "%";
    }, { passive: true });
  }

  /* ---------- Validación de formularios ---------- */
  $$("form[data-validate]").forEach(function (form) {
    form.setAttribute("novalidate", "");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      $$("[required]", form).forEach(function (field) {
        var wrap = field.closest(".form-field, .form-check");
        var valid = field.type === "checkbox" ? field.checked : field.value.trim() !== "";
        if (valid && field.type === "email") valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value.trim());
        if (wrap) wrap.classList.toggle("has-error", !valid);
        field.setAttribute("aria-invalid", String(!valid));
        if (!valid && ok) { field.focus(); ok = false; }
      });
      if (ok) {
        var success = $(".form-success", form.parentElement) || $(".form-success", form);
        form.hidden = true;
        if (success) { success.classList.add("is-visible"); success.setAttribute("tabindex", "-1"); success.focus(); }
      }
    });
    $$("[required]", form).forEach(function (field) {
      field.addEventListener("input", function () {
        var wrap = field.closest(".form-field, .form-check");
        if (wrap && wrap.classList.contains("has-error")) wrap.classList.remove("has-error");
      });
    });
  });

  /* ---------- Copiar cita ---------- */
  $$("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = $(btn.getAttribute("data-copy"));
      if (!target) return;
      navigator.clipboard.writeText(target.textContent.trim()).then(function () {
        var old = btn.textContent;
        btn.textContent = "Copiado ✓";
        setTimeout(function () { btn.textContent = old; }, 1800);
      });
    });
  });

  /* ---------- Descargar .ics ---------- */
  $$("[data-ics]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var ev = JSON.parse(btn.getAttribute("data-ics"));
      var ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Catedra de la Hispanidad//ES", "BEGIN:VEVENT",
        "UID:" + Date.now() + "@catedra-hispanidad",
        "DTSTART:" + ev.start, "DTEND:" + ev.end,
        "SUMMARY:" + ev.title, "LOCATION:" + (ev.place || ""),
        "DESCRIPTION:" + (ev.desc || ""), "END:VEVENT", "END:VCALENDAR"].join("\r\n");
      var blob = new Blob([ics], { type: "text/calendar" });
      var a = d.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "actividad-catedra.ics";
      a.click();
      URL.revokeObjectURL(a.href);
    });
  });

  /* ---------- Agenda: próximos eventos (portada) ---------- */
  var nextEvSlot = $("[data-next-event]");
  if (nextEvSlot && window.CH_EVENTS) {
    var today = new Date().toISOString().slice(0, 10);
    var next = window.CH_EVENTS.filter(function (e) { return e.date >= today; })
      .sort(function (a, b) { return a.date < b.date ? -1 : 1; })[0];
    if (next) {
      var dt = new Date(next.date + "T12:00:00");
      var months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
      nextEvSlot.innerHTML =
        '<span class="d">' + dt.getDate() + " " + months[dt.getMonth()] + " · " + esc(next.type) + "</span>" +
        '<span class="t">' + esc(next.title) + "</span>";
      nextEvSlot.href = next.url;
    }
  }

  /* ---------- Calendario mensual ---------- */
  var calRoot = $("#calendar");
  if (calRoot && window.CH_EVENTS) {
    var current = new Date();
    current.setDate(1);
    var monthNames = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
    function renderCal() {
      var y = current.getFullYear(), m = current.getMonth();
      var firstDay = (new Date(y, m, 1).getDay() + 6) % 7; // lunes=0
      var daysIn = new Date(y, m + 1, 0).getDate();
      var html = '<div class="cal__head"><span class="cal__title">' + monthNames[m] + " " + y + "</span>" +
        '<div class="cal__nav"><button type="button" aria-label="Mes anterior" data-cal="-1">←</button>' +
        '<button type="button" aria-label="Mes siguiente" data-cal="1">→</button></div></div>' +
        "<table><caption class='visually-hidden'>Calendario de actividades de " + monthNames[m] + " " + y + "</caption>" +
        "<thead><tr><th>L</th><th>M</th><th>X</th><th>J</th><th>V</th><th>S</th><th>D</th></tr></thead><tbody><tr>";
      var cell = 0;
      for (; cell < firstDay; cell++) html += '<td class="is-other"></td>';
      for (var day = 1; day <= daysIn; day++) {
        var iso = y + "-" + String(m + 1).padStart(2, "0") + "-" + String(day).padStart(2, "0");
        var evs = window.CH_EVENTS.filter(function (e) { return e.date === iso; });
        html += "<td>" + day + evs.map(function (e) {
          return '<a class="ev" href="' + e.url + '" title="' + esc(e.title) + '">' + esc(e.type) + "</a>";
        }).join("") + "</td>";
        cell++;
        if (cell % 7 === 0 && day < daysIn) html += "</tr><tr>";
      }
      while (cell % 7 !== 0) { html += '<td class="is-other"></td>'; cell++; }
      html += "</tr></tbody></table>";
      calRoot.innerHTML = html;
      $$("[data-cal]", calRoot).forEach(function (b) {
        b.addEventListener("click", function () {
          current.setMonth(current.getMonth() + parseInt(b.getAttribute("data-cal"), 10));
          renderCal();
        });
      });
    }
    // Arrancar en el mes del primer evento futuro si existe
    var t2 = new Date().toISOString().slice(0, 10);
    var nx = window.CH_EVENTS.filter(function (e) { return e.date >= t2; }).sort()[0];
    if (nx) { current = new Date(nx.date + "T12:00:00"); current.setDate(1); }
    renderCal();
  }

  /* ---------- Año automático ---------- */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- Red del atlas (hero, canvas) ---------- */
  var atlasCanvas = $("#hero-atlas");
  if (atlasCanvas && !reduceMotion && window.matchMedia("(min-width: 768px)").matches) {
    var ctx = atlasCanvas.getContext("2d");
    var nodes = [], mouse = { x: -9999, y: -9999 };
    var W, H, raf;
    function resize() {
      var r = atlasCanvas.parentElement.getBoundingClientRect();
      W = atlasCanvas.width = r.width * devicePixelRatio;
      H = atlasCanvas.height = r.height * devicePixelRatio;
      atlasCanvas.style.width = r.width + "px";
      atlasCanvas.style.height = r.height + "px";
      nodes = [];
      var count = Math.min(46, Math.floor(r.width / 34));
      for (var i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * W, y: Math.random() * H,
          vx: (Math.random() - 0.5) * 0.12 * devicePixelRatio,
          vy: (Math.random() - 0.5) * 0.12 * devicePixelRatio,
          r: (Math.random() * 1.6 + 1) * devicePixelRatio
        });
      }
    }
    function tick() {
      ctx.clearRect(0, 0, W, H);
      var linkDist = 150 * devicePixelRatio;
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > W) n.vx *= -1;
        if (n.y < 0 || n.y > H) n.vy *= -1;
        // reacción sutil al puntero
        var dxm = n.x - mouse.x, dym = n.y - mouse.y;
        var dm = Math.hypot(dxm, dym);
        if (dm < 90 * devicePixelRatio && dm > 0.01) {
          n.x += (dxm / dm) * 0.35;
          n.y += (dym / dm) * 0.35;
        }
      }
      for (i = 0; i < nodes.length; i++) {
        for (var j = i + 1; j < nodes.length; j++) {
          var dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y;
          var dist = Math.hypot(dx, dy);
          if (dist < linkDist) {
            var near = Math.hypot((nodes[i].x + nodes[j].x) / 2 - mouse.x, (nodes[i].y + nodes[j].y) / 2 - mouse.y) < 140 * devicePixelRatio;
            ctx.strokeStyle = near ? "rgba(166,32,53," + (0.5 - dist / linkDist * 0.4) + ")" : "rgba(16,61,80," + (0.28 - dist / linkDist * 0.22) + ")";
            ctx.lineWidth = devicePixelRatio * (near ? 1 : 0.6);
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }
      for (i = 0; i < nodes.length; i++) {
        ctx.fillStyle = "rgba(17,17,17,.5)";
        ctx.beginPath();
        ctx.arc(nodes[i].x, nodes[i].y, nodes[i].r, 0, Math.PI * 2);
        ctx.fill();
      }
      raf = requestAnimationFrame(tick);
    }
    var hero = atlasCanvas.closest(".hero");
    hero.addEventListener("pointermove", function (e) {
      var r = atlasCanvas.getBoundingClientRect();
      mouse.x = (e.clientX - r.left) * devicePixelRatio;
      mouse.y = (e.clientY - r.top) * devicePixelRatio;
    });
    hero.addEventListener("pointerleave", function () { mouse.x = -9999; mouse.y = -9999; });
    resize();
    window.addEventListener("resize", resize);
    // pausar fuera de pantalla
    new IntersectionObserver(function (en) {
      if (en[0].isIntersecting) { if (!raf) tick(); }
      else { cancelAnimationFrame(raf); raf = null; }
    }).observe(atlasCanvas);
  }
})();
