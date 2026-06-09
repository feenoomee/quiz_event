let currentRegEvent = {};
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
  try {
    return JSON.parse(raw);
  } catch (error) {
    return null;
  }
}

function openRegModal(name, date, price, icon) {
  currentRegEvent = { name, date, price, icon };
  if (!isAuthenticated()) {
    savePendingRegistration(currentRegEvent);
    openAuthModal();
    return;
  }
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

async function submitReg() {
  const team = document.getElementById('teamName').value.trim();
  const name = document.getElementById('regName').value.trim();
  const phone = document.getElementById('regPhone').value.trim();
  const count = document.getElementById('regCount').value;
  if (!team || !name || !phone || !count) {
    alert('Пожалуйста, заполните все обязательные поля!');
    return;
  }

  try {
    const response = await fetch('/api/register_team', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event: currentRegEvent,
        team,
        name,
        phone,
        count,
        comment: document.getElementById('regComment').value.trim()
      })
    });
    const data = await response.json();
    if (response.status === 401) {
      savePendingRegistration(currentRegEvent);
      closeRegModal();
      openAuthModal();
      return;
    }
    if (!response.ok) {
      alert(data.message || 'Не удалось отправить регистрацию.');
      return;
    }
  } catch (error) {
    alert('Не удалось отправить регистрацию. Попробуйте снова.');
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

    window.location.href = data.redirect_to || '/';
  } catch (error) {
    alert('Не удалось выполнить действие. Попробуйте снова.');
  }
}

function openCorpModal(e) {
}
