const fileInput = document.getElementById("file-input");
const preview = document.getElementById("preview");
const generateButton = document.getElementById("generate-button");

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
