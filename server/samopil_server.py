import validator
from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/task-json")
def getjson():
    # supposedly, there should be auth AND validation here.
    tbfile = "testbed.json"
    with open(tbfile) as f:
        jsonstr = f.read()
    validator.validate(jsonstr, tbfile)
    resp = make_response(jsonstr)
    resp.headers["Content-Type"] = "application/json"
    return resp

@app.route("/task-json-upload", methods=['POST'])
def postjson():
    request.get_json()
    return """{"code": 0, "status": "All correct"}"""

if __name__ == "__main__":
    app.run()