import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


SEMVER_PATTERN = re.compile(
    r"^v"
    r"(0|[1-9]\d*)"
    r"\."
    r"(0|[1-9]\d*)"
    r"\."
    r"(0|[1-9]\d*)"
    r"(?:-"
    r"[0-9A-Za-z-]+"
    r"(?:\.[0-9A-Za-z-]+)*"
    r")?"
    r"(?:\+"
    r"[0-9A-Za-z-]+"
    r"(?:\.[0-9A-Za-z-]+)*"
    r")?$"
)


def run_git(*args, capture_output=False):
    command = ["git", *args]

    print()
    print(">", " ".join(command))

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=capture_output,
    )

    if capture_output:
        return result

    if result.returncode != 0:
        print()
        print("Git command failed.")
        sys.exit(result.returncode)

    return result


def ask_yes_no(prompt):
    while True:
        answer = input(
            f"{prompt} [y/n]: "
        ).strip().lower()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False

        print(
            "Please enter y or n."
        )


def ask_commit_message():
    while True:
        message = input(
            "Commit message: "
        ).strip()

        if message:
            return message

        print(
            "Commit message cannot be empty."
        )


def ask_tag():
    while True:
        tag = input(
            "Release tag (example: v1.0.0): "
        ).strip()

        if not SEMVER_PATTERN.fullmatch(tag):
            print(
                "Invalid tag."
            )
            print(
                "Use semantic versioning such as "
                "v1.0.0, v1.2.3, or v2.0.0-beta.1."
            )
            continue

        return tag


def ensure_git_repository():
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    if (
        result.returncode != 0
        or result.stdout.strip() != "true"
    ):
        print(
            "This folder is not a Git repository."
        )
        sys.exit(1)


def ensure_clean_tag_does_not_exist(tag):
    result = run_git(
        "rev-parse",
        "--verify",
        f"refs/tags/{tag}",
        capture_output=True,
    )

    if result.returncode == 0:
        print()
        print(
            f"Tag {tag} already exists."
        )
        print(
            "Choose a different version."
        )
        sys.exit(1)


def get_current_branch():
    result = run_git(
        "branch",
        "--show-current",
        capture_output=True,
    )

    branch = result.stdout.strip()

    if not branch:
        print()
        print(
            "Could not determine the current branch."
        )
        sys.exit(1)

    return branch


def main():
    print()
    print("=" * 60)
    print("EasyPDF Release Helper")
    print("=" * 60)
    print()

    ensure_git_repository()

    branch = get_current_branch()

    print(
        f"Current branch: {branch}"
    )

    print()

    commit_message = ask_commit_message()

    print()

    release = ask_yes_no(
        "Is this commit release-worthy?"
    )

    tag = None

    if release:
        print()
        tag = ask_tag()

        ensure_clean_tag_does_not_exist(tag)

    print()
    print("-" * 60)
    print("Release summary")
    print("-" * 60)
    print(
        f"Branch:         {branch}"
    )
    print(
        f"Commit message: {commit_message}"
    )
    print(
        f"Release:        {'YES' if release else 'NO'}"
    )

    if release:
        print(
            f"Tag:            {tag}"
        )

    print("-" * 60)
    print()

    if not ask_yes_no(
        "Continue with these changes?"
    ):
        print()
        print("Cancelled.")
        return

    print()

    # Stage everything.
    run_git(
        "add",
        ".",
    )

    # Check whether there is anything to commit.
    status = run_git(
        "status",
        "--porcelain",
        capture_output=True,
    )

    if not status.stdout.strip():
        print()
        print(
            "There are no changes to commit."
        )
        print(
            "Nothing was pushed."
        )
        return

    # Commit.
    run_git(
        "commit",
        "-m",
        commit_message,
    )

    # Push normal branch.
    run_git(
        "push",
        "origin",
        branch,
    )

    if release:
        print()
        print(
            f"Creating release tag {tag}..."
        )

        run_git(
            "tag",
            tag,
        )

        run_git(
            "push",
            "origin",
            tag,
        )

        print()
        print("=" * 60)
        print("Release tag pushed successfully.")
        print("=" * 60)
        print()
        print(
            f"GitHub Actions should now build EasyPDF {tag}."
        )
        print(
            "The workflow will create the Windows installer "
            "and attach it to the GitHub Release."
        )
        print()

    else:
        print()
        print("=" * 60)
        print("Changes pushed successfully.")
        print("=" * 60)
        print()
        print(
            "No release was created."
        )
        print()


if __name__ == "__main__":
    main()