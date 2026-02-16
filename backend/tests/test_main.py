async def test_read_root(client) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
