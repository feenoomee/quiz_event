// Admin panel JavaScript
let chartsInstances = {};
let statsData = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  loadStats();
  initializePhotoUpload();
  observeFadeInElements();
});

// Observe fade-in elements
function observeFadeInElements() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
}

// Load statistics from API
function loadStats() {
  fetch('/api/stats')
    .then(response => response.json())
    .then(data => {
      statsData = data;
      updateQuickStats(data);
      populateEventsTable(data.events);
      populateDetailedStats(data.events);
      populateTopEvents(data.top_events);
      initializeCharts(data);
    })
    .catch(error => console.error('Error loading stats:', error));
}

// Update quick stats boxes
function updateQuickStats(data) {
  document.getElementById('total-events').textContent = data.total_events;
  document.getElementById('total-revenue').textContent = '₽' + formatNumber(data.total_revenue);
  document.getElementById('total-attendees').textContent = data.total_attendees;
  document.getElementById('occupancy-rate').textContent = data.occupancy_rate + '%';
}

// Populate events table
function populateEventsTable(events) {
  const tbody = document.getElementById('events-tbody');
  tbody.innerHTML = '';
  
  for (const [id, event] of Object.entries(events)) {
    const occupancy = Math.round((event.registered / event.max_seats) * 100);
    const row = document.createElement('tr');
    row.innerHTML = `
      <td><strong>${event.title}</strong></td>
      <td>${event.date}, ${event.time}</td>
      <td>${event.location}</td>
      <td>${event.registered}/${event.max_seats}</td>
      <td>${occupancy}%</td>
      <td>
        <button class="btn-edit" onclick="editEvent(${id})">✏️ Редакт.</button>
        <button class="btn-delete" onclick="deleteEvent(${id})">🗑️ Удал.</button>
        <button class="btn-close" onclick="closeEvent(${id})">⊗ Закрыть</button>
      </td>
    `;
    tbody.appendChild(row);
  }
}

// Populate detailed statistics table
function populateDetailedStats(events) {
  const tbody = document.getElementById('detailed-stats-tbody');
  tbody.innerHTML = '';
  
  for (const [id, event] of Object.entries(events)) {
    const revenue = event.registered * event.price;
    const row = document.createElement('tr');
    row.innerHTML = `
      <td><strong>${event.title}</strong></td>
      <td>${event.registered}</td>
      <td>${event.max_seats}</td>
      <td>₽${formatNumber(revenue)}</td>
      <td>₽${event.price}</td>
      <td><span class="status-active">✓ Активно</span></td>
    `;
    tbody.appendChild(row);
  }
}

// Populate top events list
function populateTopEvents(topEvents) {
  const container = document.getElementById('top-events-list');
  container.innerHTML = '';
  
  topEvents.forEach((event, index) => {
    const item = document.createElement('div');
    item.className = 'top-event-item';
    item.innerHTML = `
      <div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:1.5rem;">${['🥇', '🥈', '🥉'][index]}</span>
          <div class="top-event-title">${event.title}</div>
        </div>
      </div>
      <div class="top-event-count">${event.registered} уч.</div>
    `;
    container.appendChild(item);
  });
}

// Initialize charts
function initializeCharts(data) {
  initAttendanceChart(data.attendance_data);
  initRevenueChart(data.revenue_data);
  initDistributionChart(data.event_distribution);
}

// Attendance Chart
function initAttendanceChart(attendanceData) {
  const ctx = document.getElementById('attendanceChart').getContext('2d');
  
  // Destroy old chart if exists
  if (chartsInstances.attendance) {
    chartsInstances.attendance.destroy();
  }
  
  chartsInstances.attendance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: attendanceData.labels,
      datasets: [{
        label: 'Посещаемость',
        data: attendanceData.values,
        borderColor: '#f5c518',
        backgroundColor: 'rgba(245,197,24,0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#f5c518',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#333', drawBorder: false },
          ticks: { color: '#888' }
        },
        x: {
          grid: { color: '#333', drawBorder: false },
          ticks: { color: '#888' }
        }
      }
    }
  });
}

// Revenue Chart
function initRevenueChart(revenueData) {
  const ctx = document.getElementById('revenueChart').getContext('2d');
  
  // Destroy old chart if exists
  if (chartsInstances.revenue) {
    chartsInstances.revenue.destroy();
  }
  
  chartsInstances.revenue = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: revenueData.labels,
      datasets: [{
        label: 'Доходы (₽)',
        data: revenueData.values,
        backgroundColor: '#f5c518',
        borderColor: '#c9a000',
        borderWidth: 1,
        borderRadius: 8,
        hoverBackgroundColor: '#ffe566'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#333', drawBorder: false },
          ticks: { color: '#888' }
        },
        x: {
          grid: { color: '#333', drawBorder: false },
          ticks: { color: '#888' }
        }
      }
    }
  });
}

