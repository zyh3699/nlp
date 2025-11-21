"""
Model Context Protocol (MCP) for minisom

Self-Organizing Maps (SOM) toolkit providing comprehensive data analysis and visualization capabilities.
Enables unsupervised learning through neural network-based clustering, classification, and advanced visualization techniques.
Designed for exploratory data analysis, pattern recognition, and dimensionality reduction tasks.

This MCP Server contains tools extracted from the following tutorial files:
1. basic_usage
    - minisom_train_som: Train SOM on normalized data with PCA initialization
    - minisom_visualize_distance_map: Create distance map with sample markers
    - minisom_visualize_scatter_map: Create scatter plot visualization on distance map
    - minisom_visualize_activation_frequencies: Show neuron activation frequency heatmap
    - minisom_visualize_class_distribution: Display pie charts showing class proportions per neuron
    - minisom_track_training_errors: Monitor quantization, topographic, and distortion errors during training
2. advanced_visualization
    - minisom_create_quality_plot: Quality assessment visualization using mean differences
    - minisom_create_property_plot: Feature correlation analysis across neurons
    - minisom_create_distribution_map: Polar plots showing min/mean/max distributions
    - minisom_create_starburst_map: Gradient visualization for similarity patterns
3. classification
    - minisom_train_som_classifier: Train SOM classifier and evaluate performance
4. clustering
    - minisom_cluster_data: Cluster data using SOM and visualize results
"""

from fastmcp import FastMCP

# Import statements (alphabetical order)
from tools.advanced_visualization import advanced_visualization_mcp
from tools.basic_usage import basic_usage_mcp
from tools.classification import classification_mcp
from tools.clustering import clustering_mcp

# Server definition and mounting
mcp = FastMCP(name="minisom")
mcp.mount(advanced_visualization_mcp)
mcp.mount(basic_usage_mcp)
mcp.mount(classification_mcp)
mcp.mount(clustering_mcp)

if __name__ == "__main__":
    mcp.run()