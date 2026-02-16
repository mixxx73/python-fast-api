async def test_users_crud_and_groups_listing(client):
    # Create a user via users API
    r = await client.post("/users/", json={"email": "bob@example.com", "name": "Bob"})
    assert r.status_code == 200
    user = r.json()
    assert user["email"] == "bob@example.com"
    user_id = user["id"]

    # List users includes Bob
    r2 = await client.get("/users/")
    assert r2.status_code == 200
    emails = [u["email"] for u in r2.json()]
    assert "bob@example.com" in emails

    # Get user by id
    r3 = await client.get(f"/users/{user_id}")
    assert r3.status_code == 200
    assert r3.json()["id"] == user_id

    # Invalid UUID
    r4 = await client.get("/users/not-a-uuid")
    assert r4.status_code == 422

    # Not found UUID
    from uuid import uuid4

    r5 = await client.get(f"/users/{uuid4()}")
    assert r5.status_code == 404


async def test_user_profile_update_with_auth(client):
    # Signup to get token and identity
    r = await client.post(
        "/auth/signup",
        json={"email": "prof@example.com", "name": "Prof", "password": "s3cret"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Resolve current user via /auth/me
    me = (await client.get("/auth/me", headers=headers)).json()
    uid = me["id"]

    # Update own profile
    up = await client.patch(f"/users/{uid}", json={"name": "New Name"}, headers=headers)
    assert up.status_code == 200
    assert up.json()["name"] == "New Name"

    # Create another user and attempt to update them -> 403
    other = (await client.post("/users/", json={"email": "o@example.com", "name": "O"})).json()
    forb = await client.patch(f"/users/{other['id']}", json={"name": "X"}, headers=headers)
    assert forb.status_code == 403

    # Email conflict -> 409
    conflict = await client.patch(
        f"/users/{uid}", json={"email": "o@example.com"}, headers=headers
    )
    assert conflict.status_code == 409
