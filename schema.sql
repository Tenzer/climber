CREATE TABLE IF NOT EXISTS players (
    id            INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL UNIQUE,
    created       INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted       INTEGER,
    games_won     INTEGER NOT NULL DEFAULT 0,
    games_lost    INTEGER NOT NULL DEFAULT 0,
    games_streak  INTEGER NOT NULL DEFAULT 0,
    goals_scored  INTEGER NOT NULL DEFAULT 0,
    goals_against INTEGER NOT NULL DEFAULT 0,
    points        REAL    NOT NULL DEFAULT 1000
);

CREATE TABLE IF NOT EXISTS games (
    id            INTEGER PRIMARY KEY,
    added         INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
    winner        INTEGER NOT NULL,
    loser         INTEGER NOT NULL,
    winner_score  INTEGER NOT NULL DEFAULT 0,
    loser_score   INTEGER NOT NULL DEFAULT 0,
    winner_points REAL    NOT NULL DEFAULT 0,
    loser_points  REAL    NOT NULL DEFAULT 0,

    FOREIGN KEY(winner) REFERENCES players(id),
    FOREIGN KEY(loser) REFERENCES players(id)
);
