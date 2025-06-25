import subprocess
import os
import sys

def run_flake8():
    """Uruchamia flake8 i zwraca wyniki."""
    print("\n=== Running Flake8 ===")
    try:
        result = subprocess.run(
            ["flake8", "--exclude", "venv", "--statistics", "--count"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        else:
            print("No Flake8 issues found.")
        return result.returncode == 0
    except FileNotFoundError:
        print("Flake8 not installed. Install with: pip install flake8")
        return False


def check_code_quality():
    """Główna funkcja sprawdzająca jakość kodu."""
    print("=== Starting Code Quality Checks ===")

    flake8_passed = run_flake8()

    print("\n=== Summary ===")
    print(f"Flake8: {'PASSED' if flake8_passed else 'FAILED'}")

    return flake8_passed

if __name__ == '__main__':
    if check_code_quality():
        print("\nAll code quality checks passed!")
        exit(0)
    else:
        print("\nSome code quality checks failed.")
        exit(1)