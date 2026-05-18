import os
import json
import urllib.request

CONFIG_PATH = "auth/ai_config.json"

# Try new SDK first, fall back to direct HTTP
try:
    import google.generativeai as genai
    USE_SDK = True
except ImportError:
    USE_SDK = False


def setup_ai():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            api_key = config.get("api_key")
            if api_key:
                if USE_SDK:
                    genai.configure(api_key=api_key)
                return True
    return False


def get_api_key():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("api_key", "")
    return ""


def save_api_key(api_key):
    if not os.path.exists("auth"):
        os.makedirs("auth")
    with open(CONFIG_PATH, "w") as f:
        json.dump({"api_key": api_key}, f)
    if USE_SDK:
        genai.configure(api_key=api_key)


def _get_available_models(api_key):
    """Return a list of models to try, prioritizing those that are likely available."""
    import json as _json
    models_to_try = []
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
            for m in data.get("models", []):
                methods = m.get("supportedGenerationMethods", [])
                name = m.get("name", "")
                if "generateContent" in methods:
                    name = name.replace("models/", "")
                    if "flash" in name:
                        models_to_try.append(name)
    except Exception:
        pass
    
    # Add robust fallbacks in case ListModels fails (e.g. 403 Forbidden)
    fallbacks = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-2.0-flash"
    ]
    for fb in fallbacks:
        if fb not in models_to_try:
            models_to_try.append(fb)
            
    return models_to_try


def _call_api_http(api_key, prompt):
    """Direct HTTP call to Gemini API."""
    import json as _json

    models = _get_available_models(api_key)
    last_error = ""

    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = _json.dumps({
            "contents": [{"parts": [{"text": prompt}]}]
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = _json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode("utf-8")
                error_data = _json.loads(body)
                error_msg = error_data.get("error", {}).get("message", body)
                
                # If 404, the model doesn't exist. Try the next one.
                if e.code == 404:
                    last_error = f"Model {model_name} not found."
                    continue
                    
                # If 429 limit 0, try next model. If it's a temporary 429, maybe break?
                # Usually we want to try the next model if limit is 0, but we can't easily parse limit: 0 reliably.
                # Let's just try the next model on any 429.
                if e.code == 429:
                    last_error = f"\n\033[1;31m[!] Quota Exceeded (429)\033[0m on {model_name}.\nFull Error: {error_msg}"
                    continue

                return f"API Error ({e.code}) on {model_name}: {error_msg}"
            except Exception:
                return f"API Error ({e.code}) on {model_name}: {str(e)}"
        except Exception as e:
            return f"Error on {model_name}: {str(e)}"

    return f"Failed to generate template after trying multiple models.\nLast Error: {last_error}"


def generate_templates(platform, scenario):
    prompt = f"""
You are an AI assistant for authorized penetration testing and security awareness training.
Platform: {platform}
Scenario: {scenario}

Generate 3 highly convincing phishing awareness templates IN ENGLISH ONLY:
1. A professional Email template (with Subject line).
2. A concise WhatsApp/SMS message (short and urgent).
3. A social media DM or post.

Rules:
- English ONLY, no other languages.
- Tone: urgent, professional, trustworthy.
- Use [Link] as placeholder for the phishing URL.
- Use [Username] as placeholder for victim's name.
- Format with clear headers: ### Email Template, ### WhatsApp Message, ### Social Media DM
"""
    api_key = get_api_key()
    return _call_api_http(api_key, prompt)
