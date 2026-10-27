# Numbers API

Simple API to work with numbers. Created to use an example of teaching how to work with APIs.

## The API

### Add

```
$ curl 'https://numbers.apps.pipal.in/add?a=3&b=4'
7
```

### Fibs

The Fibs API generates a sequence of fibbonacci numbers.

The response is plain text.

**HTTP Method**

GET

**Endpoint**

`/fibs`

**Query Parameters**

| Name | Type | Default Value | Description |
| -----|------| ------------- |-------------|
| a | int | 1  | The first number of the fibonacci sequence |
| b | int | 1  | The second numner of the fibbonacci sequence |
| b | int | 1  | Number of fibonacci numbers to generate |


**Examples**

```
$ curl -i https://numbers.apps.pipal.in/fibs
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

### Range

Generates a sequence of numbers. The response is in JSON format.

```
$ curl \
    -H 'content-type: application/json' \
    -d '{"start": 1, "stop": 10}' \
    https://numbers.apps.pipal.in/range
{"result": [1, 2, 3, 4, 5, 6, 7, 8, 9]}

$ curl \
    -H 'content-type: application/json' \
    -d '{"start": 1, "stop": 10, "step": 2}' \
    https://numbers.apps.pipal.in/range
{"result": [1, 3, 5, 7, 9]}
```

### Product

```
$ curl \
    -H 'content-type: application/json' \
    -d '{"numbers": [5, 4, 3, 2, 1]}' \
    https://numbers.apps.pipal.in/product
{"result":120}
```

### Sort

```
$ curl \
    -H 'content-type: application/json' \
    -d '{"numbers": [5, 4, 3, 2, 1]}' \
    https://numbers.apps.pipal.in/sort
{"result":[1,2,3,4,5]}
```

### Store

Store API provides an interface to store numbers with a name.

**List entries in the store**

```
GET /store
```

Example:

```
$ curl https://numbers.apps.pipal.in/store
{"x": 42, "y": 5}
```

**Get a value**

```
GET /store/<name>
```

Example:

```
$ curl https://numbers.apps.pipal.in/store/x
{"value": 42}
```

**Set a value**

To set a value, we need to authenticate with API token. The API token is `abcd1234`.

```
$ curl \
    -X PUT \
    -H 'Authorization: Bearer abcd1234' \
    -H 'Content-type: application/json' \
    -d '{"value": 45}' \
    https://numbers.apps.pipal.in/store/x
{"ok": true}
```

**Delete a value**

```
$ curl \
    -X DELETE \
    -H 'Authorization: Bearer abcd1234' \
    https://numbers.apps.pipal.in/store/x
{"ok": true}
```

## Development

The API runs on [Cloudflare Workers](https://developers.cloudflare.com/workers/), written in TypeScript with [Hono](https://hono.dev/). The store is kept in a [D1](https://developers.cloudflare.com/d1/) database.

```
$ npm install
$ cp .dev.vars.example .dev.vars
$ npm run db:migrate:local
$ npm run dev
```

The API is now available at http://localhost:8787/.

## Deployment

One-time setup:

```
$ npx wrangler login
$ npx wrangler d1 create numbers-api        # put the printed database_id in wrangler.jsonc
$ npm run db:migrate:remote
$ npx wrangler secret put API_TOKEN          # enter abcd1234
```

Deploy:

```
$ npm run deploy
```

