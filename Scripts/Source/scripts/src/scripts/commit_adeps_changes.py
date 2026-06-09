import argparse
import os
import subprocess
import sys


def run_command(command, check=True):
    """Runs a command, prints its output, and returns the stripped stdout."""
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=check, encoding="utf-8"
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}", file=sys.stderr)
        print(e.stdout, file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description="Commit dependency updates to the current PR branch if needed.")
    parser.add_argument("--workspace", required=True, help="GitHub workspace path.")
    parser.add_argument("--deps-file-path", required=True, help="Relative path to the dependency file to check.")
    parser.add_argument("--branch", required=True, help="The branch to commit and push to.")
    args = parser.parse_args()

    os.chdir(args.workspace)

    # 1. Check for changes
    status_output = run_command(["git", "status", "--porcelain", args.deps_file_path])
    if not status_output:
        print(f"No changes detected in {args.deps_file_path}. Nothing to commit.")
        return

    print(f"Changes detected in {args.deps_file_path}. Proceeding to commit.")

    # 2. Configure Git
    run_command(["git", "config", "user.name", "github-actions[bot]"])
    run_command(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])

    # 3. Add, commit, and push changes to the existing PR branch
    run_command(["git", "add", args.deps_file_path])
    run_command(["git", "commit", "-m", "chore: [Automated] Update actual dependencies list"])
    run_command(["git", "push", "origin", f"HEAD:{args.branch}"])

    print(f"Successfully committed and pushed changes to branch '{args.branch}'.")

if __name__ == "__main__":
    # For local testing:
    # 1. Manually change the deps file (e.g., Source/ActualDependencies/ActualDepsList.adeps)
    # 2. Check out a feature branch.
    # 3. Run the script from the repository root: `uv run python scripts/src/scripts/commit_adeps_changes.py`
    if len(sys.argv) == 1:
        print("--- Running in local test mode with default arguments ---")
        try:
            # For local testing, we need to be on a branch to push to.
            # Get the current branch name to use as a default.
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, check=True, encoding="utf-8"
            )
            current_branch = result.stdout.strip()
            if not current_branch or current_branch == "HEAD":
                print("Error: Could not determine current git branch. Are you in a detached HEAD state?", file=sys.stderr)
                print("For local testing, please checkout a branch or provide the --branch argument.", file=sys.stderr)
                sys.exit(1)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print("Error: Failed to get current git branch for local testing.", file=sys.stderr)
            print("Please ensure 'git' is installed and you are running this script from within a git repository.", file=sys.stderr)
            if isinstance(e, subprocess.CalledProcessError):
                print(f"Git command failed with stderr: {e.stderr.strip()}", file=sys.stderr)
            sys.exit(1)

        print(f"Detected current branch: '{current_branch}'. Using it for the --branch argument.")
        sys.argv.extend([
            "--workspace", ".",
            "--deps-file-path", "Source/ActualDependencies/ActualDepsList.adeps",
            "--branch", current_branch,
        ])
    main()