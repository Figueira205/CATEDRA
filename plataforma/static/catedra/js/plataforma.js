/* Configuración de main.js en la plataforma. Se carga antes que main.js
   (ambos con defer, en este orden) y evita scripts en línea (CSP estricta). */
(function () {
  "use strict";
  var yo = document.currentScript;
  var menu = document.getElementById("ch-menu");
  window.CH_NAV = menu ? JSON.parse(menu.textContent) : [];
  window.CH_SEARCH_URL = yo.getAttribute("data-buscar");
  window.CH_INDEX_URL = yo.getAttribute("data-indice");
  window.CH_SUGGESTIONS = window.CH_NAV.map(function (s) { return { t: s.label, url: s.url, k: "Sección" }; });
})();
