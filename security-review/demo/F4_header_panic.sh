#!/bin/sh
# F4: HttpResponse::build().unwrap() panics when a header value is invalid.
# Trigger a) user-controlled `accept` query parameter on blob download.
# Trigger b) stored WebDAV media type containing a newline.
# Expected on fixed build: HTTP 200/400. Observed on 0.16.27: empty reply (curl exit 52) + panic in server stderr.
. "$(dirname "$0")/env.sh"; set -u
echo "a) upload a blob, then download with accept=text/plain<LF>x"
B=$(curl -s -u "$SW_USER" -X POST "$SW_HOST/jmap/upload/$SW_USER_ACCOUNT_ID" -H 'content-type: text/plain' --data 'demo' | sed -n 's/.*"blobId":"\([^"]*\)".*/\1/p')
echo "   blobId=$B"
curl -s -u "$SW_USER" -o /dev/null -w "   normal accept:  HTTP %{http_code}\n" "$SW_HOST/jmap/download/$SW_USER_ACCOUNT_ID/$B/x.txt?accept=text%2Fplain"
curl -s -u "$SW_USER" -o /dev/null -w "   accept with LF: HTTP %{http_code} curl_exit=%{exitcode}\n" "$SW_HOST/jmap/download/$SW_USER_ACCOUNT_ID/$B/x.txt?accept=text%2Fplain%0Ax"
echo "b) PUT a WebDAV file, PROPPATCH getcontenttype with &#10;, then GET it"
P="$SW_HOST/dav/file/$(printf '%s' "$SW_USER_NAME" | sed 's/@/%40/')"
F="f4-$(date +%s).txt"
curl -s -u "$SW_USER" -o /dev/null -w "   PUT:        HTTP %{http_code}\n" -X PUT "$P/$F" -H 'content-type: text/plain' --data 'demo'
curl -s -u "$SW_USER" -o /dev/null -w "   PROPPATCH:  HTTP %{http_code}\n" -X PROPPATCH "$P/$F" -H 'content-type: application/xml' --data '<?xml version="1.0"?><propertyupdate xmlns="DAV:"><set><prop><getcontenttype>text/plain&#10;x</getcontenttype></prop></set></propertyupdate>'
curl -s -u "$SW_USER" -o /dev/null -w "   GET after:  HTTP %{http_code} curl_exit=%{exitcode}\n" "$P/$F"
echo "Check server stderr for: panicked at crates/http-proto/src/response.rs:260  (docker logs <container> 2>&1 | grep panicked)"
