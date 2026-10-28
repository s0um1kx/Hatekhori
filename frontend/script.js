const fileInput = document.getElementById("file-input");
const preview = document.getElementById("preview");
const generateButton = document.getElementById("generate-button");
const progressSection = document.getElementById("step-progress");
const progressText = document.getElementById("progress-text");
const resultSection = document.getElementById("step-result");
const downloadFontLink = document.getElementById("download-font");
const previewText = document.getElementById("preview-text");
const previewSize = document.getElementById("preview-size");
const previewNote = document.getElementById("preview-note");

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

// Live preview: load the generated font into the page and apply it to
// the text box, so what you type is shown in your own handwriting.
async function loadPreviewFont(id) {
  previewNote.hidden = true;
  try {
    const family = `HatekhoriPreview-${id}`;
    const face = new FontFace(family, `url(/download-font/${id}?inline=true)`);
    await face.load();
    document.fonts.add(face);
    previewText.style.fontFamily = `"${family}", sans-serif`;
    applyPreviewSize();
  } catch (err) {
    previewNote.textContent = "Couldn't load the live preview — the font is still ready to download.";
    previewNote.hidden = false;
  }
}

function applyPreviewSize() {
  previewText.style.fontSize = `${previewSize.value}px`;
}

previewSize.addEventListener("input", applyPreviewSize);
applyPreviewSize();

async function postJson(path) {
  const response = await fetch(path, { method: "POST" });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request to ${path} failed (${response.status})`);
  }
  return response.json();
}

async function runPipelineFromUploadId(id) {
  resultSection.hidden = true;
  progressSection.hidden = false;

  try {
    progressText.textContent = "Building your font...";
    await postJson(`/generate/${id}`);

    progressSection.hidden = true;
    downloadFontLink.href = `/download-font/${id}`;
    resultSection.hidden = false;
    await loadPreviewFont(id);
  } catch (err) {
    progressText.textContent = err.message || "Something went wrong.";
  }
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

    await runPipelineFromUploadId(id);
  } catch (err) {
    progressText.textContent = err.message || "Something went wrong.";
  } finally {
    generateButton.disabled = false;
  }
});
