import os
import pyperclip
import sys
import tiktoken
import fnmatch
from pathlib import Path
from .config import load_config
import pathspec


def get_token_count(text, encoding):
    """
    Returns the number of tokens for the given text using the specified encoding.
    """
    return len(encoding.encode(text))


def load_gitignore():
    """
    Loads and compiles .gitignore patterns using pathspec.
    Returns a PathSpec object.
    """
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        return pathspec.PathSpec.from_lines("gitwildmatch", [])

    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gitignore_patterns = f.readlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", gitignore_patterns)
    except Exception as e:
        print(f"Error loading .gitignore: {e}", file=sys.stderr)
        return pathspec.PathSpec.from_lines("gitwildmatch", [])


def should_ignore(relative_path, spec):
    """
    Determines if a given path should be ignored based on the PathSpec.
    """
    # Convert to posix path for consistent matching
    posix_path = relative_path.replace(os.sep, "/")
    return spec.match_file(posix_path)


def matches_include_patterns(relative_path, include_patterns):
    """
    Determines if a file matches any of the include glob patterns.
    """
    for pattern in include_patterns:
        if fnmatch.fnmatch(relative_path, pattern):
            return True
    return False


def collect_file_contents(
    include_patterns,
    explicit_files,
    max_files=None,
    max_chars=None,
    max_tokens=None,
    encoding=None,
):
    """
    Collects contents of files based on include patterns and explicit files.
    Traverses the directory tree using os.walk and skips ignored directories.
    """
    spec = load_gitignore()
    output = "<code-sample>\n"
    total_chars_copied = 0
    total_tokens_copied = 0
    total_files_added = 0
    total_lines_added = 0
    total_files_skipped = 0
    total_lines_skipped = 0
    skipped_files = []
    included_files = set()

    base_dir = Path.cwd()

    # Precompute absolute explicit file paths
    explicit_files_abs = set(str(Path(f).resolve()) for f in explicit_files)

    for dirpath, dirnames, filenames in os.walk(base_dir):
        # Compute relative directory path from base_dir
        rel_dir = os.path.relpath(dirpath, base_dir)
        if rel_dir == ".":
            rel_dir = ""
        else:
            rel_dir = rel_dir.replace(os.sep, "/")

        # Modify dirnames in-place to skip ignored directories
        # Exclude .git directory
        if ".git" in dirnames:
            dirnames.remove(".git")

        # Skip directories that should be ignored
        dirs_to_remove = []
        for dirname in dirnames:
            rel_dir_path = f"{rel_dir}/{dirname}" if rel_dir else dirname
            if should_ignore(rel_dir_path + "/", spec):
                dirs_to_remove.append(dirname)
                print(
                    f"Info: Skipping directory '{rel_dir_path}/' as it's ignored by .gitignore.",
                    file=sys.stderr,
                )

        for dirname in dirs_to_remove:
            dirnames.remove(dirname)

        # Now process files
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            rel_file = os.path.relpath(file_path, base_dir)
            rel_file_posix = rel_file.replace(os.sep, "/")

            # Exclude .gitignore and .git directory files
            if rel_file_posix == ".gitignore" or rel_file_posix.startswith(".git/"):
                continue

            # Absolute path for explicit file checking
            file_abs_path = str(Path(file_path).resolve())

            # Check if file should be ignored
            if should_ignore(rel_file_posix, spec):
                if file_abs_path not in explicit_files_abs:
                    print(
                        f"Info: '{rel_file_posix}' is ignored by .gitignore. Skipping.",
                        file=sys.stderr,
                    )
                    continue

            if rel_file_posix in included_files:
                continue  # Avoid duplicates

            # Check if file matches include patterns or is explicitly included
            if (
                not matches_include_patterns(rel_file_posix, include_patterns)
                and file_abs_path not in explicit_files_abs
            ):
                continue  # Not matching any include pattern and not an explicit file

            # Read the file
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                print(f"\nFailed to read '{rel_file_posix}': {e}", file=sys.stderr)
                continue

            # Prepare file content
            file_content = f"```{rel_file_posix}\n{content}\n```\n\n"
            file_length = len(file_content)
            file_tokens = get_token_count(file_content, encoding)

            # Check character and token limits
            if max_chars is not None and (total_chars_copied + file_length) > max_chars:
                print(
                    f"\nInfo: Adding '{rel_file_posix}' would exceed character limit. Skipping.",
                    file=sys.stderr,
                )
                skipped_files.append(rel_file_posix)
                total_files_skipped += 1
                total_lines_skipped += content.count("\n") + 1
                continue

            if (
                max_tokens is not None
                and (total_tokens_copied + file_tokens) > max_tokens
            ):
                print(
                    f"\nInfo: Adding '{rel_file_posix}' would exceed token limit. Skipping.",
                    file=sys.stderr,
                )
                skipped_files.append(rel_file_posix)
                total_files_skipped += 1
                total_lines_skipped += content.count("\n") + 1
                continue

            # Add the file content to the output
            output += file_content
            total_chars_copied += file_length
            total_tokens_copied += file_tokens
            total_files_added += 1

            # Count the number of lines added
            lines_in_file = content.count("\n") + 1
            total_lines_added += lines_in_file

            included_files.add(rel_file_posix)

            # Check if limits are reached after adding the file
            if max_files is not None and total_files_added >= max_files:
                break
            if max_chars is not None and total_chars_copied >= max_chars:
                break
            if max_tokens is not None and total_tokens_copied >= max_tokens:
                break

    # Handle explicit files not captured via patterns
    for file_path in explicit_files:
        rel_file = os.path.relpath(file_path, base_dir).replace(os.sep, "/")
        rel_file_posix = Path(rel_file).as_posix()

        # Exclude .gitignore and .git directory files
        if rel_file_posix == ".gitignore" or rel_file_posix.startswith(".git/"):
            continue

        # Convert to absolute path for checking
        file_abs_path = str(Path(file_path).resolve())

        # Check if already included
        if rel_file_posix in included_files:
            continue  # Already included via traversal

        # Check if file exists
        if not Path(file_path).is_file():
            print(
                f"Warning: Explicit file '{rel_file_posix}' does not exist. Skipping.",
                file=sys.stderr,
            )
            continue

        # Check if ignored by .gitignore (unless explicitly included)
        if should_ignore(rel_file_posix, spec):
            # It's explicitly included, so we proceed
            pass

        # Read the file
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"\nFailed to read '{rel_file_posix}': {e}", file=sys.stderr)
            continue

        # Prepare file content
        file_content = f"```{rel_file_posix}\n{content}\n```\n\n"
        file_length = len(file_content)
        file_tokens = get_token_count(file_content, encoding)

        # Check character and token limits
        if max_chars is not None and (total_chars_copied + file_length) > max_chars:
            print(
                f"\nInfo: Adding '{rel_file_posix}' would exceed character limit. Skipping.",
                file=sys.stderr,
            )
            skipped_files.append(rel_file_posix)
            total_files_skipped += 1
            total_lines_skipped += content.count("\n") + 1
            continue

        if max_tokens is not None and (total_tokens_copied + file_tokens) > max_tokens:
            print(
                f"\nInfo: Adding '{rel_file_posix}' would exceed token limit. Skipping.",
                file=sys.stderr,
            )
            skipped_files.append(rel_file_posix)
            total_files_skipped += 1
            total_lines_skipped += content.count("\n") + 1
            continue

        # Add to output
        output += file_content
        total_chars_copied += file_length
        total_tokens_copied += file_tokens
        total_files_added += 1

        # Count lines
        lines_in_file = content.count("\n") + 1
        total_lines_added += lines_in_file

        included_files.add(rel_file_posix)

        # Check limits
        if max_files is not None and total_files_added >= max_files:
            break
        if max_chars is not None and total_chars_copied >= max_chars:
            break
        if max_tokens is not None and total_tokens_copied >= max_tokens:
            break

    output += "</code-sample>"
    summary = {
        "files_added": total_files_added,
        "chars_copied": total_chars_copied,
        "tokens_copied": total_tokens_copied,
        "lines_added": total_lines_added,
        "files_skipped": total_files_skipped,
        "lines_skipped": total_lines_skipped,
        "skipped_files": skipped_files,
    }
    return output, summary


