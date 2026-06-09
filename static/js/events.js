const eventsData = [
  {
    id: 1,
    title: 'Кино и сериалы 2025',
    emoji: '',
    category: 'cinema',
    date: '13 июня, пятница',
    time: '19:00',
    place: 'Ресторан Весна, Юбилейная 6а',
    price: 600,
    total: 20,
    booked: 14,
    tag: 'Скоро'
  },
  {
    id: 2,
    title: 'Угадай мелодию — Русские хиты',
    emoji: '',
    category: 'music',
    date: '15 июня, воскресенье',
    time: '18:00',
    place: 'Бар Штаб-Квартира, Юбилейная 8',
    price: 500,
    total: 16,
    booked: 6,
    tag: 'Новое'
  },
  {
    id: 3,
    title: 'ТЛТКВИЗ — Обо всём',
    emoji: '',
    category: 'classic',
    date: '18 июня, среда',
    time: '19:00',
    place: 'ТЦ Акварель, Южное шоссе',
    price: 600,
    total: 24,
    booked: 24,
    tag: ''
  },
  {
    id: 4,
    title: 'Эйнштейн Party — SHOW TIME',
    emoji: '',
    category: 'show',
    date: '20 июня, пятница',
    time: '19:00',
    place: 'Ресторан Весна, Юбилейная 6а',
    price: 700,
    total: 30,
    booked: 18,
    tag: 'Хит'
  },
  {
    id: 5,
    title: 'Мир кино — СССР и 90-е',
    emoji: '',
    category: 'cinema',
    date: '22 июня, воскресенье',
    time: '17:00',
    place: 'ТЦ Акварель, Южное шоссе',
    price: 550,
    total: 20,
    booked: 8,
    tag: ''
  },
  {
    id: 6,
    title: 'Музыкальный марафон',
    emoji: '',
    category: 'music',
    date: '25 июня, среда',
    time: '19:00',
    place: '40 лет Победы 33',
    price: 600,
    total: 20,
    booked: 3,
    tag: 'Новое'
  }
];

let currentFilter = 'all';

function getSeatsInfo(event) {
  const left = event.total - event.booked;
  if (left === 0) return { text: 'Мест нет', cls: 'seats-full', disabled: true };
  if (left <= 4) return { text: `Осталось ${left} места!`, cls: 'seats-few', disabled: false };
  return { text: `Мест: ${left} из ${event.total}`, cls: 'seats-ok', disabled: false };
}

function renderEvents(filter) {
  const grid = document.getElementById('eventsGrid');
  const filtered = filter === 'all' ? eventsData : eventsData.filter(e => e.category === filter);
  grid.innerHTML = '';
  filtered.forEach((ev, i) => {
    const seats = getSeatsInfo(ev);
    const card = document.createElement('div');
    card.className = 'event-card fade-in';
    card.style.animationDelay = (i * 0.08) + 's';
    card.innerHTML = `
      <div class="event-card-img">
        <div style="font-size:3.5rem;position:relative;z-index:1;">${ev.emoji}</div>
        ${ev.tag ? `<div class="event-tag">${ev.tag}</div>` : ''}
      </div>
      <div class="event-card-body">
        <div class="event-card-title">${ev.title}</div>
        <div class="event-meta">
          <div class="event-meta-row"><span class="event-meta-icon"></span>${ev.date}</div>
          <div class="event-meta-row"><span class="event-meta-icon"></span>${ev.time}</div>
          <div class="event-meta-row"><span class="event-meta-icon"></span>${ev.place}</div>
          <div class="event-meta-row"><span class="event-meta-icon"></span>Команды 4–10 человек</div>
        </div>
        <div class="event-card-footer">
          <div>
            <div class="event-price">${ev.price} ₽<br><small>с игрока</small></div>
          </div>
          <div class="seats-badge ${seats.cls}">${seats.text}</div>
        </div>
        <button class="btn-register" ${seats.disabled ? 'disabled' : ''}
          onclick="openRegModal('${ev.title}', '${ev.date}, ${ev.time}', '${ev.price} ₽ с игрока', '${ev.emoji}')">
          ${seats.disabled ? 'Мест нет' : 'Зарегистрироваться →'}
        </button>
      </div>
    `;
    grid.appendChild(card);
    setTimeout(() => card.classList.add('visible'), 50 + i * 80);
  });
}

function filterEvents(filter, btn) {
  currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderEvents(filter);
}
