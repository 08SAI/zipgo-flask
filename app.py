# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "ZipGo Quick Commerce service running\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=12184)
