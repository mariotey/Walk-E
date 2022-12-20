import cv2
from flask import Flask, Response, render_template, stream_with_context, request

app = Flask(__name__)
video = cv2.VideoCapture(0)

def video_stream():
    while True:
        # Read camera frame
        ret, frame = video.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpeg',frame)
            frame = buffer.tobytes()

            # return only return one image
            yield (b' --frame\r\n' 
                    b'Content-type: imgae/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def index():
    return render_template('index.html')

@app.route('/')
def video():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)