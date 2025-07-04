# Быстрый запуск OCR Переводчика

## 🚀 Быстрая установка (5 минут)

### 1. Подготовка
```bash
# Клонируйте проект
git clone <repository-url>
cd ocr-translator

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка конфигурации
```bash
# Скопируйте файл конфигурации
cp .env.example .env

# Отредактируйте .env файл
nano .env
```

**Обязательно установите:**
- `GEMINI_API_KEY` - получите на https://aistudio.google.com/app/apikey
- `DB_PASSWORD` - ваш пароль MySQL

### 3. Настройка базы данных
```bash
# Создайте базу данных
mysql -u root -p < database.sql
```

### 4. Запуск
```bash
# Автоматическая проверка и запуск
python run.py

# Или прямой запуск
python app.py
```

**Приложение доступно:** http://localhost:5000

---

## 🐳 Запуск через Docker (альтернатива)

```bash
# Установите GEMINI_API_KEY в .env файл
echo "GEMINI_API_KEY=ваш_ключ" > .env

# Запустите контейнеры
docker-compose up -d

# Приложение доступно на http://localhost:5000
```

---

## 📋 Команды для run.py

```bash
python run.py           # Полная проверка и запуск
python run.py check     # Только проверка системы
python run.py install   # Установка зависимостей
python run.py setup-db  # Инструкции по настройке БД
```

---

## ⚡ Проверка работы

1. Откройте http://localhost:5000
2. Перетащите изображение с английским текстом
3. Дождитесь обработки
4. Скачайте перевод

**Готово! 🎉**