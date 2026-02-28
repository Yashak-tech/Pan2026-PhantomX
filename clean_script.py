file_path = "process_document.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    if line.strip().startswith("!") or line.strip().startswith("%"):
        continue
    clean_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)

print("Cleaned up jupyter commands from process_document.py")
