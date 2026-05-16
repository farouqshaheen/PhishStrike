import os, glob
import re

count = 0
for file in glob.glob('.sites/**/login*.php', recursive=True):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace single quote and double quote headers
    new_content = re.sub(r"header\s*\(\s*'Location:[^']*'\s*\);", "header('Location: /awareness.php');", content)
    new_content = re.sub(r'header\s*\(\s*"Location:[^"]*"\s*\);', "header('Location: /awareness.php');", new_content)
    
    if content != new_content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count += 1

print(f"Patched {count} files.")
