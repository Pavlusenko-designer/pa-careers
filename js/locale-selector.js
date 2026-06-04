(function () {
  "use strict";

  var select = document.getElementById("pa-locale-select");
  if (!select) return;

  function combo() {
    return document.querySelector(".pa-locale-wrap .goog-te-combo");
  }

  function applyLocale(code) {
    var el = combo();
    if (!el) return false;
    el.value = code;
    el.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
  }

  select.addEventListener("change", function () {
    if (applyLocale(select.value)) return;

    var tries = 0;
    var timer = window.setInterval(function () {
      tries += 1;
      if (applyLocale(select.value) || tries > 50) {
        window.clearInterval(timer);
      }
    }, 100);
  });

  function syncFromCombo() {
    var el = combo();
    if (el && el.value !== select.value) {
      select.value = el.value;
    }
  }

  var wrap = document.querySelector(".pa-locale-wrap");
  if (!wrap) return;

  var observer = new MutationObserver(function () {
    syncFromCombo();
  });
  observer.observe(wrap, { childList: true, subtree: true });
})();
