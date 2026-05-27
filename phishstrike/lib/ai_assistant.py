import base64
import hashlib
import json
import os
import urllib.request

from cryptography.fernet import Fernet

CONFIG_PATH = "auth/ai_config.json"


def _fernet() -> Fernet:
    from phishstrike.core.config import Config

    raw = hashlib.sha256(Config.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(raw))


def _encrypt(text: str) -> str:
    return _fernet().encrypt(text.encode()).decode()


def _decrypt(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except Exception:
        return token


def setup_ai():
    from phishstrike.lib.logger import get_logger

    log = get_logger("AI")
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
            api_key = config.get("api_key", "")
            if api_key:
                return True
        except Exception as e:
            log.error(f"Failed to load AI config: {e}")
    return False


def get_api_key():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                encrypted = json.load(f).get("api_key", "")
                return _decrypt(encrypted) if encrypted else ""
        except Exception:
            pass
    return ""


def save_api_key(api_key):
    if not os.path.exists("auth"):
        os.makedirs("auth")
    with open(CONFIG_PATH, "w") as f:
        json.dump({"api_key": _encrypt(api_key)}, f)


def _make_request(url: str, api_key: str, data: bytes | None = None, method: str = "GET", timeout: int = 10):
    """Make a request to Gemini API with key in header (never in URL)."""
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    req = urllib.request.Request(
        url, data=data, headers=headers, method=method
    )
    return urllib.request.urlopen(req, timeout=timeout)


def _get_available_models(api_key):
    """Return a list of models to try, prioritizing those that are likely available."""
    from phishstrike.lib.logger import get_logger

    log = get_logger("AI")
    models_to_try = []
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    try:
        with _make_request(url, api_key, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for m in data.get("models", []):
                methods = m.get("supportedGenerationMethods", [])
                name = m.get("name", "")
                if "generateContent" in methods:
                    name = name.replace("models/", "")
                    if "flash" in name:
                        models_to_try.append(name)
    except Exception as e:
        log.warning(f"Model list fetch failed: {e}")

    fallbacks = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-2.0-flash",
    ]
    for fb in fallbacks:
        if fb not in models_to_try:
            models_to_try.append(fb)

    return models_to_try


def _call_api_http(api_key, prompt):
    """Direct HTTP call to Gemini API with key in header."""
    from phishstrike.lib.logger import get_logger

    log = get_logger("AI")
    models = _get_available_models(api_key)
    last_error = ""

    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")

        try:
            with _make_request(url, api_key, data=payload, method="POST", timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode("utf-8")
                error_data = json.loads(body)
                error_msg = error_data.get("error", {}).get("message", body)
                if e.code == 404:
                    last_error = f"Model {model_name} not found."
                    continue
                if e.code == 429:
                    last_error = f"Quota Exceeded on {model_name}: {error_msg}"
                    continue
                return f"API Error ({e.code}) on {model_name}: {error_msg}"
            except Exception:
                return f"API Error ({e.code}) on {model_name}"
        except Exception as e:
            log.error(f"Request failed on {model_name}: {e}")
            return f"Error on {model_name}: {e}"

    return f"Failed after multiple models.\nLast Error: {last_error}"


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
