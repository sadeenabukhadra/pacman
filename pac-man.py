"""Launch Pac-Man and report missing dependencies clearly."""

import sys


def launch() -> int:
    """Start the game or report a missing dependency."""
    try:
        from main import main
    except ModuleNotFoundError as error:
        if error.name == "pygame":
            print(
                "ERROR: pygame-ce is not installed in this "
                "Python environment.\n"
                "Activate your virtual environment, then run:\n"
                "  python -m pip install -r requirements.txt",
                file=sys.stderr,
            )
            return 1
        print(
            f"ERROR: Required module '{error.name}' was not found.\n"
            "Check the project files and install its dependencies.",
            file=sys.stderr,
        )
        return 1

    return main()


if __name__ == "__main__":
    raise SystemExit(launch())
