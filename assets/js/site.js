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

  // «Te ayudamos con tus dudas»: filtros combinados de público y tema
  var dd = document.querySelector('[data-dd-filters]');
  if (dd) {
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-dd-list] .dd-item'));
    var audBtns = dd.querySelectorAll('.seg button');
    var topicBtns = dd.querySelectorAll('.chips button');
    var count = document.querySelector('[data-dd-count]');
    var none = document.querySelector('[data-dd-none]');
    var state = { aud: 'todo', topic: '' };
    var audOk = function (it) {
      var a = it.getAttribute('data-aud');
      return state.aud === 'todo' || a === state.aud || a === 'ambos';
    };
    var apply = function () {
      // Temas disponibles para el público elegido
      topicBtns.forEach(function (b) {
        var id = b.getAttribute('data-topic');
        if (!id) return;
        b.hidden = !items.some(function (it) { return audOk(it) && it.getAttribute('data-topic') === id; });
      });
      var active = dd.querySelector('.chips button[data-topic="' + state.topic + '"]');
      if (!active || active.hidden) state.topic = '';
      topicBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-topic') === state.topic ? 'true' : 'false'); });
      audBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-aud') === state.aud ? 'true' : 'false'); });
      var n = 0;
      items.forEach(function (it) {
        var show = audOk(it) && (!state.topic || it.getAttribute('data-topic') === state.topic);
        it.hidden = !show;
        if (show) n++;
      });
      if (count) count.textContent = n === 1 ? '1 pregunta' : n + ' preguntas';
      if (none) none.hidden = n > 0;
    };
    audBtns.forEach(function (b) { b.addEventListener('click', function () { state.aud = b.getAttribute('data-aud'); apply(); }); });
    topicBtns.forEach(function (b) { b.addEventListener('click', function () { state.topic = b.getAttribute('data-topic'); apply(); }); });
    apply();
  }

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
