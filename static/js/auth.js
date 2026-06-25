let currentRegEvent = null;
const pendingRegStorageKey = 'tltquizPendingRegistration';

function isAuthenticated() {
  return Boolean(window.currentUser);
}

function savePendingRegistration(regEvent) {
  sessionStorage.setItem(pendingRegStorageKey, JSON.stringify(regEvent));
}

function popPendingRegistration() {
  const raw = sessionStorage.getItem(pendingRegStorageKey);
  if (!raw) return null;
  sessionStorage.removeItem(pendingRegStorageKey);
  try { return JSON.parse(raw); }
  catch { return null; }
}

async function openRegModal(eventId, name, date, price) {
  currentRegEvent = { eventId, name, date, price };

  if (!isAuthenticated()) {
    savePendingRegistration(currentRegEvent);
    openAuthModal();
    return;
  }

  document.getElementById('regEventName').textContent = name;
  document.getElementById('regEventDate').textContent = date;
  document.getElementById('regEventPrice').textContent = price;
  document.getElementById('regSuccess').style.display = 'none';
  document.getElementById('regModalFooter').style.display = 'flex';

  document.getElementById('regStepTeam').style.display = 'block';
  document.getElementById('regStepCreate').style.display = 'none';

  await loadUserTeams();

  document.getElementById('regModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeRegModal(e) {
  if (e && e.target !== document.getElementById('regModal')) return;
  document.getElementById('regModal').classList.remove('open');
  document.body.style.overflow = '';
}

async function loadUserTeams() {
  const select = document.getElementById('regTeamSelect');
  select.innerHTML = '<option value="">— Загружаем...</option>';
  try {
    const resp = await fetch('/api/my/teams');
    const teams = await resp.json();
    if (!teams.length) {
      select.innerHTML = '<option value="">— У вас нет команд</option>';
      return;
    }
    select.innerHTML = '<option value="">— Выберите команду —</option>';
    teams.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = `${t.name}`;
      select.appendChild(opt);
    });
  } catch {
    select.innerHTML = '<option value="">— Ошибка загрузки</option>';
  }
}

function showCreateTeam() {
  document.getElementById('regStepTeam').style.display = 'none';
  document.getElementById('regStepCreate').style.display = 'block';
}

function hideCreateTeam() {
  document.getElementById('regStepCreate').style.display = 'none';
  document.getElementById('regStepTeam').style.display = 'block';
}

async function submitReg() {
  const eventId = currentRegEvent?.eventId;
  if (!eventId) { alert('Ошибка: не выбрано мероприятие.'); return; }

  let teamId = null;
  const stepCreate = document.getElementById('regStepCreate');
  if (stepCreate && stepCreate.style.display !== 'none') {
    const name = document.getElementById('regNewTeamName').value.trim();
    if (!name) { alert('Введите название команды.'); return; }
    try {
      const resp = await fetch('/api/teams', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      const data = await resp.json();
      if (!resp.ok) { alert(data.message || 'Ошибка создания команды'); return; }
      teamId = data.team.id;
    } catch { alert('Ошибка сети'); return; }
  } else {
    const select = document.getElementById('regTeamSelect');
    teamId = select.value;
    if (!teamId) { alert('Выберите команду.'); return; }
  }

  const count = document.getElementById('regCount').value || 1;
  const comment = document.getElementById('regComment').value.trim();

  try {
    const resp = await fetch('/api/register_team', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_id: eventId, team_id: teamId, player_count: count, comment }),
    });
    const data = await resp.json();
    if (!resp.ok) { alert(data.message || 'Ошибка регистрации'); return; }
  } catch {
    alert('Ошибка сети');
    return;
  }

  document.getElementById('regStepTeam').style.display = 'none';
  document.getElementById('regStepCreate').style.display = 'none';
  document.getElementById('regModalFooter').style.display = 'none';
  document.getElementById('regSuccess').style.display = 'block';
  document.getElementById('regCount').value = 4;
  document.getElementById('regComment').value = '';
  document.getElementById('regNewTeamName').value = '';
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

  const endpoint = isLoginTab ? '/api/login' : '/api/signup';
  const payload = isLoginTab
    ? {
        email: document.getElementById('authIdentifier')?.value.trim(),
        password: document.getElementById('authPassword')?.value
      }
    : {
        first_name: document.getElementById('signupFirstName')?.value.trim(),
        second_name: document.getElementById('signupSecondName')?.value.trim(),
        phone: document.getElementById('signupPhone')?.value.trim(),
        email: document.getElementById('signupEmail')?.value.trim(),
        password: document.getElementById('signupPassword')?.value
      };

  const errorEl = document.getElementById('signupPasswordError');
  if (errorEl) errorEl.style.display = 'none';

  if (!isLoginTab) {
    const confirm = document.getElementById('signupPasswordConfirm')?.value;
    if (payload.password !== confirm) {
      if (errorEl) errorEl.style.display = 'block';
      return;
    }
  }

  const requiredValues = Object.values(payload);
  if (requiredValues.some(value => !value)) {
    alert(isLoginTab ? 'Введите email и пароль.' : 'Заполните все поля регистрации.');
    return;
  }

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) {
      alert(data.message || 'Ошибка входа.');
      return;
    }

    window.currentUser = data.user;
    const pending = popPendingRegistration();
    if (pending) {
      openRegModal(pending.eventId, pending.name, pending.date, pending.price);
    } else {
      window.location.href = data.redirect_to || '/';
    }
  } catch (error) {
    alert('Не удалось выполнить действие. Попробуйте снова.');
  }
}

function openCorpModal(e) {
}
