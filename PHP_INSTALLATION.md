# PHP Installation Guide for PhishStrike

## Why PHP is Required

PhishStrike requires PHP to run the local phishing server. The phishing templates are PHP-based and need a PHP interpreter to function correctly.

## Windows Installation

### Option 1: Download from PHP.net (Recommended)

1. **Download PHP**
   - Visit: https://windows.php.net/download/
   - Download the latest stable version (x64 Thread Safe)
   - Choose the ZIP archive (not the installer)

2. **Extract PHP**
   - Extract the ZIP file to: `C:\php`
   - Ensure the folder structure looks like: `C:\php\php.exe`

3. **Add to PATH**
   - Press `Win + X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\php`
   - Click "OK" on all dialogs

4. **Configure php.ini**
   - Navigate to `C:\php`
   - Rename `php.ini-development` to `php.ini`
   - Open `php.ini` in a text editor
   - Find and uncomment (remove `;`) these lines:
     ```
     extension_dir = "ext"
     extension=curl
     extension=openssl
     extension=mbstring
     ```
   - Save the file

5. **Verify Installation**
   - Open a new Command Prompt or PowerShell
   - Run: `php --version`
   - You should see PHP version information

### Option 2: Using XAMPP (Alternative)

1. Download XAMPP from: https://www.apachefriends.org/
2. Install XAMPP with default settings
3. Add XAMPP's PHP to PATH:
   - Add `C:\xampp\php` to your system PATH
4. Verify with: `php --version`

## After Installation

Once PHP is installed, you can run PhishStrike:

```bash
python phishstrike.py
```

## Troubleshooting

### "php is not recognized"
- Make sure you added PHP to PATH
- Restart your terminal/IDE after adding to PATH
- Try the full path: `C:\php\php.exe --version`

### Extension errors
- Make sure you uncommented the required extensions in php.ini
- Ensure the `ext` folder exists in your PHP directory

### Still having issues?
- Check that you downloaded the "Thread Safe" version
- Verify your PHP version is 7.4 or higher
