#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = psycopg2.connect("dbname=tournament")
    t = DB.cursor()
    t.execute("DELETE FROM matches")
    t.execute("UPDATE players SET matches = 0")
    t.execute("UPDATE players SET points = 0")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = psycopg2.connect("dbname=tournament")
    t = DB.cursor()
    t.execute("DELETE FROM players")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = psycopg2.connect("dbname=tournament")
    t = DB.cursor()
    t.execute("SELECT COUNT(*) FROM players")
    result = t.fetchone()
    num = result[0]
    DB.close()
    return num


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = psycopg2.connect("dbname=tournament")
    t = DB.cursor()
    t.execute("INSERT INTO players (name, points, matches) VALUES (%s, %s, %s)",
             (name, 0, 0))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = psycopg2.connect("dbname=tournament")
    t = DB.cursor()
    stats = []
    t.execute("SELECT id, name, points, matches FROM players ORDER BY id ASC")
    for row in t.fetchall():
        tup = ((row[0]), (row[1]), (row[2]), (row[3]))
        stats.append(tup)
        tup = ()
    DB.close()
    return stats


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = psycopg2.connect("dbname=tournament")
    t = DB.cursor()
    t.execute("INSERT INTO matches (p1, p2, winner) VALUES (%s, %s, %s)",
             (winner, loser, winner))
    t.execute("UPDATE players SET points = (points + 1) WHERE id = (%s)",
             (winner,))
    t.execute("UPDATE players SET matches = (matches + 1) WHERE id = (%s) OR id = (%s)",
             (winner, loser))
    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    DB = psycopg2.connect("dbname=tournament")
    t = DB.cursor()
    standinglist = []
    matchlist = []
    t.execute("SELECT id, name, points FROM players ORDER BY points DESC")
    for row in t.fetchall():
        idnames = ((row[0]), (row[1]))
        standinglist.append(idnames)
    counter = 0
    while counter < len(standinglist):
        tup = (standinglist[counter]) + (standinglist[counter + 1])
        matchlist.append(tup)
        tup = ()
        counter = counter + 2
    DB.close()
    return matchlist




