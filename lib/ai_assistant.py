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


def _get_available_model(api_key):
    """Query ListModels to find a model that supports generateContent."""
    import json as _json
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
            for m in data.get("models", []):
                methods = m.get("supportedGenerationMethods", [])
                name = m.get("name", "")
                if "generateContent" in methods and "flash" in name:
                    return name.replace("models/", "")
            # Fallback: return first model that supports generateContent
            for m in data.get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    return m.get("name", "").replace("models/", "")
    except Exception:
        pass
    return "gemini-2.0-flash"  # last resort


def _call_api_http(api_key, prompt):
    """Direct HTTP call to Gemini API."""
    import json as _json

    model_name = _get_available_model(api_key)
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
        body = e.read().decode("utf-8")
        return f"API Error ({e.code}): {body}"
    except Exception as e:
        return f"Error: {str(e)}"


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
