const $ = (sel) => document.querySelector(sel);
const promptInput = $('#promptInput');
const polishBtn   = $('#polishBtn');
const resultText  = $('#resultText');
const copyBtn     = $('#copyBtn');
const errorBox    = $('#errorBox');

async function polish() {
  errorBox.hidden = true;
  resultText.textContent = '';

  const prompt = (promptInput.value || '').trim();
  if (!prompt) {
    errorBox.textContent = 'Please enter something for Charles to polish.';
    errorBox.hidden = false;
    return;
  }

  polishBtn.disabled = true;
  polishBtn.textContent = 'Polishing…';

  try {
    const res = await fetch('/polish', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ prompt })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Server error (${res.status})`);
    }

    const data = await res.json();
    resultText.textContent = data.polished || '';
  } catch (e) {
    errorBox.textContent = e.message || 'Connection error.';
    errorBox.hidden = false;
  } finally {
    polishBtn.disabled = false;
    polishBtn.textContent = 'Polish My Prompt';
  }
}

function copyOut() {
  const text = resultText.textContent.trim();
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    copyBtn.textContent = 'Copied!';
    setTimeout(() => (copyBtn.textContent = 'Copy'), 900);
  });
}

polishBtn.addEventListener('click', polish);
copyBtn.addEventListener('click', copyOut);

