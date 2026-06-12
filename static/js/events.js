let eventsData = [];
let currentFilter = 'all';

function loadEvents() {
  const grid = document.getElementById('eventsGrid');
  if (grid) {
    grid.innerHTML = '<div style="text-align:center;padding:40px;color:#888;">Загрузка мероприятий...</div>';
  }

  fetch('/api/events', { credentials: 'same-origin' })
    .then(r => r.json())
    .then(data => {
      eventsData = data;
      renderEvents(currentFilter);
    })
    .catch(err => {
      console.error('Failed to load events:', err);
      if (grid) {
        grid.innerHTML = '<div style="text-align:center;padding:40px;color:#888;">Не удалось загрузить мероприятия</div>';
      }
    });
}

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
        <div style="font-size:3.5rem;position:relative;z-index:1;"></div>
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
          onclick="openRegModal('${ev.title.replace(/'/g, "\\'")}', '${ev.date}, ${ev.time}', '${ev.price} ₽ с игрока', '')">
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

document.addEventListener('DOMContentLoaded', loadEvents);
