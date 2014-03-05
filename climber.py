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
    return render_template('index.html', recent_games=recent_games)

if __name__ == '__main__':
    app.debug = True
    app.run()
