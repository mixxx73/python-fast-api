from uuid import uuid4


def _signup_and_token(
    client, email="bal_tester@example.com", name="Owner", password="s3cret"
):
    # ensure uniqueness to avoid 409 on duplicate email across tests
    local, at, domain = email.partition("@")
    unique_email = f"{local}+{uuid4().hex}@{domain}" if at else f"{email}+{uuid4().hex}"
    r = client.post(
        "/auth/signup",
        json={"email": unique_email, "name": name, "password": password},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def test_group_balances_invalid_and_not_found(client):
    token = _signup_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid UUID
    r1 = client.get("/groups/not-a-uuid/balances", headers=headers)
    assert r1.status_code == 422

    # Not found
    r2 = client.get(f"/groups/{uuid4()}/balances", headers=headers)
    assert r2.status_code == 404


def test_group_balances_no_members_and_no_expenses(client):
    token = _signup_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a group but do not add members
    g = client.post("/groups/", json={"name": "Empty"}, headers=headers).json()

    # No members -> empty list
    r = client.get(f"/groups/{g['id']}/balances", headers=headers)
    assert r.status_code == 200
    assert r.json() == []

    # Add two members but no expenses -> zeros for each
    u1 = client.post("/users/", json={"email": "z1@example.com", "name": "Z1"}).json()
    u2 = client.post("/users/", json={"email": "z2@example.com", "name": "Z2"}).json()
    client.post(f"/groups/{g['id']}/members/{u1['id']}", headers=headers)
    client.post(f"/groups/{g['id']}/members/{u2['id']}", headers=headers)
    r2 = client.get(f"/groups/{g['id']}/balances", headers=headers)
    assert r2.status_code == 200
    bals = {b["user_id"]: b["balance"] for b in r2.json()}
    assert bals[u1["id"]] == 0.0
    assert bals[u2["id"]] == 0.0


def test_group_balances_three_members_rounding(client):
    token = _signup_and_token(client, email="owner3@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    # Three users
    u1 = client.post("/users/", json={"email": "a@example.com", "name": "A"}).json()
    u2 = client.post("/users/", json={"email": "b@example.com", "name": "B"}).json()
    u3 = client.post("/users/", json={"email": "c@example.com", "name": "C"}).json()
    # Group
    g = client.post("/groups/", json={"name": "Rounding"}, headers=headers).json()
    # Add members
    client.post(f"/groups/{g['id']}/members/{u1['id']}", headers=headers)
    client.post(f"/groups/{g['id']}/members/{u2['id']}", headers=headers)
    client.post(f"/groups/{g['id']}/members/{u3['id']}", headers=headers)
    # Expenses: u1 pays 100, u2 pays 40
    er1 = client.post(
        "/expenses/",
        json={
            "group_id": g["id"],
            "payer_id": u1["id"],
            "amount": 100,
            "description": "X",
        },
        headers=headers,
    )
    assert er1.status_code == 200
    er2 = client.post(
        "/expenses/",
        json={
            "group_id": g["id"],
            "payer_id": u2["id"],
            "amount": 40,
            "description": "Y",
        },
        headers=headers,
    )
    assert er2.status_code == 200
    # Balances
    br = client.get(f"/groups/{g['id']}/balances")
    assert br.status_code == 200
    bals = {b["user_id"]: b["balance"] for b in br.json()}
    # Expected rounding behavior (two decimals)
    assert bals[u1["id"]] == 53.33
    assert bals[u2["id"]] == -6.67
    assert bals[u3["id"]] == -46.67
