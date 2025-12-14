// Gère le menu déroulant boutique (hover + clic + clavier)
(function () {
  const dropdowns = document.querySelectorAll("[data-dropdown]");

  dropdowns.forEach((dropdown) => {
    const trigger = dropdown.querySelector("[data-dropdown-trigger]");
    const menu = dropdown.querySelector("[data-dropdown-menu]");
    if (!trigger || !menu) return;

    let closeTimer = null; // évite de fermer trop vite quand on va vers le menu

    const open = () => dropdown.classList.add("is-open");
    const close = () => dropdown.classList.remove("is-open");
    const scheduleClose = () => {
      closeTimer = setTimeout(close, 120);
    };
    const cancelClose = () => {
      if (closeTimer) {
        clearTimeout(closeTimer);
        closeTimer = null;
      }
    };

    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      dropdown.classList.toggle("is-open");
    });

    dropdown.addEventListener("mouseenter", () => {
      cancelClose();
      open();
    });
    dropdown.addEventListener("mouseleave", scheduleClose);

    menu.addEventListener("mouseenter", cancelClose);
    menu.addEventListener("mouseleave", scheduleClose);

    trigger.addEventListener("blur", (event) => {
      if (!dropdown.contains(event.relatedTarget)) {
        close();
      }
    });
    menu.addEventListener("blur", (event) => {
      if (!dropdown.contains(event.relatedTarget)) {
        close();
      }
    });

    dropdown.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        close();
        trigger.focus();
      }
    });
  });

  document.addEventListener("click", (event) => {
    dropdowns.forEach((dropdown) => {
      if (!dropdown.contains(event.target)) {
        dropdown.classList.remove("is-open");
      }
    });
  });
})();
