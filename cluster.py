import os
import glob
import argparse
import json
import openai
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, models

# Optional: try importing hdbscan if requested
try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False


def load_prompts(prompt_dir):
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


def get_embeddings_by_category(data, model):
    all_embeddings = []
    all_categories = []
    grouped = {}
    for item in data:
        grouped.setdefault(item['category'], []).append(item['prompt'])

    for category, prompts in grouped.items():
        print(f"Generating embeddings for category: {category} ({len(prompts)} prompts)")
        for prompt in tqdm(prompts[2:3], desc=f"Embedding [{category}]"):
            try:
                response = openai.embeddings.create(
                    input=prompt,
                    model=model
                )
                embedding = response.data[0].embedding
                # embedding = model.encode(prompt)
                all_embeddings.append(embedding)
                all_categories.append(category)
            except Exception as e:
                print(f"Failed to embed prompt in category {category}: {e}")
    return all_embeddings, all_categories


def main():
    parser = argparse.ArgumentParser(description="PCA and Clustering of Prompt Embeddings")
    parser.add_argument("--prompt_dir", required=True, help="Directory containing .jsonl files of prompts")
    parser.add_argument("--output_plot", default="pca_plot.png", help="File path to save the PCA scatter plot")
    parser.add_argument("--cluster_method", default="dbscan", choices=["dbscan", "kmeans", "hdbscan"],
                        help="Clustering method: dbscan, kmeans, or hdbscan")
    parser.add_argument("--kmeans_k", type=int, default=5, help="Number of clusters for KMeans")
    args = parser.parse_args()

    print("Loading model (CodeBERT)...")
    default_model = models.Transformer('microsoft/codebert-base')
    pooling_model = models.Pooling(default_model.get_word_embedding_dimension())
    model = SentenceTransformer(modules=[default_model, pooling_model])
    model = "text-embedding-3-small"

    load_dotenv()

    data = load_prompts(args.prompt_dir)
    if not data:
        print("No prompts loaded. Exiting.")
        return

    embeddings, categories = get_embeddings_by_category(data, model)
    emb_array = np.array(embeddings)

    # Choose clustering algorithm
    if args.cluster_method == "dbscan":
        print("Clustering with DBSCAN...")
        cluster_model = DBSCAN(eps=0.5, min_samples=1).fit(emb_array)
    elif args.cluster_method == "kmeans":
        print(f"Clustering with KMeans (k={args.kmeans_k})...")
        cluster_model = KMeans(n_clusters=args.kmeans_k, random_state=42).fit(emb_array)
    elif args.cluster_method == "hdbscan":
        if not HDBSCAN_AVAILABLE:
            print("Error: hdbscan not installed. Please run 'pip install hdbscan'")
            return
        print("Clustering with HDBSCAN...")
        cluster_model = hdbscan.HDBSCAN(min_cluster_size=2, min_samples=1).fit(emb_array)
    else:
        raise ValueError("Unsupported clustering method.")

    labels = cluster_model.labels_
    unique_labels = set(labels)
    print(f"Found {len(unique_labels) - (1 if -1 in unique_labels else 0)} clusters.")

    representatives = []
    for label in unique_labels:
        if label == -1:
            continue
        idxs = np.where(labels == label)[0]
        cluster_embs = emb_array[idxs]
        centroid = cluster_embs.mean(axis=0)
        closest_idx, _ = pairwise_distances_argmin_min([centroid], cluster_embs)
        selected_idx = idxs[closest_idx[0]]
        representatives.append((selected_idx, categories[selected_idx]))

    print("\n=== Selected Representative Points per Cluster ===")
    for idx, cat in representatives:
        cluster_label = labels[idx]
        prompt = data[idx]['prompt']
        print("------------")
        print(f"Cluster: {cluster_label}")
        print(f"Category (Sentence Tone): {cat}")
        print(f"Prompt: {prompt}")

    # PCA for visualization
    pca = PCA(n_components=2)
    coords = pca.fit_transform(emb_array)

    plt.figure(figsize=(10, 8))
    cmap = plt.get_cmap('tab20')
    color_map = {label: cmap(i % cmap.N) for i, label in enumerate(unique_labels)}

    for label in unique_labels:
        idxs = np.where(labels == label)[0]
        color = 'gray' if label == -1 else color_map[label]
        label_name = 'Noise' if label == -1 else f'Cluster {label}'

        plt.scatter(
            coords[idxs, 0], coords[idxs, 1],
            label=label_name,
            color=color,
            edgecolors='black',
            s=200,
            alpha=0.8,
            linewidths=1
        )

    for idx, _ in representatives:
        plt.scatter(
            coords[idx, 0], coords[idx, 1],
            color='red',
            edgecolors='black',
            s=400,
            marker='*',
            linewidths=1.5,
            label='Selected'
        )

    plt.title(f"PCA of Prompt Embeddings ({args.cluster_method.upper()})")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.grid(True)
    plt.legend(title="Clusters", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(args.output_plot, dpi=300)
    print(f"Saved PCA plot with clustering to {args.output_plot}")
    plt.show()


if __name__ == "__main__":
    main()
