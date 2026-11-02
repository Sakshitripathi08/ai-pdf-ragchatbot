const uploadBtn = document.getElementById('uploadBtn');
const askBtn = document.getElementById('askBtn');
const pdfFile = document.getElementById('pdfFile');
const question = document.getElementById('question');
const uploadStatus = document.getElementById('uploadStatus');
const answerBox = document.getElementById('answer');

uploadBtn.addEventListener('click', async () => {
  const file = pdfFile.files[0];
  if (!file) {
    uploadStatus.textContent = 'Please select a PDF file first.';
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  uploadStatus.textContent = 'Uploading and indexing...';

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Upload failed');
    }

    uploadStatus.textContent = `${data.message} (${data.chunks_indexed} chunks indexed)`;
  } catch (error) {
    uploadStatus.textContent = error.message;
  }
});

askBtn.addEventListener('click', async () => {
  const text = question.value.trim();
  if (!text) {
    answerBox.textContent = 'Please enter a question.';
    return;
  }

  answerBox.textContent = 'Thinking...';

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Chat request failed');
    }

    answerBox.textContent = data.answer;
  } catch (error) {
    answerBox.textContent = error.message;
  }
});
