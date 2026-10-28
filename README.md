# Numbers API

A small web API for working with numbers, built for teaching how APIs work.

The operations are deliberately simple (add two numbers, generate a sequence,
sort a list) so the focus stays on the API itself: URLs, HTTP methods, query
parameters, JSON bodies, headers, status codes and authentication.

Live at: <https://numbers.apps.pipal.in>

## What's in it

| Endpoint | Method | What it does | Teaches |
|----------|--------|--------------|---------|
| `/add` | `GET` | Adds two numbers | Query parameters, plain-text responses |
| `/fibs` | `GET` | Generates Fibonacci numbers | Default values, choosing a response format |
| `/random` | `GET` | Generates random numbers | Query parameters, input validation |
| `/range` | `POST` | Generates a range of numbers | Sending a JSON body |
| `/product` | `POST` | Multiplies a list of numbers | JSON in, JSON out |
| `/sum`, `/average` | `POST` | Adds or averages a list of numbers | JSON in, JSON out, errors |
| `/stats` | `POST` | Count, sum, mean, min and max of a list | JSON responses with several fields |
| `/sort` | `POST` | Sorts a list of numbers | JSON in, JSON out |
| `/store` | `GET` `PUT` `DELETE` | Saves named numbers | Resources, HTTP methods, auth tokens, 404s |

## Quick sample

```
$ curl 'https://numbers.apps.pipal.in/add?a=3&b=4'
7

$ curl \
    -H 'Content-Type: application/json' \
    -d '{"numbers": [5, 3, 9, 1]}' \
    https://numbers.apps.pipal.in/sort
{"result":[1,3,5,9]}
```

## Documentation

See **[docs/api.md](docs/api.md)** for the full reference, with parameters,
responses, errors and examples for every endpoint.

## Running locally

```
$ pip install -r requirements.txt
$ flask --app app run
```

The API is then available at `http://127.0.0.1:5000`.
