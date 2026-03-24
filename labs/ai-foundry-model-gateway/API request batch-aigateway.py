import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

# Foundry project endpoint (V3 deployment with model gateway)
ENDPOINT = "https://foundry1-vrsym2oc7ggvg.services.ai.azure.com/api/projects/ai-agent-service-foundry1"
MODEL = "ai-gateway/gpt-4.1-mini"

TOTAL_REQUESTS = 30

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
        return (i, f"ERROR: {type(e).__name__}", 0, 0, str(e)[:60], time.time())

print(f"Sending {TOTAL_REQUESTS} concurrent requests via Foundry model gateway")
print(f"Model: {MODEL}")
print(f"Route: SDK → Foundry → APIM → AI Services\n")

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
    print(f"{ts(t)}  Request {i:02d} → {status:30s} ({tokens})")

print(f"\n{'='*60}")
print(f"  Successful:       {ok_count} requests")
print(f"  Errors:           {err_count} requests")
print(f"  Total tokens:     {total_prompt} prompt + {total_completion} completion = {total_prompt + total_completion}")
print(f"  Duration:         {ts()} seconds")
print(f"{'='*60}")
