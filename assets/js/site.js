(function () {
  'use strict';

  // mobile menu
  var burger = document.getElementById('burger'), nav = document.getElementById('nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // product gallery
  var thumbs = document.getElementById('thumbs'), hero = document.getElementById('hero');
  if (thumbs && hero) {
    thumbs.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      hero.src = b.dataset.src;
      thumbs.querySelectorAll('button').forEach(function (x) {
        x.setAttribute('aria-selected', String(x === b));
      });
    });
  }

  // components listing: industry filter + A-Z / grid toggle
  var rows = document.getElementById('rows');
  var sel = document.getElementById('indsel');
  var az = document.getElementById('azview');
  var vaz = document.getElementById('vaz'), vgr = document.getElementById('vgr');
  var pag = document.getElementById('pag');

  if (sel && rows) {
    sel.addEventListener('change', function () {
      var v = sel.value;
      // jump straight to that category page
      if (v) window.location.href = 'category/' + v + '.html';
    });
  }

  function setView(mode) {
    var azOn = mode === 'az';
    if (az) az.hidden = !azOn;
    if (rows) rows.hidden = azOn;
    if (pag) pag.hidden = azOn;
    if (vaz) vaz.setAttribute('aria-pressed', String(azOn));
    if (vgr) vgr.setAttribute('aria-pressed', String(!azOn));
    try { localStorage.setItem('jj-view', mode); } catch (e) {}
  }
  if (vaz && vgr) {
    vaz.addEventListener('click', function () { setView('az'); });
    vgr.addEventListener('click', function () { setView('grid'); });
    var saved = null;
    try { saved = localStorage.getItem('jj-view'); } catch (e) {}
    if (saved === 'az') setView('az');
  }

  // category page sorting
  var grid = document.getElementById('grid'), sort = document.getElementById('sort');
  if (grid && sort) {
    var cards = Array.prototype.slice.call(grid.children);
    cards.forEach(function (c, i) {
      var n = c.querySelector('.pc__n');
      c._n = n ? n.textContent.trim().toLowerCase() : '';
      c._p = parseFloat(c.dataset.p) || 0;
      c._i = i;
    });
    sort.addEventListener('change', function () {
      var v = sort.value, s = cards.slice();
      if (v === 'az') s.sort(function (a, b) { return a._n.localeCompare(b._n); });
      else if (v === 'lo') s.sort(function (a, b) { return a._p - b._p; });
      else if (v === 'hi') s.sort(function (a, b) { return b._p - a._p; });
      else s.sort(function (a, b) { return a._i - b._i; });
      var f = document.createDocumentFragment();
      s.forEach(function (c) { f.appendChild(c); });
      grid.appendChild(f);
    });
  }
})();
