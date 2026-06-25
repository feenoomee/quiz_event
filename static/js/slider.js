let currentSlide = 0;
let totalSlides = 0;

function initSlider(total) {
  totalSlides = total;
  const dots = document.getElementById('sliderDots');
  const slides = document.getElementById('slides');
  if (!dots || !slides) return;
  dots.innerHTML = '';
  for (let i = 0; i < total; i++) {
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

function nextSlide() {
  if (totalSlides === 0) return;
  goToSlide((currentSlide + 1) % totalSlides);
}

function prevSlide() {
  if (totalSlides === 0) return;
  goToSlide((currentSlide - 1 + totalSlides) % totalSlides);
}

let sliderInterval;

function startSliderAuto() {
  clearInterval(sliderInterval);
  if (totalSlides <= 1) return;
  sliderInterval = setInterval(nextSlide, 4500);
  const slidesContainer = document.getElementById('slides');
  if (slidesContainer) {
    slidesContainer.addEventListener('mouseenter', () => clearInterval(sliderInterval));
    slidesContainer.addEventListener('mouseleave', () => {
      clearInterval(sliderInterval);
      sliderInterval = setInterval(nextSlide, 4500);
    });
  }
}

function renderResults(games) {
  const slides = document.getElementById('slides');
  if (!slides) return;

  if (!games.length) {
    slides.innerHTML = '<div class="slide loading-slide"><p>Результаты пока не добавлены</p></div>';
    return;
  }

  slides.innerHTML = '';
  games.forEach((game) => {
    const slide = document.createElement('div');
    slide.className = 'slide';

    const emojiDiv = document.createElement('div');
    emojiDiv.className = 'slide-emoji';
    if (game.photo) {
      emojiDiv.innerHTML = `<img src="${game.photo}" alt="" style="width:100%;height:100%;object-fit:cover;">`;
    } else {
      emojiDiv.textContent = '🏆';
    }

    const infoDiv = document.createElement('div');

    const numDiv = document.createElement('div');
    numDiv.className = 'slide-num';
    numDiv.textContent = `${game.date} · ${game.time}`;
    infoDiv.appendChild(numDiv);

    const titleDiv = document.createElement('div');
    titleDiv.className = 'slide-title';
    titleDiv.textContent = game.title;
    infoDiv.appendChild(titleDiv);

    const tableWrap = document.createElement('div');
    tableWrap.className = 'slide-results-wrap';

    const table = document.createElement('table');
    table.className = 'slide-results-table';

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Место', 'Команда', 'Сумма'].forEach((h) => {
      const th = document.createElement('th');
      th.textContent = h;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    game.results.forEach((r) => {
      const tr = document.createElement('tr');
      if (r.place === 1) tr.classList.add('place-1');
      if (r.place === 2) tr.classList.add('place-2');
      if (r.place === 3) tr.classList.add('place-3');

      const tdPlace = document.createElement('td');
      tdPlace.className = 'td-place';
      if (r.place === 1) tdPlace.textContent = '🥇';
      else if (r.place === 2) tdPlace.textContent = '🥈';
      else if (r.place === 3) tdPlace.textContent = '🥉';
      else tdPlace.textContent = r.place;
      tr.appendChild(tdPlace);

      const tdTeam = document.createElement('td');
      tdTeam.className = 'td-team';
      tdTeam.textContent = r.team_name;
      tr.appendChild(tdTeam);

      const tdTotal = document.createElement('td');
      tdTotal.className = 'td-total';
      tdTotal.textContent = r.total;
      tr.appendChild(tdTotal);

      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    tableWrap.appendChild(table);
    infoDiv.appendChild(tableWrap);

    slide.appendChild(emojiDiv);
    slide.appendChild(infoDiv);
    slides.appendChild(slide);
  });

  totalSlides = games.length;
  initSlider(totalSlides);
  startSliderAuto();
}

(function fetchAndRender() {
  const slides = document.getElementById('slides');
  if (!slides) return;
  fetch('/api/games/past')
    .then((r) => r.json())
    .then((data) => {
      renderResults(data.games || []);
    })
    .catch(() => {
      slides.innerHTML = '<div class="slide loading-slide"><p>Не удалось загрузить результаты</p></div>';
    });
})();
