#!/bin/python

from sqlalchemy import Column, ForeingKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()




#Table_A
#__tablename__ = 'some_table'

#columname = Column(attributes,...)
#e.g. 
#name = Column(String(80), nullable = False) 
#id = Column(Integer, primary_key = True)

#Table_B
#place_id = Column(Integer, ForeingKey('table_a.id'))
#table_a = relationship(Table_A)


class Shelter(Base):
	__tablename__ = 'shelter'
	name = Column(String(80), nullable = False)
	address = Column(String(100), nullable = False)
	city = Column(String(80), nullable = False)
	state = Column(String(80), nullable = False)
	zipCode = Column(Integer, nullable = False)
	website = Column(String(200))
	id = Column(Integer, primary_key = True)


class Puppy(Base):
	__tablename__ = 'puppy'
	name = Column(String(80), nullable = False)
	birth_date = Column(String(80), nullable = False) # provisional date
	gender = Column(Boolean, nullable = False) # 1 means boy, 0 means girl...
	weight = Column(Integer) # weight in grams
	shelter_id = Column(Integer,ForeingKey('shelter.id'))

	shelter = relationship(Shelter)

#open DB
engine = create_engine('sqlite:///puppy_shelter.db')