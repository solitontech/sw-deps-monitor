import argparse, os
from pathlib import Path
from collections import OrderedDict
import shutil
import datetime

def parse_file(p):
    sections = OrderedDict()
    header = []
    cur = None
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\n")
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            cur = s[1:-1]
            if cur not in sections:
                sections[cur] = []
        else:
            if cur is None:
                header.append(line)
            else:
                # treat non-empty, non-comment lines as keys
                if line.strip() == "":
                    continue
                if line.lstrip().startswith(";") or line.lstrip().startswith("#"):
                    # ignore comments for sorting output
                    continue
                sections[cur].append(line.strip())
    return header, sections

def sort_sections_and_keys(header, sections):
    # sort section names case-insensitive, stable
    sorted_sections = OrderedDict()
    for sec in sorted(sections.keys(), key=lambda s: s.lower()):
        keys = sections[sec]
        # sort keys by left-hand side before '=', case-insensitive
        def key_sort(k):
            if '=' in k:
                return k.split('=',1)[0].strip().lower()
            return k.strip().lower()
        sorted_sections[sec] = sorted(keys, key=key_sort)
    return header, sorted_sections

def write_file(p, header, sections, make_backup=False):
    # backup (only if enabled)
    if make_backup:
        bak = p.with_suffix(p.suffix + ".bak." + datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        shutil.copy2(p, bak)
    parts = []
    if header:
        parts.extend(header)
    for sec, keys in sections.items():
        parts.append(f"[{sec}]")
        for k in keys:
            parts.append(k)
        parts.append("")  # blank line after each section
    # ensure single trailing newline
    content = "\n".join(parts).rstrip() + "\n"
    p.write_text(content, encoding="utf-8")

def process_path(folder: Path, exts, recursive=False):
    pattern = "**/*" if recursive else "*"
    for f in folder.glob(pattern):
        if f.is_file() and f.suffix.lower() in exts:
            header, sections = parse_file(f)
            if not sections:
                continue
            header, sorted_sections = sort_sections_and_keys(header, sections)
            write_file(f, header, sorted_sections)
            print(f"Processed: {f}")

def main(folder, ext=".adeps,.ini", recursive=False):
    """
    folder: path string or Path
    ext: comma-separated extensions string (e.g. ".adeps,.ini") or iterable
    recursive: bool
    """
    folder = Path(folder)
    # accept ext as either set/iterable or comma-separated string
    if isinstance(ext, (set, list, tuple)):
        exts = {e.lower() if e.startswith('.') else '.'+e.lower() for e in ext}
    else:
        exts = {e.lower() if e.startswith('.') else '.'+e.lower() for e in (x.strip() for x in str(ext).split(","))}
    if not folder.is_dir():
        print("Not a folder:", folder)
        return
    process_path(folder, exts, recursive=recursive)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Sort INI-style sections and keys in files.")
    ap.add_argument("folder", nargs="?", default=str(os.path.join(Path.cwd(), "Source", "ActualDependencies")), help="Folder containing files (default: current working directory)")
    ap.add_argument("--ext", default=".adeps,.ini", help="Comma-separated extensions to process (default: .adeps,.ini)")
    ap.add_argument("-r", "--recursive", action="store_false", help="Recurse into subfolders")
    args = ap.parse_args()
    main(args.folder, args.ext, args.recursive)

# >uv run python e:\sw-deps-monitor\scripts\src\scripts\sort_actual_deps_list.py "e:\sw-deps-monitor\Source\ActualDependencies" -r -
# -ext .adeps,.ini