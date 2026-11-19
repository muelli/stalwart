#!/bin/sh
# F1 on Stalwart 1.1.x: the login API changed; the authorization parameters are passed as a `query` string.
# Registered client "labclient" has redirectUris={https://good.example/cb}. Expected on a fixed build: unregistered URI refused.
. "$(dirname "$0")/../demo/env.sh"; set -u
for URI in https://attacker.example/cb https://good.example/cb; do
  Q="response_type=code&client_id=labclient&redirect_uri=$(printf '%s' "$URI" | sed 's#:#%3A#g; s#/#%2F#g')&scope=openid"
  printf '%s -> ' "$URI"
  curl -s --noproxy '*' -X POST "$SW_HOST/api/auth" -H 'content-type: application/json' -H "Origin: $SW_HOST" \
    -d "{\"type\":\"authCode\",\"accountName\":\"$SW_USER_NAME\",\"accountSecret\":\"${SW_USER#*:}\",\"query\":\"$Q\",\"consent\":true}" | cut -c1-220; echo
done
