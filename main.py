from AutoChangelog import AutoChangelog
import argparse


def main():
    VERSION = "Changelog Generator 1.0.3"

    parser = argparse.ArgumentParser(
        prog='autochangelog',
        description='Generate CHANGELOG.md from git log',
        epilog='Example: autochangelog -g /path/to/git/repository -t /path/to/template_file.md -o /path/to/output -u -p'
    )
    parser.version = VERSION
    parser.author = 'Guilherme Saldanha'
    parser.add_argument("-v", "--version", action="version")
    parser.add_argument(
        "-a", "--amend", help="Amend the last commit with the generated CHANGELOG.md. The CHANGELOG.md file will be added to the last commit.",
        action="store_true")
    parser.add_argument(
        "-p", "--push", help="Push the last commit to the remote origin, if it exists.",
        action="store_true")
    parser.add_argument(
        "-ap", "--amend-push", help="Amend the last commit and push it to the remote origin, if it exists.",
        action="store_true")
    parser.add_argument(
        "-f", "--force", help="Add the -f command to the amend and push commands",
        action="store_true")
    parser.add_argument(
        "-rm", "--remove_message", help="Remove the autocreated message from CHANGELOG.md file",
    )
    parser.add_argument(
        "-g", "--git_path", help="Path to the directory containing the git repository. For the current directory, use '.' or leave blank.")
    parser.add_argument(
        "-t", "--template_path", help="Path to the template file. To use the built-in template in the program, leave it blank.")
    parser.add_argument(
        "-o", "--output_path", help="Path to the directory to save CHANGELOG.md. For the current directory, use '.' or leave blank.")
    parser.add_argument(
        "-r", "--remote_git", help="URL of the remote git repository. If the remote origin is set, it will be used.")
    parser.add_argument(
        "-c", "--changelog_file", help="Name of the CHANGELOG.md file. Default is CHANGELOG.md")

    args = parser.parse_args()

    if args.amend_push:
        args.amend = True
        args.push = True

    delattr(args, 'amend_push')

    # convert args to kwargs
    args = vars(args)

    changelog = AutoChangelog(**args)


if __name__ == "__main__":
    main()
