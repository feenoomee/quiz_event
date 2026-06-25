let currentRegTab = 'active';

document.addEventListener('DOMContentLoaded', function () {
  loadRegistrations('active');
  loadTeams();
});

async function loadRegistrations(tab) {
  const container = document.getElementById('regList');
  if (!container) return;
  container.innerHTML = '<div style="text-align:center;padding:30px;color:#888;">Загрузка...</div>';

  try {
    const resp = await fetch('/api/my/registrations');
    const regs = await resp.json();
    renderRegistrations(regs, tab);
  } catch {
    container.innerHTML = '<div style="text-align:center;padding:30px;color:#888;">Ошибка загрузки</div>';
  }
}

function renderRegistrations(regs, tab) {
  const container = document.getElementById('regList');
  const now = new Date();

  const filtered = regs.filter(r => {
    const parts = (r.event_date || '').split(' ');
    if (parts.length < 2) return tab === 'active';
    const monthMap = { 'января':0,'февраля':1,'марта':2,'апреля':3,'мая':4,'июня':5,'июля':6,'августа':7,'сентября':8,'октября':9,'ноября':10,'декабря':11 };
    const month = monthMap[parts[1]];
    const day = parseInt(parts[0]);
    const year = parseInt(parts[2]);
    if (isNaN(day) || isNaN(year) || month === undefined) return tab === 'active';
    const eventDate = new Date(year, month, day);
    return tab === 'active' ? eventDate >= now : eventDate < now;
  });

  if (!filtered.length) {
    container.innerHTML = '<div style="text-align:center;padding:30px;color:#888;">Нет регистраций</div>';
    return;
  }

  container.innerHTML = '';
  filtered.forEach(r => {
    const status = r.status || 'pending';
    const isPending = status === 'pending';

    const parts = (r.event_date || '').split(' ');
    const monthMap = { 'января':0,'февраля':1,'марта':2,'апреля':3,'мая':4,'июня':5,'июля':6,'августа':7,'сентября':8,'октября':9,'ноября':10,'декабря':11 };
    const day = parseInt(parts[0]);
    const month = monthMap[parts[1]];
    const year = parseInt(parts[2]);
    const timeParts = (r.event_time || '00:00').split(':');
    const eventDate = (!isNaN(day) && month !== undefined && !isNaN(year))
      ? new Date(year, month, day, parseInt(timeParts[0]), parseInt(timeParts[1]))
      : null;
    const withinConfirmWindow = eventDate && (eventDate.getTime() - Date.now()) <= 14 * 60 * 60 * 1000;

    const card = document.createElement('div');
    card.className = 'profile-card';
    card.innerHTML = `
      <div class="reg-card-header">
        <div class="reg-card-title-group">
          <h3>${escapeHtml(r.event_name)}</h3>
          <p>${escapeHtml(r.event_date)}, ${escapeHtml(r.event_time)}</p>
        </div>
      </div>
      <div class="reg-card-body">
        <div class="reg-card-detail">
          <span>${escapeHtml(r.event_location)}</span>
        </div>
        <div class="reg-card-detail">
          <span>Команда: "${escapeHtml(r.team_name)}" (${r.player_count} чел.)</span>
        </div>
        <div class="reg-card-detail">
          <span>${r.event_price} ₽ с игрока</span>
        </div>
      </div>
      <div class="reg-card-footer">
        ${isPending && withinConfirmWindow
          ? `<button class="btn-main" onclick="confirmRegistration(${r.id})">Подтвердить участие</button>
             <button class="btn-cancel" onclick="cancelRegistration(${r.id})" style="margin-left:8px;">Отменить</button>`
          : `<button class="btn-cancel" onclick="cancelRegistration(${r.id})">Отменить</button>`}
      </div>
    `;
    container.appendChild(card);
  });
}

async function confirmRegistration(regId) {
  try {
    const resp = await fetch(`/api/registrations/${regId}/confirm`, { method: 'POST' });
    const data = await resp.json();
    if (!resp.ok) { alert(data.message || 'Ошибка'); return; }
    loadRegistrations(currentRegTab);
  } catch {
    alert('Ошибка сети');
  }
}

