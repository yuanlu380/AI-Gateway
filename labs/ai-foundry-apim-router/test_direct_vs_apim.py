import requests, time, subprocess

# Direct call (your token) vs APIM call (managed identity)
APIM_URL = "https://apim-q6z6fj63xd7he.azure-api.net/inference/openai/deployments/gpt-4.1/chat/completions?api-version=2024-12-01-preview"
DIRECT_URL = "https://csavatar380.cognitiveservices.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2024-12-01-preview"
APIM_HEADERS = {"api-key": "29d5d6dc6fe748f1a9a08e08a67a3051", "Content-Type": "application/json"}
BODY = {"messages": [{"role": "user", "content": "Say hello in one word"}], "max_tokens": 5}
N = 10

# Get user token for direct calls
import os
token = os.environ.get("AZ_TOKEN")
if not token:
    print("Run first: $env:AZ_TOKEN = (az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken -o tsv)")
    exit(1)
DIRECT_HEADERS = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print(f"\n{'='*60}")
print(f"TEST 1: {N} sequential calls DIRECT to csavatar380 (East)")
print(f"{'='*60}")
for i in range(N):
    r = requests.post(DIRECT_URL, headers=DIRECT_HEADERS, json=BODY, timeout=60)
    remaining = r.headers.get("x-ratelimit-remaining-requests", "?")
    print(f"  Request {i+1:02d}: [{r.status_code}] remaining={remaining}")

time.sleep(2)

print(f"\n{'='*60}")
print(f"TEST 2: {N} sequential calls through APIM (managed identity)")
print(f"{'='*60}")
for i in range(N):
    r = requests.post(APIM_URL, headers=APIM_HEADERS, json=BODY, timeout=60)
    region = r.headers.get("x-backend-region", "?")
    remaining = r.headers.get("x-ratelimit-remaining-requests", "?")
    print(f"  Request {i+1:02d}: [{r.status_code}] region={region:5s} remaining={remaining}")
