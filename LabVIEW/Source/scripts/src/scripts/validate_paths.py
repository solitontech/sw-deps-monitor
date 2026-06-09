#!/usr/bin/env python3
"""
validate-paths.py

Python replacement for the PowerShell-based path validator.

Usage examples:
  python scripts/validate-paths.py --paths-file changed-files.txt
  python scripts/validate-paths.py --paths Source\MyFile.cs Tests\BarTest.cs

Exit codes:
  0 - all checked paths valid
  1 - validation failures found
  2 - script error (missing files, etc.)
"""
import argparse
import os
import re
import sys


SKIP_NAMES = {'.git', '.github', 'node_modules'}


def test_segment(segment: str) -> bool:
    if segment in SKIP_NAMES:
        return True
    if segment.startswith('.'):
        return True
    return bool(re.match(r'^[A-Z][A-Za-z0-9]*$', segment))


def load_paths_file(path):
    if not os.path.exists(path):
        print(f"Paths file not found: {path}", file=sys.stderr)
        sys.exit(2)
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def scan_repo_files(root):
    out = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            out.append(rel.replace('/', os.sep))
    return out


def parse_path_config(config_path):
    include = []
    exclude = []
    if not os.path.exists(config_path):
        return include, exclude

    print(f"Loading path config: {config_path}")
    section = ''
    with open(config_path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith(';'):
                continue
            m = re.match(r'\[(.+)\]', line)
            if m:
                section = m.group(1).strip()
                continue

            if section.lower() == 'globalincludepaths':
                mkey = re.match(r'^([^=]+)', line)
                if mkey:
                    include.append(mkey.group(1).strip().lstrip('./\\/'))
                continue
            if section.lower() == 'globalexcludepaths':
                mkey = re.match(r'^([^=]+)', line)
                if mkey:
                    exclude.append(mkey.group(1).strip().lstrip('./\\/'))
                continue

            m = re.match(r'^Include\s*=\s*(.+)$', line, flags=re.IGNORECASE)
            if m:
                include = [s.strip().lstrip('./\\/') for s in m.group(1).split(',') if s.strip()]
                continue
            m = re.match(r'^Exclude\s*=\s*(.+)$', line, flags=re.IGNORECASE)
            if m:
                exclude = [s.strip().lstrip('./\\/') for s in m.group(1).split(',') if s.strip()]
                continue

    if include:
        print('Include paths: ' + ', '.join(include))
    if exclude:
        print('Exclude paths: ' + ', '.join(exclude))
    return include, exclude


def in_scope(rel, include_list, exclude_list):
    rel_norm = rel.replace('/', os.sep).replace('\\', os.sep).lstrip('./\\')
    # If include list present, require prefix match
    if include_list:
        matched = False
        for inc in include_list:
            inc_norm = inc.replace('/', os.sep).rstrip(os.sep)
            if rel_norm == inc_norm or rel_norm.startswith(inc_norm + os.sep):
                matched = True
                break
        if not matched:
            return False
    # If exclude list present, reject any match
    if exclude_list:
        for exc in exclude_list:
            exc_norm = exc.replace('/', os.sep).rstrip(os.sep)
            if rel_norm == exc_norm or rel_norm.startswith(exc_norm + os.sep):
                return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--paths', nargs='*', help='List of relative paths to validate')
    parser.add_argument('--paths-file', dest='paths_file', help='File containing list of relative paths')
    args = parser.parse_args()

    try:
        root = os.getcwd()
    except Exception as e:
        print(f"Failed to determine repository root: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"Repository root: {root}")

    if args.paths_file:
        target_paths = load_paths_file(args.paths_file)
    elif args.paths:
        target_paths = args.paths
    else:
        target_paths = scan_repo_files(root)

    config_path = os.path.join(root, 'CICD', 'Configs', 'PathConfigs.ini')
    include_list, exclude_list = parse_path_config(config_path)

    invalid = []

    for rel in target_paths:
        if not in_scope(rel, include_list, exclude_list):
            continue
        rel_norm = rel.replace('/', os.sep).lstrip('./\\')
        parts = re.split(r'[\\/]+', rel_norm)

        # validate directory segments
        if len(parts) > 1:
            dirs = parts[:-1]
            if not all(test_segment(p) for p in dirs):
                invalid.append(os.path.normpath(os.path.join(root, rel)))
                continue

        # validate filename without extension
        file_seg = parts[-1]
        file_no_ext = os.path.splitext(file_seg)[0]
        if not test_segment(file_no_ext):
            invalid.append(os.path.normpath(os.path.join(root, rel)))
            continue

    if invalid:
        print('Invalid paths found:')
        for p in sorted(set(invalid)):
            print(' - ' + p)
        sys.exit(1)
    else:
        print('All paths conform to PascalCase rules.')
        sys.exit(0)


if __name__ == '__main__':
    main()
