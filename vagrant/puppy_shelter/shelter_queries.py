#!/bin/python
from sqlalchemy import create_engine, desc, asc, Date
from sqlalchemy.orm import sessionmaker
import datetime
from puppies import Base, Shelter, Puppy

engine = create_engine('sqlite:///puppyshelter.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()


#1. Query all of the puppies and return the results in ascending alphabetical order

query1 = session.query(Puppy).order_by(asc(Puppy.name)).all()
for item in query1:
	print item.name #, ', ',  item.dateOfBirth

#2. Query all of the puppies that are less than 6 months old organized by the youngest firs
today = datetime.datetime.now().date()
sixMonths = datetime.timedelta(days=(6*30))
sixMonthsAgo = today-sixMonths

query2 = session.query(Puppy).filter( Puppy.dateOfBirth > sixMonthsAgo ).order_by(desc(Puppy.dateOfBirth)).all()
for item in query2:
	
	print item.name , ', ', item.dateOfBirth

#3. Query all puppies by ascending weight
query3 = session.query(Puppy).order_by(asc(Puppy.weight)).all()
#for item in query3:
#	print item.name , ', ',  item.weight

#4. Query all puppies grouped by the shelter in which they are staying
query4 = session.query(Puppy).order_by(asc(Puppy.shelter_id)).all()
#for item in query4:
#	print item.name , ', ',  item.shelter_id
