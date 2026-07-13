import argparse
import sys
from scripts import analyze_dependencies

def main():
    parser = argparse.ArgumentParser(description="Check for circular dependencies in .hawkeyelist file")
    parser.add_argument("--folder", default="Hawkeye/ActualDependencies", help="Path to .hawkeyelist file")
    args = parser.parse_args()

    try:
        G = analyze_dependencies.load_graph_from_adeps(args.folder)
        analyze_dependencies.check_circular_paths(G)
        print("No circular paths detected.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()