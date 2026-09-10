// Scroll-reveal for the heritage gallery and hero.
// Content is visible by default in HTML/CSS; JS only ever ADDS a temporary
// hidden state right before it can guarantee revealing it — so a JS failure
// or slow load never leaves real content invisible.
document.addEventListener("DOMContentLoaded", () => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const hero = document.querySelector(".hero");
  if (hero && !reduceMotion) hero.classList.add("js-anim");

  const cards = document.querySelectorAll(".gallery-card");
  if (!cards.length || reduceMotion || !("IntersectionObserver" in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.remove("pending");
          entry.target.classList.add("revealed");
        }, i * 60);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  cards.forEach(el => {
    el.classList.add("pending"); // only hide once we're set up to reveal it
    observer.observe(el);
  });
});
