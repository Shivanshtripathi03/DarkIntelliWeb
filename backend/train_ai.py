import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Load dataset
with open("data/dataset.json", "r") as f:
    dataset = json.load(f)

texts = [entry["text"] for entry in dataset if entry["text"].strip() != ""]

print("Loaded texts:", len(texts))
for t in texts:
    print(t[:300], "...")  # show first 300 chars
