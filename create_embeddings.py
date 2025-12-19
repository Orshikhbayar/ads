#!/usr/bin/env python3
"""
Create pre-computed embeddings for all documents in docs.jsonl
Output: Data/embeddings.npz (numpy compressed format)
"""
import json
import numpy as np
import os
import sys
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.embedding import get_embeddings_batch

def main():
    docs_path = "Data/docs.jsonl"
    output_path = "Data/embeddings.npz"
    
    # Load documents
    print(f"Loading documents from {docs_path}...")
    docs = []
    with open(docs_path, "r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    
    print(f"Loaded {len(docs)} documents")
    
    # Prepare texts for embedding
    texts = []
    for doc in docs:
        # Combine keyword and text for better embedding
        text = f"{doc.get('keyword', '')} {doc.get('text', '')}"
        texts.append(text)
    
    # Get embeddings in batches
    print("Computing embeddings (this may take a few minutes)...")
    embeddings = get_embeddings_batch(texts, batch_size=64)
    
    print(f"Embeddings shape: {embeddings.shape}")
    
    # Save to npz file
    print(f"Saving to {output_path}...")
    np.savez_compressed(output_path, embeddings=embeddings)
    
    # Also save keywords for reference
    keywords = [doc.get('keyword', '') for doc in docs]
    with open("Data/keywords.json", "w", encoding="utf-8") as f:
        json.dump(keywords, f, ensure_ascii=False)
    
    print("Done!")

if __name__ == "__main__":
    main()