// Distribution Chart (Pie)
function initDistributionChart(distributionData) {
  const ctx = document.getElementById('distributionChart').getContext('2d');
  
  // Destroy old chart if exists
  if (chartsInstances.distribution) {
    chartsInstances.distribution.destroy();
  }
  
  chartsInstances.distribution = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: distributionData.labels,
      datasets: [{
        data: distributionData.values,
        backgroundColor: [
          '#f5c518',
          '#ffe566',
          '#c9a000',
          '#ffaa00'
        ],
        borderColor: '#1e1e1e',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#888', padding: 16 }
        }
      }
    }
  });
}

// Update stats by period
function updateStats() {
  const period = document.getElementById('stats-period').value;
  console.log('Updating stats for period:', period);
  
  // Trigger chart redraw
  setTimeout(() => {
    if (chartsInstances.attendance) chartsInstances.attendance.resize();
    if (chartsInstances.revenue) chartsInstances.revenue.resize();
    if (chartsInstances.distribution) chartsInstances.distribution.resize();
  }, 100);
}

// Modal functions
function openCreateEventModal() {
  document.getElementById('modalTitle').textContent = 'Создать событие';
  document.getElementById('eventForm').reset();
  removePhoto();
  document.getElementById('eventModal').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function editEvent(id) {
  if (!statsData || !statsData.events[id]) return;
  
  const event = statsData.events[id];
  document.getElementById('modalTitle').textContent = 'Редактировать событие';
  
  document.querySelector('input[name="title"]').value = event.title;
  document.querySelector('input[name="date"]').value = event.date;
  document.querySelector('input[name="time"]').value = event.time;
  document.querySelector('input[name="location"]').value = event.location;
  document.querySelector('input[name="max_seats"]').value = event.max_seats;
  document.querySelector('input[name="price"]').value = event.price;
  
  document.getElementById('eventModal').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeEventModal(e) {
  if (e && e.target !== document.getElementById('eventModal')) return;
  document.getElementById('eventModal').classList.remove('show');
  document.body.style.overflow = '';
}

function deleteEvent(id) {
  if (confirm('Вы уверены? Это действие нельзя отменить!')) {
    console.log('Deleting event:', id);
    // API call here
    loadStats();
  }
}

function closeEvent(id) {
  if (confirm('Закрыть событие досрочно? Новые регистрации будут невозможны.')) {
    console.log('Closing event:', id);
    // API call here
    loadStats();
  }
}

// Photo upload functions
function previewPhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = function(e) {
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
  const formData = new FormData(form);
  
  // Validate form
  if (!form.title.value || !form.date.value || !form.time.value || 
      !form.location.value || !form.max_seats.value || !form.price.value) {
    alert('Пожалуйста, заполните все обязательные поля!');
    return;
  }
  
  console.log('Submitting event form with data:', {
    title: form.title.value,
    date: form.date.value,
    time: form.time.value,
    location: form.location.value,
    max_seats: form.max_seats.value,
    price: form.price.value,
    category: form.category.value,
    rules: form.rules.value,
    photo: document.getElementById('eventPhoto').files[0]
  });
  
  // Here would be the API call to save event
  closeEventModal();
  loadStats();
}

// Export functions
function exportReport(format) {
  const formats = {
    'pdf': 'PDF',
    'excel': 'Excel',
    'csv': 'CSV'
  };
  alert(`Начинаем экспорт в ${formats[format]}...`);
  // Here would be the actual export logic
}

// Utility function to format numbers
function formatNumber(num) {
  return new Intl.NumberFormat('ru-RU').format(num);
}

// Initialize photo upload with drag & drop
function initializePhotoUpload() {
  const uploadArea = document.getElementById('photoUploadArea');
  const fileInput = document.getElementById('eventPhoto');
  
  if (!uploadArea || !fileInput) return;
  
  // Prevent default drag behaviors
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });
  
  // Highlight drop area when item is dragged over it
  ['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, highlight, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, unhighlight, false);
  });
  
  // Handle dropped files
  uploadArea.addEventListener('drop', handleDrop, false);
  
  // Close modal on ESC key
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      const modal = document.getElementById('eventModal');
      if (modal && modal.classList.contains('show')) {
        closeEventModal();
      }
    }
  });
}

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function highlight(e) {
  document.getElementById('photoUploadArea').style.borderColor = 'rgba(245,197,24,0.8)';
  document.getElementById('photoUploadArea').style.backgroundColor = 'rgba(245,197,24,0.1)';
}

function unhighlight(e) {
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