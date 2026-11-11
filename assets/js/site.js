// Menú móvil
(function () {
  var btn = document.querySelector('.menu-toggle');
  if (btn) {
    btn.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Año en el pie de página
  var y = document.getElementById('y');
  if (y) y.textContent = new Date().getFullYear();

  // Animación suave al aparecer
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('in'); });
  }

  // Filtro por categoría (Ideas y análisis, Novedades)
  var filters = document.querySelectorAll('.filters button');
  filters.forEach(function (b) {
    b.addEventListener('click', function () {
      var cat = b.getAttribute('data-cat');
      filters.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      document.querySelectorAll('.post-card[data-cat], [data-filter-item]').forEach(function (c) {
        c.hidden = !(cat === 'todas' || c.getAttribute('data-cat') === cat);
      });
    });
  });

  // Desplegable «Cómo te podemos ayudar»: botón para abrir/cerrar (teclado y pantallas táctiles) y tecla Esc
  document.querySelectorAll('.has-sub').forEach(function (li) {
    var t = li.querySelector('.sub-toggle');
    if (!t) return;
    var set = function (open) {
      li.classList.toggle('open', open);
      li.classList.toggle('closed', !open);
      t.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    t.addEventListener('click', function () { set(!li.classList.contains('open')); });
    li.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { set(false); li.querySelector('a').focus(); }
    });
    li.addEventListener('mouseleave', function () { li.classList.remove('closed'); });
    li.addEventListener('focusout', function (e) {
      if (!li.contains(e.relatedTarget)) { li.classList.remove('closed'); if (li.classList.contains('open')) set(false); li.classList.remove('closed'); }
    });
    document.addEventListener('click', function (e) { if (!li.contains(e.target) && li.classList.contains('open')) set(false); });
  });

  // Visor de diapositivas (Presentaciones especiales)
  document.querySelectorAll('[data-slides]').forEach(function (box) {
    var track = box.querySelector('.slides-track');
    var prev = box.querySelector('[data-prev]');
    var next = box.querySelector('[data-next]');
    var count = box.querySelector('[data-count]');
    var total = track.children.length;
    var current = function () { return track.clientWidth ? Math.round(track.scrollLeft / track.clientWidth) : 0; };
    var go = function (i) { track.scrollLeft = Math.max(0, Math.min(total - 1, i)) * track.clientWidth; update(); };
    var update = function () {
      var i = current();
      if (count) count.textContent = (i + 1) + ' / ' + total;
      if (prev) prev.disabled = i <= 0;
      if (next) next.disabled = i >= total - 1;
    };
    if (prev) prev.addEventListener('click', function () { go(current() - 1); });
    if (next) next.addEventListener('click', function () { go(current() + 1); });
    track.addEventListener('scroll', function () { window.requestAnimationFrame(update); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(current() + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(current() - 1); }
    });
    // Sin menú contextual sobre las diapositivas (no impide una captura de pantalla, pero evita «Guardar imagen»)
    box.addEventListener('contextmenu', function (e) { e.preventDefault(); });
    update();
  });

  // Botón «Copiar enlace» de los artículos
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var url = b.getAttribute('data-copy');
      var done = function () { b.textContent = 'Enlace copiado'; setTimeout(function () { b.textContent = 'Copiar enlace'; }, 2000); };
      if (navigator.clipboard) { navigator.clipboard.writeText(url).then(done, function () { window.prompt('Copia este enlace:', url); }); }
      else { window.prompt('Copia este enlace:', url); }
    });
  });
})();
