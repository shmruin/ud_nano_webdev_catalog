import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.sql import func
 
Base = declarative_base()

 
class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        #Return object data in easily serializable format
        return {
            'id': self.id,
            'name': self.name
        }
 

class CategoryItem(Base):
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable=False)
    description = Column(String(250))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category) 

    @property
    def serialize(self):
        #Return object data in easily serializable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_time': self.time_created,
            'updated_time': self.time_updated,
            'cat_id': self.category_id
        }
 

engine = create_engine('sqlite:///categoryItems.db')
Base.metadata.create_all(engine)