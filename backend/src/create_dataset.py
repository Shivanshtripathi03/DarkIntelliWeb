import os
import json

input_dir = "data/processed"
output_file = "data/dataset.json"

dataset = []

for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        filepath = os.path.join(input_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        dataset.append({"filename": filename, "text": text})

with open(output_file, "w", encoding="utf-8") as out:
    json.dump(dataset, out, ensure_ascii=False, indent=2)

print(f"Dataset saved to {output_file} with {len(dataset)} entries.")
