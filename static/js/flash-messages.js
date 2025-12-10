document.addEventListener("DOMContentLoaded", () => {
  const stack = document.querySelector("[data-flash-stack]");
  if (!stack) return;

  const dismiss = (flash) => {
    if (flash.dataset.closing === "1") return;
    flash.dataset.closing = "1";
    flash.classList.add("is-hiding");
    setTimeout(() => flash.remove(), 220);
  };

  stack.querySelectorAll(".flash").forEach((flash, index) => {
    // Trigger a small entrance animation
    requestAnimationFrame(() => flash.classList.add("is-visible"));

    const closeBtn = flash.querySelector("[data-flash-close]");
    const timeout = 4200 + index * 120;
    const timer = setTimeout(() => dismiss(flash), timeout);

    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        clearTimeout(timer);
        dismiss(flash);
      });
    }
  });
});
