-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

--CREATE DATABASE tournament;

CREATE TABLE IF NOT EXISTS players(
	name varchar(80) NOT NULL,
	id serial NOT NULL,
	PRIMARY KEY (id)
);


DROP VIEW IF EXISTS standings;

DROP TABLE IF EXISTS  matches;
CREATE TABLE IF NOT EXISTS matches(
	winner serial NOT NULL REFERENCES players (id),
	loser serial NOT NULL REFERENCES players (id),
	match_id serial NOT NULL,
	PRIMARY KEY (match_id),
	UNIQUE (winner, loser)
);

CREATE OR REPLACE VIEW standings AS (
	select q1.id as id,name,wins,COALESCE(rnds_cnt,0) as rounds_cnt

		from ( 
			select pl1.id,pl1.name,count(winner) as wins
			from players  as pl1 left join matches on id=winner 
			group by pl1.id
			order by wins desc
		) as q1
		left join (
			select id,count(id) as rnds_cnt
			from players,matches
			where id=winner or id=loser
			group by id
		) as q2
		on q1.id=q2.id

	order by wins desc, rnds_cnt asc
);