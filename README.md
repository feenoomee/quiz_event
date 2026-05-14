# TLTQUIZ - Quiz Event Management Platform

A Flask-based web application for managing bar quiz events in Tolyatti.

## 📁 Project Structure

```
quiz_event/
├── app.py                 # Тонкая обёртка: create_app() из пакета quiz_app
├── run.py                 # Запуск: from app import app
├── quiz_app/              # Логика Flask (макет + демо)
│   ├── __init__.py        # create_app(), пути к templates/ и static/
│   ├── config.py          # SECRET_KEY и задел под БД (комментарии)
│   └── routes.py          # Маршруты и демо-данные users/events
├── requirements.txt
├── static/
│   ├── css/               # base.css (общее), home.css, profile.css, admin.css; style.css — не подключён
│   ├── js/                # profile.js, admin.js
│   └── script.js          # Главная: календарь, слайдер, чат, модалки
├── templates/
│   ├── layout/base.html   # Шапка, main, футер
│   ├── pages/             # index, profile, admin
│   └── partials/          # footer, блок аватара
└── media/                 # Картинки и ассеты
```

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
python run.py
```

The app will be available at `http://localhost:5000`

## 📋 Features

### Frontend
- **Landing Page** (`templates/pages/index.html`)
  - Hero section with featured event
  - Statistics section
  - Event slider with past games
  - Events calendar with filtering
  - Registration modal
  - Chat widget
  - Footer with contacts

- **Styling** (`static/css/base.css` + страничные `home.css` / `profile.css` / `admin.css`)
  - Dark theme with yellow accents
  - Fully responsive design
  - CSS variables for theming
  - Smooth animations and transitions

- **Interactivity** (`static/script.js`)
  - Event filtering
  - Slider carousel
  - Modal windows (registration, auth)
  - Chat interface
  - Fade-in animations on scroll
  - Counter animations

### Backend
- **Flask Routes**
  - `GET /` - Renders landing page
  - `POST /api/register` - Team registration endpoint (placeholder)

## 🎨 Design System

### Color Palette
- Primary Yellow: `#f5c518`
- Light Yellow: `#ffe566`
- Dark Yellow: `#c9a000`
- Background: `#0d0d0d`
- Cards: `#1e1e1e`
- Text: `#f5f5f5`

### Responsive Breakpoints
- Desktop: 1200px+
- Tablet: 768px - 1024px
- Mobile: Below 768px
- Small Mobile: Below 480px

## 📝 Events Data

Currently using sample data with 6 events:
1. Кино и сериалы 2025 🎬
2. Угадай мелодию — Русские хиты 🎵
3. ТЛТКВИЗ — Обо всём 🧠
4. Эйнштейн Party — SHOW TIME 🎭
5. Мир кино — СССР и 90-е 📽
6. Музыкальный марафон 🎸

Categories: cinema, music, classic, show

## 🔧 Customization

### Update Events
Edit the `eventsData` array in `static/script.js` to add/modify events.

### Update Styling
Modify CSS variables at the top of `static/css/base.css` (и при необходимости страничных CSS) for theming.

### Add New Routes
Edit `app.py` to add new Flask routes and endpoints.

## 🚧 Development Notes

- Frontend is fully static, no backend integration for chat/modals yet
- Registration modal shows success state but doesn't actually submit
- Auth modal is a placeholder for future implementation
- Event data is hardcoded in JavaScript (should be moved to database)

## 📚 Technologies Used

- **Backend**: Flask 3.0.3, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Architecture**: MVC (Model-View-Controller)

## 🤝 Next Steps

1. Connect registration form to backend
2. Set up database for events and registrations
3. Implement user authentication
4. Add admin panel
5. Implement chat functionality with backend
6. Add email notifications

