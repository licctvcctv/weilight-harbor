/**
 * Weilight Harbor - Journal Module JS
 * Handles image upload preview and mood selector interactions.
 */

/**
 * Initialize image upload with preview grid.
 * @param {string} inputId - The file input element ID
 * @param {string} gridId - The preview grid container ID
 */
function initImageUpload(inputId, gridId) {
    const imageInput = document.getElementById(inputId);
    const previewGrid = document.getElementById(gridId);
    if (!imageInput || !previewGrid) return;

    let selectedFiles = new DataTransfer();

    imageInput.addEventListener('change', function () {
        const files = Array.from(this.files);
        const remaining = 9 - selectedFiles.files.length;
        const toAdd = files.slice(0, remaining);

        toAdd.forEach(function (file) {
            if (!file.type.startsWith('image/')) return;
            selectedFiles.items.add(file);

            var reader = new FileReader();
            reader.onload = function (e) {
                var idx = selectedFiles.files.length - 1;
                var item = document.createElement('div');
                item.className = 'image-preview-item';
                item.innerHTML =
                    '<img src="' + e.target.result + '" alt="Preview">' +
                    '<button type="button" class="remove-btn" data-index="' + idx + '">&times;</button>';
                previewGrid.appendChild(item);

                item.querySelector('.remove-btn').addEventListener('click', function () {
                    var newDt = new DataTransfer();
                    var removeIdx = parseInt(this.dataset.index);
                    for (var i = 0; i < selectedFiles.files.length; i++) {
                        if (i !== removeIdx) newDt.items.add(selectedFiles.files[i]);
                    }
                    selectedFiles = newDt;
                    imageInput.files = selectedFiles.files;
                    rebuildPreviews();
                });
            };
            reader.readAsDataURL(file);
        });

        imageInput.files = selectedFiles.files;
    });

    function rebuildPreviews() {
        previewGrid.innerHTML = '';
        Array.from(selectedFiles.files).forEach(function (file, idx) {
            var reader = new FileReader();
            reader.onload = function (e) {
                var item = document.createElement('div');
                item.className = 'image-preview-item';
                item.innerHTML =
                    '<img src="' + e.target.result + '" alt="Preview">' +
                    '<button type="button" class="remove-btn" data-index="' + idx + '">&times;</button>';
                previewGrid.appendChild(item);
                item.querySelector('.remove-btn').addEventListener('click', function () {
                    var newDt = new DataTransfer();
                    var removeIdx = parseInt(this.dataset.index);
                    for (var i = 0; i < selectedFiles.files.length; i++) {
                        if (i !== removeIdx) newDt.items.add(selectedFiles.files[i]);
                    }
                    selectedFiles = newDt;
                    imageInput.files = selectedFiles.files;
                    rebuildPreviews();
                });
            };
            reader.readAsDataURL(file);
        });
    }
}
