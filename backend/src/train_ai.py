import json
import torch
from transformers import AutoTokenizer, AutoModel
import os

# Load dataset
with open("data/dataset.json", "r") as f:
    data = json.load(f)

texts = [item["text"] for item in data if item["text"].strip() != ""]

print(f"Loaded texts: {len(texts)}")
for t in texts:
    print(t[:200], "...")  # preview first 200 chars

# Load tokenizer and model from local folder
tokenizer = AutoTokenizer.from_pretrained("models/bert-base-uncased")
model = AutoModel.from_pretrained("models/bert-base-uncased")

# Tokenize the dataset
tokenized_texts = tokenizer(
    texts,
    padding=True,
    truncation=True,
    max_length=256,
    return_tensors="pt"
)

print("Tokenized input IDs shape:", tokenized_texts["input_ids"].shape)

# Forward pass through the model to get embeddings
with torch.no_grad():
    outputs = model(**tokenized_texts)
    embeddings = outputs.last_hidden_state.mean(dim=1)  # mean pooling

print("Embeddings shape:", embeddings.shape)

# Save embeddings
os.makedirs("data/embeddings", exist_ok=True)
torch.save(embeddings, "data/embeddings/text_embeddings.pt")
print("Embeddings saved to data/embeddings/text_embeddings.pt")

