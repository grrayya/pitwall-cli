import requests
import argparse
from rich.console import Console
from rich.table import Table

console = Console()

def get_standings():
    url = "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"
    response = requests.get(url).json()
    standings = response['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    return standings

def get_schedule():
    url = "https://api.jolpi.ca/ergast/f1/current.json"
    response = requests.get(url).json()
    races = response['MRData']['RaceTable']['Races']
    return races

def print_standings(standings):
    table = Table(title="🏎️ Current F1 Driver Standings")
    table.add_column("Pos", justify="right", style="cyan", no_wrap=True)
    table.add_column("Driver", style="magenta")
    table.add_column("Constructor", style="green")
    table.add_column("Points", justify="right", style="yellow")
    table.add_column("Wins", justify="right", style="red")

    for driver in standings:
        table.add_row(
            driver['position'],
            f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}",
            driver['Constructors'][0]['name'],
            driver['points'],
            driver['wins']
        )
    
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="F1 Terminal Dashboard")
    parser.add_argument("--standings", action="store_true", help="Show current driver standings")
    parser.add_argument("--schedule", action="store_true", help="Show the upcoming race schedule")
    args = parser.parse_args()

if __name__ == "__main__":
    main()
