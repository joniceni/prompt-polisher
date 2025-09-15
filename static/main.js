const $ = (sel) => document.querySelector(sel);

const input = $("#text-input");
const btn = $("#polish-btn");
const out = $("#output-text");
const copy = $("#copy-btn");
const errorBox = $("#error");

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.hidden = !msg;
}

async function polish() {
  showError("");
  out.value = "";

  const text = (input.value || "").trim();
  if (!text) {
    showError("Please type something first.");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Polishing…";

  try {
    const res = await fetch("/polish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      showError(data.error || "Something went wrong.");
      return;
    }

    out.value = data.result || "";
    if (!out.value) {
      showError("No result received.");
    }
  } catch (e) {
    showError("Connection error. Please try again.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Polish My Prompt";
  }
}

btn.addEventListener("click", polish);

// Enter + Ctrl/Cmd+Enter support
input.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "enter") {
    polish();
  }
});

copy.addEventListener("click", async () => {
  const text = out.value || "";
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    copy.textContent = "Copied!";
    setTimeout(() => (copy.textContent = "Copy"), 900);
  } catch {
    // no-op
  }
});
