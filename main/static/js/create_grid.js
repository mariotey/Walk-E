const LandmarkGrid = window.LandmarkGrid;

// Input Frames
const landmarkContainer = document.getElementsByClassName('landmark-grid-container')[0];

export default function create_grid() {
    const grid = new LandmarkGrid(landmarkContainer, {
        connectionColor: 0xCCCCCC,
        definedColors: [{ name: 'LEFT', value: 0xffa500 }, { name: 'RIGHT', value: 0x00ffff }],
        range: 2,
        fitToGrid: true,
        labelSuffix: 'm',
        landmarkSize: 1.25,
        numCellsPerAxis: 4,
        showHidden: false,
        centered: true,
    });

    return grid;
}