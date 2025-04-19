function generateImageGrid(containerId, totalImages = 100, imagesPerRow = 4, imagePath = "../IMAGES/reference.jpg") {
    const row = document.getElementById(containerId);
    row.innerHTML = "";

    const colSize = Math.floor(12 / imagesPerRow) || 1;

    for (let i = 0; i < totalImages; i++) {
        if (i % imagesPerRow === 0) {
            var newRow = document.createElement("div");
            newRow.className = "row mb-3";
            row.appendChild(newRow);
        }

        const col = document.createElement("div");
        col.className = `col-sm-${colSize}`;

        const img = document.createElement("img");
        img.src = imagePath;
        img.alt = `Image ${i + 1}`;
        img.className = "img-fluid";

        col.appendChild(img);
        newRow.appendChild(col);
    }
}

generateImageGrid("image-row", 100, 4, "../IMAGES/reference.jpg");
