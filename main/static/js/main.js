import create_controls from "./create_controls.js";
import create_grid from "./create_grid.js";
import { grid_plot,canvas_plot } from "./create_plot.js";
// import mp_overlay from "./mediapipe_func.js";

const grid = create_grid();
const spinner = document.querySelector('.loading');
const canvasElement = document.getElementsByClassName('output_canvas')[0];

/////////////////////////////////////////////////////////////////////////////////////////////////

// Turn off animated spinner after CSS Transition is complete
spinner.ontransitionend = () => {
    spinner.style.display = 'none';
};

function mp_overlay(pose, fpsControl, activeEffect){
    var start_time = (new Date().getTime())/1000; 

    function mediapipe_overlay(results) {
        // Hide the spinner.
        document.body.classList.add('loaded');
    
        // Update the frame rate.
        fpsControl.tick();
    
        canvas_plot(results, canvasElement, activeEffect, start_time);
        grid_plot(results, grid);        
    }
    
    pose.onResults(mediapipe_overlay);
};

/////////////////////////////////////////////////////////////////////////////////////////////////

// To be added into control panel, can call tick() each time the graph runs.
const fpsControl = new window.FPS();

const pose = new window.Pose({
    locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@${window.VERSION}/${file}`;
    }
});

mp_overlay(pose, fpsControl, 'mask');
create_controls(pose, fpsControl, 'mask');
