document.addEventListener('DOMContentLoaded', () => {
  const btn   = document.getElementById('polishBtn');
  const input = document.getElementById('userInput');
  const out   = document.getElementById('result');
  const copy  = document.getElementById('copyBtn');
  const err   = document.getElementById('error');

  btn.addEventListener('click', async () => {
    err.hidden = true;
    err.textContent = '';
    out.value = '';

    const prompt = (input.value || '').trim();
    if (!prompt) {
      err.textContent = 'Please enter something first.';
      err.hidden = false;
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Polishing…';

    try {
      const res = await fetch('/polish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Request failed (${res.status})`);
      }
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      out.value = data.prompt || '';
    } catch (e) {
      err.textContent = e.message || 'Connection error.';
      err.hidden = false;
    } finally {
      btn.disabled = false;
      btn.textContent = 'Polish My Prompt';
    }
  });

  copy.addEventListener('click', async () => {
    if (!out.value) return;
    await navigator.clipboard.writeText(out.value);
    copy.textContent = 'Copied';
    setTimeout(() => (copy.textContent = 'Copy'), 900);
  });
});
