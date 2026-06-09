import argparse
import os
import sys
from scripts import analyze_dependencies

def main():
    parser = argparse.ArgumentParser(description="Generate dependency graphs for selected nodes")
    parser.add_argument("--file", default="Source/ActualDependencies", help="Path to .adeps file or directory")
    parser.add_argument("--nodes", nargs='+', required=True, help="List of nodes to analyze")
    parser.add_argument("--output-dir", default="reports", help="Directory to save output images")
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
        G = analyze_dependencies.load_graph_from_adeps(args.file)
        os.makedirs(args.output_dir, exist_ok=True)
        
        for node in args.nodes:
            output_path = os.path.join(args.output_dir, f"{node}_dependency_graph.png")
            analyze_dependencies.analyze_node_and_plot(G, node, output_path, args.h_spacing, args.v_spacing)
            print(f"Graph for '{node}' saved to {output_path}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Debugging: Inject arguments if none are passed via command line
    if len(sys.argv) == 1:
        # Simulate: python script.py --nodes ModuleA ModuleB
        sys.argv.extend(["--nodes", "ModuleA", "FileUtilities", "ModuleB"])
    main()