def print_summary(summary, max_files, max_chars, max_tokens):
    """
    Prints a summary of the copy operation.
    """
    print("\n" + "=" * 50)
    print("Summary".center(50))
    print("=" * 50)
    print(
        f"Files Copied       : {summary['files_added']}/{max_files if max_files is not None else '∞'}"
    )
    print(
        f"Total Characters   : {summary['chars_copied']}/{max_chars if max_chars is not None else '∞'}"
    )
    print(
        f"Total Tokens       : {summary['tokens_copied']}/{max_tokens if max_tokens is not None else '∞'}"
    )
    print(f"Total Lines Added  : {summary['lines_added']}")

    if summary["files_skipped"] > 0:
        print("\nWarnings:")
        print("-" * 50)
        print(f"Files Skipped      : {summary['files_skipped']}")
        print(f"Lines Skipped      : {summary['lines_skipped']}")
        print("\nSkipped Files:")
        for file in summary["skipped_files"]:
            print(f" - {file}")
    else:
        print("\nNo files were skipped.")
    print("=" * 50 + "\n")


def perform_copy(args):
    """
    Handles the copy subcommand: collects file contents and copies to clipboard.
    """
    config = load_config()
    include_patterns = config.get("include_patterns", [])
    explicit_files = config.get("explicit_files", [])

    if not include_patterns and not explicit_files:
        print(
            "\nError: No include patterns or explicit files found. Please add patterns or files using the 'add' command before copying.",
            file=sys.stderr,
        )
        return

    # Initialize tiktoken encoding
    try:
        encoding = tiktoken.encoding_for_model(args.model)
    except KeyError:
        print(
            f"\nWarning: Model '{args.model}' not found. Falling back to cl100k_base encoding.",
            file=sys.stderr,
        )
        encoding = tiktoken.get_encoding("cl100k_base")

    file_contents, summary = collect_file_contents(
        include_patterns=include_patterns,
        explicit_files=explicit_files,
        max_files=args.max_files,
        max_chars=args.max_chars,
        max_tokens=args.max_tokens,
        encoding=encoding,
    )

    if summary["files_added"] == 0:
        print(
            "\nNo files to copy after applying limits and .gitignore rules. Please adjust your patterns or limits.",
            file=sys.stderr,
        )
        return

    pyperclip.copy(file_contents)
    print("\nFiles copied to clipboard.")

    # Print the summary
    print_summary(summary, args.max_files, args.max_chars, args.max_tokens)

    # Optional: Estimate remaining tokens
    if args.max_tokens is not None:
        if summary["tokens_copied"] >= args.max_tokens:
            print(
                "Warning: Maximum token limit reached. Some files were skipped to stay within the limit."
            )
        elif summary["tokens_copied"] > 0:
            remaining = args.max_tokens - summary["tokens_copied"]
            print(f"Estimated tokens remaining for LLM: {remaining}")

    print("=" * 50 + "\n")

