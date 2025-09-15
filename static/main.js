// static/main.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("polish-form");
  const input = document.getElementById("prompt-input");
  const output = document.getElementById("prompt-output");
  const copyBtn = document.getElementById("copy-btn");

  // Handle form submit
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    output.value = "Polishing...";

    try {
      const response = await fetch("/polish", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input.value })
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.error) {
        output.value = "Error: " + data.error;
      } else {
        output.value = data.polished;
      }
    } catch (err) {
      output.value = "Error: " + err.message;
    }
  });

  // Handle copy button
  copyBtn.addEventListener("click", () => {
    if (output.value.trim() === "") {
      alert("Nothing to copy!");
      return;
    }
    navigator.clipboard.writeText(output.value)
      .then(() => {
        copyBtn.innerText = "Copied!";
        setTimeout(() => copyBtn.innerText = "Copy", 2000);
      })
      .catch(() => alert("Failed to copy"));
  });
});
