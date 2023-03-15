const elem_dict = {
    // Admin Plot Elements
    "dist_data":{
        "title": "Dist Status VS Distance",
        "x_axis": "Time (s)",
        "y_axis": "Dist Status"
    },
    "encoder_data":{
        "title": "Distance VS Time",
        "x_axis": "Time (s)",
        "y_axis": "Distance (m)"
    },
    "hiplen_data":{
        "title": "Hip Length VS Time",
        "x_axis": "Time (s)",
        "y_axis": "Hip Length (Pixel)"
    },
    "velocity_data":{
        "title": "Velocity VS Time",
        "x_axis": "Time (s)",
        "y_axis": "Velocity (m/s)"
    }
}

const horizontalDottedLine = {
    id: 'horizontalDottedLine',
    beforeDatasetsDraw(chart, args, options){
        const { ctx , chartArea: { top, right, bottom, left, width, height},
            scales: {x,y}} = chart;
        ctx.save();

        ctx.strokeStyle = 'grey';
        ctx.setLineDash([5, 10]);
        ctx.strokeRect(left, y.getPixelForValue(0.15), width, 0);
        ctx.restore();
    }
}

const upperBound = {
    id: 'horizontalDottedLine',
    beforeDatasetsDraw(chart, args, options){
        const { ctx , chartArea: { top, right, bottom, left, width, height},
            scales: {x,y}} = chart;
        ctx.save();

        ctx.strokeStyle = 'red';
        ctx.setLineDash([5, 10]);
        ctx.strokeRect(left, y.getPixelForValue(0.15 * 1.05), width, 0);
        ctx.restore();
    }
}

const lowerBound = {
    id: 'horizontalDottedLine',
    beforeDatasetsDraw(chart, args, options){
        const { ctx , chartArea: { top, right, bottom, left, width, height},
            scales: {x,y}} = chart;
        ctx.save();

        ctx.strokeStyle = 'blue';
        ctx.setLineDash([5, 10]);
        ctx.strokeRect(left, y.getPixelForValue(0.15 * 0.8), width, 0);
        ctx.restore();
    }
}

function admin_plot(stats, elem){
    config = elem_dict[elem.id];

    console.log(stats);
    
    if (elem.id == "encoder_data"){
        encoder_one = []
        encoder_two = []

        for (i=0; i < stats["encoder_one"]["dist"].length; i++){
            encoder_one.push({
                x: stats["encoder_one"]["time"][i],
                y: stats["encoder_one"]["dist"][i] 
            });
        };
        
        for (i=0; i < stats["encoder_two"]["dist"].length; i++){
            encoder_two.push({
                x: stats["encoder_two"]["time"][i],
                y: stats["encoder_two"]["dist"][i]
            });
        };

        data = {
            datasets: [{
                label: "Encoder One (Right Motor)",
                data: encoder_one,
                tension: 0.25,
                borderWidth: 1,
                radius: 1,
                showLine: true
            },
            {
                label: "Encoder Two (Left Motor)",
                data: encoder_two,
                tension: 0.25,
                borderWidth: 1,
                radius: 1,
                showLine: true
            }]
        };
    }
    else if (elem.id == "velocity_data"){
        encoder_one = []
        encoder_two = []

        for (i=0; i < stats["encoder_one"]["velocity"].length; i++){
            encoder_one.push({
                x: stats["encoder_one"]["time"][i],
                y: stats["encoder_one"]["velocity"][i] 
            });
        };
        
        for (i=0; i < stats["encoder_two"]["velocity"].length; i++){
            encoder_two.push({
                x: stats["encoder_two"]["time"][i],
                y: stats["encoder_two"]["velocity"][i]
            });
        };

        data = {
            datasets: [{
                label: "Encoder One (Right Motor)",
                data: encoder_one,
                tension: 0.25,
                borderWidth: 1,
                radius: 1,
                showLine: true
            },
            {
                label: "Encoder Two (Left Motor)",
                data: encoder_two,
                tension: 0.25,
                borderWidth: 1,
                radius: 1,
                showLine: true
            }]
        };
    }
    else{
        dataset = []

        for(i=0; i < stats["hiplen"]["hiplen"].length; i++){
            dataset.push({
                x: stats["hiplen"]["time"][i],
                y: stats["hiplen"]["hiplen"][i]
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
    };
    
    console.log(data);

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
                legend:{
                    display: true
                }
            }
        }
    };

    if (elem.id == "hiplen_data"){
        data_config.options.plugins.legend.display = false;
        data_config["plugins"] = [upperBound, lowerBound];
    }

    // Rendering block
    var chart = new Chart(
        elem,
        data_config
    );

};