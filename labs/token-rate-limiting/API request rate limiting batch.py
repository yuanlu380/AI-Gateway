import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://apim-x5o2pmo7tfdnk.azure-api.net/inference/openai/deployments/gpt-4.1-mini/chat/completions?api-version=2025-03-01-preview"
HEADERS = {
    "api-key": "48cfc7267ea4490ab9b8aad78ce14bc3",
    "Content-Type": "application/json"
}
BODY = {
    "messages": [{"role": "user", "content": "Say hello in one word"}],
    "max_tokens": 5
}

TOTAL_REQUESTS = 30

start_time = time.time()

def ts(t=None):
    return time.strftime("%M:%S", time.gmtime((t or time.time()) - start_time))

def call(i):
    try:
        r = requests.post(URL, headers=HEADERS, json=BODY, timeout=60)
        return (i, r.status_code,
                r.headers.get("x-ratelimit-remaining-tokens", "?"),
                r.headers.get("retry-after", ""),
                time.time())
    except Exception as e:
        return (i, 0, "?", "", time.time())

print(f"Sending {TOTAL_REQUESTS} sequential requests to gpt-4.1-mini")
print(f"Token rate limit: 100 TPM (per subscription)")
print(f"Expected: first ~2 requests succeed, then 429s until the window resets\n")

ok_count = 0
throttled_count = 0

results = []
for i in range(1, TOTAL_REQUESTS + 1):
    result = call(i)
    results.append(result)

for (i, status, remaining_tokens, retry_after, t) in results:
    if status == 200:
        ok_count += 1
    elif status == 429:
        throttled_count += 1

    note = ""
    if status == 429:
        note = f" ⚠ THROTTLED (retry-after: {retry_after}s)"
    elif status == 200:
        note = " ✅"

    print(f"{ts(t)}  Request {i:02d} [{status}] remaining-tokens: {remaining_tokens}{note}")

print(f"\n{'='*60}")
print(f"  Successful (200):   {ok_count} requests")
print(f"  Throttled (429):    {throttled_count} requests")
print(f"  Total:              {ok_count + throttled_count}/{TOTAL_REQUESTS}")
print(f"  Duration:           {ts()} seconds")
print(f"{'='*60}")
