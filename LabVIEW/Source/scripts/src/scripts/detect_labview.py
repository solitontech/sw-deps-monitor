from pathlib import Path
import os
import re
import sys

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

# Sort descending by version
labviews.sort(key=lambda p: p.name, reverse=True)

selected_lv = None
bitness = None

for lv in labviews:
    cicd_folder = lv / "vi.lib" / "DepsWatch" / "CICD"
    
    if cicd_folder.exists():
        selected_lv = lv
        bitness = "32" if "Program Files (x86)" in str(lv) else "64"
        break

if selected_lv is None:
    print("ERROR: DepsWatch CICD package not found in any LabVIEW installation.")
    sys.exit(1)

lv_version = selected_lv.name.replace("LabVIEW ", "")

print(f"LabVIEW Version: {lv_version}")
print(f"Bitness: {bitness}")
print(f"Path: {selected_lv}")

github_env = os.getenv("GITHUB_ENV")

if github_env:
    with open(github_env, "a") as f:
        f.write(f"LV_VERSION={lv_version}\n")
        f.write(f"LV_BITNESS={bitness}\n")
        f.write(f"LV_PATH={selected_lv}\n")