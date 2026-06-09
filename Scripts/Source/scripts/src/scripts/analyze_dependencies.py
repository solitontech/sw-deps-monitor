import argparse
import configparser
import os
import sys
from typing import Dict, Optional, List

import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio


def load_graph_from_adeps(path: str) -> nx.DiGraph:
    """
    Parses .adeps (INI-style) file(s) and returns a NetworkX Directed Graph.
    If path is a directory, loads all .adeps files in it.
    Sections are nodes, and keys within sections are outgoing edges (dependencies).
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")

    files = []
    if os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(".adeps"):
                    files.append(os.path.join(root, filename))
    else:
        files.append(path)

    config = configparser.ConfigParser(allow_no_value=True)
    # Preserve case sensitivity for keys (node names)
    config.optionxform = str
    config.read(files)

    G = nx.DiGraph()

    for section in config.sections():
        # Add the section as a node (even if it has no dependencies)
        G.add_node(section)
        # Add edges for each dependency
        for dependency in config[section]:
            G.add_edge(section, dependency)

    return G


def check_circular_paths(G: nx.DiGraph) -> None:
    """
    Checks for cycles in the graph. Raises an Exception if a cycle is found.
    """
    cycles = list(nx.simple_cycles(G))
    if cycles:
        raise Exception(f"Circular dependencies detected: {cycles}")

def find_root_nodes(G: nx.DiGraph) -> List[str]:
    """
    Finds nodes in the graph that have no incoming edges (callers).
    """
    return [n for n, d in G.in_degree() if d == 0]


def get_layered_layout(G: nx.DiGraph, horizontal_spacing: float = 2.0, vertical_spacing: float = 2.0) -> Dict[str, tuple]:
    """
    Creates a layered, hierarchical layout for a directed graph.
    Nodes are arranged in layers based on their topological sort order.
    Assumes the graph is a Directed Acyclic Graph (DAG).

    Args:
        G: The NetworkX DiGraph.
        horizontal_spacing: The horizontal distance between nodes in the same layer.
        vertical_spacing: The vertical distance between layers.

    Returns:
        A dictionary of positions keyed by node.
    """
    # This method works for DAGs. Since the script checks for cycles, any remaining
    # unvisited nodes would be part of a disconnected component.
    layers = {}
    if not G.nodes():
        return {}

    # Start with root nodes (in-degree 0)
    current_layer_nodes = [n for n, d in G.in_degree() if d == 0]
    layer_num = 0
    visited = set()

    while current_layer_nodes:
        # Sort nodes for deterministic layout
        sorted_nodes = sorted(list(set(current_layer_nodes)))
        layers[layer_num] = sorted_nodes
        visited.update(sorted_nodes)

        next_layer_nodes = []
        for node in sorted_nodes:
            for successor in G.successors(node):
                if successor not in visited:
                    # A node is in the next layer if all its parents are in current or previous layers
                    is_ready = True
                    for pred in G.predecessors(successor):
                        if pred not in visited:
                            is_ready = False
                            break
                    if is_ready:
                        next_layer_nodes.append(successor)

        current_layer_nodes = next_layer_nodes
        layer_num += 1

    # Assign positions
    pos = {}
    for layer_num, nodes in layers.items():
        # y-coordinate is based on layer number (top-down)
        y = -layer_num * vertical_spacing
        num_nodes_in_layer = len(nodes)
        # x-coordinate is spaced out to center the layer
        layer_width = (num_nodes_in_layer - 1) * horizontal_spacing
        x_start = -layer_width / 2.0
        for i, node in enumerate(nodes):
            x = x_start + i * horizontal_spacing
            pos[node] = (x, y)

    # Handle any remaining nodes (e.g., nodes in cycles if they exist) by placing them at the bottom.
    remaining_nodes = sorted(list(set(G.nodes()) - visited))
    if remaining_nodes:
        y = -layer_num * vertical_spacing
        num_nodes_in_layer = len(remaining_nodes)
        layer_width = (num_nodes_in_layer - 1) * horizontal_spacing
        x_start = -layer_width / 2.0
        for i, node in enumerate(remaining_nodes):
            x = x_start + i * horizontal_spacing
            pos[node] = (x, y)
            
    return pos


def plot_graph(
    G: nx.DiGraph,
    output_path: str,
    title: str = "Dependency Graph",
    node_colors: Optional[Dict[str, str]] = None,
    h_spacing: float = 2.0,
    v_spacing: float = 2.0,
) -> None:
    """
    Plots the directed graph using Plotly and saves it to an image file.
    """
    if not G.nodes():
        print("Warning: Graph is empty, nothing to plot.")
        return

    # Calculate layout for node positions using a layered approach
    pos = get_layered_layout(G, horizontal_spacing=h_spacing, vertical_spacing=v_spacing)

    # To draw arrows, we use annotations instead of a single scatter trace for edges.
    annotations = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        annotations.append(
            go.layout.Annotation(
                ax=x0, ay=y0, axref='x', ayref='y',
                x=x1, y=y1, xref='x', yref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor='#888',
                standoff=5  # Increase gap between arrow and node
            )
        )

    node_x = []
    node_y = []
    node_text = []
    node_color_list = []
    default_color = "#1f77b4"  # Muted blue

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        if node_colors and node in node_colors:
            node_color_list.append(node_colors[node])
        else:
            node_color_list.append(default_color)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        text=node_text,
        textposition="top center",
        marker=dict(showscale=False, color=node_color_list, size=15, line_width=2),
    )

    fig = go.Figure(
        data=[node_trace],
        layout=go.Layout(
            title=dict(text=title, font=dict(size=16)),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=annotations,
        ),
    )
    # Disable mathjax to prevent potential Kaleido hangs/errors on Windows
    pio.defaults.mathjax = None
    fig.write_image(output_path)


def analyze_node_and_plot(
    G: nx.DiGraph, node_name: str, output_path: str, h_spacing: float, v_spacing: float
) -> None:
    """
    Finds descendants and callers (ancestors) of a node and plots the subgraph.
    """
    if node_name not in G:
        print(f"Error: Node '{node_name}' not found in the graph.")
        return

    descendants = nx.descendants(G, node_name)
    ancestors = nx.ancestors(G, node_name)

    print(f"--- Analysis for Node: {node_name} ---")
    print(f"Callers (Ancestors): {', '.join(ancestors) if ancestors else 'None'}")
    print(f"Dependencies (Descendants): {', '.join(descendants) if descendants else 'None'}")

    # Create subgraph including the node, its ancestors, and its descendants
    nodes_of_interest = {node_name} | descendants | ancestors
    sub_G = G.subgraph(nodes_of_interest)

    # Assign colors
    node_colors = {}
    for n in sub_G.nodes():
        if n == node_name:
            node_colors[n] = "red"  # Selected Node
        elif n in ancestors:
            node_colors[n] = "green"  # Callers
        elif n in descendants:
            node_colors[n] = "blue"  # Descendants
        else:
            node_colors[n] = "gray"

    plot_graph(
        sub_G,
        output_path=output_path,
        title=f"Subgraph for {node_name} (Red=Target, Green=Callers, Blue=Descendants)",
        node_colors=node_colors,
        h_spacing=h_spacing,
        v_spacing=v_spacing,
    )


def main():
    parser = argparse.ArgumentParser(description="Analyze dependency graph from .adeps file")
    parser.add_argument(
        "--file",
        type=str,
        # required=True,
        default="Source/ActualDependencies",
        help="Path to the .adeps file or directory (e.g., Source/ActualDependencies)",
    )
    parser.add_argument(
        "--node",
        type=str,
        help="Optional: Name of the node to analyze (descendants/callers)",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Root directory to save reports (default: current directory)",
    )
    parser.add_argument(
        "--h-spacing",
        type=float,
        default=2.0,
        help="Horizontal spacing between nodes in the same layer (default: 2.0)",
    )
    parser.add_argument(
        "--v-spacing",
        type=float,
        default=2.0,
        help="Vertical spacing between layers (default: 2.0)",
    )

    args = parser.parse_args()

    try:
        G = load_graph_from_adeps(args.file)
        print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

        check_circular_paths(G)
        print("No circular paths detected.")

        reports_dir = os.path.join(args.root, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        if args.node:
            output_path = os.path.join(reports_dir, f"{args.node}_dependency_graph.png")
            analyze_node_and_plot(G, args.node, output_path, args.h_spacing, args.v_spacing)
        else:
            output_path = os.path.join(reports_dir, "full_dependency_graph.png")
            plot_graph(
                G,
                output_path,
                title="Full Dependency Graph",
                h_spacing=args.h_spacing,
                v_spacing=args.v_spacing,
            )

        print(f"Graph exported to: {os.path.abspath(output_path)}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()