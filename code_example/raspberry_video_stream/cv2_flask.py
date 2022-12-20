import cv2
from flask import Flask, Response

video = cv2.VideoCapture(1)
app = Flask('__name__')

def video_stream():
    while True:
        ret, frame = video.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpeg',frame)
            frame = buffer.tobytes()
            yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + frame +b'\r\n')

@app.route('/')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(port='5000', debug=False)