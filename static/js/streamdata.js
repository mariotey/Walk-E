var latest = document.getElementById('latest');
var output = document.getElementById('output');
var timer;

var position = 0;

function stream_data(xhr){
    timer = setInterval(function () {
        // check the response for new data
        // the response text include the entire response so far
        // split the messages, then take the messages that haven't been handled yet
        // position tracks how many messages have been handled
        // messages end with a newline, so split will always show one extra empty message at the end

        var messages = xhr.responseText.split('\n');

        messages.slice(position, -1).forEach(function (value) {
            latest.textContent = value;  // update the latest value in place
            
            // build and append a new item to a list to log all output
            var item = document.createElement('li');
            item.textContent = value;

            if (value != "" || value != "null") {
            console.log(JSON.parse(value));
            }

            output.appendChild(item);
        });

        position = messages.length - 1;

        // stop checking once the response has ended
        if (xhr.readyState == XMLHttpRequest.DONE) {
            clearInterval(timer);
            latest.textContent = 'Done';
        }
    }, 1000);
};