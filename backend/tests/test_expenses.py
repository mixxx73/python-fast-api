def _signup_and_token(
    client,
    email="exp_owner@example.com",
    name="Owner",
    password="s3cret",
    is_admin=False,
):
    r = client.post(
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


def test_expense_flow(client):
    # Create user and group
    ur = client.post("/users/", json={"email": "dave@example.com", "name": "Dave"})
    assert ur.status_code == 200
    uid = ur.json()["id"]

    token = _signup_and_token(client, is_admin=True)
    headers = {"Authorization": f"Bearer {token}"}
    gr = client.post("/groups/", json={"name": "Dinner"}, headers=headers)
    assert gr.status_code == 200
    gid = gr.json()["id"]

    # Add member
    am = client.post(f"/groups/{gid}/members/{uid}", headers=headers)
    assert am.status_code == 200

    # Create expense
    er = client.post(
        "/expenses/",
        json={
            "group_id": gid,
            "payer_id": uid,
            "amount": 42.5,
            "description": "meal",
        },
        headers=headers,
    )
    assert er.status_code == 200
    expense = er.json()
    assert expense["amount"] == 42.5
    eid = expense["id"]

    # List group expenses
    le = client.get(f"/groups/{gid}/expenses")
    assert le.status_code == 200
    assert any(e["id"] == eid for e in le.json())

    # List all expenses
    la = client.get("/expenses/")
    assert la.status_code == 200
    assert any(e["id"] == eid for e in la.json())

    # Get expense by id
    ge = client.get(f"/expenses/{eid}")
    assert ge.status_code == 200
    assert ge.json()["id"] == eid


def test_expense_rejects_non_member_payer(client):
    # Create two users; only one joins the group
    u1 = client.post("/users/", json={"email": "x1@example.com", "name": "X1"}).json()
    u2 = client.post("/users/", json={"email": "x2@example.com", "name": "X2"}).json()
    token = _signup_and_token(client, email="exp_owner2@example.com", is_admin=True)
    headers = {"Authorization": f"Bearer {token}"}
    g = client.post("/groups/", json={"name": "G"}, headers=headers).json()
    client.post(f"/groups/{g['id']}/members/{u1['id']}", headers=headers)
    # u2 is not a member; creating expense with u2 payer should 400
    r = client.post(
        "/expenses/",
        json={
            "group_id": g["id"],
            "payer_id": u2["id"],
            "amount": 5,
            "description": "bad",
        },
        headers=headers,
    )
    assert r.status_code == 400
