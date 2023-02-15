const elem_dict = {
    // Graphical Plot Elements
    "raw_data": {
        "statskey": "rawData",
        "title": "Raw Data of Heel",
        "x_axis": "time (sec)",
        "y_axis": "y-coordinate of Heel"
    },
    "segregate_data": {
        "statskey": "rawGaitCycle",
        "title": "Segregation of Gait Cycle",
        "x_axis": "time (sec)",
        "y_axis": "y-coordinate of Heel"
    },
    "scatter_data": {
        "statskey": "superGaitCycle",
        "title": "Scatterplot of Identified Gait Cycles",
        "x_axis": "Gait Cycle (%)",
        "y_axis": "y-coordinate of Heel"
    },
    "shoulder_angle":{
        "statskey": "shoulder",
        "title": "Shoulder",
        "x_axis": "Gait Cycle (%)",
        "y_axis": "Shoulder Angle (Degree)"
    },
    "shoulder_angle_best":{
        "statskey": "bestshoulder",
        "title": "Best Fit Curve of Shoulder Angle",
        "x_axis": "Gait Cycle (%)",
        "y_axis": "Shoulder Angle (Degree)"
    },
    "hip_angle": {
        "statskey": "hip_obliq",
        "title": "Hip" ,
        "x_axis": "Gait Cycle (%)",
        "y_axis": "Hip Angle (Degree)"  
    },
    "hip_angle_best":{
        "statskey": "besthip",
        "title": "Best Fit Curve of Hip Angle",
        "x_axis": "Gait Cycle (%)",
        "y_axis": "Hip Angle (Degree)"  
    },
    "hip_flex":{
        "statskey": "hipflex",
        "title": "Hip Flex" ,
        "x_axis": "Gait Cycle (%)" ,
        "y_axis": "Hip Flex (Degree)" 
    },
    "hip_best":{
        "statskey": "besthip",
        "title": "Best Fit Curve of Hip Flex" ,
        "x_axis": "Gait Cycle (%)" ,
        "y_axis": "Hip Flex (Degree)" 
    },
    "knee_flex":{
        "statskey": "kneeflex",
        "title": "Knee Flex" ,
        "x_axis": "Gait Cycle (%)",
        "y_axis": "Knee Flex (Degree)"  
    },
    "knee_best":{
        "statskey": "bestknee",
        "title": "Best Fit Curve of Knee Flex" ,
        "x_axis": "Gait Cycle (%)",
        "y_axis": "Knee Flex (Degree)"  
    },
    "ankle_flex":{
        "statskey": "ankleflex",
        "title": "Ankle Flex" ,
        "x_axis": "Gait Cycle (%)",
        "y_axis": "Knee Flex (Degree)"  
    },
    "ankle_best":{
        "statskey": "bestankle",
        "title": "Best Fit Curve of Ankle Flex",
        "x_axis": "Gait Cycle (%)",
        "y_axis": "Knee Flex (Degree)"  
    },
    
    // Statistics Plot Elements
    "cadence":{
        "statskey":"cadence",
        "header": "Cadence",
        "units": "steps/min"
    },
    "speed":{
        "statskey":"speed",
        "header": "Speed",
        "units": "m/sec"
    },
    "distance":{
        "statskey":"dist",
        "header": "Estimated Distance",
        "units": "m"
    },
    "stride_len":{
        "statskey":"stride_len",
        "header": "Estimated Stride Length",
        "units": "m"
    },
}

const horizontalDottedLine = {
    id: 'horizontalDottedLine',
    beforeDatasetsDraw(chart, args, options){
        const { ctx , chartArea: { top, right, bottom, left, width, height},
            scales: {x,y}} = chart;
        ctx.save();

        ctx.strokeStyle = 'grey';
        ctx.setLineDash([5, 10]);
        ctx.strokeRect(left, y.getPixelForValue(0), width, 0);
        ctx.restore();
    }
}

function norm_plot(stats, elem){
    config = elem_dict[elem.id];
    dataset = [];

    console.log(config);

    if (elem.id == "raw_data" || elem.id == "shoulder_angle_best" || elem.id == "hip_angle_best" || elem.id == "hip_best" || elem.id == "knee_best" || elem.id == "ankle_best") {
        for (i=0; i < stats[config["statskey"]]["x"].length; i++){
            dataset.push({
                x: stats[config["statskey"]]["x"][i], 
                y: stats[config["statskey"]]["y"][i]
            });
        };

        data = {
            datasets: [{
                data: dataset,
                tension: 0.25,
                borderWidth: 1,
                radius: 1,
                showLine: true
            }]
        };
    }
    else {
        for (i=0; i < stats[config["statskey"]].length; i++){
            gait_data = [];

            for (x=0; x < stats[config["statskey"]][i]["x"].length; x++){
                gait_data.push({
                    x: stats[config["statskey"]][i]["x"][x], 
                    y: stats[config["statskey"]][i]["y"][x]
                });
            }

            dataset.push({
                data: gait_data,
                tension: 0.25,
                borderWidth: 1,
                radius: 1,
                showLine: true
            });
        };

        data = {
            datasets: dataset
        };
    };
    
    // Config block
    data_config = {
        type: 'scatter',
        data: data,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: config["x_axis"] 
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: config["y_axis"] 
                    },
                }                
            },
            plugins: {
                title:{
                  display: true,
                  text: config["title"] 
                },
                legend: {
                    display: false
                }
            }
        }
    };

    if (elem.id != "raw_data" || elem.id != "segregate_data" || elem.id != "scatter_data"){
        data_config["plugins"] = [horizontalDottedLine];
    }
    // console.log(data, data_config)

    // Rendering block
    var chart = new Chart(
        elem,
        data_config
    );

};

function stats_plot(stats, elem){
    config = elem_dict[elem.id];
    elem.innerHTML = config["header"] + ": " + stats[config["statskey"]] + " " + config["units"];
}
