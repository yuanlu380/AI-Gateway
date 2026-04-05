import time
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

# Foundry project endpoint (V3 deployment with model gateway)
ENDPOINT = "https://agents-foundry-q6z6fj63xd7he.services.ai.azure.com/api/projects/foundry-project-agents-foundry"
MODEL = "ai-gateway/gpt-4.1"

TOTAL_REQUESTS = 30
WORKSPACE_ID = "8234de70-b5c0-47a4-85f6-7dd94c9a0c3a"

# Initialize Foundry client and get OpenAI client (routes through APIM via model gateway connection)
project = AIProjectClient(endpoint=ENDPOINT, credential=AzureCliCredential())
openai_client = project.get_openai_client()

start_time = time.time()

def ts(t=None):
    return time.strftime("%M:%S", time.gmtime((t or time.time()) - start_time))

def call(i):
    try:
        r = openai_client.responses.create(
            model=MODEL,
            input="Say hello in one word"
        )
        input_tokens = r.usage.input_tokens if r.usage else 0
        output_tokens = r.usage.output_tokens if r.usage else 0
        content = r.output_text.strip() if r.output_text else "?"
        return (i, "OK", input_tokens, output_tokens, content, time.time())
    except Exception as e:
        return (i, f"ERROR: {type(e).__name__}", 0, 0, str(e)[:200], time.time())

print(f"Sending {TOTAL_REQUESTS} concurrent requests via Foundry model gateway")
print(f"Model: {MODEL}")
print("Route: SDK -> Foundry -> APIM -> AI Services")
print()

ok_count = 0
err_count = 0
total_prompt = 0
total_completion = 0

with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(call, i): i for i in range(1, TOTAL_REQUESTS + 1)}
    results = []
    for future in as_completed(futures):
        results.append(future.result())

# Sort by request number for clean output
results.sort(key=lambda x: x[0])

for (i, status, input_tk, output_tk, content, t) in results:
    if status == "OK":
        ok_count += 1
        total_prompt += input_tk
        total_completion += output_tk
    else:
        err_count += 1

    tokens = f"in: {input_tk}, out: {output_tk}, response: {content}" if status == "OK" else content
    print(f"{ts(t)}  Request {i:02d} -> {status:30s} ({tokens})")

print(f"\n{'='*60}")
print(f"  Successful:       {ok_count} requests")
print(f"  Errors:           {err_count} requests")
print(f"  Total tokens:     {total_prompt} prompt + {total_completion} completion = {total_prompt + total_completion}")
print(f"  Duration:         {ts()} seconds")
print(f"{'='*60}")

# --- Query APIM logs from App Insights to show backend routing ---
print(f"\nWaiting 30s for App Insights ingestion...")
time.sleep(30)

kql = (
    "AppRequests "
    "| where TimeGenerated > ago(5m) "
    "| where AppRoleName has 'apim' "
    "| where Name has 'completions' "
    "| extend props = todynamic(Properties) "
    "| extend region = tostring(props['Response-x-ms-region']) "
    "| summarize count() by region, ResultCode "
    "| order by region asc"
)

print(f"Querying APIM logs from App Insights...\n")
try:
    result = subprocess.run(
        f'az monitor log-analytics query --workspace {WORKSPACE_ID} '
        f'--analytics-query "{kql}" '
        '--query "[].{region:region, status:ResultCode, count:count_}" -o table',
        capture_output=True, text=True, timeout=30, shell=True
    )
    if result.returncode == 0 and result.stdout.strip():
        print("APIM Backend Routing (from App Insights):")
        print(result.stdout)
    else:
        err = result.stderr.strip() if result.stderr else "No data yet"
        print(f"No logs available yet. App Insights may need more time. ({err})")
except Exception as e:
    print(f"Log query failed: {e}")
