import imaplib, time, traceback, socket, ssl

socket.setdefaulttimeout(15)
S = str(int(time.time()))
HOST, PORT = "127.0.0.1", 993
USER, PASS = "user1@lab.test", "CHANGE_ME"


def q(s):
    return '"%s"' % s


def dec(x):
    return x.decode("utf-8", "replace") if isinstance(x, bytes) else str(x)


def rec(label, r):
    typ, data = r
    d = [dec(x) for x in (data or [])]
    print(f"{label}: {typ} {d}", flush=True)
    return typ, d


def listing(M, label):
    try:
        typ, data = M.list('""', '*')
        lines = [dec(x) for x in (data or []) if x]
        mine = [l for l in lines if S in l]
        print(f"{label}: total={len(lines)} with-S={len(mine)}", flush=True)
        for l in mine:
            print("   ", l, flush=True)
        return lines
    except Exception as e:
        print(f"{label}: EXC {e!r}", flush=True)
        return []


def login():
    ctx = ssl._create_unverified_context()
    M = imaplib.IMAP4_SSL(HOST, PORT, ssl_context=ctx)
    rec("LOGIN", M.login(USER, PASS))
    return M


print("S =", S, flush=True)
M = login()

# step 1
rec("CREATE F9a", M.create(q(f"F9a_{S}")))
rec("CREATE F9a/b", M.create(q(f"F9a_{S}/b")))
rec("LIST pre", M.list('""', q(f"F9a_{S}*")))

# step 2
rec("STEP2 RENAME F9a -> F9a/b/x", M.rename(q(f"F9a_{S}"), q(f"F9a_{S}/b/x")))

# step 3
listing(M, "STEP3 LIST *")
for name in [f"F9a_{S}", "b", "x", f"F9a_{S}/b", f"F9a_{S}/b/x"]:
    try:
        rec(f"STEP3 SELECT {name}", M.select(q(name), readonly=True))
    except Exception as e:
        print(f"STEP3 SELECT {name}: EXC {e!r}", flush=True)

# step 4
rec("CREATE F9c", M.create(q(f"F9c_{S}")))
rec("STEP4 RENAME F9c -> F9c/self", M.rename(q(f"F9c_{S}"), q(f"F9c_{S}/self")))
listing(M, "STEP4 LIST *")

try:
    M.logout()
except Exception:
    pass

# step 6
try:
    M2 = login()
    rec("STEP6 SELECT INBOX", M2.select("INBOX", readonly=True))
    M2.logout()
except Exception:
    print("STEP6 LOGIN EXC", flush=True)
    traceback.print_exc()
