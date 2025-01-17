#!/usr/bin/env python3

from collections import defaultdict
from pprint import pprint
import requests
import os
from dotenv import load_dotenv
from google.cloud import cloudquotas_v1

load_dotenv()

MODEL_TO_NAME_MAPPING = {
    "@cf/deepseek-ai/deepseek-math-7b-instruct": "Deepseek Math 7B Instruct",
    "@cf/defog/sqlcoder-7b-2": "SQLCoder 7B 2",
    "@cf/fblgit/una-cybertron-7b-v2-bf16": "Una Cybertron 7B v2 (BF16)",
    "@cf/google/gemma-2b-it-lora": "Gemma 2B Instruct (LoRA)",
    "@cf/google/gemma-7b-it-lora": "Gemma 7B Instruct (LoRA)",
    "@cf/meta-llama/llama-2-7b-chat-hf-lora": "Llama 2 7B Chat (LoRA)",
    "@cf/meta/llama-2-7b-chat-fp16": "Llama 2 7B Chat (FP16)",
    "@cf/meta/llama-2-7b-chat-int8": "Llama 2 7B Chat (INT8)",
    "@cf/meta/llama-3-8b-instruct-awq": "Llama 3 8B Instruct (AWQ)",
    "@cf/meta/llama-3-8b-instruct": "Llama 3 8B Instruct",
    "@cf/meta/llama-3.1-8b-instruct-awq": "Llama 3.1 8B Instruct (AWQ)",
    "@cf/meta/llama-3.1-8b-instruct-fp8": "Llama 3.1 8B Instruct (FP8)",
    "@cf/meta/llama-3.1-8b-instruct": "Llama 3.1 8B Instruct",
    "@cf/microsoft/phi-2": "Phi-2",
    "@cf/mistral/mistral-7b-instruct-v0.1-vllm": "Mistral 7B Instruct v0.1",
    "@cf/mistral/mistral-7b-instruct-v0.1": "Mistral 7B Instruct v0.1",
    "@cf/mistral/mistral-7b-instruct-v0.2-lora": "Mistral 7B Instruct v0.2 (LoRA)",
    "@cf/openchat/openchat-3.5-0106": "OpenChat 3.5 0106",
    "@cf/qwen/qwen1.5-0.5b-chat": "Qwen 1.5 0.5B Chat",
    "@cf/qwen/qwen1.5-1.8b-chat": "Qwen 1.5 1.8B Chat",
    "@cf/qwen/qwen1.5-14b-chat-awq": "Qwen 1.5 14B Chat (AWQ)",
    "@cf/qwen/qwen1.5-7b-chat-awq": "Qwen 1.5 7B Chat (AWQ)",
    "@cf/thebloke/discolm-german-7b-v1-awq": "Discolm German 7B v1 (AWQ)",
    "@cf/tiiuae/falcon-7b-instruct": "Falcom 7B Instruct",
    "@cf/tinyllama/tinyllama-1.1b-chat-v1.0": "TinyLlama 1.1B Chat v1.0",
    "@hf/google/gemma-7b-it": "Gemma 7B Instruct",
    "@hf/meta-llama/meta-llama-3-8b-instruct": "Llama 3 8B Instruct",
    "@hf/mistral/mistral-7b-instruct-v0.2": "Mistral 7B Instruct v0.2",
    "@hf/nexusflow/starling-lm-7b-beta": "Starling LM 7B Beta",
    "@hf/nousresearch/hermes-2-pro-mistral-7b": "Hermes 2 Pro Mistral 7B",
    "@hf/thebloke/deepseek-coder-6.7b-base-awq": "Deepseek Coder 6.7B Base (AWQ)",
    "@hf/thebloke/deepseek-coder-6.7b-instruct-awq": "Deepseek Coder 6.7B Instruct (AWQ)",
    "@hf/thebloke/llama-2-13b-chat-awq": "Llama 2 13B Chat (AWQ)",
    "@hf/thebloke/llamaguard-7b-awq": "LlamaGuard 7B (AWQ)",
    "@hf/thebloke/mistral-7b-instruct-v0.1-awq": "Mistral 7B Instruct v0.1 (AWQ)",
    "@hf/thebloke/neural-chat-7b-v3-1-awq": "Neural Chat 7B v3.1 (AWQ)",
    "@hf/thebloke/openhermes-2.5-mistral-7b-awq": "OpenHermes 2.5 Mistral 7B (AWQ)",
    "@hf/thebloke/zephyr-7b-beta-awq": "Zephyr 7B Beta (AWQ)",
    "codellama-13b-instruct-hf": "CodeLlama 13B Instruct",
    "distil-whisper-large-v3-en": "Distil Whisper Large v3",
    "gemma-7b-it": "Gemma 7B Instruct",
    "gemma2-9b-it": "Gemma 2 9B Instruct",
    "google/gemma-2-9b-it:free": "Gemma 2 9B Instruct",
    "google/gemma-7b-it:free": "Gemma 7B Instruct",
    "gryphe/mythomist-7b:free": "Mythomist 7B",
    "huggingfaceh4/zephyr-7b-beta:free": "Zephyr 7B Beta",
    "llama-2-13b-chat-hf": "Llama 2 13B Chat",
    "llama-3-70b-instruct": "Llama 3 70B Instruct",
    "llama-3-8b-instruct": "Llama 3 8B Instruct",
    "llama-3.1-405b-reasoning": "Llama 3.1 405B",
    "llama-3.1-70b-versatile": "Llama 3.1 70B",
    "llama-3.1-8b-instant": "Llama 3.1 8B",
    "llama-guard-3-8b": "Llama Guard 3 8B",
    "llama3-70b-8192": "Llama 3 70B",
    "llama3-8b-8192": "Llama 3 8B",
    "llama3-groq-70b-8192-tool-use-preview": "Llama 3 70B - Groq Tool Use Preview",
    "llama3-groq-8b-8192-tool-use-preview": "Llama 3 8B - Groq Tool Use Preview",
    "meta-llama/llama-3-8b-instruct:free": "Llama 3 8B Instruct",
    "meta-llama/llama-3.1-8b-instruct:free": "Llama 3.1 8B Instruct",
    "meta-llama/meta-llama-3-70b-instruct": "Llama 3 70B Instruct",
    "meta-llama/meta-llama-3.1-405b-fp8": "Llama 3.1 405B Base (FP8)",
    "meta-llama/meta-llama-3.1-405b-instruct": "Llama 3.1 405B Instruct",
    "meta-llama/meta-llama-3.1-70b-instruct": "Llama 3.1 70B Instruct",
    "meta-llama/meta-llama-3.1-8b-instruct": "Llama 3.1 8B Instruct",
    "microsoft/phi-3-medium-128k-instruct:free": "Phi-3 Medium 128k Instruct",
    "microsoft/phi-3-mini-128k-instruct:free": "Phi-3 Mini 128k Instruct",
    "mistral-7b-instruct": "Mistral 7B Instruct",
    "mistralai/mistral-7b-instruct:free": "Mistral 7B Instruct",
    "mixtral-8x22b-instruct": "Mixtral 8x22B Instruct",
    "mixtral-8x7b-32768": "Mixtral 8x7B",
    "mixtral-8x7b-instruct": "Mixtral 8x7B Instruct",
    "nousresearch/hermes-3-llama-3.1-70b": "Hermes 3 Llama 3.1 70B",
    "nousresearch/nous-capybara-7b:free": "Nous Capybara 7B",
    "openchat/openchat-7b:free": "OpenChat 7B",
    "qwen/qwen-2-7b-instruct:free": "Qwen 2 7B Instruct",
    "qwen/qwen2-72b-instruct": "Qwen 2 72B Instruct",
    "undi95/toppy-m-7b:free": "Toppy M 7B",
    "whisper-large-v3": "Whisper Large v3",
}
MISSING_MODELS = set()


