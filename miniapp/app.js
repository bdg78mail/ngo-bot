// Mini App — поиск льгот для НКО Потенциал

const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

const form = document.getElementById('benefitsForm');
const submitBtn = document.getElementById('submitBtn');
const resultDiv = document.getElementById('result');
const resultText = document.getElementById('resultText');
const loadingDiv = document.getElementById('loading');

// API endpoint (настраивается)
const API_URL = '/api/webapp';

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const regionSelect = document.getElementById('region');
    const ageSelect = document.getElementById('age');
    const categorySelect = document.getElementById('category');
    const question = document.getElementById('question').value;

    // Собираем данные
    const data = {
        type: question ? 'consultation' : 'quick_answer',
        region: regionSelect.value,
        regionName: regionSelect.options[regionSelect.selectedIndex].dataset.name || '',
        age: ageSelect.value,
        ageName: ageSelect.options[ageSelect.selectedIndex].dataset.name || '',
        category: categorySelect.value,
        categoryName: categorySelect.options[categorySelect.selectedIndex].dataset.name || '',
        question: question,
        user_id: tg.initDataUnsafe?.user?.id || 'webapp_user',
        timestamp: new Date().toISOString(),
    };

    // Показываем загрузку
    submitBtn.disabled = true;
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (result.status === 'ok') {
            resultText.textContent = result.answer;
            resultDiv.classList.remove('hidden');
        } else {
            resultText.textContent = result.message || 'Произошла ошибка. Попробуйте позже.';
            resultDiv.classList.remove('hidden');
        }
    } catch (error) {
        resultText.textContent = 'Ошибка соединения. Проверьте интернет и попробуйте снова.';
        resultDiv.classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
        loadingDiv.classList.add('hidden');
    }
});
