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

function logout() {
  window.location.href = '/logout';
}
