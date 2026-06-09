document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('sliderDots')) {
    initSlider();
  }
  if (document.getElementById('eventsGrid')) {
    renderEvents('all');
  }
  if (isAuthenticated() && document.getElementById('regModal')) {
    const pendingReg = popPendingRegistration();
    if (pendingReg) {
      setTimeout(() => {
        openRegModal(pendingReg.name, pendingReg.date, pendingReg.price, pendingReg.icon);
      }, 250);
    }
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
  });

  const countElements = document.querySelectorAll('[data-count]');
  countElements.forEach(el => {
    const target = parseInt(el.getAttribute('data-count'));
    let current = 0;
    const increment = Math.ceil(target / 60);
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = current;
    }, 30);
  });
});