def get_model_name(id):
    id = id.lower()
    if id in MODEL_TO_NAME_MAPPING:
        return MODEL_TO_NAME_MAPPING[id]
    MISSING_MODELS.add(id)
    return id


def get_groq_limits_for_stt_model(model_id):
    print(f"Getting limits for STT model {model_id}...")
    r = requests.post(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        headers={
            "Authorization": f'Bearer {os.environ["GROQ_API_KEY"]}',
        },
        data={
            "model": model_id,
        },
        files={
            "file": open("1-second-of-silence.mp3", "rb"),
        },
    )
    r.raise_for_status()
    audio_seconds_per_minute = int(r.headers["x-ratelimit-limit-audio-seconds"])
    rpd = int(r.headers["x-ratelimit-limit-requests"])
    return {
        "audio-seconds/minute": audio_seconds_per_minute,
        "requests/day": rpd,
    }


def get_groq_limits_for_model(model_id):
    if "whisper" in model_id:
        return get_groq_limits_for_stt_model(model_id)
    print(f"Getting limits for chat model {model_id}...")
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f'Bearer {os.environ["GROQ_API_KEY"]}',
            "Content-Type": "application/json",
        },
        json={
            "model": model_id,
            "messages": [{"role": "user", "content": "Hi!"}],
            "stream": True,
        },
        stream=True,
    )
    try:
        r.raise_for_status()
        rpd = int(r.headers["x-ratelimit-limit-requests"])
        tpm = int(r.headers["x-ratelimit-limit-tokens"])
        return {"requests/day": rpd, "tokens/minute": tpm}
    except Exception as e:
        print(f"Failed to get limits for model {model_id}: {e}")
        print(r.text)
        return {"requests/day": "Unknown", "tokens/minute": "Unknown"}


