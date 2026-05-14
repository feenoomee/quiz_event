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

  input.addEventListener('change', function () {
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
    if (objectUrl) URL.revokeObjectURL(objectUrl);
    objectUrl = URL.createObjectURL(file);
    img.src = objectUrl;
    label.classList.add('has-image');
    removeBtn.hidden = false;
  });

  removeBtn.addEventListener('click', function (e) {
    e.preventDefault();
    clearPreview();
  });
})();
