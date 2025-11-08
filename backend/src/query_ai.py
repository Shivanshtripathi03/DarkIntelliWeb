import torch
from transformers import AutoTokenizer, AutoModel
import json

# Load dataset
with open("data/dataset.json", "r") as f:
    dataset = json.load(f)

# Load embeddings
embeddings = torch.load("data/embeddings/text_embeddings.pt")

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("models/bert-base-uncased")
model = AutoModel.from_pretrained("models/bert-base-uncased")

def query(text, top_k=1):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        query_emb = model(**inputs).last_hidden_state[:,0,:]  # CLS token
    # Compute cosine similarity
    sims = torch.nn.functional.cosine_similarity(query_emb, embeddings)
    top_indices = sims.topk(top_k).indices.tolist()
    results = [dataset[i]["text"] for i in top_indices]
    return results

if __name__ == "__main__":
    question = input("Enter your query: ")
    answers = query(question)
    for ans in answers:
        print("\nAnswer:\n", ans)
