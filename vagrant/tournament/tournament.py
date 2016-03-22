#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def genericDelete(table_name):
    """Generic function to delete the rows of a given table

        Args:
            table_name: the table to be truncated

    """

    db = connect()

    query = "DELETE FROM %s" % table_name

    c = db.cursor()
    
    c.execute(query)

    db.commit()
    db.close()


def deleteMatches():
    """Remove all the match records from the database."""

    genericDelete("matches")


def deletePlayers():
    """Remove all the player records from the database."""

    genericDelete("players")


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()

    curs = db.cursor()
    query = "SELECT COUNT(id) as players_count FROM players"
    curs.execute(query)
    aux = curs.fetchone()

    players = int(aux[0])

    db.close()

    return players


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    db = connect()

    c = db.cursor()

    query = "INSERT INTO players (name) VALUES (%s)"

    # as noted on
    # http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries
    data = (name, )

    c.execute(query, data)

    db.commit()

    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    NOTE: check tournamer.sql for detailed description in the 'standings' view

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    db = connect()
    c = db.cursor()

    query = "SELECT *  from standings"
    c.execute(query)

    standings = c.fetchall()

    query = "SELECT score FROM players WHERE id = {player_id}"
    players_count = len(standings)
    idx = 0
    while idx < players_count:
        # in this loop check if two players have the same wins,
        w1 = standings[idx][2]
        w2 = standings[idx+1][2]

        # if the players are matched, get the individual score of each
        # and swap places if necessary
        if w1 == w2:
            id1 = standings[idx][0]
            c.execute(query.format(player_id=id1))
            s1 = c.fetchone()
            s1 = int(s1[0])

            id2 = standings[idx+1][0]
            c.execute(query.format(player_id=id2))
            s2 = c.fetchone()
            s2 = int(s2[0])

            if s2 > s1:
                print "swaping players"
                entry1 = standings[idx]
                standings[idx] = standings[idx+1]
                standings[idx+1] = entry1

        idx = idx + 2

    db.close()

    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    This procedure also will update the player's score in the players table

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    db = connect()
    c = db.cursor()

    # these following lines will retrieve
    query = "SELECT score FROM players WHERE id = %s"

    data = (winner, )
    c.execute(query, data)
    w_score = c.fetchone()
    w_score = int(w_score[0])

    data = (loser, )
    c.execute(query, data)
    l_score = c.fetchone()
    l_score = int(l_score[0])

    # these criteria rewards/punish a player depending on
    # how strog is the opponent
    # e.g. a winner gets more points for defeating a stronger player that if
    # the opponent was weaker
    # e.g.2 A loser's punish is bigger if the winner was weaker
    if w_score == l_score:
        w_score = w_score + 2
        l_score = l_score - 2
    elif w_score < l_score:
        w_score = w_score + 3
        l_score = l_score - 3
    else:
        w_score > l_score
        w_score = w_score + 1
        l_score = l_score - 1

    query = "UPDATE players SET score = %s WHERE id = %s"

    data = (w_score, winner, )
    c.execute(query,data)

    data = (l_score, loser, )
    c.execute(query, data)

    query = "INSERT INTO matches (winner,loser) VALUES (%s,%s)" 

    data = (winner, loser)
    c.execute(query, data)

    db.commit()

    db.close()


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
    thePairings = []
    standings = playerStandings()

    players_count = len(standings)
    db = connect()
    c = db.cursor()

    players_items = [item[0:2] for item in standings]

    idx = 0
    while idx < players_count:
        newt = players_items[idx][0], players_items[idx][1], \
            players_items[idx+1][0], players_items[idx+1][1]
        thePairings.append(newt)
        idx = idx + 2

    db.close()

    return thePairings
