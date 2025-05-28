#!/usr/bin/env python3
"""
embed_pca_visualization.py

Load prompts from .jsonl files in a directory, label them by filename (category),
compute embeddings using OpenAI, perform PCA to reduce to 2D,
and visualize the embeddings with a scatter plot colored by category.

Usage:
    python embed_pca_visualization.py --prompt_dir prompts/ --output_plot pca_plot.png

Requirements:
    pip install openai scikit-learn matplotlib tqdm python-dotenv
"""

import os
import glob
import argparse
import openai
import json
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, models


def load_prompts(prompt_dir):
    """
    Load prompts from all .jsonl files in prompt_dir.
    Each file name (without extension) is treated as a category.
    Returns a list of dicts with keys: 'prompt' and 'category'.
    """
    data = []
    original_data = list(map(json.loads, open('dataset/mbpp_sanitized_for_code_generation.jsonl')))
    original_id = [int(d['task_id'].split('/')[1]) for d in original_data]
    pattern = os.path.join(prompt_dir, "*.jsonl")
    for filepath in glob.glob(pattern):
        category = os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    prompt = json.loads(line.strip())
                    task_id = prompt['task_id'] + 1
                    if task_id not in original_id:
                        continue
                    data.append({"prompt": prompt['mutation'], "category": category})
                except Exception as e:
                    print(f"Error reading line in {filepath}: {e}")
    return data

#="text-embedding-3-small"
def get_embeddings_by_category(data, model):
    """
    Generate embeddings for prompts grouped by category, sequentially.
    Returns:
        - all_embeddings: List of embeddings
        - all_categories: Matching list of category names
    """
    all_embeddings = []
    all_categories = []
    grouped = {}
    for item in data:
        grouped.setdefault(item['category'], []).append(item['prompt'])

    for category, prompts in grouped.items():
        print(f"Generating embeddings for category: {category} ({len(prompts)} prompts)")
        for prompt in tqdm(prompts[1:2], desc=f"Embedding [{category}]"):
            try:
                # response = openai.embeddings.create(
                #     input=prompt,
                #     model=model
                # )
                # embedding = response.data[0].embedding
                embedding = model.encode(prompt)
                all_embeddings.append(embedding)
                all_categories.append(category)
            except Exception as e:
                print(f"Failed to embed prompt in category {category}: {e}")
    return all_embeddings, all_categories


def main():
    parser = argparse.ArgumentParser(description="PCA Visualization of Prompt Embeddings")
    parser.add_argument("--prompt_dir", required=True, help="Directory containing .jsonl files of prompts")
    parser.add_argument("--output_plot", default="pca_plot.png", help="File path to save the PCA scatter plot")
    parser.add_argument("--api_key", default=None, help="OpenAI API key (or set OPENAI_API_KEY env var)")
    args = parser.parse_args()

    print("Loading model (CodeBERT)...")
    # model = SentenceTransformer("microsoft/codebert-base")
    default_model = models.Transformer('microsoft/codebert-base')
    pooling_model = models.Pooling(default_model.get_word_embedding_dimension())
    model = SentenceTransformer(modules=[default_model, pooling_model])
    # model = "text-embedding-3-small"

    load_dotenv()
    openai.api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("No OpenAI API key provided. Use --api_key or set OPENAI_API_KEY in environment.")

    # Load prompts
    data = load_prompts(args.prompt_dir)
    if not data:
        print("No prompts loaded. Exiting.")
        return

    # Get embeddings
    embeddings, categories = get_embeddings_by_category(data, model)

    # PCA
    pca = PCA(n_components=2)
    emb_array = np.array(embeddings)
    coords = pca.fit_transform(emb_array)

    # Plot
    plt.figure(figsize=(10, 8))
    unique_cats = sorted(set(categories))
    cmap = plt.get_cmap('tab20')
    color_map = {cat: cmap(i % cmap.N) for i, cat in enumerate(unique_cats)}

    for cat in unique_cats:
        idxs = [i for i, c in enumerate(categories) if c == cat]
        plt.scatter(
            coords[idxs, 0], coords[idxs, 1],
            label=cat,
            color=color_map[cat],
            edgecolors='black',
            s=80,
            alpha=1.0
        )

    plt.title("PCA of Prompt Embeddings by Category")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.grid(True)
    plt.legend(title="Category", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(args.output_plot, dpi=300)
    print(f"Saved PCA scatter plot to {args.output_plot}")
    plt.show()


if __name__ == "__main__":
    main()
