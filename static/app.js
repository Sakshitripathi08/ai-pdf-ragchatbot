const uploadBtn = document.getElementById('uploadBtn');
const askBtn = document.getElementById('askBtn');
const pdfFile = document.getElementById('pdfFile');
const question = document.getElementById('question');
const uploadStatus = document.getElementById('uploadStatus');
const answerBox = document.getElementById('answer');
const apiKey = document.getElementById('apiKey');

function authHeaders(extra = {}) {
  const key = apiKey.value.trim();
  return key ? { ...extra, Authorization: `Bearer ${key}` } : extra;
}

async function responseData(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) throw new Error('Access denied. Check the API key from your Render service environment.');
    throw new Error(data.detail || `Request failed (${response.status})`);
  }
  return data;
}

uploadBtn.addEventListener('click', async () => {
  const file = pdfFile.files[0];
  if (!file) {
    uploadStatus.textContent = 'Please choose a PDF first.';
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  uploadBtn.disabled = true;
  uploadStatus.textContent = 'Uploading and indexing… The first upload may take longer while the embedding model initializes.';

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
    });
    const data = await responseData(response);
    uploadStatus.textContent = `${data.message} (${data.chunks_indexed} chunks indexed).`;
  } catch (error) {
    uploadStatus.textContent = error.message;
  } finally {
    uploadBtn.disabled = false;
  }
});

askBtn.addEventListener('click', async () => {
  const text = question.value.trim();
  if (!text) {
    answerBox.textContent = 'Please enter a question.';
    return;
  }

  askBtn.disabled = true;
  answerBox.textContent = 'Thinking…';
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ question: text }),
    });
    const data = await responseData(response);
    answerBox.textContent = data.answer;
  } catch (error) {
    answerBox.textContent = error.message;
  } finally {
    askBtn.disabled = false;
  }
});
