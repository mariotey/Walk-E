
function raw_data(stats, elem){
    // Setup block
    var dataset = [];

    for (i=0; i < stats["rawData"]["x"].length; i++){
        dataset.push({
            x: stats["rawData"]["x"][i], 
            y: stats["rawData"]["y"][i]
        });
    };

    const raw_data = {
        datasets: [{
            data: dataset,
            tension: 0.25,
            borderWidth: 1,
            radius: 1,
            showLine: true
        }]
    };

    // Config block
    const raw_data_config = {
        type: 'scatter',
        data: raw_data,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: "time (sec)"  
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: "y-coordinate of Heel"  
                    },
                }                
            },
            plugins: {
                title:{
                  display: true,
                  text: "Raw Data of Heel"  
                },
                legend: {
                    display: false
                }
            }
        }
    };

    // Rendering block
    var chart = new Chart(
        elem,
        raw_data_config
    );
};

function segre_data(stats, elem){
    // Setup block
    var dataset = [];

    for (i=0; i < stats["rawGaitCycle"].length; i++){
        
        gait_data = [];

        for (x=0; x < stats["rawGaitCycle"][i]["x"].length; x++){
            gait_data.push({
                x: stats["rawGaitCycle"][i]["x"][x], 
                y: stats["rawGaitCycle"][i]["y"][x]
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

    const segre_data = {
        datasets: dataset
    };

    // Config block
    const segre_data_config = {
        type: 'scatter',
        data: segre_data,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: "time (sec)"  
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: "y-coordinate of Heel"  
                    },
                }                
            },
            plugins: {
                title:{
                    display: true,
                    text: "Segregation of Gait Cycle"  
                },
                legend: {
                    display: false
                },
            }
        }
    };

    // Rendering block
    var chart = new Chart(
        elem,
        segre_data_config
    );
};

function supergait_data(stats, elem){
    // Setup block
    var dataset = [];

    for (i=0; i < stats["superGaitCycle"].length; i++){
        
        gait_data = [];

        for (x=0; x < stats["superGaitCycle"][i]["x"].length; x++){
            gait_data.push({
                x: stats["superGaitCycle"][i]["x"][x], 
                y: stats["superGaitCycle"][i]["y"][x]
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

    const supergait_data = {
        datasets: dataset
    };

    // Config block
    const supergait_data_config = {
        type: 'scatter',
        data: supergait_data,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: "Gait Cycle (%)" 
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: "y-coordinate of Heel"  
                    },
                }                
            },
            plugins: {
                title:{
                    display: true,
                    text: "Scatterplot of Identified Gait Cycles" 
                },
                legend: {
                    display: false
                },
            }
        }
    };

    // Rendering block
    var chart = new Chart(
        elem,
        supergait_data_config
    );
};

/////////////////////////////////////////////////////////////////////////////////////////////////

function hipflex_data(stats, elem, best_elem){
    // Setup block
    var dataset = [];
    var bestfit_data = [];

    for (i=0; i < stats["hipflex"].length; i++){
        
        var gait_data = [];

        for (x=0; x < stats["hipflex"][i]["x"].length; x++){
            gait_data.push({
                x: stats["hipflex"][i]["x"][x], 
                y: stats["hipflex"][i]["y"][x]
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

    for (x=0; x < stats["besthip"]["x"].length; x++){       
        bestfit_data.push({
            x: stats["besthip"]["x"][x], 
            y: stats["besthip"]["y"][x]
        });
    }  

    const hipflex_data = {
        datasets: dataset
    };

    const hipflex_best = {
        datasets: [{
            data: bestfit_data,
            tension: 0.25,
            borderWidth: 1,
            radius: 1,
            showLine: true
        }]
    };

    const horizontalDottedLine = {
        id: 'horizontalDottedLine',
        beforeDatasetsDraw(chart, args, options){
            const { ctx , chartArea: { top, right, bottom, left, width, height},
                scales: {x,y}} = chart;
            ctx.save();

            ctx.strokeStyle = 'grey';
            ctx.setLineDash([10, 10]);
            ctx.strokeRect(left, y.getPixelForValue(0), width, 0);
            ctx.restore();
        }
    }
    // Config block
    const hipflex_data_config = {
        type: 'scatter',
        data: hipflex_data,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: "Gait Cycle (%)" 
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: "Hip Flex (Degree)"  
                    },
                }                
            },
            plugins: {
                title:{
                    display: true,
                    text: "Hip Flex" 
                },
                legend: {
                    display: false,
                },
            }
        },
        plugins: [horizontalDottedLine]
    };

    const hipflex_bestfit_config = {
        type: 'scatter',
        data: hipflex_best,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: "Gait Cycle (%)" 
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: "Hip Flex (Degree)"  
                    },
                }                
            },
            plugins: {
                title:{
                    display: true,
                    text: "Best Fit Curve of Hip Flex" 
                },
                legend: {
                    display: false,
                },
            }
        },
        plugins: [horizontalDottedLine]
    };

    
    // Rendering block
    var chart = new Chart(
        elem,
        hipflex_data_config
    );

    var best_chart = new Chart(
        best_elem,
        hipflex_bestfit_config
    );
};

