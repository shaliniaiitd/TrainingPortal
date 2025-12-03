import json

async def get_jwt_token(request, username, password):
    resp = await request.post("/api_async/token/", data=json.dumps({
        "username": username,
        "password": password
    }))

    assert resp.status == 200, "JWT Login failed"
    tokens = await resp.json()
    return tokens["access"]
