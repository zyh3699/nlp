"""
Clustering with Self-Organizing Maps using MiniSom.

This MCP Server provides 1 tool:
1. minisom_cluster_data: Cluster data using SOM and visualize results

All tools extracted from JustWhyKing/minisom/examples/Clustering.ipynb.
"""

import os
from datetime import datetime
from pathlib import Path
# Standard imports
from typing import Annotated, Any, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastmcp import FastMCP
# MiniSom import
from minisom import MiniSom

# Project structure
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DEFAULT_INPUT_DIR = PROJECT_ROOT / "tmp" / "inputs"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "tmp" / "outputs"

INPUT_DIR = Path(os.environ.get("CLUSTERING_INPUT_DIR", DEFAULT_INPUT_DIR))
OUTPUT_DIR = Path(os.environ.get("CLUSTERING_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Timestamp for unique outputs
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# MCP server instance
clustering_mcp = FastMCP(name="clustering")


@clustering_mcp.tool()
def minisom_cluster_data(
    data_path: Annotated[
        str | None,
        "Path to input CSV file. Must contain numeric features for clustering.",
    ] = None,
    som_shape: Annotated[
        tuple[int, int], "SOM grid shape as (rows, cols). Tutorial default: (1, 3)"
    ] = (1, 3),
    sigma: Annotated[
        float, "Spread of the neighborhood function. Tutorial default: 0.5"
    ] = 0.5,
    learning_rate: Annotated[
        float, "Initial learning rate. Tutorial default: 0.5"
    ] = 0.5,
    neighborhood_function: Annotated[
        Literal["gaussian", "mexican_hat", "bubble", "triangle"],
        "Neighborhood function type. Tutorial default: gaussian",
    ] = "gaussian",
    random_seed: Annotated[
        int, "Random seed for reproducibility. Tutorial default: 10"
    ] = 10,
    num_iterations: Annotated[
        int, "Number of training iterations. Tutorial default: 500"
    ] = 500,
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Cluster data using Self-Organizing Map (SOM) with MiniSom library.
    Input is CSV file with numeric features and output is cluster assignments table and visualization plot.
    """
    # Input validation
    if data_path is None:
        raise ValueError("Path to input data file must be provided")

    # File existence validation
    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Input file not found: {data_path}")

    # Load data
    data = pd.read_csv(data_path)

    # Validate data is numeric
    if not data.select_dtypes(include=[np.number]).shape[1] > 0:
        raise ValueError("Input data must contain at least one numeric column")

    # Extract numeric columns only
    data = data.select_dtypes(include=[np.number]).values

    # Data normalization (mean=0, std=1)
    data_normalized = (data - np.mean(data, axis=0)) / np.std(data, axis=0)

    # Initialization and training
    som = MiniSom(
        som_shape[0],
        som_shape[1],
        data_normalized.shape[1],
        sigma=sigma,
        learning_rate=learning_rate,
        neighborhood_function=neighborhood_function,
        random_seed=random_seed,
    )

    som.train_batch(data_normalized, num_iterations, verbose=True)

    # Cluster assignment
    # Each neuron represents a cluster
    winner_coordinates = np.array([som.winner(x) for x in data_normalized]).T
    # Convert bidimensional coordinates to monodimensional index
    cluster_index = np.ravel_multi_index(winner_coordinates, som_shape)

    # Prepare output paths
    if out_prefix is None:
        out_prefix = f"clustering_{timestamp}"

    output_csv = OUTPUT_DIR / f"{out_prefix}_clusters.csv"
    output_plot = OUTPUT_DIR / f"{out_prefix}_cluster_visualization.png"

    # Save cluster assignments
    cluster_df = pd.DataFrame({"cluster_index": cluster_index})
    cluster_df.to_csv(output_csv, index=False)

    # Visualization - using first 2 dimensions of the data
    plt.figure(figsize=(10, 8), dpi=300)

    # Plot each cluster with a different color
    for c in np.unique(cluster_index):
        plt.scatter(
            data_normalized[cluster_index == c, 0],
            data_normalized[cluster_index == c, 1],
            label="cluster=" + str(c),
            alpha=0.7,
        )

    # Plot centroids (SOM weights)
    for centroid in som.get_weights():
        plt.scatter(
            centroid[:, 0],
            centroid[:, 1],
            marker="x",
            s=80,
            linewidths=35,
            color="k",
            label="centroid",
        )

    plt.xlabel("Feature 1 (normalized)")
    plt.ylabel("Feature 2 (normalized)")
    plt.title("SOM Clustering Results")
    plt.legend()
    plt.savefig(output_plot, dpi=300, bbox_inches="tight")
    plt.close()

    # Calculate number of clusters
    num_clusters = som_shape[0] * som_shape[1]

    return {
        "message": f"SOM clustering completed with {num_clusters} clusters from {len(data_normalized)} samples",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/Clustering.ipynb",
        "artifacts": [
            {
                "description": "Cluster assignments table",
                "path": str(output_csv.resolve()),
            },
            {
                "description": "Cluster visualization plot",
                "path": str(output_plot.resolve()),
            },
        ],
    }


if __name__ == "__main__":
    clustering_mcp.run()
