import json

file_path = "Full_source_code.ipynb"
with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

script_content = ""
for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = "".join(cell.get('source', []))
        if "!pip" in source or "!apt" in source:
            continue
        script_content += source + "\n\n"

with open("process_document.py", 'w', encoding='utf-8') as f:
    f.write(script_content)

print("Created process_document.py")
