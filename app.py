import random
from flask import Flask, request, make_response, jsonify
from werkzeug.exceptions import HTTPException
import numb

app = Flask(__name__)
# keep keys in the order the endpoints build them, e.g. /stats
app.json.sort_keys = False

class InvalidInput(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status

@app.errorhandler(InvalidInput)
def invalid_input(e):
    return make_response(jsonify({"error": str(e)}), e.status)

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
        raise InvalidInput(f"{name} must be an integer")

def is_int(value):
    # bool is a subclass of int in Python, but true/false aren't numbers here
    return isinstance(value, int) and not isinstance(value, bool)

def is_number(value):
    return is_int(value) or isinstance(value, float)

def get_json_object():
    if not request.get_data():
        raise InvalidInput("request body is required")
    if not request.is_json:
        raise InvalidInput("Content-Type must be application/json", status=415)
    d = request.get_json(silent=True)
    if d is None:
        raise InvalidInput("request body is not valid JSON")
    if not isinstance(d, dict):
        raise InvalidInput("request body must be a JSON object")
    return d

def get_numbers(d, allow_empty=True):
    if "numbers" not in d:
        raise InvalidInput("numbers is required")
    numbers = d["numbers"]
    if not isinstance(numbers, list):
        raise InvalidInput("numbers must be a list")
    if not all(is_number(n) for n in numbers):
        raise InvalidInput("numbers must contain only numbers")
    if not numbers and not allow_empty:
        raise InvalidInput("numbers must not be empty")
    return numbers

def get_int_field(d, name, default):
    value = d.get(name, default)
    if not is_int(value):
        raise InvalidInput(f"{name} must be an integer")
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
        raise InvalidInput("min must not be greater than max")
    if not 1 <= count <= 1000:
        raise InvalidInput("count must be between 1 and 1000")
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
        raise InvalidInput("step must not be zero")

    result = list(range(start, stop, step))
    return jsonify({"result": result})

@app.route("/sort", methods=["POST"])
def _sort():
    numbers = get_numbers(get_json_object())
    result = sorted(numbers)
    return jsonify({"result": result})

_store = {}

@app.route("/store")
def list_values():
    return jsonify(_store)

def check_token():
    auth = request.headers.get("Authorization", "")
    return auth.lower() == "bearer abcd1234"

def unauthorized():
    response = make_response(jsonify({"error": "unauthorized"}), 401)
    response.headers["WWW-Authenticate"] = "Bearer"
    return response

@app.route("/store/<name>", methods=["PUT"])
def put_value(name):
    if not check_token():
        return unauthorized()
    value = get_int_field(get_json_object(), "value", None)
    _store[name] = value
    return jsonify({"ok": True})

@app.route("/store/<name>", methods=["DELETE"])
def delete_value(name):
    if not check_token():
        return unauthorized()

    _store.pop(name, None)
    return jsonify({"ok": True})

@app.route("/store/<name>", methods=["GET"])
def get_value(name):
    if name not in _store:
        return make_response(jsonify({"error": "not found"}), 404)
    value = _store[name]
    return jsonify({"value": value})

if __name__ == "__main__":
    app.run()