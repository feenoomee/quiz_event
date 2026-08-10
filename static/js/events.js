let eventsData = [];
let currentFilter = 'all';
let currentDetailsEvent = null;

const CATEGORY_LABELS = {
  music: 'Музыкальные квиз-вечеринки',
  cinema: 'Классический ТЛТКВИЗ',
  classic: 'Тематические игры',
  show: 'Корпоратив',
};

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

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
  const left = Math.max(0, event.total - event.booked);
  if (left === 0) return { text: 'Мест нет', cls: 'seats-full', disabled: false };
  if (left <= 4) return { text: `Осталось ${left} места!`, cls: 'seats-few', disabled: false };
  return { text: `Мест: ${left} из ${event.total}`, cls: 'seats-ok', disabled: false };
}

function renderEvents(filter) {
  const grid = document.getElementById('eventsGrid');
  const upcoming = eventsData.filter(e => !e.is_past);
  const filtered = filter === 'all' ? upcoming : upcoming.filter(e => e.category === filter);
  grid.innerHTML = '';
  if (filtered.length === 0) {
    grid.innerHTML = '<div style="text-align:center;padding:40px;color:#888;">Нет предстоящих мероприятий</div>';
    return;
  }
  filtered.forEach((ev, i) => {
    const seats = getSeatsInfo(ev);
    const seatsLeft = Math.max(0, ev.total - ev.booked);
    const card = document.createElement('div');
    card.className = 'event-card fade-in';
    card.style.animationDelay = (i * 0.08) + 's';
    const photoStyle = ev.photo ? `background-image:url('${ev.photo}');background-size:cover;background-position:center;` : '';
    card.innerHTML = `
      <div class="event-card-img" style="${photoStyle}">
        ${ev.photo ? '' : '<div style="font-size:3.5rem;position:relative;z-index:1;"></div>'}
        ${ev.tag ? `<div class="event-tag">${ev.tag}</div>` : ''}
      </div>
      <div class="event-card-body">
        <div class="event-card-title" onclick="openEventDetails(${ev.id})">${escapeHtml(ev.title)}</div>
        <div class="event-card-desc" onclick="openEventDetails(${ev.id})">${escapeHtml(ev.description)}</div>
        <div class="event-card-more" onclick="openEventDetails(${ev.id})">Подробнее →</div>
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
        ${ev.registration_open === false
          ? '<button class="btn-register btn-register--closed" disabled>Регистрация закрыта</button>'
          : `<button class="btn-register"
              onclick="openRegModal(${ev.id}, '${escapeHtml(ev.title)}', '${escapeHtml(ev.date)}, ${escapeHtml(ev.time)}', '${ev.price} ₽ с игрока')">
              ${seatsLeft === 0 ? 'В лист ожидания →' : 'Зарегистрироваться →'}
            </button>`
        }
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

function openEventDetails(eventId) {
  const ev = eventsData.find(e => e.id === eventId);
  if (!ev) {
    fetch('/api/events', { credentials: 'same-origin' })
      .then(r => r.json())
      .then(data => {
        eventsData = data;
        renderEvents(currentFilter);
        openEventDetails(eventId);
      })
      .catch(err => console.error('Failed to load events:', err));
    return;
  }
  currentDetailsEvent = ev;

  document.getElementById('detailsEventName').textContent = ev.title;
  document.getElementById('detailsEventSub').textContent = CATEGORY_LABELS[ev.category] || 'Квиз';

  const photo = document.getElementById('detailsEventPhoto');
  if (ev.photo) {
    photo.style.display = 'block';
    photo.style.backgroundImage = `url('${ev.photo}')`;
  } else {
    photo.style.display = 'none';
    photo.style.backgroundImage = '';
  }

  document.getElementById('detailsEventDesc').textContent = ev.description || '';
  document.getElementById('detailsEventDate').textContent = ev.date;
  document.getElementById('detailsEventTime').textContent = ev.time;
  document.getElementById('detailsEventPlace').textContent = ev.place;

  const seats = getSeatsInfo(ev);
  const seatsLeft = Math.max(0, ev.total - ev.booked);
  document.getElementById('detailsEventTeams').textContent = 'Команды 4–10 человек · ' + seats.text;

  const btn = document.getElementById('detailsRegBtn');
  if (ev.registration_open === false) {
    btn.disabled = true;
    btn.textContent = 'Регистрация закрыта';
  } else {
    btn.disabled = false;
    btn.textContent = seatsLeft === 0 ? 'В лист ожидания →' : 'Зарегистрироваться';
  }

  document.getElementById('eventDetailsModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeEventDetails(e) {
  if (e && window.getSelection().toString().length > 0) return;
  document.getElementById('eventDetailsModal').classList.remove('open');
  document.body.style.overflow = '';
}

function registerFromDetails() {
  const ev = currentDetailsEvent;
  if (!ev) return;
  closeEventDetails();
  openRegModal(ev.id, ev.title, `${ev.date}, ${ev.time}`, `${ev.price} ₽ с игрока`);
}

document.addEventListener('DOMContentLoaded', loadEvents);
