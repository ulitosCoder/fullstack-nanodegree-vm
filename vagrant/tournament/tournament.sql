-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

--CREATE DATABASE tournament;

DROP VIEW IF EXISTS scores;
DROP VIEW IF EXISTS standings;
DROP VIEW IF EXISTS players_scores;
DROP VIEW IF EXISTS players_loses;
DROP VIEW IF EXISTS players_wins;
DROP VIEW IF EXISTS players_matches;

DROP TABLE IF EXISTS  matches;
DROP TABLE IF EXISTS players;
CREATE TABLE IF NOT EXISTS players(
	name varchar(80) NOT NULL,
	score integer DEFAULT 0,
	id serial NOT NULL,
	PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS matches(
	winner serial NOT NULL REFERENCES players (id),
	loser serial NOT NULL REFERENCES players (id),
	match_id serial NOT NULL,
	PRIMARY KEY (match_id),
	UNIQUE (winner, loser),
	UNIQUE (loser, winner)
);



CREATE OR REPLACE VIEW players_wins AS(
	select pl.id,pl.name,count(winner) as wins
	from players  as pl left join matches on id=winner 
	group by pl.id
);

CREATE OR REPLACE VIEW players_loses AS(
	select pl.id,pl.name,count(loser) as loses
	from players  as pl left join matches on id=loser 
	group by pl.id
);

CREATE OR REPLACE VIEW players_matches AS(
	select id,count(id) as rnds_cnt
	from players,matches
	where id=winner or id=loser
	group by id
);


CREATE OR REPLACE VIEW players_scores AS(
	select pw.id as id,pw.name as name, wins, loses,rnds_cnt as matches
	from players_wins as pw, players_loses as pls,players_matches as pms 
	where pw.id = pls.id and pw.id = pms.id
);

--This VIEW gets the stadings of the tournamet by joining the players table
--whith the matches table, this view doesn't apply yet methods for unties
--The first part is to left join the players table with the matcher but couting
--the number of wins in the matches query and grouped by player id.
--The second part counts the matches of each player by mixing the rows of
--the tables, but each player must appers as winner or loser, the gourps the
--resulting rows by player id.
--Finally both subqueries are joined so we can get number of wins and number of
--matches for each player

CREATE OR REPLACE VIEW standings AS (
	select q1.id as id,name,wins,COALESCE(rnds_cnt,0) as rounds_cnt

		from ( 
			select *
			from players_wins
			order by wins desc
		) as q1
		left join (
			select * from players_matches
		) as q2
		on q1.id=q2.id

	order by wins desc, rnds_cnt asc
);