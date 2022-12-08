import cv2
from flask import Flask, render_template, Response

video = cv2.VideoCapture(0)
app = Flask(__name__)
            
@app.route('/')
def home():
    return "I will be writing a new homepage for Walk-E."

if __name__ == "__main__":
    app.run(port=5000, debug=False)
