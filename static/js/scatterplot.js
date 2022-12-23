eyelines = {
    "x": [1,2,3,4,5,6],
    "y": [2,3,4,5,6,7],
    "z": [3,4,5,6,7,8],
    mode: "lines",
    line: {
        color: "rgb(0, 0, 0)",
        width: 8,
    },
    type: "scatter3d",
};

mouthlines = {
    "x": [2,3,4,5,6,7],
    "y": [1,2,3,4,5,6],
    "z": [3,4,5,6,7,8],
    mode: "lines",
    line: {
        color: "rgb(0, 0, 0)",
        width: 8,
    },
    type: "scatter3d",
};

bodylines = {
    "x": [1,2,3,4,5,6],
    "y": [2,3,4,5,6,7],
    "z": [3,4,5,6,7,8],
    mode: "lines",
    line: {
        color: "rgb(0, 0, 0)",
        width: 8,
    },
    type: "scatter3d",
};

leftmarkers = {
    "x": [1,2,3,4,5,6],
    "y": [2,3,4,5,6,7],
    "z": [3,4,5,6,7,8],
    mode: "markers",
    marker: {
        color: "rgb(0, 0, 255)",
        size: 8,
        symbol: "circle",
    },
    type: "scatter3d",
};

rightmarkers = {
    "x": [2,3,4,5,6,7],
    "y": [1,2,3,4,5,6],
    "z": [3,4,5,6,7,8],
    mode: "markers",
    marker: {
        color: "rgb(255, 0, 0)",
        size: 8,
        symbol: "circle",
    },
    type: "scatter3d",
};

Plotly.newPlot('myDiv',{
    "data": [eyelines, mouthlines, bodylines, leftmarkers, rightmarkers],
    "layout": {
        width: 450,
        height: 450,
        autosize: true,
        showlegend: false,
        margin:{
            b: 0,
            l: 0,
            r: 0,
            t: 0
        },
        hovermode: false
    },
    "config": {
        displayModeBar: false
    }
});