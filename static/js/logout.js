document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".logout-form");
  if (!form) return;

  const button = form.querySelector(".logout-btn");
  const overlay = document.querySelector(".logout-overlay");
  const label = button?.querySelector(".logout-label");
  if (!button) return;

  let isSubmitting = false;

  form.addEventListener("submit", (event) => {
    if (isSubmitting) return;
    isSubmitting = true;
    event.preventDefault();

    button.classList.add("is-loading");
    button.setAttribute("disabled", "disabled");
    if (label) label.textContent = "Déconnexion...";
    if (overlay) overlay.classList.add("is-visible");

    // Laisse le temps d'afficher l'overlay avant la redirection
    requestAnimationFrame(() => {
      setTimeout(() => form.submit(), 800);
    });
  });
});
