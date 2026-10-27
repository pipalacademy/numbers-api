import { Hono, type Context } from "hono";
import { fibs, product } from "./numbers";

type Env = {
  DB: D1Database;
  API_TOKEN: string;
};

const app = new Hono<{ Bindings: Env }>();

function getIntParam(c: Context, name: string, defaultValue: number): number {
  const value = parseInt(c.req.query(name) ?? "");
  return Number.isNaN(value) ? defaultValue : value;
}

function textResponse(c: Context, lines: unknown[]) {
  return c.text(lines.join("\n") + "\n");
}

function badRequest(c: Context, message: string) {
  return c.json({ error: "bad-request", message }, 400);
}

async function readJson(c: Context): Promise<Record<string, unknown> | null> {
  try {
    const d = await c.req.json();
    return d !== null && typeof d === "object" && !Array.isArray(d) ? d : null;
  } catch {
    return null;
  }
}

function isNumberArray(value: unknown): value is number[] {
  return Array.isArray(value) && value.every((n) => typeof n === "number");
}

const HOME = `
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
`;

app.get("/", (c) => c.html(HOME));

/** Adds two numbers. */
app.get("/add", (c) => {
  const a = getIntParam(c, "a", 0);
  const b = getIntParam(c, "b", 0);
  return textResponse(c, [a + b]);
});

/** Returns a sequence of fibonacci numbers. */
app.get("/fibs", (c) => {
  const a = getIntParam(c, "a", 1);
  const b = getIntParam(c, "b", 1);
  const n = getIntParam(c, "n", 10);
  const numbers = fibs(a, b, n);

  if (c.req.query("format") === "json") {
    return c.json({ result: numbers });
  } else {
    return textResponse(c, numbers);
  }
});

app.post("/product", async (c) => {
  const d = await readJson(c);
  if (!d || !isNumberArray(d.numbers)) {
    return badRequest(c, "expected {\"numbers\": [...]}");
  }
  return c.json({ result: product(d.numbers) });
});

app.post("/range", async (c) => {
  const d = await readJson(c);
  if (!d) {
    return badRequest(c, "expected a JSON object");
  }
  const { start = 0, stop = 0, step = 1 } = d;
  if (![start, stop, step].every(Number.isSafeInteger)) {
    return badRequest(c, "start, stop and step must be integers");
  }
  if (step === 0) {
    return badRequest(c, "step must not be zero");
  }

  const result: number[] = [];
  const [i0, end, s] = [start, stop, step] as number[];
  for (let i = i0; s > 0 ? i < end : i > end; i += s) {
    result.push(i);
  }
  return c.json({ result });
});

app.post("/sort", async (c) => {
  const d = await readJson(c);
  if (!d || !isNumberArray(d.numbers)) {
    return badRequest(c, "expected {\"numbers\": [...]}");
  }
  const result = [...d.numbers].sort((x, y) => x - y);
  return c.json({ result });
});

app.get("/store", async (c) => {
  const { results } = await c.env.DB.prepare(
    "SELECT name, value FROM store ORDER BY name",
  ).all<{ name: string; value: number }>();
  return c.json(Object.fromEntries(results.map((r) => [r.name, r.value])));
});

function checkToken(c: Context<{ Bindings: Env }>): boolean {
  return c.req.header("Authorization") === `Bearer ${c.env.API_TOKEN}`;
}

app.put("/store/:name", async (c) => {
  if (!checkToken(c)) {
    return c.json({ error: "forbidden" }, 403);
  }
  const d = await readJson(c);
  if (!d || !Number.isSafeInteger(d.value)) {
    return badRequest(c, "expected {\"value\": <int>}");
  }
  await c.env.DB.prepare(
    "INSERT INTO store (name, value) VALUES (?, ?)" +
      " ON CONFLICT (name) DO UPDATE SET value = excluded.value",
  )
    .bind(c.req.param("name"), d.value)
    .run();
  return c.json({ ok: true });
});

app.delete("/store/:name", async (c) => {
  if (!checkToken(c)) {
    return c.json({ error: "forbidden" }, 403);
  }
  await c.env.DB.prepare("DELETE FROM store WHERE name = ?")
    .bind(c.req.param("name"))
    .run();
  return c.json({ ok: true });
});

app.get("/store/:name", async (c) => {
  const row = await c.env.DB.prepare("SELECT value FROM store WHERE name = ?")
    .bind(c.req.param("name"))
    .first<{ value: number }>();
  if (row === null) {
    return c.json({ error: "not-found" }, 404);
  }
  return c.json({ value: row.value });
});

export default app;
