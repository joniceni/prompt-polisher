// Wait for DOM
document.addEventListener("DOMContentLoaded", () => {
  const form     = document.getElementById("form");
  const statusEl = document.getElementById("status");
  const outEl    = document.getElementById("out-text");
  const copyBtn  = document.getElementById("copy");
  const toast    = document.getElementById("toast");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    statusEl.textContent = "Working…";
    outEl.textContent = "…";
    try {
      const data = new FormData(form);             // matches app.py
      const res  = await fetch("/api/polish", {    // correct endpoint
        method: "POST",
        body: data
      });
      const json = await res.json();
      if (json.ok) {
        outEl.textContent = json.response || "No content";
        statusEl.textContent = "Done";
      } else {
        outEl.textContent = json.error || "Error";
        statusEl.textContent = "Error";
      }
    } catch (err) {
      outEl.textContent = String(err);
      statusEl.textContent = "Network error";
    }
  });

  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(outEl.textContent);
      toast.classList.add("show");
      setTimeout(() => toast.classList.remove("show"), 900);
    } catch {}
  });
});
