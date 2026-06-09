let currentSlide = 0;
const totalSlides = 4;

function initSlider() {
  const dots = document.getElementById('sliderDots');
  const slides = document.getElementById('slides');
  if (!dots || !slides) return;
  for (let i = 0; i < totalSlides; i++) {
    const d = document.createElement('button');
    d.className = 'slider-dot' + (i === 0 ? ' active' : '');
    d.onclick = () => goToSlide(i);
    dots.appendChild(d);
  }
}

function goToSlide(n) {
  const slides = document.getElementById('slides');
  if (!slides) return;
  currentSlide = n;
  slides.style.transform = `translateX(-${n * 100}%)`;
  document.querySelectorAll('.slider-dot').forEach((d, i) => {
    d.classList.toggle('active', i === n);
  });
}

function nextSlide() { goToSlide((currentSlide + 1) % totalSlides); }
function prevSlide() { goToSlide((currentSlide - 1 + totalSlides) % totalSlides); }

let sliderInterval;

const slidesContainer = document.getElementById('slides');
if (slidesContainer) {
  sliderInterval = setInterval(nextSlide, 4500);
  slidesContainer.addEventListener('mouseenter', () => clearInterval(sliderInterval));
  slidesContainer.addEventListener('mouseleave', () => {
    clearInterval(sliderInterval);
    sliderInterval = setInterval(nextSlide, 4500);
  });
}
