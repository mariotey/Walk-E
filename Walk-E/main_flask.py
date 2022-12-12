from flask import Flask, render_template, request

app = Flask(__name__)
            
@app.route('/')
def home():
    return render_template("main.html")

@app.route('/Statistics', methods=["GET", "POST"])
def statistics():
    request_data = request.form
    msg = request_data["data"]
    
    return render_template("main.html")

if __name__ == "__main__":
    app.run(port=5000, debug=False)
