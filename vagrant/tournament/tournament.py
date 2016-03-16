#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")



def genericDelete(table_name):
    """Generic function to truncate a given table

        Args:
            table_name: the table to be truncated

    """

    db = connect()

    query = "DELETE FROM %s;" % table_name

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

    name = name.replace("'","''")
    
    query  = "INSERT INTO players (name) VALUES ('%s')" % name

    c.execute(query)
    
    db.commit()

    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

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

    players_count = len(standings)
    idx = 0
    while idx < players_count:
        # in this loop check if two players have the same wins,

        idx = idx + 2


    db.close()

    return standings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    db = connect()
    c = db.cursor()

    query = "SELECT score FROM players WHERE id = {player_id}"

    c.execute(query.format(player_id=winner))
    w_score = c.fetchone()
    w_score = int(w_score[0])

    c.execute(query.format(player_id=loser))
    l_score = c.fetchone()
    l_score = int(l_score[0])

    if w_score == l_score:
        #sum 2 to winner
        #sub 2 to loser
        w_score = w_score + 2
        l_score = l_score - 2
    elif w_score < l_score:
        #sum 3 to winner
        #sub 3 to loser
        w_score = w_score + 3
        l_score = l_score - 3
    else:
        w_score > l_score
        #sum 1 to winner
        #sub 1 to loser
        w_score = w_score + 1
        l_score = l_score - 1

    query = "UPDATE players SET score = {new_score} WHERE id = {player_id}"

    c.execute(query.format(new_score=w_score,player_id=winner))

    c.execute(query.format(new_score=l_score,player_id=loser))

    query = "INSERT INTO matches (winner,loser) VALUES (%d,%d)" % (winner,loser)

    c.execute(query)

    db.commit()

    query = "SELECT * FROM players"
    c.execute(query)
    print "querying all"
    print c.fetchall()

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
    print "players: ", players_count
    
    db = connect()
    c = db.cursor()

    player = [ item[0:2] for item in standings]

    #for atuple in player:
    #    print atuple

    idx = 0
    while idx < players_count:
        newt = player[idx], player[idx+1]
        thePairings.append(newt)
        idx = idx + 2

    db.close()

    #print thePairings
    
    return thePairings

