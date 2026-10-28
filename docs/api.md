# Numbers API Reference

Base URL: `https://numbers.apps.pipal.in`

All examples use [`curl`](https://curl.se/). Add `-i` to any command to see the
status code and headers along with the body.

## Contents

- [Basics](#basics)
- [Add](#add) — `GET /add`
- [Fibs](#fibs) — `GET /fibs`
- [Random](#random) — `GET /random`
- [Range](#range) — `POST /range`
- [Product](#product) — `POST /product`
- [Sum](#sum) — `POST /sum`
- [Average](#average) — `POST /average`
- [Stats](#stats) — `POST /stats`
- [Sort](#sort) — `POST /sort`
- [Authentication](#authentication)
- [Me](#me) — `GET /me`
- [Store](#store) — `GET`, `POST`, `PUT`, `DELETE /store/<name>`
- [Errors](#errors)

## Basics

The API uses two styles of request, so you can learn both.

| Style | Endpoints | How you send input | What you get back |
|-------|-----------|--------------------|-------------------|
| Query parameters | `/add`, `/fibs`, `/random` | In the URL: `?a=3&b=4` | Plain text (JSON optional for `/fibs` and `/random`) |
| JSON body | `/range`, `/product`, `/sum`, `/average`, `/stats`, `/sort`, `/store` | `POST`/`PUT` with a JSON body | JSON |
| Token | `/me`, `/store` | An `Authorization` header | JSON |

When sending a JSON body, you must set the `Content-Type` header:

```
-H 'Content-Type: application/json'
```

Without it, the server responds with `415 Unsupported Media Type`.

Errors are always JSON with an `error` field. See [Errors](#errors).

`curl -d '...'` sends a `POST` request by default. Use `-X PUT` or
`-X DELETE` to send other methods.

---

## Add

Adds two integers.

```
GET /add
```

**Query parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `a`  | int  | `0`     | First number |
| `b`  | int  | `0`     | Second number |

**Response:** plain text, the sum followed by a newline.

**Example**

```
$ curl 'https://numbers.apps.pipal.in/add?a=3&b=4'
7
```

A missing parameter is treated as `0`. A parameter that isn't an integer is
an error:

```
$ curl -i 'https://numbers.apps.pipal.in/add?a=hello&b=4'
HTTP/1.1 400 BAD REQUEST
Content-Type: application/json

{"error":"a must be an integer"}
```

> Quote the URL in the shell. Without quotes, `&` is interpreted by the shell
> and `b=4` is never sent.

---

## Fibs

Generates a [Fibonacci-like sequence](https://en.wikipedia.org/wiki/Fibonacci_sequence):
each number is the sum of the previous two.

```
GET /fibs
```

**Query parameters**

| Name     | Type   | Default | Description |
|----------|--------|---------|-------------|
| `a`      | int    | `1`     | First number of the sequence |
| `b`      | int    | `1`     | Second number of the sequence |
| `n`      | int    | `10`    | How many numbers to generate |
| `format` | string | (text)  | Set to `json` to get a JSON response |

**Response:** plain text with one number per line, or JSON when `format=json`.
Non-integer `a`, `b` or `n` returns `400 Bad Request`.

**Examples**

Default, first 10 Fibonacci numbers:

```
$ curl https://numbers.apps.pipal.in/fibs
1
1
2
3
5
8
13
21
34
55
```

Custom start and length:

```
$ curl 'https://numbers.apps.pipal.in/fibs?a=3&b=4&n=5'
3
4
7
11
18
```

Same request, as JSON:

```
$ curl 'https://numbers.apps.pipal.in/fibs?a=3&b=4&n=5&format=json'
{"result":[3,4,7,11,18]}
```

---

## Random

Returns random integers between `min` and `max`, both included.

```
GET /random
```

**Query parameters**

| Name     | Type   | Default | Description |
|----------|--------|---------|-------------|
| `min`    | int    | `1`     | Smallest possible number |
| `max`    | int    | `100`   | Largest possible number, inclusive |
| `count`  | int    | `1`     | How many numbers to return, 1 to 1000 |
| `format` | string | (text)  | Set to `json` to get a JSON response |

**Response:** plain text with one number per line, or JSON when `format=json`.
The numbers change on every request.

**Examples**

Roll a die ten times:

```
$ curl 'https://numbers.apps.pipal.in/random?min=1&max=6&count=10'
1
1
2
4
3
6
5
3
6
5
```

Three numbers between 1 and 100, as JSON:

```
$ curl 'https://numbers.apps.pipal.in/random?count=3&format=json'
{"result":[29,48,7]}
```

`min` greater than `max`, or a `count` outside 1 to 1000, returns
`400 Bad Request`:

```
$ curl 'https://numbers.apps.pipal.in/random?min=7&max=6'
{"error":"min must not be greater than max"}
```

---

## Range

Generates a sequence of integers from `start` up to (but not including) `stop`,
in increments of `step`. Works like Python's `range()`.

```
POST /range
```

**Request body (JSON)**

| Field   | Type | Default | Description |
|---------|------|---------|-------------|
| `start` | int  | `0`     | First number |
| `stop`  | int  | `0`     | Stop before this number |
| `step`  | int  | `1`     | Increment; can be negative, not zero |

**Response (JSON)**

```json
{"result": [ ...numbers... ]}
```

**Examples**

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"start": 1, "stop": 10}' \
    https://numbers.apps.pipal.in/range
{"result":[1,2,3,4,5,6,7,8,9]}
```

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"start": 1, "stop": 10, "step": 2}' \
    https://numbers.apps.pipal.in/range
{"result":[1,3,5,7,9]}
```

Counting down:

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"start": 5, "stop": 0, "step": -1}' \
    https://numbers.apps.pipal.in/range
{"result":[5,4,3,2,1]}
```

Invalid input returns `400 Bad Request`:

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"start": 1, "stop": 10, "step": 0}' \
    https://numbers.apps.pipal.in/range
{"error":"step must not be zero"}
```

---

## Product

Multiplies a list of numbers.

```
POST /product
```

**Request body (JSON)**

| Field     | Type          | Required | Description |
|-----------|---------------|----------|-------------|
| `numbers` | list of numbers | yes    | Numbers to multiply |

**Response (JSON)**

```json
{"result": 120}
```

The product of an empty list is `1`.

If `numbers` is missing, isn't a list, or contains anything other than
numbers, the response is `400 Bad Request` with a message naming the problem.
This applies to every endpoint that takes `numbers`:

| Body | Error |
|------|-------|
| `{}` | `{"error":"numbers is required"}` |
| `{"numbers": "1,2"}` | `{"error":"numbers must be a list"}` |
| `{"numbers": [1, "2"]}` | `{"error":"numbers must contain only numbers"}` |

**Example**

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"numbers": [5, 4, 3, 2, 1]}' \
    https://numbers.apps.pipal.in/product
{"result":120}
```

---

## Sum

Adds up a list of numbers.

```
POST /sum
```

**Request body (JSON)**

| Field     | Type            | Required | Description |
|-----------|-----------------|----------|-------------|
| `numbers` | list of numbers | yes      | Numbers to add |

**Response (JSON)**

```json
{"result": 15}
```

The sum of an empty list is `0`. Invalid input returns `400 Bad Request`, as
for [Product](#product).

**Example**

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"numbers": [1, 2, 3, 4, 5]}' \
    https://numbers.apps.pipal.in/sum
{"result":15}
```

---

## Average

Returns the mean of a list of numbers. The result is always a decimal number.

```
POST /average
```

**Request body (JSON)**

| Field     | Type            | Required | Description |
|-----------|-----------------|----------|-------------|
| `numbers` | list of numbers | yes      | Numbers to average; must not be empty |

**Response (JSON)**

```json
{"result": 3.0}
```

**Example**

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"numbers": [1, 2, 3, 4, 5]}' \
    https://numbers.apps.pipal.in/average
{"result":3.0}
```

The average of an empty list is undefined, so it returns `400 Bad Request`:

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"numbers": []}' \
    https://numbers.apps.pipal.in/average
{"error":"numbers must not be empty"}
```

Other invalid input returns `400 Bad Request`, as for [Product](#product).

---

## Stats

Returns several statistics about a list of numbers in one response.

```
POST /stats
```

**Request body (JSON)**

| Field     | Type            | Required | Description |
|-----------|-----------------|----------|-------------|
| `numbers` | list of numbers | yes      | Numbers to summarize; must not be empty |

**Response (JSON)**

| Field   | Description |
|---------|-------------|
| `count` | How many numbers |
| `sum`   | Their sum |
| `mean`  | Their average |
| `min`   | The smallest number |
| `max`   | The largest number |

**Example**

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"numbers": [1, 2, 3, 4, 5]}' \
    https://numbers.apps.pipal.in/stats
{"count":5,"sum":15,"mean":3.0,"min":1,"max":5}
```

An empty list returns `400 Bad Request`, as for [Average](#average). Other
invalid input returns `400 Bad Request`, as for [Product](#product).

---

## Sort

Sorts a list of numbers in ascending order.

```
POST /sort
```

**Request body (JSON)**

| Field     | Type          | Required | Description |
|-----------|---------------|----------|-------------|
| `numbers` | list of numbers | yes    | Numbers to sort |

**Response (JSON)**

```json
{"result": [ ...sorted numbers... ]}
```

**Example**

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"numbers": [5, 3, 9, 1]}' \
    https://numbers.apps.pipal.in/sort
{"result":[1,3,5,9]}
```

Invalid input returns `400 Bad Request`, as for [Product](#product).

---

## Authentication

`/me` and every `/store` endpoint need a token, sent in the `Authorization`
header:

```
Authorization: Bearer alice-token-123
```

A token is your username followed by `-token-123`. Usernames are lowercase
letters, digits, `_` and `-`, up to 32 characters. Pick any username; the
server doesn't keep a list of users.

> In a real API, a token is a long random secret the server gives you, and
> nobody can guess anyone else's. These tokens are guessable on purpose so
> nothing has to be handed out in class. Anyone can use `bob-token-123` and
> see Bob's data, so don't store anything you care about.

A missing or invalid token gets `401 Unauthorized`:

```
$ curl -i https://numbers.apps.pipal.in/me
HTTP/1.1 401 UNAUTHORIZED
WWW-Authenticate: Bearer
Content-Type: application/json

{"error":"missing token, expected header 'Authorization: Bearer <username>-token-123'"}

$ curl -H 'Authorization: Bearer hello' https://numbers.apps.pipal.in/me
{"error":"invalid token, expected <username>-token-123"}
```

> `401 Unauthorized` means "I don't know who you are" (no valid credentials).
> `403 Forbidden`, which this API doesn't use, means "I know who you are, but
> you're not allowed to do this".

---

## Me

Returns the username the token belongs to. Useful for checking that your
token works.

```
GET /me
```

**Example**

```
$ curl -H 'Authorization: Bearer alice-token-123' \
    https://numbers.apps.pipal.in/me
{"username":"alice"}
```

---

## Store

A key-value store: save a number under a name, read it back, change it,
delete it. Every user has their own store, and the token decides whose store
you're working with. Alice and Bob can both have an `x` with different values.

All store endpoints need a token. See [Authentication](#authentication).

| Method   | Path            | Description | Success | Common errors |
|----------|-----------------|-------------|---------|---------------|
| `GET`    | `/store`        | List all your values | `200` | |
| `GET`    | `/store/<name>` | Get one value | `200` | `404` no such name |
| `POST`   | `/store/<name>` | Create a value | `201` | `409` name already exists |
| `PUT`    | `/store/<name>` | Update a value | `200` | `404` no such name |
| `DELETE` | `/store/<name>` | Delete a value | `200` | `404` no such name |

`POST` creates and `PUT` updates. This is a common convention in APIs: `POST`
fails if the name is taken, and `PUT` fails if it doesn't exist yet, so you
never overwrite or create something by accident.

Values are numbers, either integers or decimals. The store lives in memory,
so it is cleared whenever the server restarts.

The examples below use a shell variable for the header:

```
$ AUTH='Authorization: Bearer alice-token-123'
```

### List all values

```
GET /store
```

Returns a JSON object mapping each name to its value. An empty store returns
`{}`.

```
$ curl -H "$AUTH" https://numbers.apps.pipal.in/store
{"x":42,"y":5}
```

### Get a value

```
GET /store/<name>
```

```
$ curl -H "$AUTH" https://numbers.apps.pipal.in/store/x
{"value":42}
```

If the name doesn't exist:

```
$ curl -i -H "$AUTH" https://numbers.apps.pipal.in/store/nope
HTTP/1.1 404 NOT FOUND
Content-Type: application/json

{"error":"nope not found"}
```

### Create a value

```
POST /store/<name>
```

**Request body (JSON)**

| Field   | Type   | Required | Description |
|---------|--------|----------|-------------|
| `value` | number | yes      | The value to store |

Returns `201 Created`, the stored value, and a `Location` header with the URL
of the new value.

```
$ curl -i \
    -H "$AUTH" \
    -H 'Content-Type: application/json' \
    -d '{"value": 42}' \
    https://numbers.apps.pipal.in/store/x
HTTP/1.1 201 CREATED
Content-Type: application/json
Location: /store/x

{"value":42}
```

If the name already exists, the response is `409 Conflict`:

```
{"error":"x already exists, use PUT to update it"}
```

### Update a value

```
PUT /store/<name>
```

**Request body (JSON)**

| Field   | Type   | Required | Description |
|---------|--------|----------|-------------|
| `value` | number | yes      | The new value |

```
$ curl \
    -X PUT \
    -H "$AUTH" \
    -H 'Content-Type: application/json' \
    -d '{"value": 43}' \
    https://numbers.apps.pipal.in/store/x
{"value":43}
```

If the name doesn't exist, the response is `404 Not Found`:

```
{"error":"x not found, use POST to create it"}
```

### Delete a value

```
DELETE /store/<name>
```

```
$ curl -X DELETE -H "$AUTH" https://numbers.apps.pipal.in/store/x
{"ok":true}
```

If the name doesn't exist, the response is `404 Not Found`.

### Invalid values

A missing `value`, or one that isn't a number, returns `400 Bad Request`:

```
$ curl \
    -H "$AUTH" \
    -H 'Content-Type: application/json' \
    -d '{"value": "hello"}' \
    https://numbers.apps.pipal.in/store/x
{"error":"value must be a number"}
```

### Walkthrough

Try the whole cycle:

```
$ AUTH='Authorization: Bearer alice-token-123'

$ curl -H "$AUTH" -H 'Content-Type: application/json' -d '{"value": 7}' \
    https://numbers.apps.pipal.in/store/lucky
{"value":7}

$ curl -X PUT -H "$AUTH" -H 'Content-Type: application/json' -d '{"value": 8}' \
    https://numbers.apps.pipal.in/store/lucky
{"value":8}

$ curl -H "$AUTH" https://numbers.apps.pipal.in/store/lucky
{"value":8}

$ curl -H 'Authorization: Bearer bob-token-123' \
    https://numbers.apps.pipal.in/store/lucky
{"error":"lucky not found"}

$ curl -X DELETE -H "$AUTH" https://numbers.apps.pipal.in/store/lucky
{"ok":true}
```

Bob gets a `404` because `lucky` is in Alice's store, not his.

---

## Errors

Every error has a JSON body with an `error` field saying what went wrong:

```json
{"error": "numbers is required"}
```

| Status | Meaning | When it happens |
|--------|---------|-----------------|
| `200 OK` | Success | |
| `201 Created` | Something new was created | `POST /store/<name>` |
| `400 Bad Request` | Invalid input | A parameter or field is missing or has the wrong type, or the body is missing, isn't valid JSON, or isn't a JSON object |
| `401 Unauthorized` | Bad or missing token | `/me` or `/store` without a valid `Authorization` header |
| `404 Not Found` | No such resource | A store name you haven't created, or an unknown URL |
| `405 Method Not Allowed` | Wrong HTTP method | e.g. `GET /range` or `GET /product` |
| `409 Conflict` | Already exists | `POST /store/<name>` for a name that is already stored |
| `415 Unsupported Media Type` | Body isn't declared as JSON | `POST`/`PUT` with a body but without `Content-Type: application/json` |
| `500 Internal Server Error` | Bug in the server | Shouldn't happen; please report it |

**Examples**

```
$ curl -X POST https://numbers.apps.pipal.in/sum
{"error":"request body is required"}

$ curl -H 'Content-Type: application/json' -d '{numbers:' \
    https://numbers.apps.pipal.in/sum
{"error":"request body is not valid JSON"}

$ curl -d '{"numbers": [1, 2]}' https://numbers.apps.pipal.in/sum
{"error":"Content-Type must be application/json"}

$ curl -i https://numbers.apps.pipal.in/product
HTTP/1.1 405 METHOD NOT ALLOWED
Allow: OPTIONS, POST
Content-Type: application/json

{"error":"method not allowed"}

$ curl https://numbers.apps.pipal.in/nope
{"error":"not found"}
```

A `405` response includes an `Allow` header listing the methods the endpoint
accepts.
