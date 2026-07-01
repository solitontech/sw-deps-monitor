"""
This Module has funtions to generate the following lists:
1. generate_changed_files_list(): Perform a git diff and Generates a list of changed files for the given base branch and head branch.
2. generate_changed_lvfiles_list(): Generates a list of changed LabVIEW files with extensions .vi, .ctl, .lvclass, .lvlib, ignore_extensions: lvproj or None.
3. filter_changed_lvfiles_based_on_scope(): Gets the list from one of the above functions and filters them based on configurations from Hawkeye/Configs/PathConfigs.ini file.
    a. section_names_for_inclusion: List of section names in the PathConfigs.ini file to include paths from.
    b. section_names_for_exclusion: List of section names in the PathConfigs.ini file to exclude paths from.
    c. additional_exclude_paths: Additional paths to be excluded apart from the ones in the PathConfigs.ini file.
    d. additional_include_paths: Additional paths to be included apart from the ones in the PathConfigs.ini file.
4. get_exclude_paths_for_given_check(): Gets the exclude paths for a given check from the PathConfigs.ini file.
    a. exclusion_section_specific_to_check: Section name in the PathConfigs.ini file to exclude paths specific to a check.
"""

## Imports
import argparse
from dataclasses import dataclass
from typing import Dict, Any
import os, subprocess, configparser


## Constants
PATH_CONFIGS_FILE = "Hawkeye/Configs/PathConfigs.ini"
section_names_for_inclusion = ["SourceFolderPaths", "GlobalIncludePaths"]
section_names_for_exclusion = ["GlobalExcludePaths"]
exclusion_section_specific_to_check = "ExcludePathsSpecificToChecks"
# default repo-relative paths (fallbacks)
changed_files_list_path = os.path.normpath(r".HawkeyeCache\Temp\CheckModifiedLVFiles\changed_files.txt")
changed_lvfiles_list_path = os.path.normpath(r".HawkeyeCache\Temp\CheckModifiedLVFiles\changed_lvfiles.txt")
in_scope_changed_lvfiles_path = os.path.normpath(r".HawkeyeCache\Temp\CheckModifiedLVFiles\in_scope_changed_lvfiles.txt")
in_scope_changed_lvlibs_path = os.path.normpath(r".HawkeyeCache\Temp\CheckModifiedLVFiles\in_scope_changed_lvlibs.txt")

def load_path_configs(workspace_root: str) -> None:
    """
    Read PATH_CONFIGS_FILE from workspace_root and set the module-global
    paths: changed_files_list_path, changed_lvfiles_list_path,
    in_scope_changed_lvfiles_path. Values in the INI are treated as
    repo-relative; surrounding quotes are stripped. Falls back to defaults.
    """

    global changed_files_list_path, changed_lvfiles_list_path, in_scope_changed_lvfiles_path, in_scope_changed_lvlibs_path

    cfg = configparser.ConfigParser()
    cfg_path = os.path.join(workspace_root, PATH_CONFIGS_FILE)
    try:
        cfg.read(cfg_path)
    except Exception:
        # leave defaults on any read/parsing error
        return

    sec = "ChangedFilesLogs"
    def _get_opt(opt_name: str, default: str) -> str:
        try:
            if cfg.has_section(sec) and cfg.has_option(sec, opt_name):
                val = cfg.get(sec, opt_name)
                if val is None:
                    return default
                val = val.strip().strip('"').strip("'")
                return os.path.normpath(val) if val else default
        except Exception:
            pass
        return default

    changed_files_list_path = _get_opt("ChangedFilesListPath", changed_files_list_path)
    changed_lvfiles_list_path = _get_opt("ChangedLVFilesListPath", changed_lvfiles_list_path)
    in_scope_changed_lvfiles_path = _get_opt("InScopeChangedLVFilesPath", in_scope_changed_lvfiles_path)
    in_scope_changed_lvlibs_path = _get_opt("InScopeChangedLVLibsPath", in_scope_changed_lvlibs_path)


## Function to get the workspace root from command line arguments using argparse
## Additionally import few more arguments using arg parse.
@dataclass
class CLIArgs:
    """
    Typed container for CLI arguments — use this return type so editors
    (IntelliSense) show completions on the returned object (e.g. args.<Tab>).
    Add fields here as you add argparse options.
    """
    workspace_root: str = r"C:\sw-deps-monitor"
    base_branch: str = "origin/main"
    head_branch: str = "HEAD"


