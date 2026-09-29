const fileInput = document.getElementById("file-input");
const preview = document.getElementById("preview");
const generateButton = document.getElementById("generate-button");
const progressSection = document.getElementById("step-progress");
const progressText = document.getElementById("progress-text");
const resultSection = document.getElementById("step-result");
const downloadFontLink = document.getElementById("download-font");

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];

  if (!file) {
    preview.hidden = true;
    generateButton.disabled = true;
    return;
  }

  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
  generateButton.disabled = false;
});

async function postJson(path) {
  const response = await fetch(path, { method: "POST" });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request to ${path} failed (${response.status})`);
  }
  return response.json();
}

generateButton.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  generateButton.disabled = true;
  resultSection.hidden = true;
  progressSection.hidden = false;

  try {
    progressText.textContent = "Uploading...";
    const formData = new FormData();
    formData.append("file", file);
    const ingestResponse = await fetch("/ingest", { method: "POST", body: formData });
    if (!ingestResponse.ok) {
      const body = await ingestResponse.json().catch(() => ({}));
      throw new Error(body.detail || "Upload failed.");
    }
    const { id } = await ingestResponse.json();

    progressText.textContent = "Cleaning up the image...";
    await postJson(`/preprocess/${id}`);

    progressText.textContent = "Finding each letter...";
    await postJson(`/segment/${id}`);

    progressText.textContent = "Tracing shapes...";
    await postJson(`/vectorize/${id}`);

    progressText.textContent = "Measuring spacing...";
    await postJson(`/metrics/${id}`);

    progressText.textContent = "Building your font...";
    const compileResult = await postJson(`/compile/${id}`);

    progressSection.hidden = true;
    downloadFontLink.href = `/download-font/${id}`;
    resultSection.hidden = false;
  } catch (err) {
    progressText.textContent = err.message || "Something went wrong.";
  } finally {
    generateButton.disabled = false;
  }
});
