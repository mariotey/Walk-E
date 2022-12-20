import cv2
import numpy
from flask import Flask, render_template, Response, stream_with_context, request

camera = cv2.VideoCapture(0)
app = Flask('__name__', template_folder='./code_example/raspberry_videostream/templates')


def video_stream():
    while True:
        
        # Read camera frame
        ret, frame = camera.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpeg',frame)
            frame = buffer.tobytes()

        # "return" will only return one image
        yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + frame +b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(port='5000', debug=False)