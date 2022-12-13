const mpPose = window;
const drawingUtils = window;

const minVis = 0.25;
const lineWidth = 2;
const radius = 2;

export function grid_plot(results, grid) {
    if (results.poseWorldLandmarks) {
        grid.updateLandmarks(results.poseWorldLandmarks, mpPose.POSE_CONNECTIONS, [
            { list: Object.values(mpPose.POSE_LANDMARKS_LEFT), color: 'LEFT' },
            { list: Object.values(mpPose.POSE_LANDMARKS_RIGHT), color: 'RIGHT' },
        ]);
    }
    else {
        grid.updateLandmarks([]);
    }
}

export function canvas_plot(results, canvasElement, activeEffect, start_time){
    const canvasCtx = canvasElement.getContext('2d');
    
    // Draw the overlays.
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

    // Segmentation Masking
    if (results.segmentationMask) {
        canvasCtx.drawImage(results.segmentationMask, 0, 0, canvasElement.width, canvasElement.height);
        // Only overwrite existing pixels.
        if (activeEffect === 'mask') {
            canvasCtx.globalCompositeOperation = 'source-out';
            canvasCtx.fillStyle = '#0000FF7F';
            canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        }

        // if (activeEffect === 'mask' || activeEffect === 'both') {
        //     canvasCtx.globalCompositeOperation = 'source-in';
        //     canvasCtx.fillStyle = '#00E642F5';
        //     canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        // }
        // else {
        //     canvasCtx.globalCompositeOperation = 'source-out';
        //     canvasCtx.fillStyle = '#0000FF7F';
        //     canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        // }
        
        // Only overwrite missing pixels.
        canvasCtx.globalCompositeOperation = 'destination-atop';
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.globalCompositeOperation = 'source-over';
    }
    else {
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
    }

    // Canvas overlays
    if (results.poseLandmarks) {
        drawingUtils.drawConnectors(canvasCtx, results.poseLandmarks, mpPose.POSE_CONNECTIONS, { visibilityMin: minVis, color: 'rgb(245, 66, 230)', lineWidth: lineWidth, radius: radius});
        drawingUtils.drawLandmarks(canvasCtx, Object.values(mpPose.POSE_LANDMARKS_LEFT)
            .map(index => results.poseLandmarks[index]), { visibilityMin: minVis, color: 'rgb(245, 66, 230)', lineWidth: lineWidth, radius: radius});
        drawingUtils.drawLandmarks(canvasCtx, Object.values(mpPose.POSE_LANDMARKS_RIGHT)
            .map(index => results.poseLandmarks[index]), { visibilityMin: minVis, color: 'rgb(245, 66, 230)', lineWidth: lineWidth, radius: radius});
        drawingUtils.drawLandmarks(canvasCtx, Object.values(mpPose.POSE_LANDMARKS_NEUTRAL)
            .map(index => results.poseLandmarks[index]), { visibilityMin: minVis, color: 'rgb(245, 66, 230)', lineWidth: lineWidth, radius: radius});
    }   

    if (cali_flag == true) {
        // console.log(results.poseLandmarks);
        calibrate_list["poseLandmark"].push(results.poseLandmarks);
        calibrate_list["worldLandmark"].push(results.poseWorldLandmarks);
        calibrate_list["time"].push((new Date().getTime())/1000 - start_time);
        // console.log(time);
    };

    if (stats_flag == true) {        
        joint_list["poseLandmark"].push(results.poseLandmarks);
        joint_list["worldLandmark"].push(results.poseWorldLandmarks);
        joint_list["time"].push((new Date().getTime())/1000 - start_time);
        // console.log(time);
    };

    // Restores the most recently saved canvas state by popping the top entry in the drawing state stack
    canvasCtx.restore();
}