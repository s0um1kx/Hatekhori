const sessionId = new URLSearchParams(window.location.search).get("session");

const captureInput = document.getElementById("capture-input");
const capturePreview = document.getElementById("capture-preview");
const statusSection = document.getElementById("step-status");
const statusText = document.getElementById("status-text");

captureInput.addEventListener("change", async () => {
  const file = captureInput.files[0];
  if (!file) return;

  capturePreview.src = URL.createObjectURL(file);
  capturePreview.hidden = false;

  if (!sessionId) {
    statusSection.hidden = false;
    statusText.textContent = "No session found — scan the QR code again from your computer.";
    return;
  }

  statusSection.hidden = false;
  statusText.textContent = "Uploading...";

  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`/session/${sessionId}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || "Upload failed.");
    }

    statusText.textContent = "Done! You can go back to your computer.";
  } catch (err) {
    statusText.textContent = err.message || "Something went wrong.";
  }
});
