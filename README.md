# 📜 AUTOCHANGELOG

[![License](https://img.shields.io/github/license/guisaldanha/autochangelog?style=flat-square)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/guisaldanha/autochangelog?style=flat-square)](https://github.com/guisaldanha/autochangelog/releases/latest)
[![Tests](https://img.shields.io/github/actions/workflow/status/guisaldanha/autochangelog/tests.yml?style=flat-square&label=tests)](.github/workflows/tests.yml)
[![Downloads](https://img.shields.io/github/downloads/guisaldanha/autochangelog/total?style=flat-square)](https://github.com/guisaldanha/autochangelog/releases)

Autochangelog is a tool to automatically generate changelogs, like [this](CHANGELOG.md), from git commits.

## ❓ What is this?

This is a tool to automatically generate a CHANGELOG.md file from your git history.

## 📦 How to install?

### 🪟 On Windows

1. Download `AutoChangelogSetup<version>.exe` from the [latest release](https://github.com/guisaldanha/autochangelog/releases/latest).
2. Run it. Choose "install for me only" (no admin rights needed) and keep the "Add to PATH" option checked.
3. Open a **new** terminal window (PATH changes don't apply to terminals already open). You can now use the `autochangelog` command on any folder on your computer.

Uninstalling removes it from PATH again automatically.

> **Upgrading from an old manual install?** Older versions of this README suggested copying `autochangelog.exe` directly into the `C:\Windows` folder to get it on PATH. Windows always searches `C:\Windows` before it looks at the PATH variable at all, so if you did that, that old copy will keep shadowing any newer version you install - including this installer's. Delete `C:\Windows\autochangelog.exe` (requires an elevated/admin terminal) before installing the new version.

### 🐧 On Linux or macOS

1. Download `autochangelog-linux-<arch>.tar.gz` or `autochangelog-macos-<arch>.tar.gz` from the [latest release](https://github.com/guisaldanha/autochangelog/releases/latest) (`<arch>` is `x86_64` or `arm64`, matching your machine).
2. Extract it: `tar -xzf autochangelog-*.tar.gz`.
3. Make it executable and put it on your PATH, e.g.: `chmod +x autochangelog && sudo mv autochangelog /usr/local/bin/`.
4. Open a new terminal and run `autochangelog`.

macOS may block the binary as being from an unidentified developer since it isn't code-signed. If so, allow it once with `xattr -d com.apple.quarantine autochangelog` before running it.

### 🛠️ From source

The tool is pure Python and runs anywhere Python and git are available:

1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run `python main.py` inside (or with `-g` pointing to) the repository you want a changelog for.

### ▶️ How to use

1. Open a terminal in the folder you want to generate the changelog for.
2. Run the command `autochangelog`.
3. Ready. You can now find the changelog in the `CHANGELOG.md` file.

**Note:** If you want create subtitles for each commit, you can use the `:` character in the commit message. For example, if you want to create a subtitle called "Added", you can use the commit message `Added: Added a new feature`. The subtitle will be created automatically and the commits will be added to it.

## ⚙️ Many options

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

    Example: autochangelog -g /path/to/git/repository -t /path/to/template_file.md -o /path/to/output -p

## 🧩 Using Jinja2 templates

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
        - **pending_amend** - `True` only when `-a`/`--amend`/`-ap` was requested and this is the commit about to be amended. Its hash is about to change (amending rewrites the commit), so the built-in template skips the hash link for this one entry instead of showing a link that would be wrong the moment the amend finishes.
- **remote_git** - URL of the remote git repository.

## 🤝 How to contribute

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Run the test suite (see below) and make sure it passes.
5. Create a pull request.
6. Done.

Or you can just open an issue if you find a bug or want to suggest a new feature.

### 🧪 Running tests

    pip install -r requirements-dev.txt
    pytest

`requirements.txt` only lists what's needed to run `autochangelog` itself. `requirements-build.txt` additionally includes PyInstaller and is only needed if you want to build a native binary yourself: `pyinstaller --noconfirm autochangelog.spec`. This produces `dist/autochangelog.exe` on Windows and `dist/autochangelog` on Linux/macOS (PyInstaller can't cross-compile, so you must run it on each target OS).

The Windows installer is built from `InnoSetup/autochangelog.iss` with [Inno Setup](https://jrsoftware.org/isinfo.php) 6, after the `.exe` above has been built: `ISCC.exe InnoSetup\autochangelog.iss`. Bump `MyAppVersion` in that file together with `_version.py` on each release. The release workflow (`.github/workflows/release-from-tag.yml`) builds the Windows installer plus Linux and macOS binaries, and attaches all of them automatically when a tag is pushed.

## 🛡️ Security

> **Don't trust. Verify.**

Transparency is part of this project.

Before running any software obtained from the Internet, it's good practice to perform an independent audit of the source code. This repository encourages that practice.

[![Audit with ChatGPT](https://img.shields.io/badge/Audit-with%20ChatGPT-10A37F?style=for-the-badge&logo=openai&logoColor=white)](https://chatgpt.com/?q=Analyze%20this%20GitHub%20repository%3A%20https%3A%2F%2Fgithub.com%2Fguisaldanha%2Fautochangelog%0A%0APerform%20a%20complete%20security%20audit.%20Analyze%20all%20the%20source%20code%2C%20dependencies%2C%20scripts%2C%20GitHub%20Actions%20workflows%2C%20and%20configuration%20files.%20Identify%20any%20potentially%20malicious%20behavior%2C%20such%20as%20credential%20theft%2C%20hidden%20data%20exfiltration%2C%20remote%20code%20execution%2C%20automatic%20downloads%2C%20cryptocurrency%20mining%2C%20suspicious%20dependencies%2C%20or%20any%20other%20security%20risk.%20Present%20your%20findings%2C%20explain%20the%20identified%20risks%2C%20and%20state%20whether%20you%20consider%20it%20safe%20to%20run%20this%20project.)
[![Audit with Claude](https://img.shields.io/badge/Audit-with%20Claude-D97757?style=for-the-badge&logo=claude&logoColor=white)](https://claude.ai/new?q=Analyze%20this%20GitHub%20repository%3A%20https%3A%2F%2Fgithub.com%2Fguisaldanha%2Fautochangelog%0A%0APerform%20a%20complete%20security%20audit.%20Analyze%20all%20the%20source%20code%2C%20dependencies%2C%20scripts%2C%20GitHub%20Actions%20workflows%2C%20and%20configuration%20files.%20Identify%20any%20potentially%20malicious%20behavior%2C%20such%20as%20credential%20theft%2C%20hidden%20data%20exfiltration%2C%20remote%20code%20execution%2C%20automatic%20downloads%2C%20cryptocurrency%20mining%2C%20suspicious%20dependencies%2C%20or%20any%20other%20security%20risk.%20Present%20your%20findings%2C%20explain%20the%20identified%20risks%2C%20and%20state%20whether%20you%20consider%20it%20safe%20to%20run%20this%20project.)

<sub>💡 Trust in software should come from the ability to verify how it works, not just the reputation of whoever built it.</sub>

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


------------------------------------------------------------------------

## 👨‍💻 Author

Developed by **Guilherme Saldanha**
- GitHub: [https://github.com/guisaldanha](https://github.com/guisaldanha)
- Site: [https://guisaldanha.com](https://guisaldanha.com)

------------------------------------------------------------------------

# ❤️ Support the Developer

If this project saves you time or helps your workflow, consider supporting its development.

Ways to help:

- ⭐ Star the repository
- 🔁 Share with other developers
- ☕ Buy me a coffee by [clicking here (PayPal)](https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=guisaldanha@gmail.com&item_name=Buy%20a%20coffee%20because%20Autochangelog)

------------------------------------------------------------------------
<div align="center">
  <p>Made with ☕ by Guilherme Saldanha</p>
</div>
