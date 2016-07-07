import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id          = Column(Integer, primary_key = True)
    name        = Column(String(80), nullable = False)
    email       = Column(String(80), nullable = True)
    picture     = Column(String(80), nullable = True)

class Restaurant(Base):
    __tablename__ = 'restaurant'
    id      = Column(Integer, primary_key = True)
    name    = Column(String(80), nullable = False)
    user_id = Column(Integer,ForeignKey('user.id'))
    
    user            = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }
    
class MenuItem(Base):
    __tablename__   = 'menu_item'
    id              = Column(Integer, primary_key=True)
    name            = Column(String(20))
    description     = Column(String(150))
    price           = Column(String(20))
    course          = Column(String(20))
    restaurant_id   = Column(Integer,ForeignKey('restaurant.id'))
    user_id         = Column(Integer,ForeignKey('user.id'))

    restaurant      = relationship(Restaurant)
    user            = relationship(User)

    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }
    


engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.create_all(engine)