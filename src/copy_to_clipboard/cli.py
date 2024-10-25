import argparse
import sys
from .config import add_patterns, remove_patterns, list_patterns, clear_all_patterns
from .copier import perform_copy


def main():
    parser = argparse.ArgumentParser(
        description="""copy-to-clipboard: A tool to copy project files to clipboard using pattern-based selection.

Patterns use glob syntax similar to .gitignore for familiarity.
Examples of common glob patterns:
  - Add all files recursively:
      ctc add "**/*"

  - Add all Python files:
      ctc add "**/*.py"

  - Add all JavaScript files in 'src' directory and subdirectories:
      ctc add "src/**/*.js"

  - Add all Markdown and text files:
      ctc add "**/*.md" "**/*.txt"

  - Add an explicit file (even if it's in .gitignore):
      ctc add "path/to/ignored-file.file"
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Sub-command: add
    parser_add = subparsers.add_parser(
        "add",
        help="Add specific files by glob pattern or explicit file path.",
    )
    parser_add.add_argument(
        "patterns",
        nargs="+",
        help='Glob patterns or specific file paths to add (e.g., "*.py", "src/**/*.js", "path/to/file.txt")',
    )

    # Sub-command: remove
    parser_remove = subparsers.add_parser(
        "remove", help="Remove specific glob patterns or explicit file paths."
    )
    parser_remove.add_argument(
        "patterns", nargs="+", help="Glob patterns or file paths to remove"
    )

    # Sub-command: list
    parser_list = subparsers.add_parser(
        "list", help="List all added glob patterns and explicit files."
    )

    # Sub-command: copy
    parser_copy = subparsers.add_parser(
        "copy", help="Copy files matching the added patterns to clipboard."
    )
    # Arguments for 'copy' sub-command
    parser_copy.add_argument(
        "--max-files",
        type=int,
        default=50,
        help="Maximum number of files to include (default: 50)",
    )
    parser_copy.add_argument(
        "--max-chars",
        type=int,
        default=1000000,
        help="Maximum number of characters to copy (default: 1,000,000)",
    )
    parser_copy.add_argument(
        "--max-tokens",
        type=int,
        default=128000,
        help="Maximum number of tokens to copy (default: 128,000)",
    )
    parser_copy.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        help="LLM model to estimate tokens for (default: gpt-3.5-turbo)",
    )

    # Sub-command: clear-all
    parser_clear = subparsers.add_parser(
        "clear-all", help="Remove all added glob patterns and explicit files."
    )

    args = parser.parse_args()

    if args.command == "add":
        add_patterns(args.patterns)
    elif args.command == "remove":
        remove_patterns(args.patterns)
    elif args.command == "list":
        list_patterns()
    elif args.command == "copy":
        perform_copy(args)
    elif args.command == "clear-all":
        clear_all_patterns()
    else:
        parser.print_help()
        sys.exit(1)

