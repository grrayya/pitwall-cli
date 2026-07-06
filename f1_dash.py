import requests
import argparse
from rich.console import Console
from rich.table import Table

console = Console()

# Configuration Constants
POINTS_WEIGHT = 1.0
WINS_BONUS = 15.0
BASE_CHANCE = 5.0
TIMEOUT_SECONDS = 10

def get_standings():
    """Fetches the current season's driver standings from the Jolpica API safely."""
    url = "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"
    
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    
    standings_lists = data['MRData']['StandingsTable']['StandingsLists']
    if not standings_lists:
        raise ValueError("No standings data available yet for this season.")
        
    return standings_lists[0]['DriverStandings']

def get_schedule():
    """Fetches the current season's race schedule safely."""
    url = "https://api.jolpi.ca/ergast/f1/current.json"
    
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    
    races = data['MRData']['RaceTable']['Races']
    if not races:
        raise ValueError("No race schedule available yet for this season.")
        
    return races

def calculate_form_index(standings):
    """Calculates a normalized Championship Form Index based on points and wins."""
    driver_scores = []
    
    for driver in standings:
        points = float(driver.get('points', 0))
        wins = float(driver.get('wins', 0))
        
        raw_score = (points * POINTS_WEIGHT) + (wins * WINS_BONUS) + BASE_CHANCE
        
        given_name = driver.get('Driver', {}).get('givenName', 'Unknown')
        family_name = driver.get('Driver', {}).get('familyName', 'Driver')
        
        driver_scores.append({
            "name": f"{given_name} {family_name}",
            "score": raw_score,
            "original_data": driver
        })
        
    total_score = sum(d['score'] for d in driver_scores)
    
    # If no points have been scored at all yet, distribute equally
    if total_score == 0:
        for d in driver_scores:
            d['form_index'] = 100.0 / len(driver_scores)
        return driver_scores
        
    for d in driver_scores:
        d['form_index'] = (d['score'] / total_score) * 100
        
    return driver_scores

def print_standings(standings):
    """Formats and prints the standings and form indices using Rich."""
    analyzed_drivers = calculate_form_index(standings)

    table = Table(title="🏎️ F1 Driver Standings & Championship Form Index")
    table.add_column("Pos", justify="right", style="cyan", no_wrap=True)
    table.add_column("Driver", style="magenta")
    table.add_column("Constructor", style="green")
    table.add_column("Points", justify="right", style="yellow")
    table.add_column("Wins", justify="right", style="red")
    table.add_column("Form Index", justify="right", style="green bold")

    for d in analyzed_drivers:
        driver = d['original_data']
        form_string = f"{d['form_index']:.1f}%"
        
        # Defensive check for constructors list
        constructors = driver.get('Constructors', [])
        constructor_name = constructors[0].get('name', 'N/A') if constructors else 'N/A'
        
        table.add_row(
            driver.get('position', '-'),
            d['name'],
            constructor_name,
            driver.get('points', '0'),
            driver.get('wins', '0'),
            form_string
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
            race.get('round', '-'),
            race.get('raceName', 'Unknown Grand Prix'),
            race.get('Circuit', {}).get('circuitName', 'Unknown Circuit'),
            race.get('date', 'TBD')
        )
    
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Pitwall CLI - F1 Terminal Dashboard")
    
    # Enforce mutual exclusivity at the CLI level
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--standings", action="store_true", help="Show current driver standings and form index")
    group.add_argument("--schedule", action="store_true", help="Show the upcoming race schedule")
    
    args = parser.parse_args()

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

if __name__ == "__main__":
    main()
