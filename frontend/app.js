const form = document.getElementById('quote-form');
const result = document.getElementById('result');
const estimatePreview = document.getElementById('estimate-preview');
const progressFill = document.getElementById('progress-fill');
const stepPills = Array.from(document.querySelectorAll('.step-pill'));
const submitButton = form.querySelector('button');
const templateInput = document.getElementById('template-file');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const templateFile = templateInput?.files?.[0];
  const payload = {
    sources: Array.from(document.getElementById('sources').files).map((file) => file.name),
    strategy: document.getElementById('strategy').value,
    output_language: document.getElementById('output-language').value,
  };

  if (templateFile) {
    const templateText = await templateFile.text();
    payload.agency_template = {
      name: templateFile.name.replace(/\.[^.]+$/, ''),
      content: templateText,
    };
  }

  submitButton.disabled = true;
  submitButton.textContent = 'Создаём задачу...';
  result.textContent = 'Отправка задачи...';
  updateWorkflowStatus('received', 20);

  try {
    const response = await fetch('http://127.0.0.1:8000/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    result.textContent = JSON.stringify(data, null, 2);
    updateWorkflowStatus(data.status, 100);
    renderEstimate(data.estimate, data);
  } catch (error) {
    result.textContent = `Ошибка: ${error.message}`;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Создать задачу';
  }
});

function updateWorkflowStatus(status, progress) {
  const stages = ['received', 'extracting', 'matching', 'ready'];
  const activeIndex = stages.indexOf(status);

  stepPills.forEach((pill, index) => {
    pill.classList.toggle('active', index <= activeIndex);
  });

  if (progressFill) {
    progressFill.style.width = `${Math.max(20, Math.min(progress, 100))}%`;
  }
}

function renderEstimate(estimate, job) {
  if (!estimate) {
    estimatePreview.innerHTML = '<h2>Предпросмотр сметы</h2><p class="placeholder">После создания задачи здесь появится структура сметы.</p>';
    return;
  }

  const itemsMarkup = estimate.items
    .map((item) => `<li><strong>${item.category}</strong> — ${item.description} · ${item.amount.toFixed(2)} · ${item.source}</li>`)
    .join('');

  const parsedFilesMarkup = job && job.parsed_files && job.parsed_files.length
    ? `<div class="parsed-files"><strong>Parsed files:</strong><ul>${job.parsed_files.map((file) => `<li><strong>${file.filename}</strong> · ${file.format || 'text'} · ${file.size_bytes} bytes<br><span>${file.sample_text || 'No content extracted'}</span></li>`).join('')}</ul></div>`
    : '';

  const exportsMarkup = job && job.exports
    ? `<div class="export-actions"><p class="placeholder"><strong>Export:</strong></p><div class="export-buttons"><a class="download-link" href="${job.exports.json}" download>Скачать JSON</a><a class="download-link" href="${job.exports.csv}" download>Скачать CSV</a></div></div>`
    : '';

  estimatePreview.innerHTML = `
    <h2>${estimate.title}</h2>
    <p class="placeholder">${estimate.subtitle}</p>
    <p class="placeholder"><strong>Status:</strong> ${job?.status || 'unknown'}</p>
    ${parsedFilesMarkup}
    <ul>${itemsMarkup}</ul>
    <p><strong>Total:</strong> ${estimate.total.toFixed(2)}</p>
    <p class="placeholder"><strong>Strategy:</strong> ${estimate.strategy}</p>
    ${exportsMarkup}
  `;
}
