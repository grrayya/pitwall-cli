import requests
import argparse
from rich.console import Console
from rich.table import Table

console = Console()

def main():
    parser = argparse.ArgumentParser(description="F1 Terminal Dashboard")
    parser.add_argument("--standings", action="store_true", help="Show current driver standings")
    parser.add_argument("--schedule", action="store_true", help="Show the upcoming race schedule")
    args = parser.parse_args()

if __name__ == "__main__":
    main()
