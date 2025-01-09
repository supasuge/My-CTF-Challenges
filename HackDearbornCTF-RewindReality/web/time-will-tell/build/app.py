#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from flask import Flask, request, jsonify, render_template
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
import gevent
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
from functools import wraps

# Initialize Flask app
app: Flask = Flask(__name__)
app.secret_key = os.urandom(16).hex()

# Read flag from file
FLAG: str = open("flag.txt").read().strip()

# 16-Byte token -> Hex
SECRET_TOKEN: str = os.urandom(16).hex()

# Magic number used for strcmp, it's magic trust me bro
MAGIC_NUMBER: float = 0.19

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10000 per minute", "1000000 per day"], 
    app=app,
    storage_uri="memory://",
)

def strcmp(s1: str, s2: str) -> bool:
    """
    Compares two strings in a "time-constant" manner 😉

    Args:
        s1 (str): First string.
        s2 (str): Second string.

    Returns:
        bool: True if strings are identical, False otherwise.
    """
    if len(s1) != len(s2):
        return False
    for c1, c2 in zip(s1, s2):
        if c1 != c2:
            return False
        gevent.sleep(MAGIC_NUMBER)  # Magic performed
    return True

def get_date() -> str:
    """
    Returns the current date in 'YYYY-MM-DD' format.

    Returns:
        str: Current date.
    """
    return datetime.today().strftime('%Y-%m-%d')

def get_time_12hr() -> str:
    """
    Returns the current time in 12-hour format with AM/PM.

    Returns:
        str: Current time in 12-hour format.
    """
    return datetime.today().strftime('%I:%M:%S %p')

def get_time_24hr() -> str:
    """
    Returns the current time in 24-hour format.

    Returns:
        str: Current time in 24-hour format.
    """
    return datetime.today().strftime('%H:%M:%S')

def get_time_date() -> str:
    """
    Returns the current date and time in 12-hour format.

    Returns:
        str: Current date and time.
    """
    return f"{get_date()} {get_time_12hr()}"

def require_tx_token(f):
    """
    Decorator to enforce TX-TOKEN authentication on the admin panel.

    Args:
        f (function): The route function to decorate.

    Returns:
        function: The decorated function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('TX-TOKEN')
        content_type = request.headers.get('Content-Type')

        if content_type != 'application/json':
            return jsonify({"error": "Invalid content type"}), 400

        if not token:
            return jsonify({"error": "Missing TX-TOKEN header"}), 400

        if strcmp(token, SECRET_TOKEN):
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Invalid token received"}), 403
    return decorated

# Define allowed commands globally
allowed_commands = {
    "get_time.12": get_time_12hr,
    "get_time.24": get_time_24hr,
    "get_date": get_date,
    "get_time_date": get_time_date,
    "get_help": lambda: (
        "Available commands:\n"
        "- get_time.12: Get current time in 12-hour format with AM/PM.\n"
        "- get_time.24: Get current time in 24-hour format.\n"
        "- get_date: Get current date.\n"
        "- get_time_date: Get current date and time in 12-hour format.\n"
        "- get_help: Get this help message.\n"
        "- helpful_hint: Receive a helpful hint."
    ),
    "helpful_hint": lambda: (
        "Hint: Use the 'get_time.12' and 'get_time.24' commands to observe time discrepancies. "
        "Though you may need to be a lot more specific with your timing requests, Good luck!"
    )
}

@app.route("/")
def index():
    """
    Renders the index.html template which serves as API documentation.

    Returns:
        Template: Rendered index.html.
    """
    return render_template("index.html")

@app.route("/get-options", methods=["GET"])
@limiter.limit("10000 per minute", override_defaults=False)
def get_options():
    """
    Returns a list of allowed commands.

    Returns:
        JSON: List of allowed command names.
    """
    command_names = list(allowed_commands.keys())
    return jsonify({"allowed_commands": command_names}), 200

@app.route("/cmd", methods=["POST"])
@limiter.limit("10000 per minute", override_defaults=False)
def cmd():
    """
    Executes a specified command.

    Expected JSON Body:
        {
            "cmd": "command_name"
        }

    Returns:
        JSON: Result of the executed command.
    """
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Invalid content type"}), 400

    data = request.get_json()
    if 'cmd' not in data:
        return jsonify({"error": "Missing 'cmd' parameter"}), 400

    command = data['cmd']

    if command not in allowed_commands:
        return jsonify({"error": "Invalid command"}), 400

    # Execute the corresponding function or lambda using match-case
    match command:
        case "get_time.12":
            current_time = allowed_commands[command]()
            return jsonify({"current_time_12hr": current_time}), 200

        case "get_time.24":
            current_time = allowed_commands[command]()
            return jsonify({"current_time_24hr": current_time}), 200

        case "get_date":
            current_date = allowed_commands[command]()
            return jsonify({"current_date": current_date}), 200

        case "get_time_date":
            current_time_date = allowed_commands[command]()
            return jsonify({"current_time_date": current_time_date}), 200

        case "get_help":
            help_message = allowed_commands[command]()
            return jsonify({"help": help_message}), 200

        case "helpful_hint":
            hint_message = allowed_commands[command]()
            return jsonify({"hint": hint_message}), 200

        case _:
            return jsonify({"error": "Unhandled command"}), 400

@app.route("/adminpanel", methods=["POST"])
@require_tx_token
def protected():
    """
    Returns the flag in JSON format if the correct TX-TOKEN header is provided and matches the SECRET_TOKEN.

    Headers:
        TX-TOKEN: <secret_token>
        Content-Type: application/json

    Returns:
        JSON: Contains the flag if authenticated.
    """
    return jsonify({"flag": FLAG}), 200

@app.errorhandler(429)
def ratelimit_handler(e):
    """
    Handles rate limit exceed errors.

    Args:
        e (Exception): The exception raised.

    Returns:
        JSON: Error message indicating rate limit exceeded.
    """
    return jsonify(error=f"ratelimit exceeded {e.description}"), 429

if __name__ == "__main__":
    # WSGI server for better concurrency handling
    http_server = WSGIServer(('0.0.0.0', 8000), app)
    http_server.serve_forever()
