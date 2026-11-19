Stalwart 0.16.27 demo scripts (findings reproduced against stalwartlabs/stalwart:latest, digest sha256:c429b311...).
Setup used: docker run -d --name sw -p 8080:8080 stalwartlabs/stalwart:latest ; complete bootstrap (x:Bootstrap/set),
create a plain user, note its JMAP accountId, fill env.sh. Then: sh F1_oauth_redirect.sh ; sh F4_header_panic.sh ;
sh F5_dav_move_cycle.sh ; sh F6_autoconfig_xml.sh ; python3 F7_ws_size.py 20
Each script prints RESULT lines and the expected behaviour of a fixed build. Use only against a throwaway instance you own.
F2 (push error body), F3 (TLSRPT redirects), F8 (bundle inflate) need external network and have no script.

## 1.1.1 re-verification
See ../verify-1.1.1/RESULTS.md. F9 reproducer: F9_imap_rename.py (IMAPS 993, self-signed, edit HOST/USER/PASS at the top).
