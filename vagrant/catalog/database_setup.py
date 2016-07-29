import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy import Numeric, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id          = Column(Integer, primary_key = True)
    name        = Column(String(80), nullable = False)
    email       = Column(String(80), nullable = True)
    picture     = Column(String(80), nullable = True)


class Category(Base):
    __tablename__   = 'category'
    id              = Column(Integer, primary_key = True)
    name            = Column(String(80), nullable = False)
    user_id         = Column(Integer,ForeignKey('user.id'))
    
    user            = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
        }

class CategoryItem(Base):
    __tablename__   = 'category_item'
    id              = Column(Integer, primary_key = True)
    name            = Column(String(80), nullable = False)
    date_added      = Column(DateTime, default=func.now())
    description     = Column(Text)
    category_id     = Column(Integer, ForeignKey('category.id'))
    user_id         = Column(Integer,ForeignKey('user.id'))
    
    category        = relationship(Category)
    user            = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'date_added' : self.date_added
        }


engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.create_all(engine)