// Глобальные переменные
let currentTranslationId = null;

// DOM элементы
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectFileBtn = document.getElementById('selectFileBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const historySection = document.getElementById('historySection');
const previewImage = document.getElementById('previewImage');
const originalText = document.getElementById('originalText');
const translatedText = document.getElementById('translatedText');
const downloadBtn = document.getElementById('downloadBtn');
const newTranslationBtn = document.getElementById('newTranslationBtn');
const historyBtn = document.getElementById('historyBtn');
const closeHistoryBtn = document.getElementById('closeHistoryBtn');
const historyList = document.getElementById('historyList');
const notification = document.getElementById('notification');

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    // Drag & Drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // File selection
    selectFileBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Action buttons
    downloadBtn.addEventListener('click', downloadTranslation);
    newTranslationBtn.addEventListener('click', resetForm);
    historyBtn.addEventListener('click', showHistory);
    closeHistoryBtn.addEventListener('click', hideHistory);
}

// Drag & Drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// Основная функция обработки файла
function handleFile(file) {
    // Проверка типа файла
    if (!file.type.startsWith('image/')) {
        showNotification('Пожалуйста, выберите изображение', 'error');
        return;
    }
    
    // Проверка размера файла (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showNotification('Размер файла не должен превышать 5 МБ', 'error');
        return;
    }
    
    uploadImage(file);
}

// Загрузка и обработка изображения
async function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Показываем прогресс
    showProgress();
    updateProgress(20, 'Загрузка изображения...');
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        updateProgress(60, 'Распознавание текста...');
        
        const result = await response.json();
        
        updateProgress(90, 'Перевод текста...');
        
        if (result.success) {
            updateProgress(100, 'Готово!');
            setTimeout(() => {
                hideProgress();
                displayResults(result);
                showNotification('Изображение успешно обработано!', 'success');
            }, 500);
        } else {
            hideProgress();
            showNotification(result.error || 'Произошла ошибка при обработке', 'error');
        }
    } catch (error) {
        hideProgress();
        showNotification('Ошибка соединения с сервером', 'error');
        console.error('Upload error:', error);
    }
}

// Управление прогресс-баром
function showProgress() {
    progressContainer.style.display = 'block';
    uploadArea.style.display = 'none';
}

function updateProgress(percent, text) {
    progressFill.style.width = percent + '%';
    progressText.textContent = text;
}

function hideProgress() {
    progressContainer.style.display = 'none';
    uploadArea.style.display = 'block';
}

// Отображение результатов
function displayResults(result) {
    currentTranslationId = result.id;
    
    // Показываем превью изображения
    previewImage.src = result.image_preview;
    
    // Отображаем тексты
    originalText.textContent = result.original_text;
    translatedText.textContent = result.translated_text;
    
    // Показываем секцию результатов
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Скачивание перевода
async function downloadTranslation() {
    if (!currentTranslationId) {
        showNotification('Ошибка: ID перевода не найден', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/download/${currentTranslationId}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `translation_${currentTranslationId}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showNotification('Файл успешно скачан!', 'success');
        } else {
            const error = await response.json();
            showNotification(error.error || 'Ошибка при скачивании', 'error');
        }
    } catch (error) {
        showNotification('Ошибка соединения с сервером', 'error');
        console.error('Download error:', error);
    }
}

// Сброс формы для нового перевода
function resetForm() {
    // Скрываем результаты
    resultsSection.style.display = 'none';
    
    // Очищаем поля
    fileInput.value = '';
    currentTranslationId = null;
    
    // Прокручиваем к началу
    uploadArea.scrollIntoView({ behavior: 'smooth' });
    
    showNotification('Готов к новому переводу', 'info');
}

// Показать историю переводов
async function showHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        if (data.history) {
            displayHistory(data.history);
            historySection.style.display = 'block';
            historySection.scrollIntoView({ behavior: 'smooth' });
        } else {
            showNotification(data.error || 'Ошибка загрузки истории', 'error');
        }
    } catch (error) {
        showNotification('Ошибка соединения с сервером', 'error');
        console.error('History error:', error);
    }
}

// Отображение истории
function displayHistory(history) {
    historyList.innerHTML = '';
    
    if (history.length === 0) {
        historyList.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">История переводов пуста</p>';
        return;
    }
    
    history.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        const date = new Date(item.created_at).toLocaleString('ru-RU');
        
        historyItem.innerHTML = `
            <div class="history-item-header">
                <span class="history-id">#${item.id}</span>
                <span class="history-date">${date}</span>
            </div>
            <div class="history-texts">
                <div class="history-text">
                    <h4>Оригинал</h4>
                    <div>${truncateText(item.original_text, 150)}</div>
                </div>
                <div class="history-text">
                    <h4>Перевод</h4>
                    <div>${truncateText(item.translated_text, 150)}</div>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <button class="btn btn-success" onclick="downloadHistoryItem(${item.id})">
                    <i class="fas fa-download"></i> Скачать
                </button>
            </div>
        `;
        
        historyList.appendChild(historyItem);
    });
}

// Скачивание элемента из истории
async function downloadHistoryItem(id) {
    try {
        const response = await fetch(`/download/${id}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `translation_${id}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showNotification('Файл успешно скачан!', 'success');
        } else {
            const error = await response.json();
            showNotification(error.error || 'Ошибка при скачивании', 'error');
        }
    } catch (error) {
        showNotification('Ошибка соединения с сервером', 'error');
        console.error('Download error:', error);
    }
}

// Скрыть историю
function hideHistory() {
    historySection.style.display = 'none';
}

// Обрезка текста
function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}

// Система уведомлений
function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

// Глобальные функции для использования в HTML
window.downloadHistoryItem = downloadHistoryItem;