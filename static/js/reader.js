// reader.js - Handles UI interactions for the reader (Theme, Font Size)

document.addEventListener('DOMContentLoaded', () => {
    const fontIncrease = document.getElementById('font-increase');
    const fontDecrease = document.getElementById('font-decrease');
    const spread = document.querySelector('.book-spread');

    let currentFontSize = 1.1; // rem

    // Font Controls
    fontIncrease.addEventListener('click', () => {
        if (currentFontSize < 2.0) {
            currentFontSize += 0.1;
            spread.style.fontSize = `${currentFontSize}rem`;
        }
    });

    fontDecrease.addEventListener('click', () => {
        if (currentFontSize > 0.8) {
            currentFontSize -= 0.1;
            spread.style.fontSize = `${currentFontSize}rem`;
        }
    });
});
