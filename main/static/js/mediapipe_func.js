import create_grid from "./create_grid.js";
import { grid_plot,canvas_plot } from "./create_plot.js";

const grid = create_grid();
const canvasElement = document.getElementsByClassName('output_canvas')[0];

export default function mp_overlay(pose, fpsControl, activeEffect){
    function mediapipe_overlay(results) {
        // Hide the spinner.
        document.body.classList.add('loaded');
    
        // Update the frame rate.
        fpsControl.tick();
    
        canvas_plot(results, canvasElement, activeEffect);
        grid_plot(results, grid);        
    }
    
    pose.onResults(mediapipe_overlay);
}
