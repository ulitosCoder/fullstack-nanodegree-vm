from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from puppies import Base, Shelter, Puppy

engine = create_engine('sqlite:///puppyshelter.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()


#1. Query all of the puppies and return the results in ascending alphabetical order

query1 = session.query(Puppy).all()
for item in query1:
	print item.name