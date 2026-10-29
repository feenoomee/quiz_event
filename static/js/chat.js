(() => {
  'use strict';
  const root = document.querySelector('[data-game-chat]');
  if (!root) return;
  const panel = root.querySelector('.game-chat-panel');
  const toggle = root.querySelector('[data-chat-toggle]');
  const messages = root.querySelector('[data-chat-messages]');
  const status = root.querySelector('[data-chat-status]');
  const history = root.querySelector('[data-chat-history]');
  const form = root.querySelector('[data-chat-form]');
  const input = form?.querySelector('textarea');
  const endpoint = root.dataset.endpoint;
  const rendered = new Map();
  let latest = 0;
  let oldest = 0;
  let loaded = false;
  let fetching = false;
  let sending = false;
  let token = '';
  let timer;
  let sendError = '';

  function setStatus(text = '', error = false) {
    status.textContent = text;
    status.dataset.error = String(error);
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function render(rows) {
    for (const message of rows) {
      if (rendered.has(message.id)) continue;
      const own = String(message.user.id) === root.dataset.userId;
      const article = element('article', `game-chat-message${own ? ' game-chat-message--own' : ''}`);
      const initials = message.user.name.split(/\s+/).map(part => part[0]).slice(0, 2).join('');
      const avatar = element('div', 'game-chat-avatar', initials);
      avatar.setAttribute('aria-hidden', 'true');
      if (message.user.avatar) {
        const img = document.createElement('img');
        img.src = message.user.avatar;
        img.alt = '';
        img.loading = 'lazy';
        img.addEventListener('error', () => avatar.replaceChildren(document.createTextNode(initials)), { once: true });
        avatar.replaceChildren(img);
      }
      const body = element('div', 'game-chat-message-body');
      const meta = element('div', 'game-chat-meta');
      meta.append(element('strong', 'game-chat-name', message.user.name));
      if (message.user.is_admin) meta.append(element('span', 'game-chat-admin', 'Администратор'));
      const date = new Date(message.created_at);
      const time = element('time', 'game-chat-time', date.toLocaleString('ru-RU', {
        day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
      }));
      time.dateTime = message.created_at;
      time.title = date.toLocaleString('ru-RU');
      meta.append(time);
      body.append(meta, element('p', 'game-chat-text', message.text));
      article.append(avatar, body);
      const nextId = [...rendered.keys()].filter(id => id > message.id).sort((a, b) => a - b)[0];
      messages.insertBefore(article, nextId === undefined ? null : rendered.get(nextId));
      rendered.set(message.id, article);
      oldest = oldest ? Math.min(oldest, message.id) : message.id;
    }
  }

  function active() {
    return !panel.hidden && !root.hidden && !document.hidden;
  }

  function schedule(delay = 3000) {
    clearTimeout(timer);
    if (active()) timer = setTimeout(() => load(), delay);
  }

  async function load(older = false) {
    if (fetching || !active()) return;
    fetching = true;
    history.disabled = true;
    const nearBottom = messages.scrollHeight - messages.scrollTop - messages.clientHeight < 80;
    const previousHeight = messages.scrollHeight;
    const wasLoaded = loaded;
    try {
      const query = older ? `?before=${oldest}` : loaded ? `?after=${latest}` : '';
      const response = await fetch(endpoint + query, { cache: 'no-store', credentials: 'same-origin' });
      if (!response.ok) throw new Error('Не удалось загрузить чат. Повторим автоматически.');
      const data = await response.json();
      token = data.csrf_token;
      render(data.messages);
      if (!older) {
        if (data.messages.length) latest = data.messages[data.messages.length - 1].id;
        loaded = true;
      }
      if (older || !wasLoaded) history.hidden = !data.has_more;
      if (older) messages.scrollTop += messages.scrollHeight - previousHeight;
      else if (!wasLoaded || nearBottom) messages.scrollTop = messages.scrollHeight;
      setStatus(sendError || (rendered.size ? '' : 'Пока тихо. Начните общение первым!'), Boolean(sendError));
      // Catch up in bounded batches without skipping messages received while offline.
      schedule(!older && wasLoaded && data.has_more ? 100 : 3000);
    } catch (error) {
      setStatus(error.message || 'Нет связи. Повторим загрузку автоматически.', true);
      schedule(6000);
    } finally {
      fetching = false;
      history.disabled = false;
    }
  }

  function setOpen(open) {
    panel.hidden = !open;
    toggle?.setAttribute('aria-expanded', String(open));
    if (open) {
      load();
      input?.focus();
    } else {
      clearTimeout(timer);
    }
  }

  toggle?.addEventListener('click', () => setOpen(panel.hidden));
  root.querySelector('[data-chat-close]')?.addEventListener('click', () => {
    setOpen(false);
    toggle.focus();
  });
  root.addEventListener('keydown', event => {
    if (event.key === 'Escape' && toggle && !panel.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });
  history.addEventListener('click', () => load(true));
  input?.addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      form.requestSubmit();
    }
  });
  form?.addEventListener('submit', async event => {
    event.preventDefault();
    if (sending || !input.value.trim()) return;
    if (!loaded || !token) {
      setStatus('Дождитесь подключения к чату и повторите отправку.', true);
      load();
      return;
    }
    const draft = input.value;
    sending = true;
    form.querySelector('button').disabled = true;
    sendError = '';
    setStatus('Отправляем…');
    try {
      const response = await fetch(endpoint, {
        method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
        body: JSON.stringify({ text: draft.trim() })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || 'Не удалось отправить сообщение');
      render([data.message]);
      // Only GET advances the cursor: a simultaneous reply must not be skipped.
      if (input.value === draft) input.value = '';
      messages.scrollTop = messages.scrollHeight;
      setStatus();
      load();
    } catch (error) {
      sendError = error.message || 'Нет связи. Сообщение не отправлено, повторите попытку.';
      setStatus(sendError, true);
    } finally {
      sending = false;
      form.querySelector('button').disabled = false;
    }
  });

  // Existing forms use open, active and show for their modal overlays.
  const modalSelector = '.modal-overlay.open, .modal-overlay.show, .modal-overlay.active, .modal-overlay-custom.active, dialog[open], [aria-modal="true"]';
  function syncModals() {
    const blocked = Boolean(document.querySelector(modalSelector));
    const changed = root.hidden !== blocked;
    root.hidden = blocked;
    if (blocked) clearTimeout(timer);
    else if (changed && active()) load();
  }
  new MutationObserver(syncModals).observe(document.body, {
    subtree: true, attributes: true, attributeFilter: ['class', 'open', 'aria-modal'], childList: true
  });
  document.addEventListener('visibilitychange', () => {
    clearTimeout(timer);
    if (active()) load();
  });
  window.addEventListener('online', () => { if (active()) load(); });
  syncModals();
  if (active()) load();
  if (new URLSearchParams(location.search).has('chat_login') && document.getElementById('authModal')) {
    window.openAuthModal();
  }
})();
