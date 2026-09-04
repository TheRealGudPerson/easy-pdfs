import os
import platform
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
SPEC_FILE = PROJECT_ROOT / "EasyPDF.spec"


def print_header():
    print()
    print("=" * 60)
    print("EasyPDF Setup")
    print("=" * 60)
    print()


def run_command(command, description):
    print()
    print("-" * 60)
    print(description)
    print("-" * 60)
    print()

    print(">", " ".join(str(x) for x in command))
    print()

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        print()
        print("=" * 60)
        print("Command failed.")
        print("=" * 60)
        print()
        sys.exit(result.returncode)


def check_python():
    print(
        f"Python: {platform.python_version()}"
    )

    if sys.version_info < (3, 10):
        print()
        print(
            "EasyPDF requires Python 3.10 or newer."
        )
        sys.exit(1)


def install_dependencies():
    if not REQUIREMENTS_FILE.exists():
        print()
        print(
            f"Could not find {REQUIREMENTS_FILE.name}."
        )
        sys.exit(1)

    run_command(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        ],
        "Updating pip...",
    )

    run_command(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(REQUIREMENTS_FILE),
        ],
        "Installing EasyPDF dependencies...",
    )


def install_pyinstaller():
    run_command(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "pyinstaller",
        ],
        "Installing PyInstaller...",
    )


def run_easypdf():
    app_file = PROJECT_ROOT / "app.py"

    if not app_file.exists():
        print()
        print(
            "Could not find app.py."
        )
        sys.exit(1)

    print()
    print("=" * 60)
    print("Starting EasyPDF...")
    print("=" * 60)
    print()

    result = subprocess.run(
        [
            sys.executable,
            "app.py",
        ],
        cwd=PROJECT_ROOT,
    )

    sys.exit(result.returncode)


def build_easypdf():
    if not SPEC_FILE.exists():
        print()
        print(
            "Could not find EasyPDF.spec."
        )
        sys.exit(1)

    install_pyinstaller()

    run_command(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            str(SPEC_FILE),
        ],
        "Building EasyPDF with PyInstaller...",
    )

    print()
    print("=" * 60)
    print("EasyPDF build completed successfully.")
    print("=" * 60)
    print()

    dist_directory = PROJECT_ROOT / "dist"

    if platform.system() == "Windows":
        executable = dist_directory / "EasyPDF.exe"

        if executable.exists():
            print(
                f"Executable: {executable}"
            )

    elif platform.system() == "Darwin":
        application = dist_directory / "EasyPDF.app"

        if application.exists():
            print(
                f"Application: {application}"
            )

    else:
        print(
            f"Build output: {dist_directory}"
        )

    print()


def main():
    print_header()
    check_python()

    print()
    print("What would you like to do?")
    print()
    print("  1. Run EasyPDF")
    print("  2. Install / build EasyPDF")
    print("  3. Exit")
    print()

    while True:
        choice = input(
            "Select an option [1-3]: "
        ).strip()

        if choice in ("1", "2", "3"):
            break

        print(
            "Please enter 1, 2, or 3."
        )

    if choice == "3":
        print()
        print("Exiting.")
        return

    print()

    # Both modes need the application dependencies.
    install_dependencies()

    if choice == "1":
        run_easypdf()

    elif choice == "2":
        build_easypdf()


if __name__ == "__main__":
    main()