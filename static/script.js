// ===== EVENTS DATA =====
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

// ===== SLIDER =====
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

// ===== MODALS =====
let currentRegEvent = {};

function openRegModal(name, date, price, icon) {
  currentRegEvent = { name, date, price, icon };
  document.getElementById('regEventName').textContent = name;
  document.getElementById('regEventDate').textContent = date;
  document.getElementById('regEventPrice').textContent = price;
  document.getElementById('regEventIcon').textContent = icon;
  document.getElementById('regForm').style.display = 'block';
  document.getElementById('regSuccess').style.display = 'none';
  document.getElementById('regModalFooter').style.display = 'flex';
  document.getElementById('regModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeRegModal(e) {
  if (e && e.target !== document.getElementById('regModal')) return;
  document.getElementById('regModal').classList.remove('open');
  document.body.style.overflow = '';
}

function submitReg() {
  const team = document.getElementById('teamName').value.trim();
  const name = document.getElementById('regName').value.trim();
  const phone = document.getElementById('regPhone').value.trim();
  const count = document.getElementById('regCount').value;
  if (!team || !name || !phone || !count) {
    alert('Пожалуйста, заполните все обязательные поля!');
    return;
  }
  document.getElementById('regForm').style.display = 'none';
  document.getElementById('regModalFooter').style.display = 'none';
  document.getElementById('regSuccess').style.display = 'block';
  ['teamName','regName','regPhone','regCount','regComment'].forEach(id => {
    document.getElementById(id).value = '';
  });
}

function openAuthModal(e) {
  if (e) e.preventDefault();
  document.getElementById('authModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeAuthModal(e) {
  if (e && e.target !== document.getElementById('authModal')) return;
  document.getElementById('authModal').classList.remove('open');
  document.body.style.overflow = '';
}

function switchAuthTab(tab, btn) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('loginForm').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('registerForm').style.display = tab === 'register' ? 'block' : 'none';
  document.getElementById('authSubmitBtn').textContent = tab === 'login' ? 'Войти' : 'Создать аккаунт';
}

async function submitAuth() {
  const isLoginTab = document.getElementById('loginForm').style.display !== 'none';
  if (!isLoginTab) {
    alert('Регистрация пока в разработке. Используйте демо-вход.');
    return;
  }

  const identifier = document.getElementById('authIdentifier')?.value.trim();
  if (!identifier) {
    alert('Введите логин или email.');
    return;
  }

  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier })
    });

    const data = await response.json();
    if (!response.ok) {
      alert(data.message || 'Ошибка входа.');
      return;
    }

    window.location.href = data.redirect_to || '/dashboard';
  } catch (error) {
    alert('Не удалось выполнить вход. Попробуйте снова.');
  }
}

function openCorpModal(e) {
  // goes to VK directly
}

// ===== CHAT =====
let chatOpen = false;
const botReplies = [
  'Спасибо за ваш вопрос! Мы ответим вам в ближайшее время 😊',
  'Отличный вопрос! Напишите нам напрямую: vk.com/tltquiz',
  'Хотите зарегистрироваться? Выберите мероприятие в календаре!',
  'Команды от 4 до 10 человек. Стоимость от 500 до 700 ₽ с игрока.',
  'Корпоративные квизы организуем! Переходите по ссылке в ВК',
];
let replyIdx = 0;

function toggleChat() {
  chatOpen = !chatOpen;
  const panel = document.getElementById('chatPanel');
  const badge = document.getElementById('chatBadge');
  const fabBtn = document.getElementById('chatFabBtn');
  if (chatOpen) {
    panel.classList.add('open');
    badge.style.display = 'none';
    fabBtn.textContent = '✕';
    fabBtn.style.fontSize = '1.1rem';
  } else {
    panel.classList.remove('open');
    fabBtn.innerHTML = '💬<div class="chat-fab-badge" id="chatBadge" style="display:none;">2</div>';
  }
}

function sendChatMsg() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;
  addChatMsg(text, 'user');
  input.value = '';
  setTimeout(() => {
    addChatMsg(botReplies[replyIdx % botReplies.length], 'bot');
    replyIdx++;
  }, 800);
}

function chatKeyPress(event) {
  if (event.key === 'Enter') {
    sendChatMsg();
  }
}

function addChatMsg(text, type) {
  const msgs = document.getElementById('chatMessages');
  const msg = document.createElement('div');
  msg.className = `chat-msg ${type}`;
  const time = new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  msg.innerHTML = `${text}<div class="chat-msg-time">${time}</div>`;
  msgs.appendChild(msg);
  msgs.scrollTop = msgs.scrollHeight;
}

// ===== MOBILE MENU =====
function toggleMobileMenu() {
  document.getElementById('mobileMenu').classList.toggle('open');
}

function closeMobileMenu() {
  document.getElementById('mobileMenu').classList.remove('open');
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('sliderDots')) {
    initSlider();
  }
  if (document.getElementById('eventsGrid')) {
    renderEvents('all');
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
