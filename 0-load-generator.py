import base64
import aiohttp
import asyncio
import requests
import time
import os
import shutil
from opentelemetry.proto.trace.v1 import trace_pb2

users = [
    'bob:p@55w0rd',
    'alice:p@55w0rd'
    #'joe:p@55w0rd'
]

auth_headers = []
for user in users:
    b64Bytes = base64.b64encode(user.encode('utf-8'))
    auth_headers.append(b64Bytes.decode('utf-8'))

run_name="live_unseen_exception_type"
total_requests = 500
print('starting loop')

def get_and_decode_trace(trace_id):
    tempo_req = requests.get(f'http://localhost:3200/api/traces/{trace_id}', headers={'Accept': 'application/protobuf'})
    tempo_req.raise_for_status()
    decoded_trace = trace_pb2.TracesData()
    decoded_trace.ParseFromString(tempo_req.content)
    return decoded_trace

async def fetch(session: aiohttp.ClientSession, url, user_auth_hdr):
    return await session.get(url, ssl=False, headers={'Authorization': f'Basic {user_auth_hdr}'})

async def execute_requests(session, n):
    tasks=[]
    trace_ids=[]
    for x in range(0, n):
        user = auth_headers[x % len(auth_headers)]
        tasks.append(asyncio.ensure_future(fetch(session, 'https://localhost:8080/WeatherForecast', user)))

    print('awaiting responses')
    responses = await asyncio.gather(*tasks)
    for x, r in enumerate(responses):
        user=r.request_info.headers['Authorization'][6:]
        trace_id=r.headers['x-trace-id']
        trace_ids.append(trace_id)
        print(f'{x}: user: {user}, status_code: {r.status}, trace_id={trace_id}')

    return trace_ids

async def main():
    connector = aiohttp.TCPConnector(limit=20)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print('executing warmup requests')
        await execute_requests(session, 100)

        print('executing actual requests')
        trace_ids = await execute_requests(session, 500)

    print('sleeping for 30 seconds to ensure all traces have flushed to tempo')
    time.sleep(30)

    path = os.path.join('D:\source\OpenAiAlerting-Python\data', run_name)
    shutil.rmtree(path)
    os.mkdir(path)

    for id in trace_ids:
        trace = get_and_decode_trace(id)
        
        with open(os.path.join(path, f'{id}.bin'), "wb") as f:
            f.write(trace.SerializeToString())

asyncio.run(main())
print('done')