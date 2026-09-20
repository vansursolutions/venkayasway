/* Shared behaviour: header/footer, language toggle, PWA install, service worker */
(function () {
  var NAV = [
    { href: 'index.html',     en: 'Home',             te: 'హోమ్' },
    { href: 'life.html',      en: 'Life Story',       te: 'జీవిత చరిత్ర' },
    { href: 'teachings.html', en: 'Teachings',        te: 'బోధనలు' },
    { href: 'temple.html',    en: 'Temple',           te: 'ఆలయం' },
    { href: 'events.html',    en: 'Events',           te: 'కార్యక్రమాలు' },
    { href: 'annadanam.html', en: 'Annadanam',        te: 'అన్నదానం' },
    { href: 'gallery.html',   en: 'Gallery',          te: 'గ్యాలరీ' },
    { href: 'donate.html',    en: 'Contact',          te: 'సంప్రదింపు' }
  ];

  function getLang() {
    try { return localStorage.getItem('lang') || 'en'; } catch (e) { return 'en'; }
  }
  function setLang(lang) {
    try { localStorage.setItem('lang', lang); } catch (e) {}
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.lang = lang;
    var t = document.querySelector('.lang-toggle');
    if (t) t.textContent = lang === 'en' ? 'తెలుగు' : 'English';
  }

  function bi(en, te) {
    return '<span class="en">' + en + '</span><span class="te">' + te + '</span>';
  }

  function currentPage() {
    var p = location.pathname.split('/').pop();
    return p === '' ? 'index.html' : p;
  }

  function renderHeader() {
    var links = NAV.map(function (n) {
      var cur = n.href === currentPage() ? ' aria-current="page"' : '';
      return '<a href="/' + n.href + '"' + cur + '>' + bi(n.en, n.te) + '</a>';
    }).join('');
    return (
      '<header class="site-header"><div class="container bar">' +
        '<a class="brand" href="/">' +
          '<img src="/icons/icon-192.png" alt="" width="42" height="42">' +
          '<span><span class="name">' + bi('Sri Venkaiah Swamy Temple', 'శ్రీ వెంకయ్య స్వామి ఆలయం') + '</span><br>' +
          '<span class="sub">' + bi('SULLURUPETA, ANDHRA PRADESH', 'సూళ్లూరుపేట, ఆంధ్రప్రదేశ్') + '</span></span>' +
        '</a>' +
        '<nav class="nav" id="nav">' + links + '</nav>' +
        // the language switch lives in the bar itself, not inside the menu: on a phone it is always one tap away, next to ☰
        '<button class="lang-toggle" type="button"></button>' +
        '<button class="menu-btn" aria-label="Menu" aria-expanded="false">&#9776;</button>' +
      '</div></header>'
    );
  }

  function renderFooter() {
    var year = new Date().getFullYear();
    return (
      '<footer class="site-footer"><div class="container">' +
        '<div class="cols">' +
          '<div><h3>' + bi('Sri Venkaiah Swamy Temple', 'శ్రీ వెంకయ్య స్వామి ఆలయం') + '</h3>' +
            '<p>' + bi('Bhagavan Sri Venkaiah Swamy Dhyana Mandiram,<br>Kollamitta, Sullurupeta,<br>Tirupati District, Andhra Pradesh 524121, India', 'భగవాన్ శ్రీ వెంకయ్య స్వామి ధ్యాన మందిరం,<br>కొల్లమిట్ట, సూళ్లూరుపేట,<br>తిరుపతి జిల్లా, ఆంధ్రప్రదేశ్ 524121') + '</p></div>' +
          '<div><h3>' + bi('Quick Links', 'త్వరిత లింకులు') + '</h3>' +
            '<p><a href="temple.html">' + bi('Darshan timings', 'దర్శన సమయాలు') + '</a><br>' +
            '<a href="/temple.html#reach">' + bi('How to reach', 'ఎలా చేరుకోవాలి') + '</a><br>' +
            '<a href="/annadanam.html">' + bi('Sponsor annadanam', 'అన్నదాన స్పాన్సర్') + '</a><br>' +
            '<a href="/donate.html">' + bi('Donate', 'విరాళం') + '</a><br>' +
            '<a href="admin/" style="opacity:.7">' + bi('Volunteer / admin login', 'వాలంటీర్ / అడ్మిన్ లాగిన్') + '</a></p></div>' +
          '<div><h3>' + bi('Follow us', 'మమ్మల్ని అనుసరించండి') + '</h3>' +
            '<p>' + '<a class="yt-link" href="https://www.youtube.com/@bhagavansrivenkaiahswamyma2343" target="_blank" rel="noopener" title="YouTube channel"><svg width="22" height="16" viewBox="0 0 24 17" aria-hidden="true"><path fill="#ff0000" d="M23.5 2.7a3 3 0 0 0-2.1-2.1C19.5 0 12 0 12 0S4.5 0 2.6.6A3 3 0 0 0 .5 2.7 31 31 0 0 0 0 8.5a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-5.8 31 31 0 0 0-.5-5.8z"/><path fill="#fff" d="M9.6 12.1V4.9l6.2 3.6z"/></svg> YouTube</a>' + '<br><span class="muted" style="color:#c9b9a5">Bhagavan Sri Venkaiah Swamy Mandiram Sullurupeta</span></p></div>' +
          '<div><h3>' + bi('Contact', 'సంప్రదించండి') + '</h3>' +
            '<p><a href="mailto:info@srivenkaiahswamy.com">info@srivenkaiahswamy.com</a><br>' +
            '<a href="tel:+919390017190">+91 93900 17190</a></p></div>' +
        '</div>' +
        '<div class="copy">&copy; ' + year + ' srivenkaiahswamy.com &middot; <a href="/privacy.html">' + bi('Privacy', 'గోప్యత') + '</a> &middot; ' + bi('Om Narayana Adi Narayana', 'ఓం నారాయణ ఆది నారాయణ') + '</div>' +
      '</div></footer>'
    );
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.body.insertAdjacentHTML('afterbegin', renderHeader());
    document.body.insertAdjacentHTML('beforeend', renderFooter());
    setLang(getLang());

    document.querySelector('.lang-toggle').addEventListener('click', function () {
      setLang(getLang() === 'en' ? 'te' : 'en');
    });
    var btn = document.querySelector('.menu-btn');
    var nav = document.getElementById('nav');
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    // PWA install prompt (Android / Chrome)
    var deferred = null;
    window.addEventListener('beforeinstallprompt', function (e) {
      e.preventDefault();
      deferred = e;
      var b = document.createElement('div');
      b.id = 'installBanner';
      b.innerHTML = '<span>' + bi('Install this site as an app on your phone', 'ఈ సైట్‌ను మీ ఫోన్‌లో యాప్‌గా ఇన్‌స్టాల్ చేయండి') + '</span>' +
        '<span><button class="btn" id="installBtn">' + bi('Install', 'ఇన్‌స్టాల్') + '</button> ' +
        '<button class="btn outline" id="installClose">&times;</button></span>';
      document.body.appendChild(b);
      document.getElementById('installBtn').onclick = function () { deferred.prompt(); b.remove(); };
      document.getElementById('installClose').onclick = function () { b.remove(); };
    });
  });

  // Lightbox: tap a gallery photo to enlarge; swipe (or arrows/keys) to move between photos with a smooth slide
  (function () {
    var items = [], idx = 0, box = null, track = null, slides = [], W = 0, animating = false;
    var EASE = 'cubic-bezier(0.22, 0.61, 0.36, 1)', DUR = 420;
    function collect() {
      items = Array.prototype.map.call(document.querySelectorAll('.gallery figure img'), function (img) {
        var cap = img.closest('figure').querySelector('figcaption');
        var a = img.closest('a'), href = a && a.getAttribute('href') || '';
        return { src: /\.(jpe?g|png|webp)(\?.*)?$/i.test(href) ? href : img.getAttribute('src'), cap: cap ? cap.innerHTML : '' };
      });
    }
    function at(i) { return items[(i + items.length) % items.length]; }
    function fill() {
      // three slides: previous, current, next
      [ -1, 0, 1 ].forEach(function (d, k) { var it = at(idx + d); slides[k].src = it.src; slides[k].alt = ''; });
      box.querySelector('.cap').innerHTML = at(idx).cap;
      box.querySelector('.count').textContent = items.length > 1 ? (((idx % items.length) + items.length) % items.length + 1) + ' / ' + items.length : '';
      setX(0, false);
    }
    function setX(x, animate) {
      track.style.transition = animate ? 'transform ' + DUR + 'ms ' + EASE : 'none';
      track.style.transform = 'translate3d(' + (x - W) + 'px,0,0)';
    }
    function go(dir) {
      if (animating || items.length < 2) { if (items.length < 2) setX(0, true); return; }
      animating = true; setX(-dir * W, true);
      setTimeout(function () { idx += dir; fill(); animating = false; }, DUR);
    }
    function settle() { setX(0, true); }
    function open(i) {
      if (!box) {
        box = document.createElement('div'); box.id = 'lightbox';
        box.innerHTML = '<button class="close" aria-label="Close">&times;</button><button class="prev" aria-label="Previous">&#8249;</button>' +
          '<div class="lb-stage"><div class="lb-track"><img><img><img></div></div><div class="cap"></div><div class="count"></div>' +
          '<button class="next" aria-label="Next">&#8250;</button>';
        track = box.querySelector('.lb-track'); slides = Array.prototype.slice.call(track.children);
        box.addEventListener('click', function (e) { if (e.target === box || e.target.classList.contains('close') || e.target.classList.contains('lb-stage')) close(); });
        box.querySelector('.prev').onclick = function (e) { e.stopPropagation(); go(-1); };
        box.querySelector('.next').onclick = function (e) { e.stopPropagation(); go(1); };
        document.addEventListener('keydown', function (e) { if (!box || !box.parentNode) return; if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') go(-1); if (e.key === 'ArrowRight') go(1); });
        window.addEventListener('resize', function () { if (box && box.parentNode) { W = box.querySelector('.lb-stage').clientWidth; setX(0, false); } });
        // touch: follow the finger, then ease into place
        var sx = 0, sy = 0, dx = 0, t0 = 0, dragging = false, horiz = null;
        var stage = box.querySelector('.lb-stage');
        stage.addEventListener('touchstart', function (e) {
          if (animating || e.touches.length !== 1) return;
          sx = e.touches[0].clientX; sy = e.touches[0].clientY; dx = 0; t0 = Date.now(); dragging = true; horiz = null; setX(0, false);
        }, { passive: true });
        stage.addEventListener('touchmove', function (e) {
          if (!dragging) return;
          var mx = e.touches[0].clientX - sx, my = e.touches[0].clientY - sy;
          if (horiz === null && (Math.abs(mx) > 6 || Math.abs(my) > 6)) horiz = Math.abs(mx) > Math.abs(my);
          if (!horiz) return;
          e.preventDefault();
          dx = mx;
          if (items.length < 2) dx = mx * 0.3;                      // rubber-band when there is nothing to slide to
          setX(dx, false);
        }, { passive: false });
        stage.addEventListener('touchend', function () {
          if (!dragging) return; dragging = false;
          var dt = Math.max(1, Date.now() - t0), v = Math.abs(dx) / dt;   // px per ms
          if (horiz && items.length > 1 && (Math.abs(dx) > W * 0.22 || v > 0.45)) go(dx < 0 ? 1 : -1); else settle();
          if (!horiz && Math.abs(dx) < 6 && Date.now() - t0 < 250) { /* tap on image: leave open */ }
        });
        stage.addEventListener('touchcancel', function () { dragging = false; settle(); });
      }
      document.body.appendChild(box); document.body.style.overflow = 'hidden';
      W = box.querySelector('.lb-stage').clientWidth; idx = i; fill();
    }
    function close() { if (box && box.parentNode) box.parentNode.removeChild(box); document.body.style.overflow = ''; }
    document.addEventListener('click', function (e) {
      var img = e.target.closest && e.target.closest('.gallery figure img');
      if (!img) return;
      e.preventDefault(); collect();
      var all = Array.prototype.slice.call(document.querySelectorAll('.gallery figure img'));
      open(all.indexOf(img));
    });
  })();

  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () {});
    });
  }
})();
