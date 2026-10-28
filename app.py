import random
import re
from flask import Flask, request, make_response, jsonify, url_for
from werkzeug.exceptions import HTTPException
import numb

app = Flask(__name__)
# keep keys in the order the endpoints build them, e.g. /stats
app.json.sort_keys = False

class APIError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status

@app.errorhandler(APIError)
def api_error(e):
    response = make_response(jsonify({"error": str(e)}), e.status)
    if e.status == 401:
        response.headers["WWW-Authenticate"] = "Bearer"
    return response

@app.errorhandler(HTTPException)
def http_error(e):
    # Flask's own errors (404, 405, ...) are HTML by default
    response = e.get_response()
    response.set_data(jsonify({"error": e.name.lower()}).get_data())
    response.content_type = "application/json"
    return response

def get_int_param(name, default=None):
    value = request.args.get(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        raise APIError(f"{name} must be an integer")

def is_int(value):
    # bool is a subclass of int in Python, but true/false aren't numbers here
    return isinstance(value, int) and not isinstance(value, bool)

def is_number(value):
    return is_int(value) or isinstance(value, float)

def get_json_object():
    if not request.get_data():
        raise APIError("request body is required")
    if not request.is_json:
        raise APIError("Content-Type must be application/json", status=415)
    d = request.get_json(silent=True)
    if d is None:
        raise APIError("request body is not valid JSON")
    if not isinstance(d, dict):
        raise APIError("request body must be a JSON object")
    return d

def get_numbers(d, allow_empty=True):
    if "numbers" not in d:
        raise APIError("numbers is required")
    numbers = d["numbers"]
    if not isinstance(numbers, list):
        raise APIError("numbers must be a list")
    if not all(is_number(n) for n in numbers):
        raise APIError("numbers must contain only numbers")
    if not numbers and not allow_empty:
        raise APIError("numbers must not be empty")
    return numbers

def get_number_field(d, name):
    if name not in d:
        raise APIError(f"{name} is required")
    if not is_number(d[name]):
        raise APIError(f"{name} must be a number")
    return d[name]

def get_int_field(d, name, default):
    value = d.get(name, default)
    if not is_int(value):
        raise APIError(f"{name} must be an integer")
    return value

def text_response(value):
    if isinstance(value, str):
        text = value
    elif hasattr(value, "__iter__"):
        text = "\n".join(str(v) for v in value)
    else:
        text = str(value)

    if not text.endswith("\n"):
        text += "\n"

    response = make_response(text, 200)
    response.mimetype = "text/plain"
    return response

HOME = """
<!doctype html>
<html>
<head>
  <title>Numbers API</title>
  <style type="text/css">

  </style>
</head>
<body>
    <h1>Numbers API</h1>
    <p>
    Simple API to work with numbers.
    </p>

    <h2>Add</h2>
    <p>API to add two numbers.<p>

    <p>Example:</p>
    <a href="/add?a=3&b=4">/add?a=3&b=4</a>

    <h2>Fibs</h2>

    <p>Generates fibonacci numbers.</p>

    <a href="/fibs?a=3&b=4&n=10">/fibs?a=3&b=4&n=10</a>

    <h2>Documentation</h2>
    <p>
    See <a href="https://github.com/anandology/numbers-api">Github repo</a> to know more details about the API.
    </p>
</body>
</html>
"""

@app.route("/")
def home():
    return HOME

@app.route("/add")
def add():
    """Adds two numbers.
    """
    a = get_int_param("a", 0)
    b = get_int_param("b", 0)
    result = a + b
    return text_response(result)

@app.route("/fibs")
def fibs():
    """Returns a sequence of fibonacci numbers.
    """
    a = get_int_param("a", 1)
    b = get_int_param("b", 1)
    n = get_int_param("n", 10)
    numbers = numb.fibs(a, b, n)

    if request.args.get("format") == "json":
        return jsonify({"result": list(numbers)})
    else:
        return text_response(numbers)

@app.route("/random")
def _random():
    """Returns random integers between min and max, inclusive.
    """
    lo = get_int_param("min", 1)
    hi = get_int_param("max", 100)
    count = get_int_param("count", 1)
    if lo > hi:
        raise APIError("min must not be greater than max")
    if not 1 <= count <= 1000:
        raise APIError("count must be between 1 and 1000")
    numbers = [random.randint(lo, hi) for _ in range(count)]

    if request.args.get("format") == "json":
        return jsonify({"result": numbers})
    else:
        return text_response(numbers)

@app.route("/product", methods=["POST"])
def product():
    numbers = get_numbers(get_json_object())
    result = numb.product(numbers)
    return jsonify({"result": result})

@app.route("/sum", methods=["POST"])
def _sum():
    numbers = get_numbers(get_json_object())
    return jsonify({"result": sum(numbers)})

@app.route("/average", methods=["POST"])
def average():
    numbers = get_numbers(get_json_object(), allow_empty=False)
    return jsonify({"result": sum(numbers) / len(numbers)})

@app.route("/stats", methods=["POST"])
def stats():
    numbers = get_numbers(get_json_object(), allow_empty=False)
    return jsonify({
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
    })

@app.route("/range", methods=["POST"])
def _range():
    d = get_json_object()
    start = get_int_field(d, "start", 0)
    stop = get_int_field(d, "stop", 0)
    step = get_int_field(d, "step", 1)
    if step == 0:
        raise APIError("step must not be zero")

    result = list(range(start, stop, step))
    return jsonify({"result": result})

@app.route("/sort", methods=["POST"])
def _sort():
    numbers = get_numbers(get_json_object())
    result = sorted(numbers)
    return jsonify({"result": result})

# Tokens are not secret: anyone can use <username>-token-123.
# This keeps the API easy to use in class while still teaching auth headers.
TOKEN_RE = re.compile(r"^([a-z0-9][a-z0-9_-]{0,31})-token-123$")

def current_user():
    auth = request.headers.get("Authorization", "")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise APIError("missing token, expected header 'Authorization: Bearer <username>-token-123'", status=401)
    match = TOKEN_RE.match(token.strip())
    if not match:
        raise APIError("invalid token, expected <username>-token-123", status=401)
    return match.group(1)

@app.route("/me")
def me():
    return jsonify({"username": current_user()})

# username -> {name: value}
_stores = {}

def user_store():
    return _stores.setdefault(current_user(), {})

@app.route("/store")
def list_values():
    return jsonify(user_store())

@app.route("/store/<name>", methods=["GET"])
def get_value(name):
    store = user_store()
    if name not in store:
        raise APIError(f"{name} not found", status=404)
    return jsonify({"value": store[name]})

@app.route("/store/<name>", methods=["POST"])
def create_value(name):
    store = user_store()
    value = get_number_field(get_json_object(), "value")
    if name in store:
        raise APIError(f"{name} already exists, use PUT to update it", status=409)
    store[name] = value
    response = make_response(jsonify({"value": value}), 201)
    response.headers["Location"] = url_for("get_value", name=name)
    return response

@app.route("/store/<name>", methods=["PUT"])
def update_value(name):
    store = user_store()
    value = get_number_field(get_json_object(), "value")
    if name not in store:
        raise APIError(f"{name} not found, use POST to create it", status=404)
    store[name] = value
    return jsonify({"value": value})

@app.route("/store/<name>", methods=["DELETE"])
def delete_value(name):
    store = user_store()
    if name not in store:
        raise APIError(f"{name} not found", status=404)
    del store[name]
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run()