function switchRegTab(tab, btn) {
  currentRegTab = tab;
  document.querySelectorAll('.profile-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  loadRegistrations(tab);
}

async function cancelRegistration(regId) {
  if (!confirm('Отменить регистрацию?')) return;
  try {
    const resp = await fetch(`/api/registrations/${regId}`, { method: 'DELETE' });
    if (!resp.ok) { const d = await resp.json(); alert(d.message || 'Ошибка'); return; }
    loadRegistrations(currentRegTab);
  } catch {
    alert('Ошибка сети');
  }
}

async function loadTeams() {
  const container = document.getElementById('teamsList');
  if (!container) return;
  container.innerHTML = '<div style="text-align:center;padding:30px;color:#888;">Загрузка...</div>';

  try {
    const resp = await fetch('/api/my/teams');
    const teams = await resp.json();
    renderTeams(teams);
  } catch {
    container.innerHTML = '<div style="text-align:center;padding:30px;color:#888;">Ошибка загрузки</div>';
  }
}

function renderTeams(teams) {
  const container = document.getElementById('teamsList');
  if (!teams.length) {
    container.innerHTML = '<div style="text-align:center;padding:30px;color:#888;">У вас пока нет команд</div>';
    return;
  }

  container.innerHTML = '';
  teams.forEach(t => {
    const card = document.createElement('div');
    card.className = 'team-card';
    card.innerHTML = `
      <div class="team-header">
        <h3 class="team-name">${escapeHtml(t.name)}</h3>
        <span class="${t.is_captain ? 'team-role' : 'team-role-member'}">${t.is_captain ? 'Капитан' : 'Участник'}</span>
      </div>
      <div class="team-members">
        <div class="team-members-title">Участники (${t.members.length})</div>
        <div class="team-members-list">
          ${t.members.map(m => `<div class="team-member-badge">${escapeHtml(m.name)}${m.id === window.currentUser?.id ? ' (вы)' : ''}</div>`).join('')}
        </div>
      </div>
      <div class="team-footer">
        <button class="btn-cancel" onclick="${t.is_captain ? `deleteTeam(${t.id})` : `leaveTeam(${t.id})`}">${t.is_captain ? 'Удалить' : 'Выйти'}</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function openCreateTeamModal() {
  document.getElementById('newTeamName').value = '';
  document.getElementById('createTeamModal').classList.add('active');
}

async function submitCreateTeam() {
  const name = document.getElementById('newTeamName').value.trim();
  if (!name) { alert('Введите название команды'); return; }
  try {
    const resp = await fetch('/api/teams', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    const data = await resp.json();
    if (!resp.ok) { alert(data.message || 'Ошибка'); return; }
    closeModal();
    loadTeams();
  } catch { alert('Ошибка сети'); }
}

async function deleteTeam(teamId) {
  if (!confirm('Удалить команду? Это действие нельзя отменить.')) return;
  try {
    const resp = await fetch(`/api/teams/${teamId}`, { method: 'DELETE' });
    if (!resp.ok) { const d = await resp.json(); alert(d.message || 'Ошибка'); return; }
    loadTeams();
  } catch { alert('Ошибка сети'); }
}

async function leaveTeam(teamId) {
  if (!confirm('Выйти из команды?')) return;
  try {
    const resp = await fetch(`/api/teams/${teamId}/leave`, { method: 'POST' });
    if (!resp.ok) { const d = await resp.json(); alert(d.message || 'Ошибка'); return; }
    loadTeams();
  } catch { alert('Ошибка сети'); }
}

function escapeHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function toggleSettingsMenu(e) {
  e.preventDefault();
  const menu = document.getElementById('settingsMenu');
  menu.classList.toggle('active');
  document.addEventListener('click', function closeMenu(event) {
    if (!menu.contains(event.target) && !event.target.closest('.btn-edit') && !event.target.closest('.btn-profile')) {
      menu.classList.remove('active');
      document.removeEventListener('click', closeMenu);
    }
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.classList.add('active');
  const settingsMenu = document.getElementById('settingsMenu');
  if (settingsMenu) settingsMenu.classList.remove('active');
}

function closeModal(e) {
  if (e && e.target !== e.currentTarget) return;
  const overlays = document.querySelectorAll('.modal-overlay-custom');
  overlays.forEach(overlay => overlay.classList.remove('active'));
}

async function submitProfileEditModal(event) {
  event.preventDefault();
  const payload = {
    first_name: document.getElementById('modalEditFirstName').value.trim(),
    second_name: document.getElementById('modalEditSecondName').value.trim(),
    email: document.getElementById('modalEditEmail').value.trim(),
    phone: document.getElementById('modalEditPhone').value.trim(),
  };
  if (!payload.first_name || !payload.second_name || !payload.email) {
    alert('Имя, фамилия и email обязательны');
    return;
  }
  try {
    const resp = await fetch('/api/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) {
      alert(data.message || 'Ошибка сохранения');
      return;
    }
    alert('Профиль обновлён');
    location.reload();
  } catch {
    alert('Не удалось сохранить профиль');
  }
}

function logout() {
  window.location.href = '/logout';
}

(function initProfileAvatarPreview() {
  const MAX_BYTES = 2 * 1024 * 1024;
  const input = document.getElementById('profileAvatarInput');
  const label = input && input.closest('.profile-avatar');
  const img = document.querySelector('.profile-avatar-img');
  const removeBtn = document.getElementById('profileAvatarRemove');
  if (!input || !label || !img || !removeBtn) return;

  let objectUrl = null;

  function clearPreview() {
    if (objectUrl) {
      URL.revokeObjectURL(objectUrl);
      objectUrl = null;
    }
    img.removeAttribute('src');
    label.classList.remove('has-image');
    removeBtn.hidden = true;
    input.value = '';
  }

  async function uploadAvatar(file) {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const resp = await fetch('/api/upload/avatar', { method: 'POST', body: formData });
      const data = await resp.json();
      if (!resp.ok) { alert(data.message || 'Ошибка загрузки'); return null; }
      return data.url;
    } catch { alert('Ошибка сети при загрузке'); return null; }
  }

  input.addEventListener('change', async function () {
    const file = input.files && input.files[0];
    if (!file) return;
    if (!/^image\/(png|jpeg|gif|webp)$/i.test(file.type)) {
      alert('Выберите изображение PNG, JPEG, GIF или WebP.');
      input.value = '';
      return;
    }
    if (file.size > MAX_BYTES) {
      alert('Файл не больше 2 МБ.');
      input.value = '';
      return;
    }
    const url = await uploadAvatar(file);
    if (!url) { input.value = ''; return; }
    img.src = url;
    label.classList.add('has-image');
    removeBtn.hidden = false;
    if (objectUrl) { URL.revokeObjectURL(objectUrl); objectUrl = null; }
  });

  removeBtn.addEventListener('click', function (e) {
    e.preventDefault();
    clearPreview();
  });
})();
