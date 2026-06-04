(function () {
  var dropdowns = document.querySelectorAll("[data-nav-dropdown]");
  if (!dropdowns.length) return;

  var desktopQuery = window.matchMedia("(min-width: 992px)");
  var hoverTimers = new WeakMap();

  function getParts(dropdown) {
    return {
      toggle: dropdown.querySelector(".pa-nav-dropdown__toggle"),
      menu: dropdown.querySelector(".pa-nav-dropdown__menu"),
      items: dropdown.querySelectorAll(".pa-nav-dropdown__item"),
    };
  }

  function setOpen(dropdown, open) {
    var parts = getParts(dropdown);
    if (!parts.menu || !parts.toggle) return;

    dropdown.classList.toggle("is-open", open);
    parts.toggle.setAttribute("aria-expanded", open ? "true" : "false");
    parts.menu.hidden = !open;
  }

  function closeAll(except) {
    dropdowns.forEach(function (dropdown) {
      if (dropdown !== except) setOpen(dropdown, false);
    });
  }

  dropdowns.forEach(function (dropdown) {
    var parts = getParts(dropdown);
    if (!parts.menu || !parts.toggle) return;

    setOpen(dropdown, false);

    parts.toggle.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      var open = !dropdown.classList.contains("is-open");
      closeAll(open ? dropdown : null);
      setOpen(dropdown, open);
    });

    if (parts.items.length) {
      parts.items.forEach(function (item, index) {
        item.addEventListener("keydown", function (event) {
          if (!dropdown.classList.contains("is-open")) return;

          if (event.key === "ArrowDown") {
            event.preventDefault();
            parts.items[Math.min(index + 1, parts.items.length - 1)].focus();
          } else if (event.key === "ArrowUp") {
            event.preventDefault();
            parts.items[Math.max(index - 1, 0)].focus();
          } else if (event.key === "Escape") {
            event.preventDefault();
            setOpen(dropdown, false);
            parts.toggle.focus();
          }
        });
      });
    }

    dropdown.addEventListener("mouseenter", function () {
      if (!desktopQuery.matches) return;
      clearTimeout(hoverTimers.get(dropdown));
      hoverTimers.set(
        dropdown,
        window.setTimeout(function () {
          closeAll(dropdown);
          setOpen(dropdown, true);
        }, 80)
      );
    });

    dropdown.addEventListener("mouseleave", function () {
      if (!desktopQuery.matches) return;
      clearTimeout(hoverTimers.get(dropdown));
      hoverTimers.set(
        dropdown,
        window.setTimeout(function () {
          setOpen(dropdown, false);
        }, 120)
      );
    });
  });

  document.addEventListener("click", function (event) {
    if (!event.target.closest("[data-nav-dropdown]")) {
      closeAll();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeAll();
  });

  desktopQuery.addEventListener("change", function () {
    closeAll();
  });
})();
