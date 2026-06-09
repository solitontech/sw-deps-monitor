import argparse
import os
import sys
from scripts import analyze_dependencies

def main():
    parser = argparse.ArgumentParser(description="Generate full dependency graph image")
    parser.add_argument("--file", default="Source/ActualDependencies", help="Path to .adeps file or directory")
    parser.add_argument("--output", default="reports/full_dependency_graph.png", help="Output image file path")
    args = parser.parse_args()

    try:
        G = analyze_dependencies.load_graph_from_adeps(args.file)
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        analyze_dependencies.plot_graph(G, args.output, title="Full Dependency Graph")
        print(f"Graph saved to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()