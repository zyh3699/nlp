"""
Classification with Self-Organizing Maps using MiniSom.

This MCP Server provides 1 tool:
1. minisom_train_som_classifier: Train SOM classifier and evaluate performance

All tools extracted from JustWhyKing/minisom/examples/Classification.ipynb.
"""

import os
from datetime import datetime
from pathlib import Path
# Standard imports
from typing import Annotated, Any

import numpy as np
import pandas as pd
from fastmcp import FastMCP
# MiniSom and sklearn imports
from minisom import MiniSom
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import scale

# Project structure
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DEFAULT_INPUT_DIR = PROJECT_ROOT / "tmp" / "inputs"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "tmp" / "outputs"

INPUT_DIR = Path(os.environ.get("CLASSIFICATION_INPUT_DIR", DEFAULT_INPUT_DIR))
OUTPUT_DIR = Path(os.environ.get("CLASSIFICATION_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Timestamp for unique outputs
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# MCP server instance
classification_mcp = FastMCP(name="classification")


def classify(som, data, X_train, y_train):
    """Classifies each sample in data in one of the classes defined
    using the method labels_map.
    Returns a list of the same length of data where the i-th element
    is the class assigned to data[i].
    """
    winmap = som.labels_map(X_train, y_train)
    default_class = np.sum(list(winmap.values())).most_common()[0][0]
    result = []
    for d in data:
        win_position = som.winner(d)
        if win_position in winmap:
            result.append(winmap[win_position].most_common()[0][0])
        else:
            result.append(default_class)
    return result


@classification_mcp.tool()
def minisom_train_som_classifier(
    data_path: Annotated[
        str | None,
        "Path to input data file with extension .csv or .txt. The file should contain numerical features and a target column with class labels",
    ] = None,
    target_column: Annotated[
        str, "Name of the column containing class labels"
    ] = "target",
    sep: Annotated[str, "Delimiter used in the file"] = "\t",
    som_x: Annotated[int, "Width of the SOM grid"] = 7,
    som_y: Annotated[int, "Height of the SOM grid"] = 7,
    sigma: Annotated[float, "Spread of the neighborhood function"] = 3.0,
    learning_rate: Annotated[float, "Initial learning rate"] = 0.5,
    neighborhood_function: Annotated[str, "Neighborhood function type"] = "triangle",
    random_seed: Annotated[int, "Random seed for reproducibility"] = 10,
    n_iterations: Annotated[int, "Number of training iterations"] = 500,
    test_size: Annotated[
        float, "Proportion of dataset to include in test split"
    ] = 0.25,
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Train a Self-Organizing Map classifier on labeled data and evaluate its performance.
    Input is tabular data with numerical features and class labels, and output is classification report and trained model metrics.
    """
    # Input validation
    if data_path is None:
        raise ValueError("Path to input data file must be provided")

    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Input file not found: {data_path}")

    # Determine output prefix
    if out_prefix is None:
        out_prefix = f"classification_{timestamp}"

    # Load data
    try:
        # Try reading with pandas to detect structure
        data_df = pd.read_csv(data_path, sep=sep, engine="python")
    except Exception as e:
        raise ValueError(f"Error loading data file: {e}")

    # Validate target column exists
    if target_column not in data_df.columns:
        raise ValueError(
            f"Target column '{target_column}' not found in data. Available columns: {list(data_df.columns)}"
        )

    # Extract labels and scale data
    labels = data_df[target_column].values
    data = scale(data_df.values)

    # Train-test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        data, labels, test_size=test_size, stratify=labels, random_state=random_seed
    )

    # Initialize SOM
    som = MiniSom(
        som_x,
        som_y,
        data.shape[1],
        sigma=sigma,
        learning_rate=learning_rate,
        neighborhood_function=neighborhood_function,
        random_seed=random_seed,
    )

    # Initialize weights with PCA
    som.pca_weights_init(X_train)

    # Train the SOM
    som.train_random(X_train, n_iterations, verbose=False)

    # Classify test data
    y_pred = classify(som, X_test, X_train, y_train)

    # Generate classification report
    report = classification_report(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)

    # Save classification report
    report_file = OUTPUT_DIR / f"{out_prefix}_classification_report.txt"
    with open(report_file, "w") as f:
        f.write(f"SOM Classification Report\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Model Parameters:\n")
        f.write(f"  SOM Grid Size: {som_x} x {som_y}\n")
        f.write(f"  Sigma: {sigma}\n")
        f.write(f"  Learning Rate: {learning_rate}\n")
        f.write(f"  Neighborhood Function: {neighborhood_function}\n")
        f.write(f"  Training Iterations: {n_iterations}\n")
        f.write(f"  Test Size: {test_size}\n\n")
        f.write(f"Overall Accuracy: {accuracy:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(report)

    # Save predictions
    predictions_df = pd.DataFrame({"true_label": y_test, "predicted_label": y_pred})
    predictions_file = OUTPUT_DIR / f"{out_prefix}_predictions.csv"
    predictions_df.to_csv(predictions_file, index=False)

    # Create confusion matrix data
    unique_labels = np.unique(labels)
    confusion_data = []
    for true_label in unique_labels:
        for pred_label in unique_labels:
            count = np.sum((y_test == true_label) & (np.array(y_pred) == pred_label))
            confusion_data.append(
                {
                    "true_label": true_label,
                    "predicted_label": pred_label,
                    "count": count,
                }
            )
    confusion_df = pd.DataFrame(confusion_data)
    confusion_file = OUTPUT_DIR / f"{out_prefix}_confusion_matrix.csv"
    confusion_df.to_csv(confusion_file, index=False)

    return {
        "message": f"SOM classifier trained successfully with accuracy: {accuracy:.4f}",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/Classification.ipynb",
        "artifacts": [
            {
                "description": "Classification report",
                "path": str(report_file.resolve()),
            },
            {
                "description": "Test predictions",
                "path": str(predictions_file.resolve()),
            },
            {"description": "Confusion matrix", "path": str(confusion_file.resolve())},
        ],
    }
