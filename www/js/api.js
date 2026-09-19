/* Small API + auth helper shared by public pages and the admin page. Needs js/config.js (generated at deploy). */
window.VS = (function () {
  var C = window.VS_CONFIG || {};
  var TOKEN_KEY = 'vs_id_token';
  function token() { try { return sessionStorage.getItem(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY); } catch (e) { return null; } }
  function setToken(t, remember) { try { (remember ? localStorage : sessionStorage).setItem(TOKEN_KEY, t); } catch (e) {} }
  function clearToken() { try { sessionStorage.removeItem(TOKEN_KEY); localStorage.removeItem(TOKEN_KEY); } catch (e) {} }
  function claims() {
    var t = token(); if (!t) return null;
    try { var c = JSON.parse(atob(t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))); if (c.exp * 1000 < Date.now()) { clearToken(); return null; } return c; } catch (e) { return null; }
  }
  function isAdmin() { var c = claims(); var g = c && c['cognito:groups']; return !!(g && (Array.isArray(g) ? g : [g]).indexOf('admin') >= 0); }
  function api(method, path, data) {
    var h = { 'Content-Type': 'application/json' };
    var t = token(); if (t) h['Authorization'] = 'Bearer ' + t;
    return fetch(C.apiUrl + path, { method: method, headers: h, body: data ? JSON.stringify(data) : undefined })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || r.status); return j; }); });
  }
  function lang() { return document.documentElement.getAttribute('data-lang') || 'en'; }
  function mediaUrl(key) { return '/' + key; }
  function fmtDate(iso, opts) {
    try { return new Date(iso + 'T00:00:00').toLocaleDateString(lang() === 'te' ? 'te-IN' : 'en-IN', opts || { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }); } catch (e) { return iso; }
  }
  return { config: C, token: token, setToken: setToken, clearToken: clearToken, claims: claims, isAdmin: isAdmin, api: api, lang: lang, mediaUrl: mediaUrl, fmtDate: fmtDate };
})();
