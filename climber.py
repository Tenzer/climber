from flask import Flask, url_for, render_template, g, jsonify, request, redirect
import sqlite3
import arrow
from os import path
import json


app = Flask(__name__)


def connectDatabase():
    '''Connects to the database file'''
    climber_directory = path.dirname(path.abspath(__file__))
    database = sqlite3.connect(path.join(climber_directory, 'database.db'))
    database.row_factory = sqlite3.Row
    return database


def getDatabase():
    '''Get the database handle or set it up if doesn't exist'''
    if not hasattr(g, 'database'):
        g.database = connectDatabase()
    return g.database


def initializeDatabase():
    '''Applies the database schema to the database'''
    with app.app_context():
        db = getDatabase()
        with app.open_resource('schema.sql', mode='r') as schema:
            db.cursor().executescript(schema.read())
        db.commit()


@app.teardown_appcontext
def closeDatabase(error):
    '''Closes the database properly'''
    if hasattr(g, 'database'):
        g.database.close()


def formatGame(game):
    if type(game) is sqlite3.Row:
        game = dict(game)

    date = arrow.get(game['played'].replace(' ', 'T'))
    game['played'] = date.humanize().capitalize()
    return game


@app.route('/')
def index():
    database = getDatabase()
    recent_games = database.execute('''
        SELECT
            games.added AS played,
            winner.name AS winner_name,
            loser.name AS loser_name,
            games.winner_score AS winner_score,
            games.loser_score AS loser_score
        FROM
            games
        JOIN
            players AS winner ON games.winner=winner.id,
            players AS loser ON games.loser=loser.id
        ORDER BY
            games.added DESC
        LIMIT
            3
    ''').fetchall()
    recent_games = map(formatGame, recent_games)
    ranking = database.execute('''
        SELECT
            name,
            games_won,
            games_lost,
            games_streak,
            goals_scored,
            goals_against,
            points
        FROM
            players
        WHERE
            deleted IS NULL
        ORDER BY
            points DESC,
            games_won + games_lost DESC,
            created ASC
    ''').fetchall()
    return render_template('index.html', recent_games=recent_games, ranking=ranking)


@app.route('/results')
def results():
    database = getDatabase()
    results = database.execute('''
        SELECT
            games.added AS played,
            winner.name AS winner_name,
            loser.name AS loser_name,
            games.winner_score AS winner_score,
            games.loser_score AS loser_score,
            games.winner_points AS winner_points,
            games.loser_points AS loser_points
        FROM
            games
        JOIN
            players AS winner ON games.winner=winner.id,
            players AS loser ON games.loser=loser.id
        ORDER BY
            games.added DESC
    ''').fetchall()
    results = map(formatGame, results)
    return render_template('results.html', results=results)


@app.route('/add-result', methods=['GET', 'POST'])
def addResult():
    message = None
    error = None

    database = getDatabase()
    if request.method == 'POST' and request.form:
        pass

    players = database.execute('SELECT id, name FROM players WHERE deleted IS NULL').fetchall()
    return render_template('add-result.html', players=players, message=message, error=error)


@app.route('/add-player', methods=['GET', 'POST'])
def addPlayer():
    message = None
    error = None

    if request.method == 'POST' and request.form:
        try:
            database = getDatabase()
            result = database.execute('''
                INSERT INTO
                    players
                    (name)
                VALUES
                    (?)
            ''', (request.form['player_name'],))
            database.commit()
            message = 'The player has been created.'
        except sqlite3.IntegrityError:
            error = 'A player already exists with that name.'

    return render_template('add-player.html', message=message, error=error)


@app.route('/typeahead-players.json')
def playersJson():
    database = getDatabase()
    players = database.execute('''
        SELECT
            id,
            name
        FROM
            players
        WHERE
            deleted IS NULL
    ''').fetchall()
    return jsonify(players=[dict(player) for player in players])


if __name__ == '__main__':
    initializeDatabase()
    app.debug = True
    app.run()
