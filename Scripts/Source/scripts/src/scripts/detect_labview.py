from pathlib import Path
import os
import re
import sys
import configparser

# -----------------------------
# Step 1: Get GitHub repo path
# -----------------------------

if len(sys.argv) < 2:
    print("ERROR: GitHub workspace path not provided.")
    sys.exit(1)

repo_path = Path(sys.argv[1])

ini_path = repo_path / "CICD" / "Configs" / "PathConfigs.ini"

print(f"Using config path: {ini_path}")

if not ini_path.exists():
    print(f"ERROR: Config file not found at {ini_path}")
    sys.exit(1)

# -----------------------------
# Step 2: Read INI config
# -----------------------------
config = configparser.ConfigParser()
config.read(ini_path)

try:
    expected_lv_version = config["LabVIEW"]["Version"]
    expected_bitness = config["LabVIEW"]["Bitness"]
except KeyError as e:
    print(f"ERROR: Missing key in INI file: {e}")
    sys.exit(1)

print(f"Expected Version: {expected_lv_version}")
print(f"Expected Bitness: {expected_bitness}")
print()

# -----------------------------
# Step 3: Detect installed LabVIEW
# -----------------------------
search_roots = [
    Path(r"C:\Program Files\National Instruments"),
    Path(r"C:\Program Files (x86)\National Instruments"),
]

labviews = []

for root in search_roots:
    if root.exists():
        for item in root.iterdir():
            if item.is_dir() and re.match(r"LabVIEW \d{4}$", item.name):
                labviews.append(item)

if not labviews:
    print("ERROR: No LabVIEW installations found.")
    sys.exit(1)

# Sort descending (latest first just for logging clarity)
labviews.sort(key=lambda p: p.name, reverse=True)

print("Scanning installed LabVIEW versions...\n")

selected_lv = None
selected_bitness = None

for lv in labviews:
    lv_version = lv.name.replace("LabVIEW ", "")
    current_bitness = "32" if "Program Files (x86)" in str(lv) else "64"
    depswatch_folder = lv / "vi.lib" / "DepsWatch"

    # Match ALL conditions
    if (
        depswatch_folder.exists()
        and lv_version == expected_lv_version
        and current_bitness == expected_bitness
    ):
        selected_lv = lv
        selected_bitness = current_bitness
        break

# -----------------------------
# Step 4: Validate selection
# -----------------------------
if selected_lv is None:
    print("ERROR: No matching LabVIEW found with required version, bitness with DepsWatch.")
    sys.exit(1)

lv_version = selected_lv.name.replace("LabVIEW ", "")

# -----------------------------
# Step 5: Print final result
# -----------------------------
print(f"LabVIEW Version: {lv_version}")
print(f"Bitness: {selected_bitness}")
print(f"Path: {selected_lv}")

# -----------------------------
# Step 6: Export to GitHub ENV
# -----------------------------
github_env = os.getenv("GITHUB_ENV")

if github_env:
    with open(github_env, "a") as f:
        f.write(f"LV_VERSION={lv_version}\n")
        f.write(f"LV_BITNESS={selected_bitness}\n")
        f.write(f"LV_PATH={selected_lv}\n")