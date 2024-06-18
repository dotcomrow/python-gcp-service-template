from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
import google.cloud.logging
import logging
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from handlers import handle_get

logClient = google.cloud.logging.Client()
logClient.setup_logging()

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']
context_root = app.config['CONTEXT_ROOT']

cors = CORS(app, resources={
    r"/*": {"origins": "*"},
    # r"/login": {"origins": "*"},
}, supports_credentials=True)
         
def authorized_user_decorator(func):
    def inner(*args, **kwargs):
        try:
            token = request.headers.get('Authorization').split(" ")[1]
            user = id_token.verify_oauth2_token(token, requests.Request(), app.config['AUDIENCE'])
            kwargs["user"]= user
        except Exception as e:
            logging.error("Error: " + str(e))
            return Response(response=json.dumps({'message': 'Unauthorized'}), status=401, mimetype="application/json")
 
        return func(*args, **kwargs)

    inner.__name__ = func.__name__
    return inner

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()

@app.route("/" + context_root, methods=['GET'])
@cross_origin(supports_credentials=True)
@authorized_user_decorator
def get(**kwargs):
    user =  kwargs.get("user")
    return handle_get(user, app)

if __name__ == "__main__":
    # Development only: run "python main.py" and open http://localhost:8080
    # When deploying to Cloud Run, a production-grade WSGI HTTP server,
    # such as Gunicorn, will serve the app.
    app.run(host="localhost", port=8080, debug=True)