let statsData = null;
let scoreboardEventId = null;
let editingEventId = null;

document.addEventListener('DOMContentLoaded', function () {
  loadStats();
  initializePhotoUpload();
  observeFadeInElements();
  initScoreboardUi();
  initCustomModals();
});

function initCustomModals() {
  const modals = document.querySelectorAll('.modal-overlay-custom');
  modals.forEach(function(modal) {
    const closeBtn = modal.querySelector('.modal-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        modal.classList.remove('active');
      });
    }
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    const dropdowns = document.querySelectorAll('.cabinet-dropdown');
    dropdowns.forEach(function(dropdown) {
      dropdown.classList.remove('show');
    });
  }
}

function closeModal(e) {
  if (e && e.target !== e.currentTarget) return;
  const overlays = document.querySelectorAll('.modal-overlay-custom');
  overlays.forEach(function(overlay) {
    overlay.classList.remove('active');
  });
}

function observeFadeInElements() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  document.querySelectorAll('.fade-in').forEach((el) => observer.observe(el));
}

function loadStats() {
  fetch('/api/stats', { credentials: 'same-origin' })
    .then((response) => {
      if (response.status === 403) {
        throw new Error('Доступ запрещён');
      }
      return response.json();
    })
    .then((data) => {
      statsData = data;
      updateQuickStats(data);
      populateEventsTable(data.events);
    })
    .catch((error) => {
      console.error('Error loading stats:', error);
      const tbody = document.getElementById('events-tbody');
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#888;">Ошибка загрузки данных</td></tr>';
      }
    });
}

function updateQuickStats(data) {
  const setText = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };
  setText('total-events', data.total_events);
  setText('total-revenue', '₽' + formatNumber(data.total_revenue));
  setText('total-attendees', data.total_attendees);
  setText('occupancy-rate', data.occupancy_rate + '%');
}

function populateEventsTable(events) {
  const tbody = document.getElementById('events-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (!events || Object.keys(events).length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:30px;color:#888;">Пока мероприятий нет</td></tr>';
    return;
  }

  for (const [id, event] of Object.entries(events)) {
    const occupancy = event.max_seats ? Math.round((event.registered / event.max_seats) * 100) : 0;
    const row = document.createElement('tr');
    row.innerHTML = `
      <td><strong>${escapeHtml(event.title)}</strong></td>
      <td>${escapeHtml(event.date)}, ${escapeHtml(event.time)}</td>
      <td>${escapeHtml(event.location)}</td>
      <td>${event.registered}/${event.max_seats}</td>
      <td>${occupancy}%</td>
      <td>
        <button class="btn-edit" onclick="editEvent(${id})">Редакт.</button>
        <button class="btn-delete" onclick="deleteEvent(${id})">Удал.</button>
        <button class="btn-close" onclick="closeEvent(${id})">Закрыть</button>
      </td>
    `;
    tbody.appendChild(row);
  }
}

// --- Таблица результатов (туры / сумма / места) ---

function initScoreboardUi() {
  const openBtn = document.getElementById('btn-open-game-modal');
  if (openBtn) {
    openBtn.addEventListener('click', openGameSelectModal);
  }
  const saveBtn = document.getElementById('btn-save-scoreboard');
  if (saveBtn) {
    saveBtn.addEventListener('click', saveScoreboard);
  }
  const tbody = document.getElementById('scoreboard-tbody');
  if (tbody) {
    tbody.addEventListener('input', onScoreboardInput);
  }
}

function openGameSelectModal() {
  const modal = document.getElementById('gameSelectModal');
  const select = document.getElementById('game-select');
  if (!modal || !select) return;

  select.innerHTML = '<option value="">Загрузка…</option>';
  modal.classList.add('show');
  document.body.style.overflow = 'hidden';

  fetch('/api/admin/recent-games', { credentials: 'same-origin' })
    .then((r) => r.json())
    .then((data) => {
      select.innerHTML = '';
      const games = data.games || [];
      if (!games.length) {
        select.innerHTML = '<option value="">Нет игр</option>';
        return;
      }
      games.forEach((g) => {
        const opt = document.createElement('option');
        opt.value = String(g.id);
        opt.textContent = `${g.title} — ${g.date} ${g.time}`;
        select.appendChild(opt);
      });
    })
    .catch(() => {
      select.innerHTML = '<option value="">Ошибка загрузки</option>';
    });
}

function closeGameSelectModal(e) {
  const modal = document.getElementById('gameSelectModal');
  if (!modal) return;
  if (e && e.target !== modal) return;
  modal.classList.remove('show');
  document.body.style.overflow = '';
}

