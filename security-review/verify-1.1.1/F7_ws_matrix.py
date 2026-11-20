#!/usr/bin/env python3
"""F7 matrix: JMAP-over-WebSocket message sizes vs maxSizeRequest, plus sanity checks.
Env: SW_HOST (http://host:8080), SW_USER (user:pass), RSS_CMD (prints VmRSS kB of the server).
Cases: 1 MiB single (sanity), 12 MiB single, 20 MiB single, 20 MiB fragmented, 60 MiB fragmented (with RSS sampling),
then push enable + a mailbox change over HTTP must yield a StateChange, then push disable."""
import asyncio, base64, json, os, subprocess, sys, time, websockets, urllib.request
host = os.environ.get("SW_HOST", "http://127.0.0.1:8080"); ws_url = host.replace("http", "ws", 1) + "/jmap/ws"
user = os.environ.get("SW_USER", "user1@lab.test:CHANGE_ME"); rss_cmd = os.environ.get("RSS_CMD")
auth = "Basic " + base64.b64encode(user.encode()).decode()
hwm_cmd = os.environ.get("HWM_CMD"); sampler_cmd = os.environ.get("SAMPLER_CMD")
def hwm():
    if not hwm_cmd: return "n/a"
    try: return subprocess.run(hwm_cmd, shell=True, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception as e: return f"err {e}"
def rss():
    if not rss_cmd: return "n/a"
    try: return subprocess.run(rss_cmd, shell=True, capture_output=True, text=True, timeout=5).stdout.strip() + " kB"
    except Exception as e: return f"err {e}"
def msg(mb): return json.dumps({"@type":"Request","using":["urn:ietf:params:jmap:core"],"methodCalls":[["Core/echo",{"pad":"x"*(mb*1024*1024)},"c0"]]})
async def connect():
    return await websockets.connect(ws_url, subprotocols=["jmap"], additional_headers={"Authorization": auth}, max_size=None, compression=None, proxy=None, close_timeout=5)
async def size_case(mb, frag, sample=False):
    m = msg(mb); label = f"{mb:>2} MiB {'fragmented 1 MiB' if frag else 'single frame   '}"
    hwm_before, rss_before = hwm(), rss()
    proc = subprocess.Popen(sampler_cmd, shell=True, stdout=subprocess.PIPE, text=True) if (sample and sampler_cmd) else None
    if proc: time.sleep(0.3)
    try:
        ws = await connect()
        t0 = time.time()
        if frag: await ws.send(m[i:i+1048576] for i in range(0, len(m), 1048576))
        else: await ws.send(m)
        try:
            r = await asyncio.wait_for(ws.recv(), 60)
            body = r if isinstance(r, str) else r.decode(errors="replace")
            kind = "echo ok" if '"Core/echo"' in body and "methodResponses" in body else ("limit error" if "maxSizeRequest" in body else "other reply")
            out = f"{label}: {kind} after {time.time()-t0:.2f}s ({len(body)} bytes){'' if kind!='other reply' else ': '+body[:120]}"
        except websockets.exceptions.ConnectionClosed as e:
            out = f"{label}: connection closed by server after {time.time()-t0:.2f}s (code={e.rcvd.code if e.rcvd else None} reason={e.rcvd.reason if e.rcvd else ''!r})"
        except asyncio.TimeoutError:
            out = f"{label}: no reply within 60s (silence)"
        await ws.close()
    except websockets.exceptions.ConnectionClosed as e:
        out = f"{label}: connection closed during send (code={e.rcvd.code if e.rcvd else None})"
    except Exception as e:
        out = f"{label}: {type(e).__name__}: {e}"
    out += f"\n    VmHWM kB before {hwm_before} after {hwm()}; VmRSS before {rss_before} after {rss()}"
    if proc:
        time.sleep(0.5); proc.terminate()
        ks = [int(l.split()[0]) for l in proc.stdout.read().splitlines() if l.split() and l.split()[0].isdigit()]
        if ks: out += f"\n    in-container 20 ms sampler VmRSS kB: first {ks[0]} peak {max(ks)} last {ks[-1]} ({len(ks)} samples)"
    print(out, flush=True)
async def push_case():
    ws = await connect()
    await ws.send(json.dumps({"@type":"WebSocketPushEnable","dataTypes":["Mailbox"]}))
    await asyncio.sleep(1)
    name = f"f7push{int(time.time())}"
    req = urllib.request.Request(host + "/jmap", data=json.dumps({"using":["urn:ietf:params:jmap:core","urn:ietf:params:jmap:mail"],"methodCalls":[["Mailbox/set",{"accountId":account_id,"create":{"m":{"name":name}}},"c0"]]}).encode(), headers={"Authorization": auth, "Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=15).read()
    try:
        r = await asyncio.wait_for(ws.recv(), 20); kind = "StateChange received" if "StateChange" in r else f"unexpected: {r[:100]}"
    except asyncio.TimeoutError: kind = "no StateChange within 20s"
    await ws.send(json.dumps({"@type":"WebSocketPushDisable"}))
    await asyncio.sleep(1)
    urllib.request.urlopen(urllib.request.Request(host + "/jmap", data=json.dumps({"using":["urn:ietf:params:jmap:core","urn:ietf:params:jmap:mail"],"methodCalls":[["Mailbox/set",{"accountId":account_id,"create":{"m":{"name":name+"b"}}},"c0"]]}).encode(), headers={"Authorization": auth, "Content-Type": "application/json"}), timeout=15).read()
    try:
        r = await asyncio.wait_for(ws.recv(), 5); after = f"still received after disable: {r[:80]}"
    except asyncio.TimeoutError: after = "nothing after disable (expected)"
    await ws.close()
    print(f"push enable/disable: {kind}; {after}", flush=True)
account_id = None
async def main():
    sess = json.load(urllib.request.urlopen(urllib.request.Request(host + "/jmap/session", headers={"Authorization": auth}), timeout=15))
    global account_id; account_id = sess["primaryAccounts"]["urn:ietf:params:jmap:mail"]
    print(f"advertised maxSizeRequest: {sess['capabilities']['urn:ietf:params:jmap:core']['maxSizeRequest']}; server RSS now: {rss()}", flush=True)
    if "--push-only" not in sys.argv:
        await size_case(1, False); await size_case(12, False); await size_case(20, False); await size_case(20, True); await size_case(60, True, sample=True)
    await push_case()
asyncio.run(main())
