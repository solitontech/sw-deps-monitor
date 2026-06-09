import argparse
import sys
from scripts import analyze_dependencies

def main():
    parser = argparse.ArgumentParser(description="Find root nodes (nodes with no callers)")
    parser.add_argument("--file", default="Source/ActualDependencies", help="Path to .adeps file or directory")
    args = parser.parse_args()

    try:
        G = analyze_dependencies.load_graph_from_adeps(args.file)
        roots = analyze_dependencies.find_root_nodes(G)
        if roots:
            print("\n".join(roots))
        else:
            print("No root nodes found (graph might be fully circular or empty).")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()