(function () {
  // Scroll reveal, once
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  // Language menu: close on outside click / Esc, remember choice
  var lang = document.querySelector('.lang');
  if (lang) {
    document.addEventListener('click', function (e) { if (!lang.contains(e.target)) lang.removeAttribute('open'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') lang.removeAttribute('open'); });
  }
  document.querySelectorAll('[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () { try { localStorage.setItem('fom-lang', a.getAttribute('data-lang')); } catch (_) {} });
  });

  // First visit on the root page: jump to the browser language if we have it
  var root = document.documentElement;
  if (root.getAttribute('data-root') === '1') {
    try {
      var saved = localStorage.getItem('fom-lang');
      var supported = (root.getAttribute('data-langs') || '').split(',');
      var pick = saved || ((navigator.language || '').slice(0, 2).toLowerCase());
      if (pick && pick !== 'en' && supported.indexOf(pick) !== -1) {
        var page = location.pathname.split('/').pop() || 'index.html';
        if (!saved) localStorage.setItem('fom-lang', pick);
        location.replace(pick + '/' + page + location.hash);
      }
    } catch (_) {}
  }

  // Count-up numbers (.count): keeps prefix/suffix and the thousands separator of the original text
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function countUp(el) {
    var m = el.textContent.match(/^([^\d]*)([\d.,\u00a0 ]+)(.*)$/);
    if (!m) return;
    var raw = m[2], sep = (raw.match(/[.,\u00a0 ]/) || [''])[0];
    var target = parseInt(raw.replace(/[^\d]/g, ''), 10);
    if (!target || reduce) return;
    var fmt = function (n) { var str = String(n); return sep ? str.replace(/\B(?=(\d{3})+(?!\d))/g, sep) : str; };
    var dur = target > 100 ? 1800 : 1100, start = null;
    el.textContent = m[1] + '0' + m[3];
    function frame(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1), eased = 1 - Math.pow(1 - p, 4);
      el.textContent = m[1] + fmt(Math.round(target * eased)) + m[3];
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  var counts = document.querySelectorAll('.count');
  if ('IntersectionObserver' in window && !reduce) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { countUp(e.target); cio.unobserve(e.target); } });
    }, { threshold: 0.4 });
    counts.forEach(function (el) { cio.observe(el); });
  }

  // Mobile menu
  var burger = document.querySelector('.burger'), menu = document.querySelector('.mobile-menu');
  if (burger && menu) {
    burger.addEventListener('click', function () { menu.classList.toggle('open'); });
    menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { menu.classList.remove('open'); }); });
  }

  // FAQ: only one open at a time
  var items = document.querySelectorAll('.faq-item');
  items.forEach(function (d) {
    d.addEventListener('toggle', function () { if (d.open) items.forEach(function (o) { if (o !== d) o.removeAttribute('open'); }); });
  });
})();
