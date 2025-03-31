from flask import Flask, render_template
import fastf1
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)

os.makedirs('cache', exist_ok=True)
fastf1.Cache.enable_cache('cache')
def get_next_race():
    # Load schedule
    schedule = fastf1.get_event_schedule(datetime.now().year)

    # ✅ Drop any row where RoundNumber is missing
    schedule = schedule.dropna(subset=['RoundNumber'])

    # ✅ Skip Bahrain explicitly
    schedule = schedule[schedule['EventName'] != 'Bahrain Grand Prix']

    # ✅ Sort by RoundNumber and pick the next one
    schedule = schedule.sort_values(by='RoundNumber')

    if not schedule.empty:
        next_race = schedule.iloc[2]  # Getting the next race
        return {
            'name': next_race['EventName'],
            'location': next_race['Location'],
            'round': int(next_race['RoundNumber']),
            'dates1': next_race['Session1Date'].strftime('%Y-%m-%d %H:%M') if pd.notna(next_race['Session1Date']) else 'N/A',
            'dates2': next_race['Session2Date'].strftime('%Y-%m-%d %H:%M') if pd.notna(next_race['Session2Date']) else 'N/A',
            'dates3': next_race['Session3Date'].strftime('%Y-%m-%d %H:%M') if pd.notna(next_race['Session3Date']) else 'N/A',
            'dates4': next_race['Session4Date'].strftime('%Y-%m-%d %H:%M') if pd.notna(next_race['Session4Date']) else 'N/A',
            'dates5': next_race['Session5Date'].strftime('%Y-%m-%d %H:%M') if pd.notna(next_race['Session5Date']) else 'N/A'
        }

    return None

def previous_race_results():
    fastf1.Cache.enable_cache('cache')
    
    try:
        # ✅ Hardcoded year and round number
        race = fastf1.get_session(2025, 1, 'R')
        race.load()

        # ✅ Print available keys to debug the missing field issue
        print(race.results.columns)

        # ✅ Prepare results
        results = []
        for _, driver in race.results.iterrows():
            results.append({
                'driver': f"{driver.get('Abbreviation', 'N/A')} ({driver.get('TeamName', 'N/A')})",
                'laps': driver.get('NumberOfLaps', 'N/A'),  # Handle missing field
                'time': driver.get('Time', 'DNF') if pd.notna(driver.get('Time')) else 'DNF',
                'status': driver.get('Status', 'N/A')
            })
        
        return {
            'race_name': race.event['EventName'],
            'location': race.event['Location'],
            'date': race.event['Session5Date'].strftime('%Y-%m-%d') if pd.notna(race.event['Session5Date']) else 'N/A',
            'results': results
        }
    except Exception as e:
        print(f"Error loading race data: {e}")
        return None



@app.route('/')
def home():
    upcoming_race = get_next_race()
    last_race = previous_race_results()
    
    return render_template('home.html', upcoming_race=upcoming_race, last_race=last_race)

@app.route('/teams/teams_select')
def teams_select():
    return render_template('teams_select.html')
@app.route('/teams/redbull')
def redbull():
    return render_template('redbull.html')

@app.route('/teams/ferrari')
def ferrari():
    return render_template('ferrari.html')

@app.route('/teams/mercedes')
def mercedes():
    return render_template('mercedes.html')

@app.route('/teams/mclaren')
def mclaren():
    return render_template('mclaren.html')

@app.route('/teams/astonmartin')
def astonmartin():
    return render_template('astonmartin.html')

@app.route('/teams/williams')
def williams():
    return render_template('williams.html')

@app.route('/teams/alpine')
def alpine():
    return render_template('alpine.html')

@app.route('/teams/haas')
def haas():
    return render_template('haas.html')

@app.route('/teams/racingbulls')
def racingbulls():
    return render_template('racingbulls.html')

@app.route('/teams/kicksauber')
def kicksauber():
    return render_template('kicksauber.html')
if __name__ == '__main__':
    app.run(debug=True)
