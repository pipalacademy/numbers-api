# Numbers API Reference

Base URL: `https://numbers.apps.pipal.in`

All examples use [`curl`](https://curl.se/). Add `-i` to any command to see the
status code and headers along with the body.

## Contents

- [Basics](#basics)
- [Add](#add) — `GET /add`
- [Fibs](#fibs) — `GET /fibs`
- [Range](#range) — `POST /range`
- [Product](#product) — `POST /product`
- [Sort](#sort) — `POST /sort`
- [Store](#store) — `GET`, `PUT`, `DELETE /store/<name>`
- [Errors](#errors)

## Basics

The API uses two styles of request, so you can learn both.

| Style | Endpoints | How you send input | What you get back |
|-------|-----------|--------------------|-------------------|
| Query parameters | `/add`, `/fibs` | In the URL: `?a=3&b=4` | Plain text (JSON optional for `/fibs`) |
| JSON body | `/range`, `/product`, `/sort`, `/store` | `POST`/`PUT` with a JSON body | JSON |

When sending a JSON body, you must set the `Content-Type` header:

```
-H 'Content-Type: application/json'
```

Without it, the server responds with `415 Unsupported Media Type`.

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

The product of an empty list is `1`. If `numbers` is missing or contains
anything other than numbers, the response is `400 Bad Request`:

```json
{"error": "numbers must be a list of numbers"}
```

**Example**

```
$ curl \
    -H 'Content-Type: application/json' \
    -d '{"numbers": [5, 4, 3, 2, 1]}' \
    https://numbers.apps.pipal.in/product
{"result":120}
```

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

## Store

A simple key-value store: save an integer under a name, read it back, delete
it. This is the only part of the API that changes data on the server, so
writes require authentication.

| Method   | Path            | Auth required | Description |
|----------|-----------------|---------------|-------------|
| `GET`    | `/store`        | no            | List all entries |
| `GET`    | `/store/<name>` | no            | Get one value |
| `PUT`    | `/store/<name>` | yes           | Create or update a value |
| `DELETE` | `/store/<name>` | yes           | Delete a value |

The store is shared by everyone using the server and lives in memory, so it
is cleared whenever the server restarts.

### Authentication

Write requests need an API token in the `Authorization` header:

```
Authorization: Bearer abcd1234
```

The token is `abcd1234`. It is public on purpose; this is a teaching API.
Requests with a missing or wrong token get `401 Unauthorized`:

```
$ curl -i -X DELETE https://numbers.apps.pipal.in/store/x
HTTP/1.1 401 UNAUTHORIZED
WWW-Authenticate: Bearer
Content-Type: application/json

{"error":"unauthorized"}
```

> `401 Unauthorized` means "I don't know who you are" (no valid credentials).
> `403 Forbidden`, which this API doesn't use, means "I know who you are, but
> you're not allowed to do this".

### List all entries

```
GET /store
```

Returns a JSON object mapping each name to its value.

```
$ curl https://numbers.apps.pipal.in/store
{"x":42,"y":5}
```

An empty store returns `{}`.

### Get a value

```
GET /store/<name>
```

```
$ curl https://numbers.apps.pipal.in/store/x
{"value":42}
```

If the name does not exist, the response is `404 Not Found`:

```
$ curl -i https://numbers.apps.pipal.in/store/nope
HTTP/1.1 404 NOT FOUND
Content-Type: application/json

{"error":"not-found"}
```

### Set a value

```
PUT /store/<name>
```

**Request body (JSON)**

| Field   | Type | Required | Description |
|---------|------|----------|-------------|
| `value` | int  | yes      | The value to store |

```
$ curl \
    -X PUT \
    -H 'Authorization: Bearer abcd1234' \
    -H 'Content-Type: application/json' \
    -d '{"value": 42}' \
    https://numbers.apps.pipal.in/store/x
{"ok":true}
```

If `name` already exists, its value is replaced. A missing or non-integer
`value` (e.g. `"hello"` or `4.5`) returns `400 Bad Request`:

```json
{"error": "value must be an integer"}
```

### Delete a value

```
DELETE /store/<name>
```

```
$ curl \
    -X DELETE \
    -H 'Authorization: Bearer abcd1234' \
    https://numbers.apps.pipal.in/store/x
{"ok":true}
```

Deleting a name that does not exist also returns `{"ok": true}`.

### Walkthrough

Try the whole cycle:

```
$ curl -X PUT -H 'Authorization: Bearer abcd1234' \
    -H 'Content-Type: application/json' -d '{"value": 7}' \
    https://numbers.apps.pipal.in/store/lucky
{"ok":true}

$ curl https://numbers.apps.pipal.in/store/lucky
{"value":7}

$ curl -X DELETE -H 'Authorization: Bearer abcd1234' \
    https://numbers.apps.pipal.in/store/lucky
{"ok":true}

$ curl https://numbers.apps.pipal.in/store/lucky
{"error":"not-found"}
```

---

## Errors

Errors from the API itself have a JSON body with an `error` field:

```json
{"error": "numbers must be a list of numbers"}
```

| Status | Meaning | When it happens |
|--------|---------|-----------------|
| `200 OK` | Success | |
| `400 Bad Request` | Invalid input | A parameter or field is missing, has the wrong type, or the body isn't a JSON object |
| `401 Unauthorized` | Bad or missing token | `PUT`/`DELETE` on `/store/<name>` without `Authorization: Bearer abcd1234` |
| `404 Not Found` | No such resource | `GET /store/<name>` for a name that isn't stored, or an unknown URL |
| `405 Method Not Allowed` | Wrong HTTP method | e.g. `GET /range`, or `POST /store/x` (use `PUT`) |
| `415 Unsupported Media Type` | Body isn't declared as JSON | `POST`/`PUT` without `Content-Type: application/json` |

`404` for unknown URLs, `405` and `415` come from the web framework, and
their body is HTML, not JSON.
