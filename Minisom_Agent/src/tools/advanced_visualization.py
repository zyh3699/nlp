"""
Advanced Visualization Techniques for Self-Organizing Maps (SOM).

This MCP Server provides 4 tools for advanced SOM visualization:
1. minisom_create_quality_plot: Quality assessment visualization using mean differences
2. minisom_create_property_plot: Feature correlation analysis across neurons
3. minisom_create_distribution_map: Polar plots showing min/mean/max distributions
4. minisom_create_starburst_map: Gradient visualization for similarity patterns

All tools extracted from `minisom/examples/AdvancedVisualization.ipynb`.
"""

import math
import os
import pickle
from datetime import datetime
from pathlib import Path
# Standard imports
from typing import Annotated, Any, Literal

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# Plotly imports
import plotly.graph_objects as go
from fastmcp import FastMCP
from matplotlib import cm
# MiniSom import
from minisom import MiniSom
from plotly.subplots import make_subplots

# Project structure
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DEFAULT_INPUT_DIR = PROJECT_ROOT / "tmp" / "inputs"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "tmp" / "outputs"

INPUT_DIR = Path(os.environ.get("ADVANCED_VISUALIZATION_INPUT_DIR", DEFAULT_INPUT_DIR))
OUTPUT_DIR = Path(
    os.environ.get("ADVANCED_VISUALIZATION_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
)

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Timestamp for unique outputs
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# MCP server instance
advanced_visualization_mcp = FastMCP(name="advanced_visualization")


@advanced_visualization_mcp.tool()
def minisom_create_quality_plot(
    som_path: Annotated[str | None, "Path to trained SOM object (pickle file)"] = None,
    data_path: Annotated[
        str | None, "Path to training data file with extension .csv"
    ] = None,
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Create quality plot visualization showing mean differences between samples and neuron weights.
    Input is trained SOM model and training data, output is quality heatmap showing clustering quality per neuron.
    """
    # Input validation
    if som_path is None:
        raise ValueError("Path to trained SOM object must be provided")
    if data_path is None:
        raise ValueError("Path to training data file must be provided")

    # File existence validation
    som_file = Path(som_path)
    if not som_file.exists():
        raise FileNotFoundError(f"SOM file not found: {som_path}")

    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    # Load SOM and data
    with open(som_path, "rb") as f:
        som = pickle.load(f)

    data = pd.read_csv(data_path).values

    # Create quality plot - exact tutorial implementation
    win_map = som.win_map(data)
    size = som.distance_map().shape[0]
    qualities = np.empty((size, size))
    qualities[:] = np.NaN
    for position, values in win_map.items():
        qualities[position[0], position[1]] = np.mean(
            abs(values - som.get_weights()[position[0], position[1]])
        )

    # Generate figure
    plt.figure(figsize=(8, 6))
    plt.imshow(qualities, cmap="viridis", origin="lower")
    plt.colorbar(label="Quality")
    plt.title("Quality Plot")
    plt.xlabel("SOM X coordinate")
    plt.ylabel("SOM Y coordinate")

    # Save figure
    if out_prefix is None:
        out_prefix = "quality_plot"
    output_file = OUTPUT_DIR / f"{out_prefix}_{timestamp}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "message": "Quality plot created successfully",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/AdvancedVisualization.ipynb",
        "artifacts": [
            {
                "description": "Quality plot visualization",
                "path": str(output_file.resolve()),
            }
        ],
    }


@advanced_visualization_mcp.tool()
def minisom_create_property_plot(
    som_path: Annotated[str | None, "Path to trained SOM object (pickle file)"] = None,
    data_path: Annotated[
        str | None, "Path to training data file with extension .csv"
    ] = None,
    columns: Annotated[list | None, "List of column names for each feature"] = None,
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Create property plot showing mean values of each feature per neuron for correlation analysis.
    Input is trained SOM model, training data, and feature names; output is multi-panel heatmap showing feature distributions.
    """
    # Input validation
    if som_path is None:
        raise ValueError("Path to trained SOM object must be provided")
    if data_path is None:
        raise ValueError("Path to training data file must be provided")
    if columns is None:
        raise ValueError("Column names list must be provided")

    # File existence validation
    som_file = Path(som_path)
    if not som_file.exists():
        raise FileNotFoundError(f"SOM file not found: {som_path}")

    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    # Load SOM and data
    with open(som_path, "rb") as f:
        som = pickle.load(f)

    data = pd.read_csv(data_path).values

    # Exact tutorial implementation
    win_map = som.win_map(data)
    size = som.distance_map().shape[0]
    properties = np.empty((size * size, 2 + data.shape[1]))
    properties[:] = np.NaN
    i = 0
    for row in range(0, size):
        for col in range(0, size):
            properties[size * row + col, 0] = row
            properties[size * row + col, 1] = col

    for position, values in win_map.items():
        properties[size * position[0] + position[1], 0] = position[0]
        properties[size * position[0] + position[1], 1] = position[1]
        properties[size * position[0] + position[1], 2:] = np.mean(values, axis=0)
        i = i + 1

    B = ["row", "col"]
    B.extend(columns)
    properties = pd.DataFrame(data=properties, columns=B)

    # Create plotly figure - exact tutorial structure
    fig = make_subplots(
        rows=math.ceil(math.sqrt(data.shape[1])),
        cols=math.ceil(math.sqrt(data.shape[1])),
        shared_xaxes=False,
        horizontal_spacing=0.1,
        vertical_spacing=0.05,
        subplot_titles=columns,
        column_widths=None,
        row_heights=None,
    )

    i = 0
    zmin = min(np.min(properties.iloc[:, 2:]))
    zmax = max(np.max(properties.iloc[:, 2:]))

    for property in columns:
        fig.add_traces(
            [
                go.Heatmap(
                    z=properties.sort_values(by=["row", "col"])[
                        property
                    ].values.reshape(size, size),
                    zmax=zmax,
                    zmin=zmin,
                    coloraxis="coloraxis2",
                )
            ],
            rows=[i // math.ceil(math.sqrt(data.shape[1])) + 1],
            cols=[i % math.ceil(math.sqrt(data.shape[1])) + 1],
        )
        i = i + 1

    for layout in fig.layout:
        if layout.startswith("xaxis") or layout.startswith("yaxis"):
            fig.layout[layout].visible = False
            fig.layout[layout].visible = False
        if layout.startswith("coloraxis"):
            fig.layout[layout].cmax = zmax
            fig.layout[layout].cmin = zmin
        if layout.startswith("colorscale"):
            fig.layout[layout] = {"diverging": "viridis"}

    fig.update_layout(height=800)

    # Save figure
    if out_prefix is None:
        out_prefix = "property_plot"
    output_file = OUTPUT_DIR / f"{out_prefix}_{timestamp}.html"
    fig.write_html(str(output_file))

    return {
        "message": "Property plot created successfully",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/AdvancedVisualization.ipynb",
        "artifacts": [
            {
                "description": "Property plot visualization",
                "path": str(output_file.resolve()),
            }
        ],
    }


@advanced_visualization_mcp.tool()
def minisom_create_distribution_map(
    som_path: Annotated[str | None, "Path to trained SOM object (pickle file)"] = None,
    data_path: Annotated[
        str | None, "Path to training data file with extension .csv"
    ] = None,
    target_path: Annotated[
        str | None, "Path to target labels file with extension .csv"
    ] = None,
    columns: Annotated[list | None, "List of column names for each feature"] = None,
    label_names: Annotated[
        dict | None, "Dictionary mapping target values to label names"
    ] = None,
    plottype: Annotated[
        Literal["barpolar", "spider"], "Type of polar plot to create"
    ] = "barpolar",
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Create distribution map with polar plots showing min/mean/max per neuron colored by dominant class.
    Input is trained SOM model, training data, target labels, feature names, and label mapping; output is polar subplot grid visualization.
    """
    # Input validation
    if som_path is None:
        raise ValueError("Path to trained SOM object must be provided")
    if data_path is None:
        raise ValueError("Path to training data file must be provided")
    if target_path is None:
        raise ValueError("Path to target labels file must be provided")
    if columns is None:
        raise ValueError("Column names list must be provided")
    if label_names is None:
        raise ValueError("Label names dictionary must be provided")

    # File existence validation
    som_file = Path(som_path)
    if not som_file.exists():
        raise FileNotFoundError(f"SOM file not found: {som_path}")

    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    target_file = Path(target_path)
    if not target_file.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")

    # Load SOM, data, and targets
    with open(som_path, "rb") as f:
        som = pickle.load(f)

    data = pd.read_csv(data_path).values
    target = pd.read_csv(target_path).values.flatten()

    # Exact tutorial implementation - helper function
    def distributionMap(data, clusters, size, columns, minimum, maximum, plottype):
        spec = {"type": "polar"}
        fig = make_subplots(
            rows=size,
            cols=size,
            specs=np.full((size, size), spec).tolist(),
            shared_yaxes=True,
            shared_xaxes=True,
            horizontal_spacing=0,
            vertical_spacing=0,
            subplot_titles=None,
            column_widths=None,
            row_heights=None,
        )
        categories = columns

        if plottype == "spider":
            for index, row in data.iterrows():
                fig.add_traces(
                    [
                        go.Scatterpolargl(
                            r=row["max"],
                            name="max",
                            fillcolor="green",
                            line=dict(color="green"),
                            theta=categories,
                            opacity=0.5,
                        ),
                        go.Scatterpolargl(
                            r=row["mean"],
                            name="mean",
                            fillcolor="blue",
                            line=dict(color="blue"),
                            theta=categories,
                            opacity=0.5,
                        ),
                        go.Scatterpolargl(
                            r=row["min"],
                            name="min",
                            fillcolor="red",
                            line=dict(color="red"),
                            theta=categories,
                            opacity=0.5,
                        ),
                    ],
                    rows=[row["row"], row["row"], row["row"]],
                    cols=[row["col"], row["col"], row["col"]],
                )
        else:
            for index, row in data.iterrows():
                fig.add_traces(
                    [
                        go.Barpolar(
                            base=minimum,
                            r=row["max"] - minimum,
                            name="max" + str(index),
                            marker_color="green",
                            theta=categories,
                        ),
                        go.Barpolar(
                            base=minimum,
                            r=row["mean"] - minimum,
                            name="mean" + str(index),
                            marker_color="blue",
                            theta=categories,
                        ),
                        go.Barpolar(
                            base=minimum,
                            r=row["min"] - minimum,
                            name="min" + str(index),
                            marker_color="darkred",
                            theta=categories,
                        ),
                    ],
                    rows=[row["row"], row["row"], row["row"]],
                    cols=[row["col"], row["col"], row["col"]],
                )

        if plottype == "spider":
            fig.update_traces(mode="lines", fill="toself")

        for layout in fig.layout:
            if layout.startswith("polar"):
                fig.layout[layout].angularaxis.visible = False
                fig.layout[layout].angularaxis.tickfont.size = 7
                fig.layout[layout].radialaxis.visible = True
                fig.layout[layout].radialaxis.tickfont.size = 7
                fig.layout[layout].barmode = "overlay"
                fig.layout[layout].radialaxis.range = [minimum, maximum + 1]

        for index, row in data.iterrows():
            color = row["bgcolor"]
            if row["row"] == 0 and row["col"] == 0:
                fig.layout["polar"].bgcolor = (
                    "rgb(" + ",".join(str(i) for i in [color] * 3) + ")"
                )
            else:
                fig.layout[
                    "polar" + str((row["row"] - 1) * size + row["col"])
                ].bgcolor = ("rgb(" + ",".join(str(i) for i in [color] * 3) + ")")

        fig.update_layout(width=900, height=900, showlegend=False)

        return fig

    # Main processing - exact tutorial logic
    size = som.distance_map().shape[0]
    clusters = np.array(np.arange(0, size * size)).reshape(size, size)
    distributionMapData = pd.DataFrame(
        columns=["col", "row", "min", "mean", "max", "bgcolor"]
    )
    labels_map = som.labels_map(data, [label_names[t] for t in target])
    win_map = som.win_map(data)

    for position in win_map.keys():
        label_fracs = [labels_map[position][l] for l in label_names.values()]
        bgcolor = label_fracs.index(np.max(label_fracs)) * 255 // len(label_fracs)
        winner = win_map[position]
        minima = np.min(winner, axis=0)
        means = np.mean(winner, axis=0)
        maxima = np.max(winner, axis=0)
        row = int(position[1] + 1)
        col = int(position[0] + 1)
        distributionMapData = distributionMapData.append(
            {
                "col": col,
                "row": size - row + 1,
                "min": minima,
                "mean": means,
                "max": maxima,
                "bgcolor": bgcolor,
            },
            verify_integrity=True,
            ignore_index=True,
        )

    noClusters = np.max(clusters).item() + 1
    clusterData = pd.DataFrame(columns=["col", "row", "min", "mean", "max"])

    maximum = max([l.max() for l in distributionMapData["max"].values])
    minimum = min([l.min() for l in distributionMapData["min"].values])

    fig = distributionMap(
        distributionMapData, clusters, size, columns, minimum, maximum, plottype
    )

    # Save figure
    if out_prefix is None:
        out_prefix = "distribution_map"
    output_file = OUTPUT_DIR / f"{out_prefix}_{timestamp}.html"
    fig.write_html(str(output_file))

    return {
        "message": "Distribution map created successfully",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/AdvancedVisualization.ipynb",
        "artifacts": [
            {
                "description": "Distribution map visualization",
                "path": str(output_file.resolve()),
            }
        ],
    }


# Helper functions for starburst map
def findMin(x, y, umat):
    """Find minimum value in neighborhood of position (x,y)."""
    newxmin = max(0, x - 1)
    newxmax = min(umat.shape[0], x + 2)
    newymin = max(0, y - 1)
    newymax = min(umat.shape[1], y + 2)
    minx, miny = np.where(
        umat[newxmin:newxmax, newymin:newymax]
        == umat[newxmin:newxmax, newymin:newymax].min()
    )
    return newxmin + minx[0], newymin + miny[0]


def findInternalNode(x, y, umat):
    """Find internal node by following maximum gradient."""
    minx, miny = findMin(x, y, umat)
    if minx == x and miny == y:
        cx = minx
        cy = miny
    else:
        cx, cy = findInternalNode(minx, miny, umat)
    return cx, cy


def matplotlib_cmap_to_plotly(cmap, entries):
    """Convert matplotlib colormap to plotly format."""
    h = 1.0 / (entries - 1)
    colorscale = []

    for k in range(entries):
        C = np.array(cmap(k * h)[:3]) * 255
        colorscale.append([k * h, "rgb" + str((C[0], C[1], C[2]))])

    return colorscale


@advanced_visualization_mcp.tool()
def minisom_create_starburst_map(
    som_path: Annotated[str | None, "Path to trained SOM object (pickle file)"] = None,
    out_prefix: Annotated[str | None, "Output file prefix"] = None,
) -> dict:
    """
    Create starburst gradient visualization showing similarity patterns via maximum gradient lines.
    Input is trained SOM model and output is starburst map with gradient flow visualization.
    """
    # Input validation
    if som_path is None:
        raise ValueError("Path to trained SOM object must be provided")

    # File existence validation
    som_file = Path(som_path)
    if not som_file.exists():
        raise FileNotFoundError(f"SOM file not found: {som_path}")

    # Load SOM
    with open(som_path, "rb") as f:
        som = pickle.load(f)

    # Exact tutorial implementation
    norm = matplotlib.colors.Normalize(vmin=0, vmax=255)
    bone_r_cmap = matplotlib.cm.get_cmap("bone_r")
    bone_r = matplotlib_cmap_to_plotly(bone_r_cmap, 255)

    layout = go.Layout(title="starburstMap")
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Heatmap(z=som.distance_map().T, colorscale=bone_r))
    shapes = []

    for row in np.arange(som.distance_map().shape[0]):
        for col in np.arange(som.distance_map().shape[1]):
            cx, cy = findInternalNode(row, col, som.distance_map().T)
            shape = go.layout.Shape(
                type="line",
                x0=row,
                y0=col,
                x1=cx,
                y1=cy,
                line=dict(color="Black", width=1),
            )
            shapes = np.append(shapes, shape)

    fig.update_layout(shapes=shapes.tolist(), width=500, height=500)

    # Save figure
    if out_prefix is None:
        out_prefix = "starburst_map"
    output_file = OUTPUT_DIR / f"{out_prefix}_{timestamp}.html"
    fig.write_html(str(output_file))

    return {
        "message": "Starburst map created successfully",
        "reference": "https://github.com/JustWhyKing/minisom/blob/master/examples/AdvancedVisualization.ipynb",
        "artifacts": [
            {
                "description": "Starburst map visualization",
                "path": str(output_file.resolve()),
            }
        ],
    }


if __name__ == "__main__":
    advanced_visualization_mcp.run()
