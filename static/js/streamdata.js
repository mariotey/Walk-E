function handleNewData() {
    // the response text include the entire response so far
    // split the messages, then take the messages that haven't been handled yet
    // position tracks how many messages have been handled
    // messages end with a newline, so split will always show one extra empty message at the end
    console.log(xhr);

    var messages = xhr.responseText.split('\n');
    console.log(messages);

    messages.slice(position, -1).forEach(function (value) {
        latest.textContent = value;  // update the latest value in place
        // build and append a new item to a list to log all output
        var item = document.createElement('li');
        item.textContent = value;
        output.appendChild(item);
    });

    position = messages.length - 1;
}
