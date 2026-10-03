/* Carga el vídeo de una clase por fetch, solo si el usuario tiene acceso.
   El enlace de YouTube/Vimeo nunca llega en el HTML servido (evita que
   "Ver código fuente" lo revele a quien no ha pagado). */
(function () {
  "use strict";
  var yo = document.currentScript;
  var url = yo.getAttribute("data-url");
  var caja = document.querySelector("[data-clase-video]");
  if (!caja || !url) return;

  fetch(url, { credentials: "same-origin", headers: { "X-Requested-With": "XMLHttpRequest" } })
    .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
    .then(function (data) {
      var titulo = caja.getAttribute("data-titulo") || "";
      var iframe = document.createElement("iframe");
      iframe.src = data.embed_url;
      iframe.title = titulo;
      iframe.loading = "lazy";
      iframe.allow = "fullscreen; picture-in-picture";
      iframe.allowFullscreen = true;
      caja.textContent = "";
      caja.appendChild(iframe);
    })
    .catch(function () {
      caja.innerHTML = '<p class="video-embed__error">No se ha podido cargar el vídeo. Recarga la página o contacta con nosotros si el problema continúa.</p>';
    });
})();
