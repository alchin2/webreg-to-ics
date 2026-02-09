const uploadInput = document.getElementById('upload-input');
const uploadBtn = document.getElementById('upload-btn');
const previewBox = document.getElementById('preview-box');
const downloadBtn = document.getElementById('download-btn');

let generatedICS = null;

async function convert(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/convert", {
        method: "POST",
        body: formData
    });

    generatedICS = await response.blob();
    previewBox.textContent = "ICS file ready for download.";
    downloadBtn.disabled = false;
}

function handleDownload() {
    if (!generatedICS) {
        alert("Upload first!");
        return;
    }

    const url = window.URL.createObjectURL(generatedICS);
    const a = document.createElement("a");
    a.href = url;
    a.download = "calendar.ics";
    a.click();
    window.URL.revokeObjectURL(url);
}

uploadBtn.addEventListener('click', () => {
    uploadInput.click();
});

uploadInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        convert(file);
    }
});

downloadBtn.addEventListener('click', handleDownload);
