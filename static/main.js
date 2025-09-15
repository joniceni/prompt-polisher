(function () {
  const $ = (id) => document.getElementById(id);

  const btn = $('polish');
  const rawEl = $('raw');
  const outEl = $('polished');
  const copyBtn = $('copy');
  const msg = $('msg');
  const charles = $('charlesImg');

  // Fallback if framed-charles.png can’t be loaded (wrong name/case/path)
  if (charles) {
    charles.addEventListener('error', () => {
      charles.outerHTML = '<div class="charles charles-fallback" aria-label="Charles">C</div>';
    });
  }

  const show = (text, type = '') => {
    if (!msg) return;
    msg.textContent = text || '';
    msg.className = `msg ${type}`;
  };

  async function handlePolish() {
    try {
      const text = (rawEl.value || '').trim();
      if (!text) { show('Please type something first.', 'warn'); return; }

      btn.disabled = true;
      btn.textContent = 'Polishing…';
      show('');

      const res = await fetch('/polish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      // Try to parse JSON even on non-200 to surface server error messages
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || 'Connection error');

      outEl.value = data.polished || '';
      if (!outEl.value) show('No output returned.', 'warn');
    } catch (e) {
      show(e.message || 'Connection error', 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Polish My Prompt';
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(outEl.value || '');
      show('Copied!', 'ok');
    } catch {
      show('Copy failed.', 'warn');
    }
    setTimeout(() => show(''), 1200);
  }

  if (btn) btn.addEventListener('click', handlePolish);
  if (copyBtn) copyBtn.addEventListener('click', handleCopy);
})();
