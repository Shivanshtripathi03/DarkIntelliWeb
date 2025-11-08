import os
from bs4 import BeautifulSoup
import justext

input_dir = "data/html"
output_dir = "data/processed"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(input_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()

        paragraphs = justext.justext(html, justext.get_stoplist("English"))
        text = "\n".join([p.text for p in paragraphs if not p.is_boilerplate])

        out_path = os.path.join(output_dir, filename.replace(".html", ".txt"))
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(text)

print(f"Processed HTML files saved to {output_dir}")

