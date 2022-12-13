import create_controls from "./create_controls.js";
import mp_overlay from "./mediapipe_func.js";

// Turn off animated spinner after CSS Transition is complete
const spinner = document.querySelector('.loading');
spinner.ontransitionend = () => {
    spinner.style.display = 'none';
};

// To be added into control panel, can call tick() each time the graph runs.
const fpsControl = new window.FPS();

const pose = new window.Pose({
    locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@${window.VERSION}/${file}`;
    }
});

mp_overlay(pose, fpsControl, 'mask');
create_controls(pose, fpsControl, 'mask');