def fetch_groq_models():
    print("Fetching Groq models...")
    r = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={
            "Authorization": f'Bearer {os.environ["GROQ_API_KEY"]}',
            "Content-Type": "application/json",
        },
    )
    r.raise_for_status()
    models = r.json()["data"]
    pprint(models)
    ret_models = []
    for model in models:
        limits = get_groq_limits_for_model(model["id"])
        ret_models.append(
            {
                "id": model["id"],
                "name": get_model_name(model["id"]),
                "limits": limits,
            }
        )
    ret_models = sorted(ret_models, key=lambda x: x["name"])
    return ret_models


def fetch_openrouter_models():
    print("Fetching OpenRouter models...")
    r = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={
            "Content-Type": "application/json",
        },
    )
    r.raise_for_status()
    models = r.json()["data"]
    print(f"Fetched {len(models)} models from OpenRouter")
    ret_models = []
    for model in models:
        pricing = float(model.get("pricing", {}).get("completion", "1")) + float(
            model.get("pricing", {}).get("prompt", "1")
        )
        if pricing != 0:
            continue
        if ":free" not in model["id"]:
            continue
        ret_models.append(
            {
                "id": model["id"],
                "name": get_model_name(model["id"]),
                "limits": {
                    "requests/minute": 20,
                    "requests/day": 200,
                },
            }
        )
    ret_models = sorted(ret_models, key=lambda x: x["name"])
    return ret_models


def fetch_cloudflare_models():
    print("Fetching Cloudflare models...")
    r = requests.get(
        f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/ai/models/search?search=Text+Generation",
        headers={
            "Authorization": f'Bearer {os.environ["CLOUDFLARE_API_KEY"]}',
            "Content-Type": "application/json",
        },
    )
    r.raise_for_status()
    models = r.json()["result"]
    print(f"Fetched {len(models)} models from Cloudflare")
    ret_models = []
    for model in models:
        ret_models.append(
            {
                "id": model["name"],
                "name": get_model_name(model["name"]),
            }
        )
    ret_models = sorted(ret_models, key=lambda x: x["name"])
    return ret_models


