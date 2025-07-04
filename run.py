#!/usr/bin/env python3
"""
Скрипт для запуска OCR Переводчика
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Проверка установленных зависимостей"""
    try:
        import flask
        import easyocr
        import google.generativeai
        import pymysql
        import PIL
        print("✓ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"✗ Отсутствует зависимость: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False

def check_env_file():
    """Проверка файла конфигурации"""
    env_file = Path('.env')
    if not env_file.exists():
        print("✗ Файл .env не найден")
        print("Скопируйте .env.example в .env и заполните параметры")
        return False
    
    # Проверяем основные переменные
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_gemini_api_key_here' in content:
            print("✗ Не настроен GEMINI_API_KEY в файле .env")
            return False
        if 'your_database_password' in content:
            print("⚠ Возможно не настроен пароль базы данных в файле .env")
    
    print("✓ Файл .env настроен")
    return True

def check_database():
    """Проверка подключения к базе данных"""
    try:
        from dotenv import load_dotenv
        import pymysql
        
        load_dotenv()
        
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'ocr_translator'),
            charset='utf8mb4'
        )
        connection.close()
        print("✓ Подключение к базе данных успешно")
        return True
    except Exception as e:
        print(f"✗ Ошибка подключения к базе данных: {e}")
        print("Убедитесь, что MySQL запущен и база данных создана")
        return False

def install_dependencies():
    """Установка зависимостей"""
    print("Установка зависимостей...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Зависимости установлены")
        return True
    except subprocess.CalledProcessError:
        print("✗ Ошибка установки зависимостей")
        return False

def setup_database():
    """Настройка базы данных"""
    print("Настройка базы данных...")
    db_file = Path('database.sql')
    if not db_file.exists():
        print("✗ Файл database.sql не найден")
        return False
    
    print("Выполните команду для создания базы данных:")
    print(f"mysql -u root -p < {db_file}")
    return True

def run_app():
    """Запуск приложения"""
    print("Запуск OCR Переводчика...")
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"✗ Ошибка запуска: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 OCR Переводчик - Система запуска")
    print("=" * 50)
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'install':
            install_dependencies()
            return
        elif command == 'setup-db':
            setup_database()
            return
        elif command == 'check':
            print("Проверка системы...")
            checks = [
                check_requirements(),
                check_env_file(),
                check_database()
            ]
            if all(checks):
                print("\n✓ Система готова к запуску!")
            else:
                print("\n✗ Требуется настройка системы")
            return
    
    # Полная проверка и запуск
    print("Проверка системы...")
    
    # Проверяем зависимости
    if not check_requirements():
        response = input("Установить зависимости? (y/n): ")
        if response.lower() == 'y':
            if not install_dependencies():
                return
        else:
            return
    
    # Проверяем конфигурацию
    if not check_env_file():
        return
    
    # Проверяем базу данных
    if not check_database():
        print("Настройте базу данных с помощью: python run.py setup-db")
        return
    
    print("\n🎉 Все проверки пройдены! Запускаем приложение...")
    print("Приложение будет доступно по адресу: http://localhost:5000")
    print("Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    run_app()

if __name__ == '__main__':
    main()