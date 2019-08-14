from init_db import Base
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    category = relationship('Category', backref='user')
    item = relationship('Item', backref='user')

    def __repr__(self):
        return "<User(name='%s', email='%s')>" % (self.name, self.email)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    item = relationship("Item", backref='category')
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        return {
    'id': self.id,
    'name': self.name,
    'Item': [i.serialize for i in self.item]
        }

    def __repr__(self):
        return "<Category(name='%s')>" % (self.name)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200))
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        return {
    'cat_id': self.category_id,
    'description': self.description,
    'id': self.id,
    'title': self.name
        }

    def __repr__(self):
        return "<Item(name='%s', description='%s')>" % (self.name, self.description)