import json

nb = json.load(open(r"c:\git\AI-Gateway\labs\ai-foundry-model-gateway\foundry-ai-gateway.ipynb", encoding="utf-8"))
for i, c in enumerate(nb["cells"]):
    src = "".join(c.get("source", []))
    if "openai_client" in src or "responses.create" in src or "model_gateway_connection" in src:
        print(f"=== Cell {i} ===")
        print(src[:600])
        print()
