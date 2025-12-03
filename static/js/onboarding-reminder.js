// Affiche un rappel si l'onboarding n'est pas complété.
(function () {
    const overlay = document.getElementById("onboarding-reminder");
    if (!overlay) return;

    const shouldShow = document.body.dataset.onboardingIncomplete === "1";
    const isOnOnboardingPage = window.location.pathname.includes("/onboarding");

    if (!shouldShow || isOnOnboardingPage) return;

    const showOverlay = () => {
        overlay.classList.add("is-visible");
        overlay.setAttribute("aria-hidden", "false");
    };

    const hideOverlay = () => {
        overlay.classList.remove("is-visible");
        overlay.setAttribute("aria-hidden", "true");
    };

    overlay.querySelectorAll("[data-onboarding-close]").forEach((btn) => {
        btn.addEventListener("click", hideOverlay);
    });

    const goBtn = overlay.querySelector("[data-onboarding-go]");
    if (goBtn) {
        goBtn.addEventListener("click", (event) => {
            event.preventDefault();
            hideOverlay();
            window.location.href = goBtn.getAttribute("href");
        });
    }

    showOverlay();
})();
