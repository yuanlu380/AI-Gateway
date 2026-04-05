import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://apim-q6z6fj63xd7he.azure-api.net/inference/openai/responses?api-version=2025-03-01-preview"
HEADERS = {
    "api-key": "29d5d6dc6fe748f1a9a08e08a67a3051",
    "Content-Type": "application/json"
}
BODY = {
    "model": "gpt-4.1",
    "input": "Say hello in one word"
}

TOTAL_REQUESTS = 15

start_time = time.time()

def ts(t=None):
    return time.strftime("%M:%S", time.gmtime((t or time.time()) - start_time))

def call(i):
    try:
        r = requests.post(URL, headers=HEADERS, json=BODY, timeout=60)
        return (i, r.headers.get("x-backend-region", "?"), r.status_code,
                r.headers.get("x-ratelimit-remaining-requests", "?"),
                r.headers.get("x-ratelimit-remaining-tokens", "?"),
                r.headers.get("x-retry-count", "0"),
                time.time())
    except Exception as e:
        return (i, "ERROR", 0, "?", "?", "0", time.time())

print(f"Sending {TOTAL_REQUESTS} concurrent requests to gpt-4.1")
print(f"West: absorbs overflow on 429\n")

east_count = 0
west_count = 0

with ThreadPoolExecutor(max_workers=TOTAL_REQUESTS) as pool:
    futures = {pool.submit(call, i): i for i in range(1, TOTAL_REQUESTS + 1)}
    results = []
    for future in as_completed(futures):
        results.append(future.result())

results.sort(key=lambda x: x[0])

for (i, region, status, rpm, tpm, retries, t) in results:
    if region == "East":
        east_count += 1
    elif region == "West":
        west_count += 1

    note = ""
    if status == 429:
        note += " ** THROTTLED"
    if status == 503:
        note += " ** SERVICE UNAVAILABLE"
    if region == "West":
        note += " << East 429 -> retried to West"

    print(f"{ts(t)}  Request {i:02d} -> {region:7s} [{status}] retries:{retries} (rpm: {rpm}, tpm: {tpm}){note}")

print(f"\n{'='*60}")
print(f"  East (direct):    {east_count} requests")
print(f"  West (failover):  {west_count} requests")
print(f"  Total:            {east_count + west_count}/{TOTAL_REQUESTS}")
print(f"  Duration:         {ts()} seconds")
print(f"{'='*60}")