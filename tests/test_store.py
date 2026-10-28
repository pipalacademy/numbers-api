import pytest
import app as app_module


@pytest.fixture
def client():
    app_module._stores.clear()
    return app_module.app.test_client()


def auth(username):
    return {"Authorization": f"Bearer {username}-token-123"}


@pytest.mark.parametrize("header, username", [
    ("Bearer alice-token-123", "alice"),
    ("bearer alice-token-123", "alice"),
    ("Bearer mary-jane-token-123", "mary-jane"),
])
def test_me_valid_tokens(client, header, username):
    r = client.get("/me", headers={"Authorization": header})
    assert r.status_code == 200
    assert r.json == {"username": username}


@pytest.mark.parametrize("header", [
    None,
    "",
    "Bearer",
    "Bearer ",
    "alice-token-123",            # missing scheme
    "Basic alice-token-123",
    "Bearer Alice-token-123",     # usernames are lowercase
    "Bearer alice-token-124",
    "Bearer -token-123",          # empty username
    "Bearer abcd1234",            # the old shared token
])
def test_me_rejects_bad_tokens(client, header):
    headers = {"Authorization": header} if header is not None else {}
    r = client.get("/me", headers=headers)
    assert r.status_code == 401
    assert r.headers["WWW-Authenticate"] == "Bearer"
    assert "error" in r.json


def test_users_have_separate_stores(client):
    assert client.post("/store/x", json={"value": 1}, headers=auth("alice")).status_code == 201
    assert client.post("/store/x", json={"value": 2}, headers=auth("bob")).status_code == 201

    assert client.get("/store/x", headers=auth("alice")).json == {"value": 1}
    assert client.get("/store/x", headers=auth("bob")).json == {"value": 2}

    client.delete("/store/x", headers=auth("alice"))
    assert client.get("/store/x", headers=auth("alice")).status_code == 404
    assert client.get("/store/x", headers=auth("bob")).json == {"value": 2}
    assert client.get("/store", headers=auth("carol")).json == {}


def test_store_lifecycle(client):
    h = auth("alice")
    assert client.put("/store/x", json={"value": 1}, headers=h).status_code == 404
    assert client.delete("/store/x", headers=h).status_code == 404

    r = client.post("/store/x", json={"value": 42}, headers=h)
    assert r.status_code == 201
    assert r.headers["Location"] == "/store/x"

    assert client.post("/store/x", json={"value": 1}, headers=h).status_code == 409
    assert client.get("/store/x", headers=h).json == {"value": 42}

    assert client.put("/store/x", json={"value": 4.5}, headers=h).status_code == 200
    client.post("/store/y", json={"value": 5}, headers=h)
    assert client.get("/store", headers=h).json == {"x": 4.5, "y": 5}

    assert client.delete("/store/x", headers=h).status_code == 200
    assert client.get("/store", headers=h).json == {"y": 5}


@pytest.mark.parametrize("body", [{}, {"value": "42"}, {"value": True}, {"value": None}, {"value": [1]}])
def test_store_rejects_non_numbers(client, body):
    h = auth("alice")
    assert client.post("/store/x", json=body, headers=h).status_code == 400
    client.post("/store/y", json={"value": 1}, headers=h)
    assert client.put("/store/y", json=body, headers=h).status_code == 400
    assert client.get("/store", headers=h).json == {"y": 1}


@pytest.mark.parametrize("method, path", [
    ("get", "/store"),
    ("get", "/store/x"),
    ("post", "/store/x"),
    ("put", "/store/x"),
    ("delete", "/store/x"),
])
def test_store_requires_token(client, method, path):
    # checked before the body, so a valid body doesn't change the answer
    r = getattr(client, method)(path, json={"value": 1})
    assert r.status_code == 401
