-- Создание базы данных
CREATE DATABASE IF NOT EXISTS ocr_translator 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Использование базы данных
USE ocr_translator;

-- Создание таблицы переводов
CREATE TABLE IF NOT EXISTS translations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    image_filename VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Пример данных для тестирования (опционально)
-- INSERT INTO translations (original_text, translated_text, image_filename) VALUES 
-- ('Hello World', 'Привет Мир', 'test_image.jpg'),
-- ('This is a test', 'Это тест', 'test_image2.jpg');