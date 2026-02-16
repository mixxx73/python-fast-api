from uuid import uuid4


async def _signup_and_token(
    client,
    email="carol@example.com",
    name="Carol",
    password="s3cret",
    is_admin=False,
):
    r = await client.post(
        "/auth/signup",
        json={
            "email": email,
            "name": name,
            "password": password,
            "is_admin": is_admin,
        },
    )
    assert r.status_code == 200
    return r.json()["access_token"]


async def test_group_creation_and_membership(client):
    # Create a user (member-to-be)
    ur = await client.post("/users/", json={"email": "carol@example.com", "name": "Carol"})
    assert ur.status_code == 200
    user_id = ur.json()["id"]

    # Auth required for creating group and adding member
    token = await _signup_and_token(client, email="owner@example.com", name="Owner")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a group (protected)
    gr = await client.post("/groups/", json={"name": "Trip"}, headers=headers)
    assert gr.status_code == 200
    group_id = gr.json()["id"]

    # Add member (protected)
    am = await client.post(f"/groups/{group_id}/members/{user_id}", headers=headers)
    assert am.status_code == 200
    group = am.json()
    assert user_id in group["members"]

    # List user's groups includes this group
    lug = await client.get(f"/users/{user_id}/groups")
    assert lug.status_code == 200
    ids = [g["id"] for g in lug.json()]
    assert group_id in ids

    # List groups without auth -> 401
    lg = await client.get("/groups/")
    assert lg.status_code == 401

    # Get group by id
    gg = await client.get(f"/groups/{group_id}")
    assert gg.status_code == 200
    assert gg.json()["id"] == group_id

    # Invalid UUID
    bad = await client.post(f"/groups/not-a-uuid/members/{user_id}", headers=headers)
    assert bad.status_code == 422

    # Not found group
    nf = await client.post(f"/groups/{uuid4()}/members/{user_id}", headers=headers)
    assert nf.status_code == 404


async def test_group_balances(client):
    # Two users and group
    token = await _signup_and_token(
        client, email="bal_owner@example.com", name="Owner", is_admin=True
    )
    headers = {"Authorization": f"Bearer {token}"}
    u1 = (await client.post("/users/", json={"email": "u1@example.com", "name": "U1"})).json()
    u2 = (await client.post("/users/", json={"email": "u2@example.com", "name": "U2"})).json()
    g = (await client.post("/groups/", json={"name": "Balance"}, headers=headers)).json()
    await client.post(f"/groups/{g['id']}/members/{u1['id']}", headers=headers)
    await client.post(f"/groups/{g['id']}/members/{u2['id']}", headers=headers)

    # u1 pays 40, u2 pays 10 (equal split among 2)
    er1 = await client.post(
        "/expenses/",
        json={
            "group_id": g["id"],
            "payer_id": u1["id"],
            "amount": 4000,
            "description": "A",
        },
        headers=headers,
    )
    assert er1.status_code == 200
    er2 = await client.post(
        "/expenses/",
        json={
            "group_id": g["id"],
            "payer_id": u2["id"],
            "amount": 1000,
            "description": "B",
        },
        headers=headers,
    )
    assert er2.status_code == 200

    # Balances: u1 = +15, u2 = -15
    br = await client.get(f"/groups/{g['id']}/balances")
    assert br.status_code == 200
    bals = {b["user_id"]: b["balance"] for b in br.json()}
    assert bals[u1["id"]] == 15.0
    assert bals[u2["id"]] == -15.0
