(function () {
  const slidesEl = document.getElementById('heroSlides');
  if (!slidesEl) return;

  const slides = slidesEl.querySelectorAll('.hero-slide');
  const total = slides.length;
  const dotsEl = document.getElementById('heroSliderDots');
  const prevBtn = document.getElementById('heroPrev');
  const nextBtn = document.getElementById('heroNext');
  const slider = document.getElementById('heroSlider');
  let current = 0;
  let timer = null;

  function goTo(n) {
    current = (n + total) % total;
    const width = slider ? slider.clientWidth : slidesEl.clientWidth;
    slidesEl.style.transform = 'translateX(-' + current * width + 'px)';
    if (dotsEl) {
      dotsEl.querySelectorAll('.slider-dot').forEach(function (dot, i) {
        dot.classList.toggle('active', i === current);
      });
    }
  }

  function startAuto() {
    clearInterval(timer);
    if (total <= 1) return;
    timer = setInterval(function () {
      goTo(current + 1);
    }, 5000);
  }

  if (dotsEl && total > 1) {
    dotsEl.innerHTML = '';
    for (let i = 0; i < total; i++) {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'slider-dot' + (i === 0 ? ' active' : '');
      dot.addEventListener('click', function () {
        goTo(i);
        startAuto();
      });
      dotsEl.appendChild(dot);
    }
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      goTo(current - 1);
      startAuto();
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      goTo(current + 1);
      startAuto();
    });
  }

  if (slider) {
    slider.addEventListener('mouseenter', function () {
      clearInterval(timer);
    });
    slider.addEventListener('mouseleave', startAuto);
  }

  startAuto();
  window.addEventListener('resize', function () {
    goTo(current);
  });

  const lightbox = document.getElementById('posterLightbox');
  const lightboxImg = document.getElementById('posterLightboxImg');
  const closeBtn = document.getElementById('posterLightboxClose');

  function openLightbox(src) {
    if (!lightbox || !lightboxImg || !src) return;
    lightboxImg.src = src;
    lightbox.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.hidden = true;
    if (lightboxImg) lightboxImg.src = '';
    document.body.style.overflow = '';
  }

  document.querySelectorAll('.hero-poster-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      openLightbox(btn.getAttribute('data-poster-src'));
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
  if (lightbox) {
    lightbox.addEventListener('click', function (event) {
      if (event.target === lightbox) closeLightbox();
    });
  }
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') closeLightbox();
  });
})();
