const controls = window;

// Input Frames
const canvasElement = document.getElementsByClassName('output_canvas')[0];
// const videoElement = document.getElementsByClassName('input_video')[0];

export default function create_controls(pose, fpsControl, activeEffect) {
    // Present a control panel for manipulating solution options.
    new controls
    .ControlPanel(document.getElementsByClassName('control-panel')[0], {
        selfieMode: false,
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        smoothSegmentation: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
        effect: 'background',
        calibrate: false,
        statistics: false,
    })

    .add([
        new controls.StaticText({ title: 'Walk-E' }),
        fpsControl,
        // new controls.Toggle({ title: 'Selfie Mode', field: 'selfieMode' }),
        new controls.SourcePicker({
            // Resets because this model gives better results when reset between source changes.
            onSourceChanged: () => {
                pose.reset();
            },
            onFrame: async (input, size) => {
                const aspect = size.height / size.width;
                let width, height;
                if (window.innerWidth > window.innerHeight) {
                    height = window.innerHeight;
                    width = height / aspect;
                }
                else {
                    width = window.innerWidth;
                    height = width * aspect;
                }
                canvasElement.width = width;
                canvasElement.height = height;
                await pose.send({ image: input });
            },
        }),
        new controls.Slider({
            title: 'Model Complexity',
            field: 'modelComplexity',
            discrete: ['Lite', 'Full', 'Heavy'],
        }),
        new controls.Slider({
            title: 'Min Detection Confidence',
            field: 'minDetectionConfidence',
            range: [0, 1],
            step: 0.01
        }),
        new controls.Slider({
            title: 'Min Tracking Confidence',
            field: 'minTrackingConfidence',
            range: [0, 1],
            step: 0.01
        }),
        new controls.Toggle({ title: 'Smooth Landmarks', field: 'smoothLandmarks' }),
        new controls.Toggle({ title: 'Smooth Segmentation', field: 'smoothSegmentation' }),
        new controls.Toggle({ title: 'Enable Segmentation', field: 'enableSegmentation' }),       
        // new controls.Slider({
        //     title: 'Effect',
        //     field: 'effect',
        //     discrete: { 'background': 'Background', 'mask': 'Foreground' },
        // }),

        // new controls.Toggle({title: "Calibrate", field: "calibrate", name: "calibrate"}),
        // new controls.Toggle({title: "Statistics", field: "statistics"}),
    ])

    .on(options => {
        // const options = x;
        // videoElement.classList.toggle('selfie', options.selfieMode);
        options["effect"] = activeEffect;
        pose.setOptions(options);
    })
}