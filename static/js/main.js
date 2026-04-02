document.addEventListener("DOMContentLoaded", () => {
  const burgerBtn = document.getElementById("burgerBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  if (burgerBtn && mobileMenu) {
    burgerBtn.addEventListener("click", () => {
      mobileMenu.classList.toggle("open");
      const expanded = mobileMenu.classList.contains("open");
      burgerBtn.setAttribute("aria-expanded", expanded ? "true" : "false");
    });
  }

  const messages = document.querySelectorAll(".message");
  if (messages.length) {
    setTimeout(() => {
      messages.forEach((el) => {
        el.style.transition = "opacity 0.5s";
        el.style.opacity = "0";
      });
    }, 3500);
  }
});
