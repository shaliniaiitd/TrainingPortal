import json

async def get(request_context, url, headers):
    return await request_context.get(url, headers=headers)

async def post(request_context, url, headers, payload):
    return await request_context.post(url, headers=headers, data=json.dumps(payload))

async def put(request_context, url, headers, payload):
    return await request_context.put(url, headers=headers, data=json.dumps(payload))

async def delete(request_context, url, headers):
    return await request_context.delete(url, headers=headers)