def get_args() -> CLIArgs:
    """
    Parse command-line arguments and return a typed dataclass (CLIArgs).
    This avoids using globals and enables proper editor completions.
    """
    parser = argparse.ArgumentParser(description="Get workspace root and other arguments")
    parser.add_argument("--workspace_root", type=str, default=CLIArgs.workspace_root,
                        help="Path to the workspace root (default: C:\\sw-deps-monitor)")

    parser.add_argument("--base_branch", type=str, default=CLIArgs.base_branch,
                        help="base branch to compare (default: origin/main)")
    parser.add_argument("--head_branch", type=str, default=CLIArgs.head_branch,
                        help="head branch to compare (default: HEAD)")

    ns = parser.parse_args()
    try:
        ns_dict: Dict[str, Any] = vars(ns)
    except TypeError:
        ns_dict = {}
    # Map argparse Namespace -> CLIArgs for proper typing/completion
    return CLIArgs(**ns_dict)


def get_cli_args() -> CLIArgs:
    """
    Convenience wrapper: call this from other modules to obtain a typed args object.
    Does NOT store anything in globals().
    """
    return get_args()

def run(cmd: list[str]) -> tuple[int, str, str]:
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def git_diff(repo_path:str, base_branch: str, head_branch: str) -> None:
    # try to find merge-base
    rc, mb, err = run(["git", "-C", repo_path, "merge-base", base_branch, head_branch])
    if rc == 0 and mb:
        rc, out, err = run(["git", "-C", repo_path, "diff", "--name-only", mb, head_branch])
    else:
        # fallback when merge-base can't be resolved (shallow/detached)
        rc, out, err = run(["git", "-C", repo_path, "diff", "--name-only", f"{base_branch}..{head_branch}"])

    if rc != 0:
        raise RuntimeError(f"git diff failed: {err}")
    if not out:
        return []
    
    changed_files_list = [line for line in out.splitlines() if line.strip()]
    return changed_files_list

