#!/bin/sh
# F5: WebDAV MOVE of a collection into its own descendant is accepted and creates a parent-id cycle.
# Expected on fixed build: MOVE refused (403/409/502). Observed on 0.16.27: 201, then x.parentId=b and b.parentId=x.
. "$(dirname "$0")/env.sh"; set -u
P="$SW_HOST/dav/file/$(printf '%s' "$SW_USER_NAME" | sed 's/@/%40/')"
T=$(date +%s); A="a$T"; B="b$T"; X="x$T"
curl -s -u "$SW_USER" -o /dev/null -w "MKCOL $A:        HTTP %{http_code}\n" -X MKCOL "$P/$A/"
curl -s -u "$SW_USER" -o /dev/null -w "MKCOL $A/$B:   HTTP %{http_code}\n" -X MKCOL "$P/$A/$B/"
curl -s -u "$SW_USER" -o /dev/null -w "MOVE $A -> $A/$B/$X:  HTTP %{http_code}   (expected: refused)\n" -X MOVE "$P/$A/" -H "Destination: $P/$A/$B/$X/"
echo "FileNode parent ids after MOVE (look for $B and $X pointing at each other):"
curl -s -u "$SW_USER" -X POST "$SW_HOST/jmap" -H 'content-type: application/json' -d "{\"using\":[\"urn:ietf:params:jmap:core\",\"urn:ietf:params:jmap:filenode\"],\"methodCalls\":[[\"FileNode/query\",{\"accountId\":\"$SW_USER_ACCOUNT_ID\"},\"c0\"],[\"FileNode/get\",{\"accountId\":\"$SW_USER_ACCOUNT_ID\",\"#ids\":{\"resultOf\":\"c0\",\"name\":\"FileNode/query\",\"path\":\"/ids\"},\"properties\":[\"id\",\"name\",\"parentId\"]},\"c1\"]]}" | grep -o '{"id":"[^"]*","name":"[^"]*","parentId":[^}]*}' | grep "$T"
curl -s -u "$SW_USER" -o /dev/null -w "PROPFIND $A/ afterwards: HTTP %{http_code}   (404 = collection vanished from the tree)\n" -X PROPFIND "$P/$A/" -H 'Depth: 0'
