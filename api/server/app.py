from flask import Flask, session, make_response, jsonify, request
from flask_cors import CORS
import requests

# setup Flask
app = Flask(__name__, instance_relative_config=True)
cors = CORS(app, supports_credentials=True)

# load configuration file
app.logger.info("Loading configuration file")
app.config.from_pyfile("config.py")
app.logger.info("Finished loading configuration file")

@app.before_request
def make_session_permanent():
    session.permanent = True
    
@app.route("/login/<cwid>/<password>", methods=["POST"])
def login(cwid, password):
    r = requests.get(app.config["DB_INTERFACE_URL"] + "/user/login/" + cwid + "/" + password)
    if r.status_code == 200:
        session["cwid"] = cwid
        return make_response(jsonify(message="Login successful"), 200, {"Content-Type": "application/json"})
    elif r.status_code == 401:
        return make_response(jsonify(message="Incorrect password"), 401, {"Content-Type": "application/json"})
    elif r.status_code == 404:
        return make_response(jsonify(message="No user with that cwid exists"), 404, {"Content-Type": "application/json"})

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("cwid", None)
    return make_response(jsonify(message="logged out"), 200, {"Content-Type": "application/json"})
    
@app.route("/sessions/<cwid>", methods=["GET"])
def listSessions(cwid):
    if "cwid" in session and session["cwid"] == cwid:
        r = requests.get(app.config["DB_INTERFACE_URL"] + "/sessions/user/" + cwid)
        if r.status_code == 200:
            return make_response(jsonify(r.json()), 200, {"Content-Type": "application/json"})
        elif r.status_code == 404:
            if r.json()["message"] == "User has no sessions":
                return make_response(jsonify(message="User has no sessions"), 404, {"Content-Type": "application/json"})
            else:
                return make_response(jsonify(message="There is no user with that cwid"), 404, {"Content-Type": "application/json"})
        elif r.status_code == 500:
            return make_response(jsonify(message="Unexpected server error"), 500, {"Content-Type": "application/json"})
    else:
        return make_response(jsonify(message="Not authenticated to make that request"), 401, {"Content-Type": "application/json"})

@app.route("/sessions/shared/<cwid>", methods=["GET"])
def listSharedSessions(cwid):
    if "cwid" in session and session["cwid"] == cwid:
        r = requests.get(app.config["DB_INTERFACE_URL"] + "/sessions/shared/user/" + cwid)
        if r.status_code == 200:
            return make_response(jsonify(r.json()), 200, {"Content-Type": "application/json"})
        elif r.status_code == 204:
            return make_response(jsonify(message="User has no sessions"), 204, {"Content-Type": "application/json"})
        elif r.status_code == 404:
            return make_response(jsonify(message="There is no user with that cwid"), 404, {"Content-Type": "application/json"})
        elif r.status_code == 500:
            return make_response(jsonify(message="Unexpected server error"), 500, {"Content-Type": "application/json"})
    else:
        return make_response(jsonify(message="Not authenticated to make that request"), 401, {"Content-Type": "application/json"})

@app.route("/sessions/get/<cwid>/<sessionNumber>", methods=["GET"])
def getSession(cwid, sessionNumber):
    if "cwid" in session and session["cwid"] == cwid:
        r = requests.get(app.config["DB_INTERFACE_URL"] + "/getSession/" + cwid + "/" + sessionNumber)
        if r.status_code == 200:
            return make_response(jsonify(r.json()), 200, {"Content-Type": "application/json"})
        elif r.status_code == 404:
            return make_response(jsonify(message="There is no session with that session number"), 404, {"Content-Type": "application/json"})
        elif r.status_code == 500:
            return make_response(jsonify(message="Unexpected server error"), 500, {"Content-Type": "application/json"})
    else:
        return make_response(jsonify(message="Not authenticated to make that request"), 401, {"Content-Type": "application/json"})

@app.route("/users/create/<cwid>/<name>/<password>", methods=["POST"])
def createUser(cwid, name, password):
    r = requests.post(app.config["DB_INTERFACE_URL"] + "/create/user/" + cwid + "/" + name + "/" + password)
    if r.status_code == 201:
        return make_response(jsonify(message="Successfully created user"), 201, {"Content-Type": "application/json"})
    elif r.status_code == 409:
        return make_response(jsonify(message="There is already a user with that cwid"), 409, {"Content-Type": "application/json"})
    elif r.status_code == 500:
        return make_response(jsonify(message="Unexpected server error"), 500, {"Content-Type": "application/json"})

@app.route("/sessions/create", methods=["POST"])
def createSession():
    if "cwid" in session:
        data = request.get_json()
        if data is not None:
            requestData = {"cwid": session["cwid"], "description": data["description"], "data": data["data"], "length": data["length"], "width": data["width"]}
            r = requests.post(app.config["DB_INTERFACE_URL"] + "/create/session", json=requestData)
            if r.status_code == 201:
                return make_response(jsonify(message="Successfully created the session"), 201, {"Content-Type": "application/json"})
            elif r.status_code == 400:
                if r.json()["message"] == "No data received or not interpreted":
                    return make_response(jsonify(message="No data received or not interpreted"), 400, {"Content-Type": "application/json"})
                else:
                    return make_response(jsonify(message="The number of sensors did not match the length and width"), 400, {"Content-Type": "application/json"})
            elif r.status_code == 500:
                return make_response(jsonify(message="Unexpected server error"), 500, {"Content-Type": "application/json"})
        else:
            return make_response(jsonify(message="No data received or not interpreted"), 400, {"Content-Type": "application/json"})
    else:
        return make_response(jsonify(message="Not authenticated to make that request"), 401, {"Content-Type": "application/json"})

@app.route("/sessions/share/<sessionCWID>/<sessionNumber>/<shareToCWID>", methods=["POST"])
def shareSession(sessionCWID, sessionNumber, shareToCWID):
    if "cwid" in session and session["cwid"] == sessionCWID:
        r = requests.post(app.config["DB_INTERFACE_URL"] + "/create/sharedSession/" + sessionCWID + "/" + sessionNumber + "/" + shareToCWID)
        if r.status_code == 201:
            return make_response(jsonify(message="Successfully shared the session"), 201, {"Content-Type": "application/json"})
        elif r.status_code == 400:
            return make_response(jsonify(message="Cannot share a session with yourself"), 400, {"Content-Type": "application/json"})
        elif r.status_code == 409:
            return make_response(jsonify(message="Session has already been shared to that user or the session or cwid does not exist"), 409, {"Content-Type": "application/json"})
        elif r.status_code  ==  500:
            return make_response(jsonify(message="Unexpected server error"), 500, {"Content-Type": "application/json"})
    else:
        return make_response(jsonify(message="Not authenticated to make that request"), 401, {"Content-Type": "application/json"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='4000')