def fetch_ovh_models():
    print("Fetching OVH models...")
    r = requests.get(
        "https://endpoints-backend.ai.cloud.ovh.net/rest/v1/models_v2",
        params={"select": "*", "order": "id.desc", "offset": "0", "limit": "100"},
        headers={
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "accept-profile": "public",
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzEwNzE2NDAwLAogICJleHAiOiAxODY4NDgyODAwCn0.Jty_eO4oWqLm4Lx_LfbpRW5WESXYXtT2humbBq2Pal8",
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzEwNzE2NDAwLAogICJleHAiOiAxODY4NDgyODAwCn0.Jty_eO4oWqLm4Lx_LfbpRW5WESXYXtT2humbBq2Pal8",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "x-client-info": "supabase-js-web/2.39.7",
        },
    )
    r.raise_for_status()
    models = list(
        filter(lambda x: x["available"] and x["category"] == "Assistant", r.json())
    )
    print(f"Fetched {len(models)} models from OVH")
    ret_models = []
    for model in models:
        ret_models.append(
            {
                "id": model["name"],
                "name": get_model_name(model["name"]),
                "limits": {
                    "requests/minute": 12,
                },
            }
        )
    ret_models = sorted(ret_models, key=lambda x: x["name"])
    return ret_models


def fetch_hyperbolic_models():
    print("Fetching Hyperbolic models...")

    r = requests.post(
        "https://firestore.googleapis.com/v1/projects/ai-dashboard-cfd6a/databases/(default)/documents:runQuery",
        headers={
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-type": "text/plain",
            "dnt": "1",
            "google-cloud-resource-prefix": "projects/ai-dashboard-cfd6a/databases/(default)",
            "origin": "https://app.hyperbolic.xyz",
            "priority": "u=1, i",
            "referer": "https://app.hyperbolic.xyz/",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "x-goog-api-client": "gl-js/ fire/10.10.0_lite",
            "x-goog-request-params": "project_id=ai-dashboard-cfd6a",
        },
        json={
            "structuredQuery": {
                "from": [{"collectionId": "models"}],
                "where": {
                    "compositeFilter": {
                        "op": "AND",
                        "filters": [
                            {
                                "fieldFilter": {
                                    "field": {"fieldPath": "type"},
                                    "op": "IN",
                                    "value": {
                                        "arrayValue": {
                                            "values": [
                                                {"stringValue": "llm"},
                                                # {"stringValue": "vlm"},
                                            ]
                                        }
                                    },
                                },
                            },
                            # {
                            #     "fieldFilter": {
                            #         "field": {"fieldPath": "hidden"},
                            #         "op": "NOT_EQUAL",
                            #         "value": {"booleanValue": True},
                            #     },
                            # },
                        ],
                    },
                },
            }
        },
    )
    r.raise_for_status()
    models = r.json()
    print(f"Fetched {len(models)} models from Hyperbolic")
    ret_models = []
    for model in models:
        model_data = model["document"]["fields"]
        if "hidden" in model_data and model_data["hidden"]["booleanValue"]:
            continue
        ret_models.append(
            {
                "id": model_data["model"]["stringValue"],
                "name": get_model_name(model_data["model"]["stringValue"]),
                "limits": {
                    # https://discord.com/channels/1196951041971863664/1197273823192547500/1267279465226965065
                    # Unclear if this is a global rate limit or a per-model rate limit
                    "requests/minute": 200,
                },
            }
        )
    pprint(ret_models)
    return ret_models

