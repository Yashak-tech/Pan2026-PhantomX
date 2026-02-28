import json

file_path = "Full_source_code.ipynb"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"/content/{PDF_NAME}"', '"./{PDF_NAME}"')
text = text.replace('"/content/Autonomous"', '"./Autonomous"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated remaining colab paths.")
