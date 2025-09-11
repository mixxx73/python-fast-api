def test_signup_login_me_flow(client):
    # Signup
    r = client.post(
        "/auth/signup",
        json={"email": "alice@example.com", "name": "Alice", "password": "s3cret"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    # Duplicate signup returns 409
    r2 = client.post(
        "/auth/signup",
        json={"email": "alice@example.com", "name": "Alice", "password": "s3cret"},
    )
    assert r2.status_code == 409

    # Login with wrong password
    r3 = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "wrong"},
    )
    assert r3.status_code == 401

    # Login with correct password
    r4 = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "s3cret"},
    )
    assert r4.status_code == 200
    token2 = r4.json()["access_token"]
    assert token2

    # Me endpoint
    r5 = client.get("/auth/me", headers={"Authorization": f"Bearer {token2}"})
    assert r5.status_code == 200
    me = r5.json()
    assert me["email"] == "alice@example.com"
