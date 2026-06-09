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
