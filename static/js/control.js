calibrate_btn = document.getElementById("calibrate");
walkE_btn = document.getElementById("walkEMove");
stats_btn = document.getElementById("stats");

function get_calibrate() {
    if (calibrate_btn.className == "control-panel-entry control-panel-toggle negative") {
        walkE_btn.disabled = false;
        stats_btn.disabled = false;
        calibrate_btn.innerHTML = "Calibrate";

        calibrate_btn.className = "control-panel-entry control-panel-toggle positive";
        walkE_btn.className = "control-panel-entry control-panel-toggle positive";
        stats_btn.className = "control-panel-entry control-panel-toggle positive";

        cali_flag = false;

        console.log("Calibration is stopped.\n");

        ajax_data = {
            poseLandmark: JSON.stringify(calibrate_list["poseLandmark"]),
            worldLandmark: JSON.stringify(calibrate_list["worldLandmark"]),
            time: JSON.stringify(calibrate_list["time"]),
        };

        console.log(ajax_data);

        $.ajax({
            url: '/Recalibrate',
            type: "POST",
            data: ajax_data,
            success: function (result) {
                console.log("Successfully Recalibrated.");
            },
            error: function (request, error) {
                console.log("Error:" + error);
            }
        });

        calibrate_list = {
            "poseLandmark": [],
            "worldLandmark": [],
            "time": [],
        }
    }
    else {
        walkE_btn.disabled = true;
        stats_btn.disabled = true;
        calibrate_btn.innerHTML = "Stop Calibration";

        calibrate_btn.className = "control-panel-entry control-panel-toggle negative";
        walkE_btn.className = "control-panel-entry control-panel-toggle disable";
        stats_btn.className = "control-panel-entry control-panel-toggle disable";

        cali_flag = true;

        console.log("Recalibrating...");
    }
};

function walkE_move() {
    if (walkE_btn.className == "control-panel-entry control-panel-toggle negative") {
        calibrate_btn.disabled = false;
        stats_btn.disabled = false;
        walkE_btn.innerHTML = "Start";

        calibrate_btn.className = "control-panel-entry control-panel-toggle positive";
        walkE_btn.className = "control-panel-entry control-panel-toggle positive";
        stats_btn.className = "control-panel-entry control-panel-toggle positive";

        stats_flag = false;
    }
    else {
        calibrate_btn.disabled = true;
        stats_btn.disabled = true;
        walkE_btn.innerHTML = "Stop";

        calibrate_btn.className = "control-panel-entry control-panel-toggle disable";
        walkE_btn.className = "control-panel-entry control-panel-toggle negative";
        stats_btn.className = "control-panel-entry control-panel-toggle disable";

        stats_flag = true;
    }

    $.ajax({
        url: '/move',
        type: "POST",
        data: { data: JSON.stringify(stats_flag) },
        success: function (result) {
            // calibrate_btn.disabled = false;
            // stats_btn.disabled = false;
            // walkE_btn.innerHTML = "Start";

            // calibrate_btn.className = "control-panel-entry control-panel-toggle positive";
            // walkE_btn.className = "control-panel-entry control-panel-toggle positive";
            // stats_btn.className = "control-panel-entry control-panel-toggle positive";

            // stats_flag = false;             
        },
        error: function (request, error) {
            console.log("Error:" + error);
        }
    });
};

function get_stats() {
    calibrate_btn.disabled = true;
    walkE_btn.disabled = true;
    stats_btn.innerHTML = "Processing...";

    calibrate_btn.className = "control-panel-entry control-panel-toggle disable";
    walkE_btn.className = "control-panel-entry control-panel-toggle disable";
    stats_btn.className = "control-panel-entry control-panel-toggle negative";

    ajax_data = {
        poseLandmark: JSON.stringify(joint_list["poseLandmark"]),
        worldLandmark: JSON.stringify(joint_list["worldLandmark"]),
        time: JSON.stringify(joint_list["time"]),
    };

    console.log(ajax_data);

    $.ajax({
        url: '/GetStats',
        type: "POST",
        data: ajax_data,
        success: function (result) {
            console.log("Successfully Calculated Stats.");

            let a_elem = document.createElement("a");
            a_elem.href = "/PlotStats";
            a_elem.click();
        },
        error: function (request, error) {
            console.log("Error:" + error);
        }
    });
};