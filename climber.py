from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    recent_games = [
        {
            'day': 'Monday',
            'challenger': 'Jeppe',
            'opponent': 'Mads',
            'challenger_score': 10,
            'opponent_score': 7
        },
        {
            'day': 'Today',
            'challenger': 'Jaap',
            'opponent': 'Jaime',
            'challenger_score': 4,
            'opponent_score': 10
        }
    ]
    ranking = [
        {
            'name': 'Jeppe',
            'games_won': 10,
            'games_lost': 3,
            'games_streak': 3,
            'goals_scored': 74,
            'goals_against': 22,
            'points': 128
        }
    ]
    return render_template('index.html', recent_games=recent_games, ranking=ranking)

if __name__ == '__main__':
    app.debug = True
    app.run()
