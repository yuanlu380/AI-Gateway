import requests
import time

URL = "https://apim-q6z6fj63xd7he.azure-api.net/inference/openai/deployments/gpt-4.1/chat/completions?api-version=2024-12-01-preview"
HEADERS = {
    "api-key": "29d5d6dc6fe748f1a9a08e08a67a3051",
    "Content-Type": "application/json"
}
BODY = {
    "messages": [{"role": "user", "content": "Say hello in one word"}],
    "max_tokens": 5
}

TOTAL_REQUESTS = 15

def ts():
    return time.strftime("%M:%S", time.gmtime(time.time() - start_time))

# Pre-flight: wait for East's rate limit to reset
print("Checking East capacity...", end=" ", flush=True)
while True:
    r = requests.post(URL, headers=HEADERS, json=BODY, timeout=60)
    region = r.headers.get("x-backend-region", "?")
    remaining = r.headers.get("x-ratelimit-remaining-requests", "?")
    if region == "East" and remaining not in ("?", "0"):
        print(f"OK (remaining: {remaining})\n")
        break
    print(f"\nEast exhausted (went to {region}). Waiting for rate limit reset...")
    for s in range(5, 0, -1):
        print(f"\r  Retrying in {s}s... ", end="", flush=True)
        time.sleep(1)
    print()

east_count = 0
west_count = 0
previous_region = None
start_time = time.time()

print(f"Sending {TOTAL_REQUESTS} sequential requests to gpt-4.1 (no delay)\n")

for i in range(1, TOTAL_REQUESTS + 1):
    try:
        r = requests.post(URL, headers=HEADERS, json=BODY, timeout=60)
        region = r.headers.get("x-backend-region", "?")
        remaining = r.headers.get("x-ratelimit-remaining-requests", "?")
        remaining_tokens = r.headers.get("x-ratelimit-remaining-tokens", "?")

        if region == "East":
            east_count += 1
        elif region == "West":
            west_count += 1

        note = ""
        if r.status_code == 429:
            note += " ⚠ THROTTLED"
        if r.status_code == 503:
            note += " ⚠ SERVICE UNAVAILABLE"
        if region == "West" and previous_region == "East":
            note += " 🔄 failover to West"

        print(f"{ts()}  Request {i:02d} → {region:7s} [{r.status_code}] (rpm: {remaining}, tpm: {remaining_tokens}){note}")
        if region in ("East", "West"):
            previous_region = region

    except Exception as e:
        print(f"{ts()}  Request {i:02d} → ERROR [{e}]")

print(f"\n{'='*60}")
print(f"  East (direct):    {east_count} requests")
print(f"  West (failover):  {west_count} requests")
print(f"  Total:            {east_count + west_count}/{TOTAL_REQUESTS}")
print(f"{'='*60}")