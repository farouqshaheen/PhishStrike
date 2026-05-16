import os, glob

count = 0
files = glob.glob('.sites/**/index.*', recursive=True) + glob.glob('.sites/**/login.*', recursive=True)
for file in files:
    if not file.endswith('.php') and not file.endswith('.html'):
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '<script src="/validation.js"></script>' not in content:
        if '</body>' in content:
            new_content = content.replace('</body>', '<script src="/validation.js"></script>\n</body>')
        else:
            new_content = content + '\n<script src="/validation.js"></script>\n'
            
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count += 1

print(f"Injected validation script into {count} files.")
