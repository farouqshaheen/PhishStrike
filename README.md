<p align="center">
  <img src="https://raw.githubusercontent.com/farouqshaheen/PhishStrike/main/.github/misc/logo.png" width="200">
</p>

<h1 align="center">PHISH STRIKE</h1>

<p align="center">
  <b>Elite Cybersecurity Phishing Dashboard & Automation Framework</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Authors-Farouq%20Shaheen%20%26%20Lujain%20Ghatasheh-white?style=for-the-badge&logo=github">
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/farouqshaheen/PhishStrike?style=for-the-badge&color=blueviolet">
  <img src="https://img.shields.io/github/stars/farouqshaheen/PhishStrike?style=for-the-badge&color=FF2DAA">
  <img src="https://img.shields.io/github/forks/farouqshaheen/PhishStrike?style=for-the-badge&color=0066CC">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/UI-Cyber%20Dashboard-neon?style=flat-square">
  <img src="https://img.shields.io/badge/Language-Python-blue?style=flat-square&logo=python">
  <img src="https://img.shields.io/badge/Requires-PHP-purple?style=flat-square&logo=php">
</p>

---

### ⚡ Overview
**PhishStrike** is a modernized, high-performance automated phishing tool designed for security professionals and ethical hackers. It features a premium **Cyber Dashboard UI** with neon accents, a live web intelligence panel, AI-powered phishing assistant, and 30+ sophisticated templates for major social, email, and financial platforms.

### 💎 Key Features
*   **Modern UI/UX**: Sleek terminal dashboard with neon gradients, glitch animations, and real-time status indicators.
*   **30+ Templates**: Authentic login pages for Facebook, Instagram, Google, Microsoft, Netflix, Discord, and more.
*   **Reels/Video Lure**: New Social Media Reels module — send a video link that requires login to watch, then redirect to the real video.
*   **Triple Tunneling**: Built-in support for `Localhost`, `Cloudflared`, and `LocalXpose`.
*   **Dynamic Masking**: Advanced URL masking and shortening via is.gd, TinyURL, and shrtco.de.
*   **Web Dashboard**: Live Flask-based intelligence panel at `http://localhost:5000` with export to Excel, CSV, and PDF.
*   **AI Assistant**: Gemini-powered social engineering template generator.
*   **Advanced Fingerprinting**: Silently collects OS, browser, screen resolution, language, and timezone from every visitor.
*   **Custom Post-Login Alerts**: Displays a convincing security alert page before redirecting the victim.
*   **Docker Ready**: Fully containerized for easy deployment and isolation.

---

### 🚀 Installation

#### Step 1 — Prerequisites

> [!IMPORTANT]
> **PHP** is required to run the local phishing server. Install it before launching PhishStrike.

| Platform | Install Command |
| :--- | :--- |
| **Ubuntu / Debian / Kali** | `sudo apt install php` |
| **Arch / Manjaro** | `sudo pacman -S php` |
| **Windows** | Download from [php.net/downloads](https://www.php.net/downloads.php) and add to PATH |
| **Termux (Android)** | `pkg install php` |
| **macOS (Homebrew)** | `brew install php` |

#### Step 2 — Clone & Install

```bash
# Clone the repository
git clone https://github.com/farouqshaheen/PhishStrike.git

# Navigate to directory
cd PhishStrike

# Install Python dependencies
pip install -r requirements.txt
```

> [!TIP]
> **Platform-specific install commands:**
> ```bash
> # Windows
> pip install -r requirements.txt
>
> # Linux / macOS
> pip3 install -r requirements.txt
>
> # Kali Linux / Debian (if you get an "externally-managed-environment" error)
> pip3 install -r requirements.txt --break-system-packages
>
> # Termux (Android)
> pip install -r requirements.txt
> ```

#### Step 3 — Launch

```bash
python phishstrike.py
```

> On Linux/macOS use `python3 phishstrike.py`

#### Docker Deployment
```bash
docker run --rm -ti farouqshaheen/phishstrike
```

---

### 📦 Python Dependencies

| Package | Purpose |
| :--- | :--- |
| `qrcode[pil]` | QR code generation for sharing phishing links |
| `Pillow` | Image processing (required by qrcode) |
| `Flask` | Web framework for the live intelligence dashboard |
| `Flask-SocketIO` | Real-time WebSocket updates in the dashboard |
| `google-generativeai` | Gemini AI API for the phishing assistant |
| `pandas` | Data handling and Excel export |
| `openpyxl` | Excel (.xlsx) file writing |
| `fpdf2` | PDF report generation |
| `requests` | HTTP requests for URL shortening and API calls |

---

### 🛠️ Tested Environments
| Operating System | Support | Status |
| :--- | :--- | :--- |
| **Ubuntu / Debian** | Full | ✅ Stable |
| **Kali Linux** | Full | ✅ Stable |
| **Arch / Manjaro** | Full | ✅ Stable |
| **Termux (Android)** | Full | ✅ Stable |
| **Windows (Native)** | Full | ✅ Stable |
| **Windows (WSL)** | Partial | ⚠️ Beta |

---

### ⚠️ Disclaimer
> [!CAUTION]
> **PhishStrike** is developed for **Educational and Ethical Testing** purposes only. Any unauthorized use of this tool for criminal activities is strictly prohibited. The developers, **Farouq Shaheen and Lujain Ghatasheh**, hold no responsibility for any misuse or damage caused by this toolkit. Use it responsibly and within the legal framework of your jurisdiction.

---

### 🤝 Connect & Support
<p align="left">
  <a href="https://www.linkedin.com/in/farouq-shaheen-667b24305/" target="_blank">
    <img src="https://img.shields.io/badge/Farouq%20Shaheen-LinkedIn-0077B5?style=for-the-badge&logo=linkedin">
  </a>
  <a href="https://www.linkedin.com/in/lujain-ghatasheh-7a25a5344/" target="_blank">
    <img src="https://img.shields.io/badge/Lujain%20Ghatasheh-LinkedIn-0077B5?style=for-the-badge&logo=linkedin">
  </a>
</p>

<p align="center">
  <i>Developed by <a href="https://github.com/farouqshaheen">Farouq Shaheen</a> & <a href="https://github.com/LujainGhatasheh">Lujain Ghatasheh</a></i>
</p>
