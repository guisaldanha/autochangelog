# AUTOCHANGELOG

Autochangelog is a tool to automatically generate changelogs, like [this](CHANGELOG.md), from git commits.

## What is this?

This is a tool to automatically generate a CHANGELOG.md file from your git history.

## How to install?

### On Windows

1. Download the latest release from [here](https://guisaldanha.com/downloads/autochangelog.exe) and extract it to the Windows directory, or add the Windows directory to the PATH environment variable.
2. Ready. You can now use the autochangelog command on any folder on your computer.

### How to use

1. Open a terminal in the folder you want to generate the changelog for.
2. Run the command `autochangelog`.
3. Ready. You can now find the changelog in the `CHANGELOG.md` file.

**Note:** If you want create subtitles for each commit, you can use the `:` character in the commit message. For example, if you want to create a subtitle called "Added", you can use the commit message `Added: Added a new feature`. The subtitle will be created automatically and the commits will be added to it.

## Many options

You can use the following options:

    Generate CHANGELOG.md from git log

    options:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit
    -a, --amend           Amend the last commit with the generated CHANGELOG.md. The CHANGELOG.md file will be added to the last commit.
    -p, --push            Push the last commit to the remote origin, if it exists.
    -ap, --amend-push     Amend the last commit and push it to the remote origin, if it exists.
    -g GIT_PATH, --git_path GIT_PATH
                            Path to the directory containing the git repository. For the current directory, use '.' or leave blank.
    -t TEMPLATE_PATH, --template_path TEMPLATE_PATH
                            Path to the template file. To use the built-in template in the program, leave it blank.
    -o OUTPUT_PATH, --output_path OUTPUT_PATH
                            Path to the directory to save CHANGELOG.md. For the current directory, use '.' or leave blank.
    -r REMOTE_GIT, --remote_git REMOTE_GIT
                            URL of the remote git repository. If the remote origin is set, it will be used.
    -c CHANGELOG_FILE, --changelog_file CHANGELOG_FILE
                            Name of the CHANGELOG.md file. Default is CHANGELOG.md

    Example: autochangelog -g /path/to/git/repository -t /path/to/template_file.md -o /path/to/output -u -p

## Using Jinja2 templates

You can use Jinja2 templates to customize the output of the CHANGELOG.md file. You can use the following variables:

- **changelog** - List of tags. Each tag has the following attributes:
  - **tag** - List of tags. Each tag has the following attributes:
    - **tag** - Tag name.
    - **message** - Tag message.
    - **date** - Tag date.
    - **changes** - List of changes. Each change has the following attributes:
      - **changes** - A list of changes. Each change has the following attributes:
        - **message** - Commit message.
        - **date** - Commit date.
        - **hash** - Commit hash.
        - **user** - The user who made the commit.
- **remote_git** - URL of the remote git repository.

## How to contribute

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Create a pull request.
5. Done.

Or you can just open an issue if you find a bug or want to suggest a new feature.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