def fetch_gemini_limits():
    print("Fetching Gemini limits...")
    client = cloudquotas_v1.CloudQuotasClient()
    request = cloudquotas_v1.ListQuotaInfosRequest(
        parent=f"projects/{os.environ["GCP_PROJECT_ID"]}/locations/global/services/generativelanguage.googleapis.com")
    pager = client.list_quota_infos(request=request)
    models = defaultdict(dict)
    for quota in pager:
        if quota.metric == 'generativelanguage.googleapis.com/generate_content_free_tier_input_token_count':
            for dimension in quota.dimensions_infos:
                models[dimension.dimensions.get("model")][f"tokens/{quota.refresh_interval}"] = dimension.details.value
        elif quota.metric == 'generativelanguage.googleapis.com/generate_content_free_tier_requests':
            for dimension in quota.dimensions_infos:
                models[dimension.dimensions.get("model")][f"requests/{quota.refresh_interval}"] = dimension.details.value
    pprint(models)
    return models
    

def get_human_limits(model):
    if "limits" not in model:
        return ""
    limits = model["limits"]
    return "<br>".join([f"{value} {key}" for key, value in limits.items()])


def main():
    # markdown_table = "|Provider|Provider Limits/Notes|Model Name|Model Limits|\n|---|---|---|---|\n"
    table = """<table>
    <thead>
        <tr>
            <th>Provider</th>
            <th>Provider Limits/Notes</th>
            <th>Model Name</th>
            <th>Model Limits</th>
        </tr>
    </thead>
    <tbody>
"""

    groq_models = fetch_groq_models()
    for idx, model in enumerate(groq_models):
        table += f"<tr>{f'<td rowspan="{len(groq_models)}"><a href="https://console.groq.com" target="_blank">Groq</a></td>' if idx == 0 else ''}{ f'<td rowspan="{len(groq_models)}"></td>' if idx == 0 else ''}<td>{model['name']}</td><td>{get_human_limits(model)}</td></tr>\n"

    openrouter_models = fetch_openrouter_models()
    for idx, model in enumerate(openrouter_models):
        table += f"<tr>{f'<td rowspan="{len(openrouter_models)}"><a href="https://openrouter.ai" target="_blank">OpenRouter</a></td>' if idx == 0 else ''}{ f'<td rowspan="{len(openrouter_models)}"></td>' if idx == 0 else ''}<td>{model['name']}</td><td>{get_human_limits(model)}</td></tr>\n"

    gemini_models = fetch_gemini_limits()
    table += f"""<tr>
            <td rowspan="6"><a href="https://aistudio.google.com" target="_blank">Google AI Studio</a></td>
            <td rowspan="4">Free tier Gemini API access not available within UK/CH/EEA/EU/<br>Data is used for training.</td>
            <td>Gemini 1.5 Flash</td>
            <td>{get_human_limits({"limits": gemini_models["gemini-1.5-flash"]})}</td>
        </tr>
        <tr>
            <td>Gemini 1.5 Pro</td>
            <td>{get_human_limits({"limits": gemini_models["gemini-1.5-pro"]})}</td>
        </tr>
        <tr>
            <td>Gemini 1.5 Pro (Experimental 0801)</td>
            <td>{get_human_limits({"limits": gemini_models["gemini-1.5-pro-exp"]})}</td>
        </tr>
        <tr>
            <td>Gemini 1.0 Pro</td>
            <td>{get_human_limits({"limits": gemini_models["gemini-1.0-pro"]})}</td>
        </tr>
        <tr>
            <td rowspan="2">Embeddings are available in UK/CH/EEA/EU</td>
            <td>text-embedding-004</td>
            <td>1500 requests/min<br>100 content/batch</td>
        </tr>
        <tr>
            <td>embedding-001</td>
            <td>1500 requests/min<br>100 content/batch</td>
        </tr>"""
    
    table += """<tr>
        <td><a href="https://console.cloud.google.com/vertex-ai/publishers/meta/model-garden" target="_blank">Google Cloud Vertex AI</a></td>
        <td>Very stringent payment verification for Google Cloud.</td>
        <td><a href="https://console.cloud.google.com/vertex-ai/publishers/meta/model-garden/llama3-405b-instruct-maas" target="_blank">Llama 3.1 405B Instruct</a></td>
        <td>Llama 3.1 API Service free during preview.<br>60 requests/minute</td>
    </tr>"""

    table += """<tr>
        <td><a href="https://glhf.chat/" target="_blank">glhf.chat (Free Beta)</a></td>
        <td></td>
        <td>Any model on Hugging Face runnable on vLLM and fits on a A100 node (~640GB VRAM), including Llama 3.1 405B at FP8</td>
        <td></td>
    </tr>"""

    table += """<tr>
            <td rowspan="2"><a href="https://cohere.com" target="_blank">Cohere</a></td>
            <td rowspan="2">10 requests/min<br>1000 requests/month</td>
            <td>Command-R</td>
            <td>Shared Limit</td>
        </tr>
        <tr>
            <td>Command-R+</td>
            <td>Shared Limit</td>
        </tr>"""

    table += """<tr>
            <td><a href="https://huggingface.co/docs/api-inference/en/index" target="_blank">HuggingFace Serverless Inference</a></td>
            <td>Dynamic Rate Limits.<br>Limited to models smaller than 10GB.<br>Some popular models are supported even if they exceed 10GB.</td>
            <td>Various open models</td>
            <td></td>
        </tr>"""

    hyperbolic_models = fetch_hyperbolic_models()
    for idx, model in enumerate(hyperbolic_models):
        table += f"<tr>{f'<td rowspan="{len(hyperbolic_models)}"><a href="https://app.hyperbolic.xyz/" target="_blank">Hyperbolic (Free Testing Period)</a></td>' if idx == 0 else ''}{ f'<td rowspan="{len(hyperbolic_models)}"></td>' if idx == 0 else ''}<td>{model['name']}</td><td>{get_human_limits(model)}</td></tr>\n"

    ovh_models = fetch_ovh_models()
    for idx, model in enumerate(ovh_models):
        table += f"<tr>{f'<td rowspan="{len(ovh_models)}"><a href="https://endpoints.ai.cloud.ovh.net/" target="_blank">OVH AI Endpoints (Free Alpha)</a></td>' if idx == 0 else ''}{ f'<td rowspan="{len(ovh_models)}">Token expires every 2 weeks.</td>' if idx == 0 else ''}<td>{model['name']}</td><td>{get_human_limits(model)}</td></tr>\n"

    cloudflare_models = fetch_cloudflare_models()
    for idx, model in enumerate(cloudflare_models):
        table += f"<tr>{f'<td rowspan="{len(cloudflare_models)}"><a href="https://developers.cloudflare.com/workers-ai" target="_blank">Cloudflare Workers AI</a></td>' if idx == 0 else ''}{ f'<td rowspan="{len(cloudflare_models)}">10000 neurons/day<br>Beta models have unlimited usage.<br>Typically 300 requests/min for text models.</td>' if idx == 0 else ''}<td>{model['name']}</td><td></td></tr>\n"

    table += """<tr>
            <td><a href="https://docs.lambdalabs.com/on-demand-cloud/using-the-lambda-chat-completions-api" target="_blank">Lambda Labs (Free Preview)</a></td>
            <td><a href="https://lambdalabs.com/blog/unveiling-hermes-3-the-first-fine-tuned-llama-3.1-405b-model-is-on-lambdas-cloud" target="_blank">Free for a limited time</a></td>
            <td>Nous Hermes 3 Llama 3.1 405B (FP8)</td>
            <td></td>
        </tr>"""
    
    table += """<tr>
        <td><a href="https://codestral.mistral.ai/" target="_blank">Mistral (Codestral)</a></td>
        <td>Currently free to use, monthly subscription based, requires phone number verification.</td>
        <td>Codestral</td>
        <td>30 requests/minute<br>2000 requests/day</td>
    </tr>"""

    table += "</tbody></table>"

    print("Missing models:")
    print(list(MISSING_MODELS))

    with open("README_template.md", "r") as f:
        readme = f.read()
    with open("../README.md", "w") as f:
        f.write(readme.replace("{{MODEL_LIST}}", table))
    print("Wrote models to README.md")


if __name__ == "__main__":
    main()
