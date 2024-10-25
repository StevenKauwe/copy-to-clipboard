# Copy-to-Clipboard

**Copy-to-Clipboard** is a command-line tool that allows you to copy selected project files to your clipboard using pattern-based selection. It's handy for sharing code snippets, configurations, or any text-based files quickly.

## Features

- **Pattern-Based Selection:** Choose files to copy using glob patterns similar to `.gitignore`.
- **Flexible Limits:** Control the number of files, characters, and tokens included in the clipboard content.
- **Summary Report:** Get a detailed summary after copying.
- **Clipboard Integration:** Seamlessly copies the aggregated file contents to your clipboard.
- **Respect `.gitignore`:** By default, files listed in `.gitignore` are excluded unless explicitly added.

## Installation

Ensure you have Python 3.12 or higher installed.

You can install `copy-to-clipboard` using `pipx` for isolated and easy installation:

```bash
pipx install git+https://github.com/stevenk/copytoclipboard.git
```

Alternatively, if you have cloned the repository locally, navigate to the project directory and run:

```bash
pipx install .
```

## Usage

After installation, use the `ctc` command to interact with the tool.

### Add Patterns or Explicit Files

Add glob patterns to select which files to include or add specific file paths to include ignored files.

```bash
# Adding glob patterns
ctc add "**/*.py" "**/*.md"

# Adding an explicit file (even if it's in .gitignore)
ctc add "path/to/ignored-file.file"
```

### Remove Patterns or Explicit Files

Remove specific glob patterns or explicit file paths.

```bash
# Removing glob patterns
ctc remove "**/*.txt"

# Removing an explicit file
ctc remove "path/to/ignored-file.file"
```

### List Patterns and Explicit Files

List all currently added glob patterns and explicit files.

```bash
ctc list
```

### Clear All Patterns and Explicit Files

Remove all added glob patterns and explicit files.

```bash
ctc clear-all
```

### Copy to Clipboard

Aggregate the contents of the selected files and copy them to the clipboard.

```bash
ctc copy --max-files 100 --max-chars 500000 --max-tokens 128000 --model gpt-3.5-turbo
```

**Arguments:**

- `--max-files`: Maximum number of files to include (default: 50)
- `--max-chars`: Maximum number of characters to copy (default: 1,000,000)
- `--max-tokens`: Maximum number of tokens to copy (default: 128,000)
- `--model`: LLM model to estimate tokens for (default: gpt-3.5-turbo)

**Behavior:**

- **Respecting `.gitignore`:** By default, any files or directories listed in your `.gitignore` will be excluded from the copy operation. To include a file that is normally ignored, add its specific path using the `add` command without wildcards.
  
  ```bash
  # Assuming 'secrets.env' is in .gitignore
  ctc add "secrets.env"
  ```

## Examples

- **Add All Python Files:**

  ```bash
  ctc add "**/*.py"
  ```

- **Add an Explicit Ignored File:**

  ```bash
  ctc add "path/to/ignored-file.file"
  ```

- **Copy Files with Default Limits:**

  ```bash
  ctc copy
  ```

- **Copy with Custom Limits:**

  ```bash
  ctc copy --max-files 100 --max-chars 500000
  ```

## Configuration

The tool stores its configuration in a file named `.copytoclipboard_config.json`. By default, it checks the current directory and then the user's home directory for this configuration file. The configuration separates glob patterns and explicit file paths.

```json
{
    "include_patterns": ["**/*.py", "**/*.md"],
    "explicit_files": ["path/to/ignored-file.file"]
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Support

If you encounter any issues or have questions, feel free to open an issue on the [GitHub repository](https://github.com/skauwe/copy-to-clipboard).
