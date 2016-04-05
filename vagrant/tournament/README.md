
# Udacity's Web developer full stack Project 2
==============================================================

This project helps to manage a simple tournament in the Swiss system
where every  player gets to play in every round. 

## Install
------------

To properly use the tourname.py module these pre-requisites must be met.
* PostgreSQL 9.3.11 installed
* psycopg2 module installed
* Before starting the test, run the tournamet.sql script

The easiest way to test this code is with [Vagrant](https://www.vagrantup.com/)

Follow these steps to get you started:

1. Install [Vagrant](https://www.vagrantup.com/)
2. Install [VirtualBox](https://www.virtualbox.org/)
3. Install [cygwin](https://www.cygwin.com/), be sure to select **git** from le packages list 

---------------

## Setting up the environment

1. Clone my tournament repository 
    * Open a cygwin terminal
    * execute `git clone https://github.com/ulitosCoder/fullstack-nanodegree-vm`
2. Navigate to the ntournament directory
    * `cd fullstack-nanodegree-vm/vagrant/tournament/`
3. Start the Vagrant VM
    * `vagrant up`

   The source code in the repository will be accessible in the VM with the synced folders in /vagrant/
   
-------------------

## Running the code

After the Vagrant VM was prepared log into it by executing `vagrant ssh`, in the tournament directory in your cygwin terminal.

Once inside the VM do the following:

1. `cd /vagrant/tournament/`
2. `psql`

Once you are in the PosrgreSQL console proceed to create the database and the schema

1. `create database tournament;`
2. `\c tournament`
3. `\i tournament.sql`
4. `\q`

Run the `tournament_test.py` script

* `python tournament_test.py`

------------------------

For furher details check this [Getting started](https://docs.google.com/document/d/16IgOm4XprTaKxAa8w02y028oBECOoB1EI1ReddADEeY/pub?embedded=true) guide





