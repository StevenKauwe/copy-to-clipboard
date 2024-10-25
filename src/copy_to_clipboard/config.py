import json
import sys
from pathlib import Path

CONFIG_FILENAME = ".copytoclipboard_config.json"


def get_config_path():
    """
    Determines the path to the configuration file.
    Checks the current directory first, then falls back to the user's home directory.
    """
    current_dir = Path.cwd()
    project_config = current_dir / CONFIG_FILENAME
    if project_config.exists():
        return project_config
    home_dir = Path.home()
    home_config = home_dir / CONFIG_FILENAME
    return home_config


def load_config():
    """
    Loads the configuration from the config file.
    Returns a dictionary with 'include_patterns' and 'explicit_files' as keys.
    """
    config_path = get_config_path()
    if not config_path.exists():
        return {"include_patterns": [], "explicit_files": []}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return {"include_patterns": [], "explicit_files": []}


def save_config(config):
    """
    Saves the configuration dictionary to the config file.
    """
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}", file=sys.stderr)


def is_glob_pattern(pattern):
    """
    Determines if a pattern is a glob pattern based on the presence of wildcard characters.
    """
    return any(char in pattern for char in ["*", "?", "[", "]"])


def add_patterns(patterns):
    """
    Adds new patterns to the configuration.
    Separates glob patterns and explicit file paths.
    """
    config = load_config()
    added_globs = []
    added_files = []
    for pattern in patterns:
        normalized = pattern.strip()
        if is_glob_pattern(normalized):
            if normalized not in config["include_patterns"]:
                config["include_patterns"].append(normalized)
                added_globs.append(normalized)
            else:
                print(f"Info: Glob pattern '{normalized}' is already in the list.")
        else:
            absolute_path = str(Path(normalized).resolve())
            if absolute_path not in config["explicit_files"]:
                config["explicit_files"].append(absolute_path)
                added_files.append(absolute_path)
            else:
                print(f"Info: File '{absolute_path}' is already in the list.")
    save_config(config)
    if added_globs:
        print("\nAdded glob patterns:")
        for p in added_globs:
            print(f" - {p}")
    if added_files:
        print("\nAdded explicit files:")
        for f in added_files:
            print(f" - {f}")
    if not added_globs and not added_files:
        print("\nNo new patterns or files were added.")


def remove_patterns(patterns):
    """
    Removes patterns from the configuration.
    Separates glob patterns and explicit file paths.
    """
    config = load_config()
    removed_globs = []
    removed_files = []
    for pattern in patterns:
        normalized = pattern.strip()
        if is_glob_pattern(normalized):
            if normalized in config["include_patterns"]:
                config["include_patterns"].remove(normalized)
                removed_globs.append(normalized)
            else:
                print(f"Info: Glob pattern '{normalized}' is not in the list.")
        else:
            absolute_path = str(Path(normalized).resolve())
            if absolute_path in config["explicit_files"]:
                config["explicit_files"].remove(absolute_path)
                removed_files.append(absolute_path)
            else:
                print(f"Info: File '{absolute_path}' is not in the list.")
    save_config(config)
    if removed_globs:
        print("\nRemoved glob patterns:")
        for p in removed_globs:
            print(f" - {p}")
    if removed_files:
        print("\nRemoved explicit files:")
        for f in removed_files:
            print(f" - {f}")
    if not removed_globs and not removed_files:
        print("\nNo patterns or files were removed.")


def list_patterns():
    """
    Lists all currently added patterns and explicit files.
    """
    config = load_config()
    glob_patterns = config.get("include_patterns", [])
    explicit_files = config.get("explicit_files", [])
    if glob_patterns or explicit_files:
        if glob_patterns:
            print("\nCurrent include patterns (glob):")
            for p in glob_patterns:
                print(f" - {p}")
        if explicit_files:
            print("\nCurrent explicit files:")
            for f in explicit_files:
                print(f" - {f}")
    else:
        print("\nNo include patterns or explicit files found.")


def clear_all_patterns():
    """
    Clears all patterns and explicit files from the configuration.
    """
    config = load_config()
    has_patterns = bool(config["include_patterns"] or config["explicit_files"])
    if has_patterns:
        config["include_patterns"] = []
        config["explicit_files"] = []
        save_config(config)
        print("\nAll include patterns and explicit files have been cleared.")
    else:
        print("\nNo include patterns or explicit files to clear.")

