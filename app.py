import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import easyocr
import google.generativeai as genai
import pymysql
from PIL import Image
import io
import base64
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
CORS(app)

# Конфигурация
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB максимальный размер файла
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Создаем папку для загрузок
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Инициализация EasyOCR (английский язык)
ocr_reader = easyocr.Reader(['en'])

# Инициализация Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'ocr_translator'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def init_database():
    """Инициализация базы данных"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS translations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    original_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    image_filename VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Файл не найден'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Недопустимый формат файла. Разрешены: JPG, PNG, JPEG'}), 400
        
        # Сохраняем файл
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Открываем изображение для OCR
        image = Image.open(filepath)
        
        # Распознавание текста
        results = ocr_reader.readtext(filepath)
        extracted_text = ' '.join([result[1] for result in results])
        
        if not extracted_text.strip():
            return jsonify({'error': 'Текст на изображении не обнаружен'}), 400
        
        # Перевод текста
        prompt = f"Переведи следующий английский текст на русский язык. Переведи только текст без дополнительных комментариев:\n\n{extracted_text}"
        response = model.generate_content(prompt)
        translated_text = response.text
        
        # Сохранение в базу данных
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO translations (original_text, translated_text, image_filename) VALUES (%s, %s, %s)",
                (extracted_text, translated_text, filename)
            )
            translation_id = cursor.lastrowid
        connection.commit()
        connection.close()
        
        # Конвертируем изображение в base64 для превью
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'id': translation_id,
            'original_text': extracted_text,
            'translated_text': translated_text,
            'image_preview': f"data:image/png;base64,{img_str}",
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка обработки: {str(e)}'}), 500

@app.route('/download/<int:translation_id>')
def download_translation(translation_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT translated_text, created_at FROM translations WHERE id = %s", (translation_id,))
            result = cursor.fetchone()
        connection.close()
        
        if not result:
            return jsonify({'error': 'Перевод не найден'}), 404
        
        # Создаем временный файл с переводом
        filename = f"translation_{translation_id}.txt"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Дата перевода: {result['created_at']}\n\n")
            f.write("Переведенный текст:\n")
            f.write(result['translated_text'])
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Ошибка скачивания: {str(e)}'}), 500

@app.route('/history')
def get_history():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, original_text, translated_text, created_at FROM translations ORDER BY created_at DESC LIMIT 20"
            )
            results = cursor.fetchall()
        connection.close()
        
        return jsonify({'history': results})
        
    except Exception as e:
        return jsonify({'error': f'Ошибка получения истории: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Файл слишком большой. Максимальный размер: 5 МБ'}), 413

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)