function confirmGameSelection() {
  const select = document.getElementById('game-select');
  if (!select || !select.value) {
    alert('Выберите игру из списка.');
    return;
  }
  const id = parseInt(select.value, 10);
  if (Number.isNaN(id)) return;

  fetch(`/api/admin/games/${id}/scoreboard`, { credentials: 'same-origin' })
    .then((r) => {
      if (r.status === 403) {
        alert('Нет доступа. Войдите как администратор.');
        throw new Error('403');
      }
      return r.json();
    })
    .then((data) => {
      if (data.status === 'error') {
        alert(data.message || 'Ошибка');
        return;
      }
      scoreboardEventId = data.event_id;
      renderScoreboard(data);
      closeGameSelectModal();
      const emptyEl = document.getElementById('scoreboard-empty');
      const wrap = document.getElementById('scoreboard-wrap');
      const hint = document.getElementById('scoreboard-places-hint');
      if (emptyEl) emptyEl.hidden = true;
      if (wrap) wrap.hidden = false;
      if (hint) hint.hidden = false;
    })
    .catch((err) => {
      if (err.message !== '403') console.error(err);
    });
}

function renderScoreboard(data) {
  const banner = document.getElementById('scoreboard-banner-title');
  const thead = document.getElementById('scoreboard-thead');
  const tbody = document.getElementById('scoreboard-tbody');
  if (!thead || !tbody || !banner) return;

  const teams = data.teams || [];
  const rounds = data.rounds || 7;
  const scores = data.scores || [];

  banner.textContent = data.title || '—';

  const headRow1 = document.createElement('tr');
  headRow1.innerHTML = `
    <th class="scoreboard-th-team" rowspan="2">Команда</th>
    <th class="scoreboard-th-tour" colspan="${rounds}">Тур</th>
    <th class="scoreboard-th-sum" rowspan="2">Σ</th>
    <th class="scoreboard-th-place" rowspan="2">Место</th>
  `;
  const headRow2 = document.createElement('tr');
  for (let r = 1; r <= rounds; r++) {
    const th = document.createElement('th');
    th.className = 'scoreboard-th-round';
    th.textContent = String(r);
    headRow2.appendChild(th);
  }
  thead.innerHTML = '';
  thead.appendChild(headRow1);
  thead.appendChild(headRow2);

  tbody.innerHTML = '';
  if (!teams.length) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td colspan="${rounds + 3}" class="scoreboard-no-teams">Для этой игры пока нет команд в базе.</td>`;
    tbody.appendChild(tr);
    refreshScoreboardTotals();
    return;
  }

  teams.forEach((team, ti) => {
    const row = document.createElement('tr');
    const nameTd = document.createElement('td');
    nameTd.className = 'scoreboard-team-name';
    nameTd.textContent = team.name;

    const inputsHtml = [];
    const rowScores = scores[ti] || [];
    for (let ri = 0; ri < rounds; ri++) {
      const v = rowScores[ri];
      const val = v === null || v === undefined ? '' : String(v);
      inputsHtml.push(`
        <td class="scoreboard-td-round">
          <input type="number" min="0" step="1" class="score-round-input" inputmode="numeric"
            data-team-index="${team.index}" data-round="${ri}" value="${escapeAttr(val)}" placeholder="—" />
        </td>
      `);
    }

    row.innerHTML = `
      ${nameTd.outerHTML}
      ${inputsHtml.join('')}
      <td class="scoreboard-total" data-total-for="${team.index}">0</td>
      <td class="scoreboard-place" data-place-for="${team.index}">—</td>
    `;
    row.dataset.teamIndex = String(team.index);
    tbody.appendChild(row);
  });

  refreshScoreboardTotals();
}

function onScoreboardInput(ev) {
  const el = ev.target;
  if (!el || !el.classList || !el.classList.contains('score-round-input')) return;
  refreshScoreboardTotals();
}

function parseRoundValue(raw) {
  if (raw === '' || raw === null || raw === undefined) return null;
  const n = Number(raw);
  if (!Number.isFinite(n) || Number.isNaN(n)) return null;
  return Math.trunc(n);
}

function readScoresMatrixFromDom() {
  const tbody = document.getElementById('scoreboard-tbody');
  if (!tbody) return { matrix: [], complete: false };

  const rows = tbody.querySelectorAll('tr[data-team-index]');
  const matrix = [];
  let complete = rows.length > 0;

  rows.forEach((tr) => {
    const inputs = tr.querySelectorAll('.score-round-input');
    const row = [];
    inputs.forEach((inp) => {
      const v = parseRoundValue(inp.value);
      row.push(v);
      if (v === null) complete = false;
    });
    matrix.push(row);
  });

  return { matrix, complete };
}

function rowSum(row) {
  return row.reduce((acc, v) => acc + (v === null ? 0 : v), 0);
}

function computePlaces(totals) {
  const n = totals.length;
  const placeByIndex = new Array(n).fill(null);
  const indexed = totals.map((t, i) => ({ t, i }));
  indexed.sort((a, b) => b.t - a.t);
  let rank = 1;
  let k = 0;
  while (k < indexed.length) {
    const score = indexed[k].t;
    let span = 0;
    while (k + span < indexed.length && indexed[k + span].t === score) span++;
    for (let j = 0; j < span; j++) {
      placeByIndex[indexed[k + j].i] = rank;
    }
    rank += span;
    k += span;
  }
  return placeByIndex;
}

function refreshScoreboardTotals() {
  const tbody = document.getElementById('scoreboard-tbody');
  const { matrix, complete } = readScoresMatrixFromDom();
  const totals = matrix.map(rowSum);
  const places = complete && totals.length ? computePlaces(totals) : null;

  const rows = tbody ? tbody.querySelectorAll('tr[data-team-index]') : [];
  rows.forEach((tr, ti) => {
    const totalCell = tr.querySelector('.scoreboard-total');
    const placeCell = tr.querySelector('.scoreboard-place');
    if (totalCell) totalCell.textContent = String(totals[ti] ?? 0);
    if (placeCell) placeCell.textContent = places ? String(places[ti]) : '—';
  });
}

function saveScoreboard() {
  if (scoreboardEventId === null) {
    alert('Сначала выберите игру.');
    return;
  }
  const { matrix } = readScoresMatrixFromDom();
  const tbody = document.getElementById('scoreboard-tbody');
  if (tbody && !tbody.querySelector('tr[data-team-index]')) {
    alert('Нет строк для сохранения.');
    return;
  }

  fetch(`/api/admin/games/${scoreboardEventId}/scoreboard`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scores: matrix }),
  })
    .then((r) => r.json().then((body) => ({ ok: r.ok, body })))
    .then(({ ok, body }) => {
      if (!ok || body.status === 'error') {
        alert(body.message || 'Не удалось сохранить');
        return;
      }
      alert('Сохранено.');
    })
    .catch(() => alert('Ошибка сети'));
}

// --- Модалка события и прочее ---

function openCreateEventModal() {
  editingEventId = null;
  document.getElementById('modalTitle').textContent = 'Создать событие';
  document.getElementById('eventForm').reset();
  removePhoto();
  document.getElementById('eventModal').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function editEvent(id) {
  if (!statsData || !statsData.events[id]) return;

  editingEventId = id;
  const event = statsData.events[id];
  document.getElementById('modalTitle').textContent = 'Редактировать событие';

  document.querySelector('input[name="title"]').value = event.title;
  document.querySelector('input[name="date"]').value = event.date;
  document.querySelector('input[name="time"]').value = event.time;
  document.querySelector('input[name="location"]').value = event.location;
  document.querySelector('input[name="max_seats"]').value = event.max_seats;
  document.querySelector('input[name="price"]').value = event.price;
  const catSelect = document.querySelector('select[name="category"]');
  if (catSelect && event.category) catSelect.value = event.category;

  document.getElementById('eventModal').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeEventModal(e) {
  if (e && e.target !== document.getElementById('eventModal')) return;
  document.getElementById('eventModal').classList.remove('show');
  document.body.style.overflow = '';
}

function deleteEvent(id) {
  if (!confirm('Вы уверены? Это действие нельзя отменить!')) return;
  fetch(`/api/events/${id}`, {
    method: 'DELETE',
    credentials: 'same-origin',
  })
    .then((r) => r.json())
    .then((result) => {
      if (result.status === 'success') {
        loadStats();
      } else {
        alert(result.message || 'Ошибка');
      }
    })
    .catch(() => alert('Ошибка сети'));
}

function closeEvent(id) {
  if (confirm('Закрыть событие досрочно? Новые регистрации будут невозможны.')) {
    fetch(`/api/events/${id}`, {
      method: 'DELETE',
      credentials: 'same-origin',
    })
      .then((r) => r.json())
      .then((result) => {
        if (result.status === 'success') {
          loadStats();
        } else {
          alert(result.message || 'Ошибка');
        }
      })
      .catch(() => alert('Ошибка сети'));
  }
}

function previewPhoto(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    const preview = document.getElementById('photoPreview');
    const uploadArea = document.getElementById('photoUploadArea');
    const previewImg = document.getElementById('previewImg');

    previewImg.src = e.target.result;
    uploadArea.style.display = 'none';
    preview.style.display = 'block';
  };
  reader.readAsDataURL(file);
}

function removePhoto() {
  document.getElementById('eventPhoto').value = '';
  document.getElementById('photoPreview').style.display = 'none';
  document.getElementById('photoUploadArea').style.display = 'block';
  document.getElementById('previewImg').src = '';
}

function submitEventForm() {
  const form = document.getElementById('eventForm');
  if (
    !form.title.value ||
    !form.date.value ||
    !form.time.value ||
    !form.location.value ||
    !form.max_seats.value ||
    !form.price.value
  ) {
    alert('Пожалуйста, заполните все обязательные поля!');
    return;
  }

  const data = {
    title: form.title.value,
    category: form.category.value,
    date: form.date.value,
    time: form.time.value,
    location: form.location.value,
    max_seats: parseInt(form.max_seats.value, 10),
    price: parseInt(form.price.value, 10),
    description: form.rules.value,
  };

  const url = editingEventId ? `/api/events/${editingEventId}` : '/api/events';
  const method = editingEventId ? 'PUT' : 'POST';

  fetch(url, {
    method: method,
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
    .then((r) => r.json())
    .then((result) => {
      if (result.status === 'success') {
        closeEventModal();
        loadStats();
      } else {
        alert(result.message || 'Ошибка');
      }
    })
    .catch(() => alert('Ошибка сети'));
}

function exportReport(format) {
  const formats = {
    pdf: 'PDF',
    excel: 'Excel',
    csv: 'CSV',
  };
  alert(`Начинаем экспорт в ${formats[format]}...`);
}

function formatNumber(num) {
  return new Intl.NumberFormat('ru-RU').format(num);
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeAttr(s) {
  return escapeHtml(s).replace(/'/g, '&#39;');
}

function initializePhotoUpload() {
  const uploadArea = document.getElementById('photoUploadArea');
  const fileInput = document.getElementById('eventPhoto');

  if (!uploadArea || !fileInput) return;

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((eventName) => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  ['dragenter', 'dragover'].forEach((eventName) => {
    uploadArea.addEventListener(eventName, highlight, false);
  });

  ['dragleave', 'drop'].forEach((eventName) => {
    uploadArea.addEventListener(eventName, unhighlight, false);
  });

  uploadArea.addEventListener('drop', handleDrop, false);

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    const eventModal = document.getElementById('eventModal');
    if (eventModal && eventModal.classList.contains('show')) {
      closeEventModal();
      return;
    }
    const gameModal = document.getElementById('gameSelectModal');
    if (gameModal && gameModal.classList.contains('show')) {
      closeGameSelectModal();
    }
  });
}

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function highlight() {
  document.getElementById('photoUploadArea').style.borderColor = 'rgba(245,197,24,0.8)';
  document.getElementById('photoUploadArea').style.backgroundColor = 'rgba(245,197,24,0.1)';
}

function unhighlight() {
  document.getElementById('photoUploadArea').style.borderColor = 'rgba(245,197,24,0.3)';
  document.getElementById('photoUploadArea').style.backgroundColor = 'rgba(245,197,24,0.02)';
}

function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;

  if (files.length > 0) {
    document.getElementById('eventPhoto').files = files;
    previewPhoto({ target: { files: files } });
  }
}

function toggleCabinetDropdown(event) {
  event.stopPropagation();
  const dropdown = document.getElementById('cabinetDropdown') || document.getElementById('cabinetDropdownMobile');
  if (dropdown) {
    dropdown.classList.toggle('show');
  }
}

document.addEventListener('click', function (e) {
  const dropdowns = document.querySelectorAll('.cabinet-dropdown');
  dropdowns.forEach(function(dropdown) {
    if (!dropdown.parentElement.contains(e.target)) {
      dropdown.classList.remove('show');
    }
  });
});

document.addEventListener('keydown', function (event) {
  if (event.key === 'Escape') {
    const dropdowns = document.querySelectorAll('.cabinet-dropdown');
    dropdowns.forEach(function(dropdown) {
      dropdown.classList.remove('show');
    });
  }
});
