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


CREATE TABLE IF NOT EXISTS matches(
	winner serial NOT NULL REFERENCES players (id),
	loser serial NOT NULL REFERENCES players (id),
	round integer NOT NULL DEFAULT(1),
	match_id serial NOT NULL,
	PRIMARY KEY (match_id)
);