function kneeflex_data(stats, elem, best_elem){
    // Setup block
    var dataset = [];
    var bestfit_data = [];

    for (i=0; i < stats["kneeflex"].length; i++){
        
        gait_data = [];

        for (x=0; x < stats["kneeflex"][i]["x"].length; x++){
            gait_data.push({
                x: stats["kneeflex"][i]["x"][x], 
                y: stats["kneeflex"][i]["y"][x]
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

    for (x=0; x < stats["bestknee"]["x"].length; x++){       
        bestfit_data.push({
            x: stats["bestknee"]["x"][x], 
            y: stats["bestknee"]["y"][x]
        });
    }  

    const kneeflex_data = {
        datasets: dataset
    };

    const kneeflex_best = {
        datasets: [{
            data: bestfit_data,
            tension: 0.25,
            borderWidth: 1,
            radius: 1,
            showLine: true
        }]
    };

    const horizontalDottedLine = {
        id: 'horizontalDottedLine',
        beforeDatasetsDraw(chart, args, options){
            const { ctx , chartArea: { top, right, bottom, left, width, height},
                scales: {x,y}} = chart;
            ctx.save();

            ctx.strokeStyle = 'grey';
            ctx.setLineDash([10, 10]);
            ctx.strokeRect(left, y.getPixelForValue(0), width, 0);
            ctx.restore();
        }
    }

    // Config block
    const kneeflex_data_config = {
        type: 'scatter',
        data: kneeflex_data,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: "Gait Cycle (%)" 
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: "Knee Flex (Degree)"  
                    },
                }                
            },
            plugins: {
                title:{
                    display: true,
                    text: "Knee Flex" 
                },
                legend: {
                    display: false
                },
            }
        },
        plugins: [horizontalDottedLine]
    };

    const kneeflex_bestfit_config = {
        type: 'scatter',
        data: kneeflex_best,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: "Gait Cycle (%)" 
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: "Knee Flex (Degree)"  
                    },
                }                
            },
            plugins: {
                title:{
                    display: true,
                    text: "Best Fit Curve of Knee Flex" 
                },
                legend: {
                    display: false,
                },
            }
        },
        plugins: [horizontalDottedLine]
    };

    // Rendering block
    var chart = new Chart(
        elem,
        kneeflex_data_config
    );

    var best_chart = new Chart(
        best_elem,
        kneeflex_bestfit_config
    );
};

function ankleflex_data(stats, elem, best_elem){
    // Setup block
    var dataset = [];
    var bestfit_data = [];

    for (i=0; i < stats["ankleflex"].length; i++){
        
        gait_data = [];

        for (x=0; x < stats["ankleflex"][i]["x"].length; x++){
            gait_data.push({
                x: stats["ankleflex"][i]["x"][x], 
                y: stats["ankleflex"][i]["y"][x]
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

    for (x=0; x < stats["bestankle"]["x"].length; x++){       
        bestfit_data.push({
            x: stats["bestankle"]["x"][x], 
            y: stats["bestankle"]["y"][x]
        });
    }  

    const ankleflex_data = {
        datasets: dataset
    };

    const ankleflex_best = {
        datasets: [{
            data: bestfit_data,
            tension: 0.25,
            borderWidth: 1,
            radius: 1,
            showLine: true
        }]
    };

    const horizontalDottedLine = {
        id: 'horizontalDottedLine',
        beforeDatasetsDraw(chart, args, options){
            const { ctx , chartArea: { top, right, bottom, left, width, height},
                scales: {x,y}} = chart;
            ctx.save();

            ctx.strokeStyle = 'grey';
            ctx.setLineDash([10, 10]);
            ctx.strokeRect(left, y.getPixelForValue(0), width, 0);
            ctx.restore();
        }
    }

    // Config block
    const ankleflex_data_config = {
        type: 'scatter',
        data: ankleflex_data,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: "Gait Cycle (%)" 
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: "Ankle Flex (Degree)"  
                    },
                }                
            },
            plugins: {
                title:{
                    display: true,
                    text: "Ankle Flex" 
                },
                legend: {
                    display: false
                },
            }
        },
        plugins: [horizontalDottedLine]
    };

    const ankleflex_bestfit_config = {
        type: 'scatter',
        data: ankleflex_best,
        options: {
            scales:{
                x:{ 
                    title:{
                        display: true,
                        text: "Gait Cycle (%)" 
                    },
                },
                y:{ 
                    title:{
                        display: true,
                        text: "Ankle Flex (Degree)"  
                    },
                }                
            },
            plugins: {
                title:{
                    display: true,
                    text: "Best Fit Curve of Ankle Flex" 
                },
                legend: {
                    display: false,
                },
            }
        },
        plugins: [horizontalDottedLine]
    };

    // Rendering block
    var chart = new Chart(
        elem,
        ankleflex_data_config
    );

    var best_chart = new Chart(
        best_elem,
        ankleflex_bestfit_config
    );
};