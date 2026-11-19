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
| F2 Push error body unbounded | not testable | NOT TESTABLE | needs a public HTTPS endpoint; no outbound network in the lab |
| F3 TLSRPT redirects | not testable | NOT TESTED | needs outbound delivery; reported fixed upstream |
| F4 build().unwrap() panic | VULNERABLE | NOT VULNERABLE | both triggers now return HTTP 500, 0 panics in stderr |
| F5 DAV MOVE into own subtree | VULNERABLE | NOT VULNERABLE | MOVE -> 403, tree intact, PROPFIND 207 |
| F6 autoconfig XML unescaped | VULNERABLE | NOT VULNERABLE | `<probe/>` is escaped |
| F7 WebSocket buffers beyond maxSizeRequest | VULNERABLE | VULNERABLE | advertised maxSizeRequest 10000000; a 20 MiB fragmented message is fully read, then answered with the maxSizeRequest limit error |
| F8 bundle inflate unbounded | not testable | NOT TESTABLE | needs a crafted bundle at resource_url |
| F9 IMAP RENAME into own subtree | VULNERABLE | NOT VULNERABLE | `NO [CANNOT] Mailbox cannot be moved under itself.` for both cases; tree intact |
