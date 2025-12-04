// Dropdown navigation for "Boutique"
// Handles hover, click, keyboard (Escape) and outside clicks to open/close the menu.
(function () {
  // Grab all dropdown containers
  const dropdowns = document.querySelectorAll("[data-dropdown]");

  dropdowns.forEach((dropdown) => {
    const trigger = dropdown.querySelector("[data-dropdown-trigger]");
    const menu = dropdown.querySelector("[data-dropdown-menu]");
    if (!trigger || !menu) return;

    let closeTimer = null; // used to add a tiny delay so moving the mouse to the menu doesn't close it

    // Helper to open the menu
    const open = () => dropdown.classList.add("is-open");
    // Helper to close the menu
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

    // Toggle on click (for touch / keyboard users)
    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      dropdown.classList.toggle("is-open");
    });

    // Open on hover, close when leaving
    dropdown.addEventListener("mouseenter", () => {
      cancelClose();
      open();
    });
    dropdown.addEventListener("mouseleave", scheduleClose);

    // Keep menu open while the mouse is over it
    menu.addEventListener("mouseenter", cancelClose);
    menu.addEventListener("mouseleave", scheduleClose);

    // Close when focusing away from the menu
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

    // Close on Escape key
    dropdown.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        close();
        trigger.focus();
      }
    });
  });

  // Close any open dropdown when clicking outside
  document.addEventListener("click", (event) => {
    dropdowns.forEach((dropdown) => {
      if (!dropdown.contains(event.target)) {
        dropdown.classList.remove("is-open");
      }
    });
  });
})();
