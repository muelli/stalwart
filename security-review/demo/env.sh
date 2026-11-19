# Lab target: stalwartlabs/stalwart:latest (0.16.27), bootstrapped with domain lab.test.
# Adjust to your instance. All demos are read-mostly probes against a throwaway server.
export SW_HOST="${SW_HOST:-http://127.0.0.1:8080}"
export SW_ADMIN="${SW_ADMIN:-admin@lab.test:CHANGE_ME}"
export SW_USER="${SW_USER:-user1@lab.test:CHANGE_ME}"
export SW_USER_NAME="${SW_USER_NAME:-user1@lab.test}"
export SW_USER_ACCOUNT_ID="${SW_USER_ACCOUNT_ID:-c}"   # JMAP accountId of SW_USER
export SW_ADMIN_ACCOUNT_ID="${SW_ADMIN_ACCOUNT_ID:-d333333}"
