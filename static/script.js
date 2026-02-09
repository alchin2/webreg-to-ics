const uploadBtn = document.getElementById('upload-btn');
const uploadInput = document.getElementById('upload-input');
const previewBox = document.getElementById('preview-box');
const downloadBtn = document.getElementById('download-btn');

uploadBtn.addEventListener('click', () => {
    uploadInput.click();
});

uploadInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            previewBox.textContent = e.target.result;
            downloadBtn.disabled = false;
        };
        reader.readAsText(file);
    }
});

downloadBtn.addEventListener('click', () => {
    const content = previewBox.textContent;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'schedule.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});
