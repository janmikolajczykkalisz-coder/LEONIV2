const diametersSet1 = [0.2011, 0.1878, 0.1749, 0.1631, 0.1521, 0.1418, 0.1323, 0.1233, 0.1150, 0.1072];
const diametersSet2 = [0.5089, 0.4620, 0.4200, 0.3820, 0.3470, 0.3158, 0.2870, 0.2610, 0.2373, 0.2150];
const diametersSet3 = [1.5830, 1.4100, 1.2560, 1.1190, 0.9970, 0.8880, 0.7910, 0.7049, 0.6280, 0.5590];

document.addEventListener("DOMContentLoaded", () => {
    const select = document.getElementById('diameter_set');
    select.addEventListener('change', function() {
        let diameters = diametersSet3;
        if (this.value === '1') diameters = diametersSet1;
        else if (this.value === '2') diameters = diametersSet2;

        const cells = document.querySelectorAll('.diam-cell');
        cells.forEach((cell, index) => {
            if (diameters[index] !== undefined) {
                cell.textContent = diameters[index].toFixed(4);
            }
        });
    });
});
