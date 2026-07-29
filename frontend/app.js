const form = document.getElementById('quote-form');
const result = document.getElementById('result');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const payload = {
    sources: Array.from(document.getElementById('sources').files).map((file) => file.name),
    strategy: document.getElementById('strategy').value,
  };

  result.textContent = 'Отправка задачи...';

  try {
    const response = await fetch('http://127.0.0.1:8000/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    result.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    result.textContent = `Ошибка: ${error.message}`;
  }
});
