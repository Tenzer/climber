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

    date = arrow.get(game['added'].replace(' ', 'T'))
    game['added'] = date.humanize().capitalize()
    return game


def prepareResult(result):
    if int(result['team1_goals']) > int(result['team2_goals']):
        return {
            'winners': result.getlist('team1'),
            'winners_string': ','.join(result.getlist('team1')),
            'losers': result.getlist('team2'),
            'losers_string': ','.join(result.getlist('team2')),
            'winners_score': result['team1_goals'],
            'losers_score': result['team2_goals']
        }
    else:
        return {
            'winners': result.getlist('team2'),
            'winners_string': ','.join(result.getlist('team2')),
            'losers': result.getlist('team1'),
            'losers_string': ','.join(result.getlist('team1')),
            'winners_score': result['team2_goals'],
            'losers_score': result['team1_goals']
        }

def playerExists(player_id):
    database = getDatabase()
    result = database.execute('''
        SELECT
            count(id) AS found
        FROM
            players
        WHERE
            id = ?
    ''', player_id).fetchone()[0]
    return result


@app.route('/')
def index():
    database = getDatabase()
    recent_games = database.execute('''
        SELECT
            added,
            winners,
            losers,
            winners_score,
            losers_score
        FROM
            games
        ORDER BY
            added DESC
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
            added,
            winners,
            losers,
            winners_score,
            losers_score,
            winners_points,
            losers_points
        FROM
            games
        ORDER BY
            added DESC
    ''').fetchall()
    results = map(formatGame, results)
    return render_template('results.html', results=results)


@app.route('/add-result', methods=['GET', 'POST'])
def addResult():
    message = None
    error = None

    database = getDatabase()
    if request.method == 'POST' and request.form:
        checked_players = []
        for player_id in request.form.getlist('team1') + request.form.getlist('team2'):
            if player_id in checked_players:
                error = 'A player was specified multiple times, please check your input.'
                break

            if not playerExists(player_id):
                error = 'One of the players in the input does not exist in the database.'
                break

            checked_players.append(player_id)

        if not error:
            result = prepareResult(request.form)

            database.execute('''
                INSERT INTO
                    games
                (
                    winners,
                    losers,
                    winners_score,
                    losers_score
                )
                VALUES (
                    :winners_string,
                    :losers_string,
                    :winners_score,
                    :losers_score
                )
            ''', result)

            for player_id in result['winners']:
                result['player_id'] = player_id
                database.execute('''
                    UPDATE
                        players
                    SET
                        games_won = games_won + 1,
                        goals_scored = goals_scored + :winners_score,
                        goals_against = goals_against + :losers_score,
                        games_streak = CASE
                            WHEN games_streak < 1 THEN
                                1
                            ELSE
                                games_streak + 1
                        END
                    WHERE
                        id = :player_id
                ''', result)

            for player_id in result['losers']:
                result['player_id'] = player_id
                database.execute('''
                    UPDATE
                        players
                    SET
                        games_lost = games_lost + 1,
                        goals_scored = goals_scored + :losers_score,
                        goals_against = goals_against + :winners_score,
                        games_streak = CASE
                            WHEN games_streak < 1 THEN
                                games_streak - 1
                            ELSE
                                -1
                        END
                    WHERE
                        id = :player_id
                ''', result)

            database.commit()
            message = 'The result has been saved.'

    players = database.execute('''
        SELECT
            id,
            name
        FROM
            players
        WHERE
            deleted IS NULL
        ORDER BY
            name ASC
    ''').fetchall()
    return render_template('add-result.html', players=players, message=message, error=error)


@app.route('/add-player', methods=['GET', 'POST'])
def addPlayer():
    message = None
    error = None

    if request.method == 'POST' and request.form:
        try:
            database = getDatabase()
            database.execute('''
                INSERT INTO
                    players
                (
                    name
                )
                VALUES (
                    :player_name
                )
            ''', request.form)
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
    app.run(host='0.0.0.0')
