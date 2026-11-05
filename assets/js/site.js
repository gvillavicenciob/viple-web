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

  // Filtro por categoría (página de Novedades)
  var filters = document.querySelectorAll('.filters button');
  filters.forEach(function (b) {
    b.addEventListener('click', function () {
      var cat = b.getAttribute('data-cat');
      filters.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      document.querySelectorAll('.post-card[data-cat]').forEach(function (c) {
        c.hidden =!(cat === 'todas' || c.getAttribute('data-cat') === cat);
      });
    });
  });
})();
