const form = document.getElementById('quote-form');
const result = document.getElementById('result');
const estimatePreview = document.getElementById('estimate-preview');
const submitButton = form.querySelector('button');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const payload = {
    sources: Array.from(document.getElementById('sources').files).map((file) => file.name),
    strategy: document.getElementById('strategy').value,
    output_language: document.getElementById('output-language').value,
  };

  submitButton.disabled = true;
  submitButton.textContent = 'Создаём задачу...';
  result.textContent = 'Отправка задачи...';

  try {
    const response = await fetch('http://127.0.0.1:8000/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    result.textContent = JSON.stringify(data, null, 2);
    renderEstimate(data.estimate);
  } catch (error) {
    result.textContent = `Ошибка: ${error.message}`;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Создать задачу';
  }
});

function renderEstimate(estimate) {
  if (!estimate) {
    estimatePreview.innerHTML = '<h2>Предпросмотр сметы</h2><p class="placeholder">После создания задачи здесь появится структура сметы.</p>';
    return;
  }

  const itemsMarkup = estimate.items
    .map((item) => `<li><strong>${item.category}</strong> — ${item.description} · ${item.amount.toFixed(2)} · ${item.source}</li>`)
    .join('');

  estimatePreview.innerHTML = `
    <h2>${estimate.title}</h2>
    <p class="placeholder">${estimate.subtitle}</p>
    <ul>${itemsMarkup}</ul>
    <p><strong>Total:</strong> ${estimate.total.toFixed(2)}</p>
    <p class="placeholder"><strong>Strategy:</strong> ${estimate.strategy}</p>
  `;
}
