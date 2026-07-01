import argparse
import os
import sys
from typing import List, Dict, Any

from scripts import analyze_dependencies


def calculate_metrics(G) -> List[Dict[str, Any]]:
    """
    Calculates Ca, Ce, and Instability for each node in the graph.

    Args:
        G: A NetworkX DiGraph.

    Returns:
        A list of dictionaries, where each dictionary contains the metrics for a module.
    """
    metrics = []
    # Sort nodes for consistent, alphabetical output
    sorted_nodes = sorted(list(G.nodes()))

    for node in sorted_nodes:
        # Ca (Afferent Coupling): Number of incoming edges (other modules depending on this one)
        ca = G.in_degree(node)

        # Ce (Efferent Coupling): Number of outgoing edges (modules this one depends on)
        ce = G.out_degree(node)

        # I (Instability): I = Ce / (Ca + Ce)
        denominator = ca + ce
        instability = 0.0 if denominator == 0 else ce / denominator

        metrics.append({
            "module": node,
            "ca": ca,
            "ce": ce,
            "instability": instability
        })
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Calculate coupling metrics (Ca, Ce, I) from .adeps files.")
    parser.add_argument("--file", default="Source/ActualDependencies", help="Path to .adeps file or directory")
    parser.add_argument("--output", default="reports/coupling_metrics.md", help="Output markdown file path")
    args = parser.parse_args()

    try:
        G = analyze_dependencies.load_graph_from_adeps(args.file)
        print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

        all_metrics = calculate_metrics(G)

        if not all_metrics:
            print("No modules found to analyze.")
            return

        # --- Console and File Output ---
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(args.output, "w", encoding="utf-8") as f:
            # Write Markdown Header
            f.write("# Coupling Metrics\n\n")
            f.write("The Instability (I) is calculated using the formula: `I = Ce / (Ca + Ce)`\n\n")
            f.write("| Module Name | Ca (Afferent) | Ce (Efferent) | Instability (I) |\n")
            f.write("|:------------|:-------------:|:-------------:|:---------------:|\n")

            # Print Console Header
            print("\nInstability Formula: I = Ce / (Ca + Ce)")
            print("-" * 84)
            print(f"{'Module Name':<40} | {'Ca (Afferent)':>15} | {'Ce (Efferent)':>15} | {'Instability (I)':>15}")
            print("-" * 84)

            # Single loop for both console and file output
            for m in all_metrics:
                print(f"{m['module']:<40} | {m['ca']:>15} | {m['ce']:>15} | {m['instability']:>15.3f}")
                f.write(f"| {m['module']} | {m['ca']} | {m['ce']} | {m['instability']:.3f} |\n")

            print("-" * 84)

            total_instability = sum(m['instability'] for m in all_metrics)
            average_instability = total_instability / len(all_metrics)

            f.write("\n---\n\n")
            f.write(f"**Average Repository Instability:** `{average_instability:.3f}`\n")

        print(f"\nMetrics report saved to: {os.path.abspath(args.output)}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()