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
            '<p>' + bi('Sullurupeta, Tirupati District,<br>Andhra Pradesh, India', 'సూళ్లూరుపేట, తిరుపతి జిల్లా,<br>ఆంధ్రప్రదేశ్, భారతదేశం') + '</p></div>' +
          '<div><h3>' + bi('Quick Links', 'త్వరిత లింకులు') + '</h3>' +
            '<p><a href="temple.html">' + bi('Darshan timings', 'దర్శన సమయాలు') + '</a><br>' +
            '<a href="/temple.html#reach">' + bi('How to reach', 'ఎలా చేరుకోవాలి') + '</a><br>' +
            '<a href="/annadanam.html">' + bi('Sponsor annadanam', 'అన్నదాన స్పాన్సర్') + '</a><br>' +
            '<a href="/donate.html">' + bi('Donate', 'విరాళం') + '</a><br>' +
            '<a href="admin/" style="opacity:.7">' + bi('Volunteer / admin login', 'వాలంటీర్ / అడ్మిన్ లాగిన్') + '</a></p></div>' +
          '<div><h3>' + bi('Follow us', 'మమ్మల్ని అనుసరించండి') + '</h3>' +
            '<p>' + '<a class="yt-link" href="https://www.youtube.com/@bhagavansrivenkaiahswamyma2343" target="_blank" rel="noopener" title="YouTube channel"><svg width="22" height="16" viewBox="0 0 24 17" aria-hidden="true"><path fill="#ff0000" d="M23.5 2.7a3 3 0 0 0-2.1-2.1C19.5 0 12 0 12 0S4.5 0 2.6.6A3 3 0 0 0 .5 2.7 31 31 0 0 0 0 8.5a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-5.8 31 31 0 0 0-.5-5.8z"/><path fill="#fff" d="M9.6 12.1V4.9l6.2 3.6z"/></svg> YouTube</a>' + '<br><span class="muted" style="color:#c9b9a5">Bhagavan Sri Venkaiah Swamy Mandiram Sullurupeta</span></p></div>' +
          '<div><h3>' + bi('Contact', 'సంప్రదించండి') + '</h3>' +
            '<p><a href="mailto:info@venkayaswamy.com">info@venkayaswamy.com</a><br>' +
            '<a href="tel:+910000000000">+91 00000 00000</a></p></div>' +
        '</div>' +
        '<div class="copy">&copy; ' + year + ' venkayaswamy.com &middot; ' + bi('Om Narayana Adi Narayana', 'ఓం నారాయణ ఆది నారాయణ') + '</div>' +
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

  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () {});
    });
  }
})();
