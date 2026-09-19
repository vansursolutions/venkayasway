/* Runs before paint so the chosen language shows without a flash */
(function(){var l='en';try{l=localStorage.getItem('lang')||'en'}catch(e){}document.documentElement.setAttribute('data-lang',l);document.documentElement.lang=l;})();