def generate_changed_files_list(base_branch: str, head_branch: str, workspace_root: str) -> list[str]:
    """
    Return list of changed files between `base_branch` and `head_branch`.
    Prefer the true merge-base (what a PR would introduce). If merge-base
    can't be resolved (shallow/detached checkouts), fall back to base..head.
    """
    repo_path = os.path.abspath(workspace_root)
    
    changed_files_list = git_diff(repo_path, base_branch, head_branch)

    global changed_files_list_path
    file_path = os.path.join(repo_path, changed_files_list_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w+") as f:
        for file_ in changed_files_list:
            f.write(f"{file_}\n")

    return changed_files_list

def generate_changed_lvfiles_list(repo_path: str, include_extensions: list[str] = [".vi", ".ctl", ".lvclass", ".lvlib"],
                                  ) -> list[str]:
    """
    Generate a list of changed LabVIEW files with specified extensions.
    """
    global changed_files_list_path
    global changed_lvfiles_list_path

    lv_files_file_path = os.path.join(repo_path, changed_lvfiles_list_path)
    os.makedirs(os.path.dirname(lv_files_file_path), exist_ok=True)
    
    all_changed_file_path = os.path.join(repo_path, changed_files_list_path)
    os.makedirs(os.path.dirname(all_changed_file_path), exist_ok=True)
    if not os.path.exists(all_changed_file_path):
        raise FileNotFoundError(f"Changed files list not found at {all_changed_file_path}. Please run generate_changed_files_list first.")
    
    changed_lvfiles_list = []
    with open(all_changed_file_path, "r") as f:
        changed_files = f.readlines()
        for file_ in changed_files:
            file_ = file_.strip()
            if any(file_.endswith(ext) for ext in include_extensions):
                changed_lvfiles_list.append(file_)
    
    with open(lv_files_file_path, "w+") as f:
        for file_ in changed_lvfiles_list:
            f.write(f"{file_}\n")

    return changed_lvfiles_list

def filter_changed_lvfiles_based_on_scope(
    repo_path: str,
    section_names_for_inclusion: list[str] | None = None,
    section_names_for_exclusion: list[str] | None = None,
    additional_include_paths: list[str] | None = None,
    additional_exclude_paths: list[str] | None = None,
    ignore_extensions: list[str] | None = None,
) -> list[str]:
    """
    Read the changed LV files list and return the subset that is in-scope
    according to PathConfigs.ini sections + additional include/exclude lists.
    Writes the resulting list to in_scope_changed_lvfiles_path and returns it.
    """
    import configparser

    section_names_for_inclusion = section_names_for_inclusion or globals().get("section_names_for_inclusion", [])
    section_names_for_exclusion = section_names_for_exclusion or globals().get("section_names_for_exclusion", [])
    additional_include_paths = additional_include_paths or []
    additional_exclude_paths = additional_exclude_paths or []
    ignore_extensions = ignore_extensions if ignore_extensions is not None else [".lvproj"]

    cfg = configparser.ConfigParser()
    cfg_path = os.path.join(repo_path, PATH_CONFIGS_FILE)
    cfg.read(cfg_path)

    def collect_paths(sections: list[str]) -> list[str]:
        out: list[str] = []
        for sec in sections:
            if not cfg.has_section(sec):
                continue
            for k, v in cfg.items(sec):
                for raw in (k, v):
                    if not raw:
                        continue
                    # allow comma/semicolon/newline separated values inside an item
                    for part in (s.strip() for s in raw.replace("\r", ",").replace("\n", ",").replace(";", ",").split(",")):
                        if part:
                            out.append(part)
        return out

    include_raw = collect_paths(section_names_for_inclusion) + additional_include_paths
    exclude_raw = collect_paths(section_names_for_exclusion) + additional_exclude_paths

    def abs_norm(p: str) -> str:
        p = p.strip()
        if not p:
            return ""
        if os.path.isabs(p):
            return os.path.normcase(os.path.normpath(p))
        return os.path.normcase(os.path.normpath(os.path.join(repo_path, p)))

    include_abs = [abs_norm(p) for p in include_raw if p]
    exclude_abs = [abs_norm(p) for p in exclude_raw if p]

    changed_lv_path = os.path.join(repo_path, changed_lvfiles_list_path)
    if not os.path.exists(changed_lv_path):
        raise FileNotFoundError(f"Changed LV files list not found: {changed_lv_path}")

    in_scope: list[str] = []
    with open(changed_lv_path, "r", encoding="utf-8") as fh:
        for line in fh:
            file_rel = line.strip()
            if not file_rel:
                continue
            if any(file_rel.lower().endswith(ext.lower()) for ext in ignore_extensions):
                continue
            file_abs = abs_norm(file_rel)
            if not file_abs:
                continue

            # excluded?
            excluded = any(
                file_abs == ex or file_abs.startswith(ex + os.path.sep)
                for ex in exclude_abs
            )
            if excluded:
                continue

            # included? if no include paths configured, treat as included
            if include_abs:
                included = any(
                    file_abs == inc or file_abs.startswith(inc + os.path.sep)
                    for inc in include_abs
                )
                if not included:
                    continue

            in_scope.append(file_rel)

    # write results
    out_path = os.path.join(repo_path, in_scope_changed_lvfiles_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w+", encoding="utf-8") as fh:
        for f in in_scope:
            fh.write(f"{f}\n")

    return in_scope

def generate_inscope_changed_lvlibs_list(repo_path: str) -> list[str]:
    """
    Generate a list of in-scope changed LabVIEW libraries (.lvlib) from
    the in-scope changed LV files list.
    """
    global in_scope_changed_lvlibs_path
    
    # g-cli -v --lv-ver 2023 --arch 32 "<LabVIEW>\vi.lib\Hawkeye\CheckModifiedVIs\GenerateChangedLibrariesList.vi" -- "E:\sw-deps-monitor"

    lv_path = os.environ.get("LV_PATH")
    if not lv_path:
        raise EnvironmentError("LV_PATH not set in environment")
    lv_version = os.environ.get("LV_VERSION")
    lv_bitness = os.environ.get("LV_BITNESS")

    vi_path = os.path.join(
        lv_path,
        "vi.lib",
        "Hawkeye",
        "CheckModifiedVIs",
        "GenerateChangedLibrariesList.vi"
    )
    
    gcli_args = [
        "g-cli",
        "-v",
        "--lv-ver", lv_version,
        "--arch", lv_bitness,
        vi_path,
        "--",
        repo_path
    ] 
    rc, out, err = run(gcli_args)
    if rc != 0:
        raise RuntimeError(f"g-cli call to GenerateChangedLibrariesList.vi failed: {err}")
    else:
        print(out)
    
    changed_lib_log_path = os.path.join(repo_path, in_scope_changed_lvlibs_path)
    if not os.path.exists(changed_lib_log_path):
        raise FileNotFoundError(f"In-scope changed LV libraries list not found: {changed_lib_log_path}")
    else:
        print(f"In-scope changed LV libraries list generated at: {changed_lib_log_path}")

    return None

def main():
    args = get_cli_args()
    print("Workspace Root:", args.workspace_root)

    # Load path configs to set global path variables
    load_path_configs(args.workspace_root)

    generate_changed_files_list(
        base_branch=args.base_branch,
        head_branch=args.head_branch,
        workspace_root=args.workspace_root
    )
    generate_changed_lvfiles_list(
        repo_path=args.workspace_root
    )
    filter_changed_lvfiles_based_on_scope(
        repo_path=args.workspace_root
    )
    generate_inscope_changed_lvlibs_list(
        repo_path=args.workspace_root
    )

if __name__ == "__main__":
    main()