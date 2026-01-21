# Threads Pain Scanner

🔍 Инструмент для маркетинговых исследований — поиск болей и идей для приложений через анализ постов в Threads.

## Возможности

- 🔎 Поиск по ключевым словам в Threads
- 🤖 AI-анализ через локальную нейросеть (Ollama + Qwen 2.5)
- 😤 Выявление болей и проблем пользователей
- 💡 Генерация идей для новых приложений
- 📊 Красивый веб-дашборд
- 📥 Экспорт в JSON/CSV

## Требования

- Python 3.10+
- [Ollama](https://ollama.ai/)
- (Опционально) Аккаунт разработчика Meta для реального API

## Быстрый старт

### 1. Установка зависимостей

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Установка Ollama и модели

```powershell
# Установка Ollama
winget install Ollama.Ollama

# Скачивание модели (5GB)
ollama pull qwen2.5:7b
```

### 3. Запуск

```powershell
cd backend
python main.py
```

Откройте http://localhost:8000 в браузере.

## Настройка Threads API (опционально)

Для поиска по реальным постам (не demo-данным):

1. Создайте приложение на [developers.facebook.com](https://developers.facebook.com)
2. Добавьте продукт "Threads API"
3. Получите Access Token
4. Создайте файл `backend/.env`:

```env
THREADS_ACCESS_TOKEN=your_token_here
```

## Использование

1. Введите ключевые слова (например: "продуктивность", "выгорание", "тайм-менеджмент")
2. Нажмите "Найти и проанализировать"
3. Изучите найденные боли, потребности и идеи
4. Экспортируйте результаты в JSON или CSV

## Структура проекта

```
threads-pain-scanner/
├── backend/
│   ├── main.py              # FastAPI сервер
│   ├── threads_client.py    # Клиент Threads API
│   ├── ollama_client.py     # Интеграция с Ollama
│   ├── analyzer.py          # Логика анализа
│   ├── models.py            # Pydantic модели
│   └── requirements.txt     # Зависимости
├── frontend/
│   ├── index.html           # Веб-интерфейс
│   ├── styles.css           # Стили
│   └── app.js               # JavaScript
└── README.md
```

## Лицензия

MIT
