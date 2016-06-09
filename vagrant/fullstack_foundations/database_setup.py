import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    
    
class MenuItem(Base):
    __tablename__ = 'menu_item'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    description = Column(String(150))
    price = Column(String(20))
    course = Column(String(20))
    restaurant_id = Column(Integer,ForeignKey('restaurant.id'))

    restaurant = relationship(Restaurant)
    


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)