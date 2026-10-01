const fileInput = document.getElementById("file-input");
const preview = document.getElementById("preview");
const generateButton = document.getElementById("generate-button");
const progressSection = document.getElementById("step-progress");
const progressText = document.getElementById("progress-text");
const resultSection = document.getElementById("step-result");
const downloadFontLink = document.getElementById("download-font");
const usePhoneButton = document.getElementById("use-phone-button");
const qrArea = document.getElementById("qr-area");
const qrImage = document.getElementById("qr-image");
const qrStatus = document.getElementById("qr-status");

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

// Shared by both the direct-upload button and the QR/phone flow — once
// an upload id exists (from either source), the rest of the pipeline
// is identical.
async function runPipelineFromUploadId(id) {
  resultSection.hidden = true;
  progressSection.hidden = false;

  try {
    progressText.textContent = "Cleaning up the image...";
    await postJson(`/preprocess/${id}`);

    progressText.textContent = "Finding each letter...";
    await postJson(`/segment/${id}`);

    progressText.textContent = "Tracing shapes...";
    await postJson(`/vectorize/${id}`);

    progressText.textContent = "Measuring spacing...";
    await postJson(`/metrics/${id}`);

    progressText.textContent = "Building your font...";
    await postJson(`/compile/${id}`);

    progressSection.hidden = true;
    downloadFontLink.href = `/download-font/${id}`;
    resultSection.hidden = false;
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

let pollTimer = null;

usePhoneButton.addEventListener("click", async () => {
  usePhoneButton.disabled = true;
  qrStatus.textContent = "Waiting for your phone...";

  try {
    const { session_id } = await postJson("/qr-session");
    qrImage.src = `/session/${session_id}/qr.png`;
    qrArea.hidden = false;

    pollTimer = setInterval(async () => {
      const response = await fetch(`/session/${session_id}/status`);
      if (!response.ok) return;
      const data = await response.json();

      if (data.status === "received") {
        clearInterval(pollTimer);
        qrArea.hidden = true;
        usePhoneButton.disabled = false;
        await runPipelineFromUploadId(data.upload_id);
      }
    }, 2000);
  } catch (err) {
    qrStatus.textContent = err.message || "Couldn't start phone capture.";
    usePhoneButton.disabled = false;
  }
});
