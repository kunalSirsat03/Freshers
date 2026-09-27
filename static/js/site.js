document.addEventListener("DOMContentLoaded", () => {
  const menuButton = document.querySelector(".menu-toggle");
  const navigation = document.querySelector(".site-nav");

  if (menuButton && navigation) {
    menuButton.addEventListener("click", () => {
      const isOpen = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!isOpen));
      menuButton.setAttribute("aria-label", isOpen ? "Open navigation" : "Close navigation");
      navigation.classList.toggle("is-open", !isOpen);
    });

    navigation.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.setAttribute("aria-label", "Open navigation");
        navigation.classList.remove("is-open");
      });
    });
  }

  const confirmationDialog = document.querySelector("[data-confirm-dialog]");
  if (confirmationDialog) {
    document.querySelectorAll("[data-confirm-open]").forEach((button) => {
      button.addEventListener("click", () => confirmationDialog.showModal());
    });
    confirmationDialog.querySelectorAll("[data-confirm-close]").forEach((button) => {
      button.addEventListener("click", () => confirmationDialog.close());
    });
    confirmationDialog.addEventListener("click", (event) => {
      if (event.target === confirmationDialog) confirmationDialog.close();
    });
  }

  const countdown = document.querySelector("[data-countdown]");
  if (!countdown) return;

  const target = new Date(countdown.dataset.countdown).getTime();
  const fields = {
    days: countdown.querySelector("[data-days]"),
    hours: countdown.querySelector("[data-hours]"),
    minutes: countdown.querySelector("[data-minutes]"),
    seconds: countdown.querySelector("[data-seconds]"),
  };

  const updateCountdown = () => {
    const remaining = Math.max(0, target - Date.now());
    const days = Math.floor(remaining / 86_400_000);
    const hours = Math.floor((remaining % 86_400_000) / 3_600_000);
    const minutes = Math.floor((remaining % 3_600_000) / 60_000);
    const seconds = Math.floor((remaining % 60_000) / 1_000);

    fields.days.textContent = String(days).padStart(3, "0");
    fields.hours.textContent = String(hours).padStart(2, "0");
    fields.minutes.textContent = String(minutes).padStart(2, "0");
    fields.seconds.textContent = String(seconds).padStart(2, "0");
  };

  updateCountdown();
  window.setInterval(updateCountdown, 1_000);
});