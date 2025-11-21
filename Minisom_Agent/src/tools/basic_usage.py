"""
Basic Usage of MiniSom - Fundamental SOM operations and visualizations.

This MCP Server provides 5 tools:
1. minisom_train_som: Train SOM on normalized data with PCA initialization
2. minisom_visualize_distance_map: Create distance map with sample markers
3. minisom_visualize_scatter_map: Create scatter plot visualization on distance map
4. minisom_visualize_activation_frequencies: Show neuron activation frequency heatmap
5. minisom_visualize_class_distribution: Display pie charts showing class proportions per neuron
6. minisom_track_training_errors: Monitor quantization, topographic, and distortion errors during training

All tools extracted from `minisom/examples/BasicUsage.ipynb`.
"""

import os
from datetime import datetime
from pathlib import Path
# Standard imports
from typing import Annotated, Any, Literal

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastmcp import FastMCP
from minisom import MiniSom

# Project structure
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DEFAULT_INPUT_DIR = PROJECT_ROOT / "tmp" / "inputs"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "tmp" / "outputs"

INPUT_DIR = Path(os.environ.get("BASIC_USAGE_INPUT_DIR", DEFAULT_INPUT_DIR))
OUTPUT_DIR = Path(os.environ.get("BASIC_USAGE_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Timestamp for unique outputs
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# MCP server instance
basic_usage_mcp = FastMCP(name="basic_usage")


@basic_usage_mcp.tool()
def minisom_train_som(
    data_path: Annotated[
        str | None,
        "Path to input data file with extension .csv or .txt. The file should contain numerical features in columns (excluding target column if present).",
    ] = None,
    target_column: Annotated[
        str | None,
        "Name of the target/label column to exclude from training features. If None, all columns are used.",
    ] = None,
    n_neurons: Annotated[
        int, "Number of neurons in the first dimension of the SOM grid"
    ] = 9,
    m_neurons: Annotated[
        int, "Number of neurons in the second dimension of the SOM grid"
    ] = 9,
    sigma: Annotated[float, "Spread of the neighborhood function"] = 1.5,
    learning_rate: Annotated[float, "Initial learning rate"] = 0.5,
    neighborhood_function: Annotated[
        Literal["gaussian", "mexican_hat", "bubble", "triangle"],
        "Neighborhood function type",
    ] = "gaussian",
    random_seed: Annotated[int, "Random seed for reproducibility"] = 0,
    topology: Annotated[
        Literal["rectangular", "hexagonal"], "Topology of the map"
    ] = "rectangular",
    n_iterations: Annotated[int, "Number of training iterations"] = 1000,
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Train a Self-Organizing Map on normalized data with PCA weight initialization.
    Input is tabular data file with numerical features and output is trained SOM model saved as pickle file.
    """
    # Input file validation
    if data_path is None:
        raise ValueError("Path to input data file must be provided")

    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Input file not found: {data_path}")

    # Load data based on file extension
    if data_path.endswith(".csv"):
        data_df = pd.read_csv(data_path)
    elif data_path.endswith(".txt"):
        # Try tab-separated format first
        try:
            data_df = pd.read_csv(data_path, sep="\t+", engine="python")
        except:
            data_df = pd.read_csv(data_path, delim_whitespace=True)
    else:
        raise ValueError(
            f"Unsupported file format. Expected .csv or .txt, got: {data_path}"
        )

    # Extract target if specified
    target = None
    if target_column and target_column in data_df.columns:
        target = data_df[target_column].values
        data_df = data_df.drop(columns=[target_column])

    # Data normalization (z-score)
    data_normalized = (data_df - np.mean(data_df, axis=0)) / np.std(data_df, axis=0)
    data = data_normalized.values

    # Initialize SOM
    som = MiniSom(
        n_neurons,
        m_neurons,
        data.shape[1],
        sigma=sigma,
        learning_rate=learning_rate,
        neighborhood_function=neighborhood_function,
        random_seed=random_seed,
        topology=topology,
    )

    # PCA weights initialization
    som.pca_weights_init(data)

    # Train the SOM
    som.train(data, n_iterations, verbose=False)

    # Save the trained model and data
    if out_prefix is None:
        out_prefix = f"som_trained_{timestamp}"

    model_path = OUTPUT_DIR / f"{out_prefix}.pkl"
    data_path_out = OUTPUT_DIR / f"{out_prefix}_data.npy"
    target_path_out = OUTPUT_DIR / f"{out_prefix}_target.npy"

    import pickle

    with open(model_path, "wb") as f:
        pickle.dump(som, f)

    np.save(data_path_out, data)
    if target is not None:
        np.save(target_path_out, target)

    artifacts = [
        {
            "description": "Trained SOM model (pickle file)",
            "path": str(model_path.resolve()),
        },
        {
            "description": "Normalized training data",
            "path": str(data_path_out.resolve()),
        },
    ]

    if target is not None:
        artifacts.append(
            {"description": "Target labels", "path": str(target_path_out.resolve())}
        )

    return {
        "message": f"SOM training completed: {n_neurons}x{m_neurons} grid, {n_iterations} iterations",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/BasicUsage.ipynb",
        "artifacts": artifacts,
    }


@basic_usage_mcp.tool()
def minisom_visualize_distance_map(
    model_path: Annotated[str | None, "Path to trained SOM model pickle file"] = None,
    data_path: Annotated[
        str | None, "Path to normalized data numpy file (.npy)"
    ] = None,
    target_path: Annotated[
        str | None,
        "Path to target labels numpy file (.npy). If None, no markers are plotted.",
    ] = None,
    label_names: Annotated[
        dict | None,
        "Dictionary mapping target values to label names (e.g., {1:'Kama', 2:'Rosa', 3:'Canadian'})",
    ] = None,
    figsize: Annotated[tuple, "Figure size as (width, height)"] = (9, 9),
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Create distance map (U-Matrix) visualization with sample markers overlaid.
    Input is trained SOM model and data files, output is distance map figure showing neuron distances and sample positions.
    """
    # Input validation
    if model_path is None:
        raise ValueError("Path to trained SOM model must be provided")
    if data_path is None:
        raise ValueError("Path to normalized data file must be provided")

    model_file = Path(model_path)
    data_file = Path(data_path)

    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    # Load model and data
    import pickle

    with open(model_path, "rb") as f:
        som = pickle.load(f)

    data = np.load(data_path)

    target = None
    if target_path:
        target_file = Path(target_path)
        if target_file.exists():
            target = np.load(target_path)

    # Create figure
    plt.figure(figsize=figsize, dpi=300)

    # Plot distance map as background
    plt.pcolor(som.distance_map().T, cmap="bone_r")
    plt.colorbar()

    # Plot markers if target is provided
    if target is not None:
        markers = ["o", "s", "D"]
        colors = ["C0", "C1", "C2"]

        for cnt, xx in enumerate(data):
            w = som.winner(xx)
            plt.plot(
                w[0] + 0.5,
                w[1] + 0.5,
                markers[target[cnt] - 1],
                markerfacecolor="None",
                markeredgecolor=colors[target[cnt] - 1],
                markersize=12,
                markeredgewidth=2,
            )

    # Save figure
    if out_prefix is None:
        out_prefix = f"distance_map_{timestamp}"

    output_path = OUTPUT_DIR / f"{out_prefix}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "message": "Distance map visualization created successfully",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/BasicUsage.ipynb",
        "artifacts": [
            {
                "description": "Distance map with sample markers",
                "path": str(output_path.resolve()),
            }
        ],
    }


@basic_usage_mcp.tool()
def minisom_visualize_scatter_map(
    model_path: Annotated[str | None, "Path to trained SOM model pickle file"] = None,
    data_path: Annotated[
        str | None, "Path to normalized data numpy file (.npy)"
    ] = None,
    target_path: Annotated[
        str | None, "Path to target labels numpy file (.npy)"
    ] = None,
    label_names: Annotated[
        dict | None,
        "Dictionary mapping target values to label names (e.g., {1:'Kama', 2:'Rosa', 3:'Canadian'})",
    ] = None,
    figsize: Annotated[tuple, "Figure size as (width, height)"] = (10, 9),
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Create scatter plot showing sample distribution across the SOM with random offset to avoid overlaps.
    Input is trained SOM model and data files, output is scatter plot on distance map background with legend.
    """
    # Input validation
    if model_path is None:
        raise ValueError("Path to trained SOM model must be provided")
    if data_path is None:
        raise ValueError("Path to normalized data file must be provided")
    if target_path is None:
        raise ValueError("Path to target labels file must be provided")

    model_file = Path(model_path)
    data_file = Path(data_path)
    target_file = Path(target_path)

    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    if not target_file.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")

    # Load model and data
    import pickle

    with open(model_path, "rb") as f:
        som = pickle.load(f)

    data = np.load(data_path)
    target = np.load(target_path)

    # Default label names if not provided
    if label_names is None:
        label_names = {i: f"Class {i}" for i in np.unique(target)}

    # Get winner coordinates for all samples
    w_x, w_y = zip(*[som.winner(d) for d in data])
    w_x = np.array(w_x)
    w_y = np.array(w_y)

    # Create figure
    plt.figure(figsize=figsize, dpi=300)
    plt.pcolor(som.distance_map().T, cmap="bone_r", alpha=0.2)
    plt.colorbar()

    # Plot scatter for each class
    colors = ["C0", "C1", "C2"]
    for c in np.unique(target):
        idx_target = target == c
        plt.scatter(
            w_x[idx_target] + 0.5 + (np.random.rand(np.sum(idx_target)) - 0.5) * 0.8,
            w_y[idx_target] + 0.5 + (np.random.rand(np.sum(idx_target)) - 0.5) * 0.8,
            s=50,
            c=colors[c - 1],
            label=label_names[c],
        )

    plt.legend(loc="upper right")
    plt.grid()

    # Save figure
    if out_prefix is None:
        out_prefix = f"scatter_map_{timestamp}"

    output_path = OUTPUT_DIR / f"{out_prefix}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "message": "Scatter plot visualization created successfully",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/BasicUsage.ipynb",
        "artifacts": [
            {
                "description": "Scatter plot on distance map",
                "path": str(output_path.resolve()),
            }
        ],
    }


@basic_usage_mcp.tool()
def minisom_visualize_activation_frequencies(
    model_path: Annotated[str | None, "Path to trained SOM model pickle file"] = None,
    data_path: Annotated[
        str | None, "Path to normalized data numpy file (.npy)"
    ] = None,
    figsize: Annotated[tuple, "Figure size as (width, height)"] = (7, 7),
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Create heatmap showing activation frequency for each neuron in the SOM.
    Input is trained SOM model and data files, output is frequency heatmap showing which neurons are activated most often.
    """
    # Input validation
    if model_path is None:
        raise ValueError("Path to trained SOM model must be provided")
    if data_path is None:
        raise ValueError("Path to normalized data file must be provided")

    model_file = Path(model_path)
    data_file = Path(data_path)

    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    # Load model and data
    import pickle

    with open(model_path, "rb") as f:
        som = pickle.load(f)

    data = np.load(data_path)

    # Create figure
    plt.figure(figsize=figsize, dpi=300)
    frequencies = som.activation_response(data)
    plt.pcolor(frequencies.T, cmap="Blues")
    plt.colorbar()

    # Save figure
    if out_prefix is None:
        out_prefix = f"activation_frequencies_{timestamp}"

    output_path = OUTPUT_DIR / f"{out_prefix}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "message": "Activation frequency visualization created successfully",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/BasicUsage.ipynb",
        "artifacts": [
            {
                "description": "Activation frequency heatmap",
                "path": str(output_path.resolve()),
            }
        ],
    }


@basic_usage_mcp.tool()
def minisom_visualize_class_distribution(
    model_path: Annotated[str | None, "Path to trained SOM model pickle file"] = None,
    data_path: Annotated[
        str | None, "Path to normalized data numpy file (.npy)"
    ] = None,
    target_path: Annotated[
        str | None, "Path to target labels numpy file (.npy)"
    ] = None,
    label_names: Annotated[
        dict | None,
        "Dictionary mapping target values to label names (e.g., {1:'Kama', 2:'Rosa', 3:'Canadian'})",
    ] = None,
    n_neurons: Annotated[
        int, "Number of neurons in the first dimension (must match trained model)"
    ] = 9,
    m_neurons: Annotated[
        int, "Number of neurons in the second dimension (must match trained model)"
    ] = 9,
    figsize: Annotated[tuple, "Figure size as (width, height)"] = (9, 9),
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Create grid of pie charts showing class proportion distribution per neuron.
    Input is trained SOM model with labeled data, output is visualization with pie chart for each neuron showing class proportions.
    """
    # Input validation
    if model_path is None:
        raise ValueError("Path to trained SOM model must be provided")
    if data_path is None:
        raise ValueError("Path to normalized data file must be provided")
    if target_path is None:
        raise ValueError("Path to target labels file must be provided")

    model_file = Path(model_path)
    data_file = Path(data_path)
    target_file = Path(target_path)

    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    if not target_file.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")

    # Load model and data
    import pickle

    with open(model_path, "rb") as f:
        som = pickle.load(f)

    data = np.load(data_path)
    target = np.load(target_path)

    # Default label names if not provided
    if label_names is None:
        label_names = {i: f"Class {i}" for i in np.unique(target)}

    # Create labels map
    labels_map = som.labels_map(data, [label_names[t] for t in target])

    # Create figure with grid
    fig = plt.figure(figsize=figsize, dpi=300)
    the_grid = gridspec.GridSpec(n_neurons, m_neurons, fig)

    for position in labels_map.keys():
        label_fracs = [labels_map[position][l] for l in label_names.values()]
        plt.subplot(the_grid[n_neurons - 1 - position[1], position[0]], aspect=1)
        patches, texts = plt.pie(label_fracs)

    plt.legend(patches, label_names.values(), bbox_to_anchor=(3.5, 6.5), ncol=3)

    # Save figure
    if out_prefix is None:
        out_prefix = f"class_distribution_{timestamp}"

    output_path = OUTPUT_DIR / f"{out_prefix}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "message": "Class distribution pie chart visualization created successfully",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/BasicUsage.ipynb",
        "artifacts": [
            {
                "description": "Pie chart grid showing class distribution",
                "path": str(output_path.resolve()),
            }
        ],
    }


@basic_usage_mcp.tool()
def minisom_track_training_errors(
    data_path: Annotated[
        str | None,
        "Path to input data file with extension .csv or .txt. The file should contain numerical features in columns (excluding target column if present).",
    ] = None,
    target_column: Annotated[
        str | None,
        "Name of the target/label column to exclude from training features. If None, all columns are used.",
    ] = None,
    n_neurons: Annotated[
        int, "Number of neurons in the first dimension of the SOM grid"
    ] = 10,
    m_neurons: Annotated[
        int, "Number of neurons in the second dimension of the SOM grid"
    ] = 10,
    sigma: Annotated[float, "Spread of the neighborhood function"] = 1.5,
    learning_rate: Annotated[float, "Initial learning rate"] = 0.5,
    neighborhood_function: Annotated[
        Literal["gaussian", "mexican_hat", "bubble", "triangle"],
        "Neighborhood function type",
    ] = "gaussian",
    random_seed: Annotated[int, "Random seed for reproducibility"] = 10,
    max_iter: Annotated[int, "Maximum number of training iterations"] = 200,
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Train SOM while tracking quantization error, topographic error, and distortion measure at each iteration.
    Input is tabular data file and output is error tracking plots and CSV file with error metrics showing convergence.
    """
    # Input file validation
    if data_path is None:
        raise ValueError("Path to input data file must be provided")

    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Input file not found: {data_path}")

    # Load data based on file extension
    if data_path.endswith(".csv"):
        data_df = pd.read_csv(data_path)
    elif data_path.endswith(".txt"):
        # Try tab-separated format first
        try:
            data_df = pd.read_csv(data_path, sep="\t+", engine="python")
        except:
            data_df = pd.read_csv(data_path, delim_whitespace=True)
    else:
        raise ValueError(
            f"Unsupported file format. Expected .csv or .txt, got: {data_path}"
        )

    # Extract target if specified
    if target_column and target_column in data_df.columns:
        data_df = data_df.drop(columns=[target_column])

    # Data normalization (z-score)
    data_normalized = (data_df - np.mean(data_df, axis=0)) / np.std(data_df, axis=0)
    data = data_normalized.values

    # Initialize SOM
    som = MiniSom(
        n_neurons,
        m_neurons,
        data.shape[1],
        sigma=sigma,
        learning_rate=learning_rate,
        neighborhood_function=neighborhood_function,
        random_seed=random_seed,
    )

    # Training with error tracking
    q_error = []
    t_error = []
    d_error = []

    for i in range(max_iter):
        rand_i = np.random.randint(len(data))
        som.update(data[rand_i], som.winner(data[rand_i]), i, max_iter)
        q_error.append(som.quantization_error(data))
        t_error.append(som.topographic_error(data))
        d_error.append(som.distortion_measure(data))

    # Create error tracking plot
    fig = plt.figure(figsize=(10, 8), dpi=300)

    plt.subplot(3, 1, 1)
    plt.plot(np.arange(max_iter), q_error)
    plt.ylabel("quantization error")

    plt.subplot(3, 1, 2)
    plt.plot(np.arange(max_iter), t_error)
    plt.ylabel("topographic error")

    plt.subplot(3, 1, 3)
    plt.plot(np.arange(max_iter), d_error)
    plt.ylabel("divergence measure")
    plt.xlabel("iteration index")

    plt.tight_layout()

    # Save figure
    if out_prefix is None:
        out_prefix = f"training_errors_{timestamp}"

    plot_path = OUTPUT_DIR / f"{out_prefix}.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()

    # Save error data to CSV
    error_df = pd.DataFrame(
        {
            "iteration": np.arange(max_iter),
            "quantization_error": q_error,
            "topographic_error": t_error,
            "distortion_measure": d_error,
        }
    )

    csv_path = OUTPUT_DIR / f"{out_prefix}.csv"
    error_df.to_csv(csv_path, index=False)

    return {
        "message": f"Training error tracking completed for {max_iter} iterations",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/BasicUsage.ipynb",
        "artifacts": [
            {"description": "Error tracking plots", "path": str(plot_path.resolve())},
            {"description": "Error metrics CSV file", "path": str(csv_path.resolve())},
        ],
    }


if __name__ == "__main__":
    basic_usage_mcp.run()
