document.addEventListener('DOMContentLoaded', function () {
    // Обработка отправки форм транзакций
    const transactionForms = document.querySelectorAll('.transaction-form');
    transactionForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch('/api/transactions/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.errors) {
                    alert('Ошибка: ' + JSON.stringify(data.errors));
                } else {
                    alert('Транзакция добавлена: ' + JSON.stringify(data));
                    updateUserStats();
                    updateSpendingStats();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Обработка формы изменения баланса
    const balanceForm = document.querySelector('.balance-form');
    if (balanceForm) {
        balanceForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch('/api/topup/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.errors) {
                    alert('Ошибка: ' + JSON.stringify(data.errors));
                } else {
                    alert(data.message);
                    updateUserStats();
                    updateSpendingStats();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Обработка кнопки очистки трат
    const clearButton = document.querySelector('#clear-transactions');
    if (clearButton) {
        clearButton.addEventListener('click', function () {
            if (confirm('Вы уверены, что хотите удалить все транзакции?')) {
                fetch('/api/clear-transactions/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.errors) {
                        alert('Ошибка: ' + JSON.stringify(data.errors));
                    } else {
                        alert(data.message);
                        updateUserStats();
                        updateSpendingStats();
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    }

    // Функция для получения и обновления статистики пользователя
    function updateUserStats() {
        fetch('/api/user-stats/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('balance').textContent = data.balance.toFixed(2) + ' ₽';
            document.getElementById('daily-spent').textContent = data.daily_spent.toFixed(2) + ' ₽';
            document.getElementById('weekly-spent').textContent = data.weekly_spent.toFixed(2) + ' ₽';
        })
        .catch(error => {
            console.error('Error fetching user stats:', error);
            document.getElementById('balance').textContent = 'Ошибка';
            document.getElementById('daily-spent').textContent = 'Ошибка';
            document.getElementById('weekly-spent').textContent = 'Ошибка';
        });
    }

    // Функция для получения и обновления статистики трат
    function updateSpendingStats() {
        const container = document.querySelector('.purchases-container');
        const userId = container ? container.dataset.userId : null;
        
        if (userId === 'null' || !userId) {
            console.warn('No user ID available, skipping spending stats fetch');
            document.getElementById('total-spent').textContent = 'Н/Д';
            document.getElementById('by-category').textContent = 'Н/Д';
            document.getElementById('by-day').textContent = 'Н/Д';
            document.getElementById('daily-average').textContent = 'Н/Д';
            return;
        }

        fetch(`/api/users/${userId}/stats/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Spending stats data:', data); 
            if (data.errors) {
                console.error('API error:', data.errors);
                document.getElementById('total-spent').textContent = 'Ошибка';
                document.getElementById('by-category').textContent = 'Ошибка';
                document.getElementById('by-day').textContent = 'Ошибка';
                document.getElementById('daily-average').textContent = 'Ошибка';
                return;
            }

            // Обновление общей суммы трат
            document.getElementById('total-spent').textContent = data.total_spent.toFixed(2) + ' ₽';

            // Обновление статистики по категориям
            const byCategory = data.by_category;
            if (Object.keys(byCategory).length === 0) {
                document.getElementById('by-category').textContent = '-';
            } else {
                const categoryList = Object.entries(byCategory)
                    .map(([category, amount]) => `${category}: ${amount.toFixed(2)} ₽`)
                    .join(', ');
                document.getElementById('by-category').textContent = categoryList;
            }

            // Обновление статистики по дням
            const byDay = data.by_day;
            if (Object.keys(byDay).length === 0) {
                document.getElementById('by-day').textContent = '-';
            } else {
                const dayList = Object.entries(byDay)
                    .map(([date, amount]) => `${date}: ${amount.toFixed(2)} ₽`)
                    .join(', ');
                document.getElementById('by-day').textContent = dayList;
            }

            // Обновление среднедневной суммы
            document.getElementById('daily-average').textContent = data.daily_average.toFixed(2) + ' ₽';
        })
        .catch(error => {
            console.error('Error fetching spending stats:', error);
            document.getElementById('total-spent').textContent = 'Ошибка';
            document.getElementById('by-category').textContent = 'Ошибка';
            document.getElementById('by-day').textContent = 'Ошибка';
            document.getElementById('daily-average').textContent = 'Ошибка';
        });
    }

    // Инициализация: загрузка статистики при загрузке страницы
    updateUserStats();
    updateSpendingStats();

});