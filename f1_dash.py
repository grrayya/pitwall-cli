import requests
import argparse
from rich.console import Console
from rich.table import Table

console = Console()

def get_standings():
    """Fetches the current season's driver standings from the Jolpica API."""
    url = "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"
    response = requests.get(url).json()
    return response['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

def get_schedule():
    """Fetches the current season's race schedule."""
    url = "https://api.jolpi.ca/ergast/f1/current.json"
    response = requests.get(url).json()
    return response['MRData']['RaceTable']['Races']

def calculate_probabilities(standings):
    """Calculates heuristic win probabilities based on points and previous wins."""
    POINTS_WEIGHT = 1.0
    WINS_BONUS = 15.0
    BASE_CHANCE = 5.0

    driver_scores = []
    
    # Calculate raw momentum scores
    for driver in standings:
        points = float(driver['points'])
        wins = float(driver['wins'])
        
        raw_score = (points * POINTS_WEIGHT) + (wins * WINS_BONUS) + BASE_CHANCE
        
        driver_scores.append({
            "name": f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}",
            "score": raw_score,
            "original_data": driver
        })
        
    # Normalize to exactly 100%
    total_score = sum(d['score'] for d in driver_scores)
    
    for d in driver_scores:
        d['win_probability'] = (d['score'] / total_score) * 100
        
    return driver_scores

def print_standings(standings):
    """Formats and prints the standings and probabilities using Rich."""
    analyzed_drivers = calculate_probabilities(standings)

    table = Table(title="🏎️ Current F1 Driver Standings & Win Probabilities")
    table.add_column("Pos", justify="right", style="cyan", no_wrap=True)
    table.add_column("Driver", style="magenta")
    table.add_column("Constructor", style="green")
    table.add_column("Points", justify="right", style="yellow")
    table.add_column("Wins", justify="right", style="red")
    table.add_column("Next Race Win %", justify="right", style="green bold")

    for d in analyzed_drivers:
        driver = d['original_data']
        prob_string = f"{d['win_probability']:.1f}%"
        
        table.add_row(
            driver['position'],
            d['name'],
            driver['Constructors'][0]['name'],
            driver['points'],
            driver['wins'],
            prob_string
        )
    
    console.print(table)

def print_schedule(races):
    """Formats and prints the race schedule using Rich."""
    table = Table(title="📅 F1 Race Schedule")
    table.add_column("Round", justify="right", style="cyan")
    table.add_column("Race", style="magenta")
    table.add_column("Circuit", style="green")
    table.add_column("Date", style="yellow")

    for race in races:
        table.add_row(
            race['round'],
            race['raceName'],
            race['Circuit']['circuitName'],
            race['date']
        )
    
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Pitwall CLI - F1 Terminal Dashboard")
    parser.add_argument("--standings", action="store_true", help="Show current driver standings and win probabilities")
    parser.add_argument("--schedule", action="store_true", help="Show the upcoming race schedule")
    args = parser.parse_args()

    # Route the command to the correct functions based on flags
    if args.standings:
        try:
            with console.status("[bold green]Fetching live F1 standings..."):
                standings = get_standings()
            print_standings(standings)
        except Exception as e:
            console.print(f"[red]Error fetching standings: {e}[/red]")
            
    elif args.schedule:
        try:
            with console.status("[bold green]Fetching race schedule..."):
                races = get_schedule()
            print_schedule(races)
        except Exception as e:
            console.print(f"[red]Error fetching schedule: {e}[/red]")
            
    else:
        console.print("[red]Please specify a flag! Try running:[/red] [cyan]python pitwall.py --standings[/cyan]")

if __name__ == "__main__":
    main()
