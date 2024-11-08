# src/copy_to_clipboard/cli.py

import argparse
import sys
from .config import add_patterns, remove_patterns, list_patterns, clear_all_patterns
from .copier import perform_copy, update_from_clipboard

DEFAULT_INSTRUCTIONS = """\
<code-style>
Always use build in typing when possible, e.g. list, dict, tuple, etc.
Use loguru for all logging. Use loguru's logger instead of print statements.
Use pydantic>=2.0 for data validation and settings management.
</code-style>

<refactor>
Refactor code to use built in typing even when the original uses the typing module.
Refactor code to use loguru for logging instead of print statements.
Refactor code to update from pydantic 1.x to 2.0 for data validation and settings management.
Refactor code to use f-strings for string formatting.
`IFF os.path is used` Refactor code to use pathlib for file path manipulation instead of os.path.
Refactor to use absulete imports instead of relative imports.
Refactor to remove any depricated classes, functions, methods, arguments, etc. (Assume python>=3.12)
</refactor>

Text Generation Protocol
- Only update required files, any other files are for context.
- Assume the latest libraries are installed.
- When updating a file, also refactor it to use the latest libraries and best practices.


If you are ChatGPT, GPT-4, or GPT-4o: Please format the output as a single Markdown (.md) file.
If you are Anthropic Claude: Please use artifacts.
Strictly adhere to the refactoring guidelines.

Always start with the Header (#) for the title.
For complete Python files, encapsulate the content within Python code blocks using:

```python
# path/to/file.py
{full implementation here}
```

Ensure each file starts with a comment that specifies its full path.
When working with code snippets, use ```path/to/file.py``` to specify the file being quoted.
```path/to/file.py
...
specific code snippet
...

```
"""


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
    parser_copy.add_argument(
        "--instructions",
        type=str,
        default=DEFAULT_INSTRUCTIONS,
        help=(
            "Instructions to include before the code samples in the clipboard content. "
            "If not provided, default instructions will be used."
        ),
    )

    # Sub-command: clear-all
    parser_clear = subparsers.add_parser(
        "clear-all", help="Remove all added glob patterns and explicit files."
    )

    # Sub-command: update-files
    parser_update = subparsers.add_parser(
        "update-files",
        help="Update file contents based on structured data from the clipboard.",
    )
    # By default, perform a dry run
    parser_update.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Proceed with updating files without prompting for confirmation.",
    )
    parser_update.add_argument(
        "--backup",
        action="store_true",
        help="Create backups of files before updating them.",
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
    elif args.command == "update-files":
        update_from_clipboard(yes=args.yes, backup=args.backup)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
