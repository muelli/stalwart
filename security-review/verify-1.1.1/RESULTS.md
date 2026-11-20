# Re-verification against Stalwart 1.1.1

Image: docker.io/stalwartlabs/stalwart:v1.1.1 (there is no `1.1.1` tag), digest
sha256:5ebdf474b237161742fe4309396af4ae8797c938e8e6eb7e2d4837332c4f9851, built 2026-11-16, server logs version = "1.1.1".
Lab: fresh container, bootstrap via `x:Bootstrap/set` (property renamed: `serverHostname` -> `defaultHostname`), domain lab.test,
users user1/user2 (roles User), OAuth client `labclient` with redirectUris {https://good.example/cb}, no secret.
Commands: the scripts in ../demo (env vars SW_HOST, SW_USER, SW_ADMIN, SW_USER_ACCOUNT_ID=c) plus F1_oauth_redirect_111.sh here.
Captured output: out_F*.txt in this directory. Container has no outbound network (webui bundle fetch fails at startup).

| Finding | 0.16.27 | 1.1.1 | Evidence |
|---|---|---|---|
| F1 OAuth redirect_uri not enforced | VULNERABLE | NOT VULNERABLE | Login API changed (authorization params now in `query`); unregistered URI -> `invalid_request: redirect_uri ... does not match the client registration`; registered URI proceeds (fails later only on missing `state`). Source: authorize.rs enforces `client.redirect_uri_matches` unconditionally. |
| F2 Push error body unbounded | not testable | VULNERABLE | lab-internal HTTPS target (docker subnet 11.22.33.0/24 passes is_global_ipv4, --add-host, lab CA in the container trust store); one PushSubscription/set -> verification POST answered with 500 + 256 MiB body; VmRSS 95 MB -> 513 MB peak (run 1), 131 MB -> 689 MB peak (run 2). Control with v1.1/push-error-body-limit a35a27c built from source: 108 MB -> 112 MB, connection closed after 1 KiB. See out_F2.txt, out_F2_control.txt, F2_push_body.sh, F2_push_target.py. |
| F3 TLSRPT redirects | not testable | NOT TESTED | needs outbound delivery; reported fixed upstream |
| F4 build().unwrap() panic | VULNERABLE | NOT VULNERABLE | both triggers now return HTTP 500, 0 panics in stderr |
| F5 DAV MOVE into own subtree | VULNERABLE | NOT VULNERABLE | MOVE -> 403, tree intact, PROPFIND 207 |
| F6 autoconfig XML unescaped | VULNERABLE | NOT VULNERABLE | `<probe/>` is escaped |
| F7 WebSocket buffers beyond maxSizeRequest | VULNERABLE | VULNERABLE (fixed by v1.1/websocket-message-limit d6dcde6) | Stock: 12 MiB single frame and 20/60 MiB fragmented are read completely, then answered with the maxSizeRequest error; 60 MiB raises VmRSS 121 MB -> 177 MB peak (20 ms sampler), HWM +9 MB; a 20 MiB single frame is dropped by tungstenite's 16 MiB frame default. Patched build (d6dcde6 built from source, binary hash verified in the container, reports 1.1.1): every over-limit message (12 MiB single, 20 MiB single, 20 and 60 MiB fragmented) is rejected mid-send by closing the connection, RSS flat (120,044 -> 120,052 kB peak); 1 MiB Core/echo and WebSocket push enable/disable (StateChange delivered, silent after disable) still work. Behaviour note: the patched server closes the TCP connection without a close frame or JMAP error. See out_F7_stock_*.txt, out_F7_patched_*.txt, F7_ws_matrix.py. |
| F8 bundle inflate unbounded | not testable | NOT TESTABLE | needs a crafted bundle at resource_url |
| F9 IMAP RENAME into own subtree | VULNERABLE | NOT VULNERABLE | `NO [CANNOT] Mailbox cannot be moved under itself.` for both cases; tree intact |
